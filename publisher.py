import argparse
import logging
import socket
import time
import random
from payload_imu_class import Payload_IMU as IMU, STRUCT_SIZE

def dataloader(csv_path):
    """
    Load data from a CSV file and return it as a list of tuples.

    Args:
        csv_path (str): Path to the CSV file.
    Returns:
        list: A list of tuples containing the data from the CSV file
    """
    data = []
    is_first_line = True
    with open(csv_path, 'r') as f:
        for line in f:
            if is_first_line:
                is_first_line = False
                continue
            # Skip the header line
            values = line.strip().split(',')
            data.append(tuple(map(float, values)))
    return data


if __name__ == "__main__":
    # Initalize argument parser and define the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket-path", dest="socket_path", type=str, default="/tmp/imu_sensor_socket", help="set socket path, match with consumer socket path")
    parser.add_argument("--log-level", dest="log_level", type=str, default="INFO", choices=["INFO", "WARNING", "ERROR", "CRITICAL"])
    parser.add_argument("--frequency-hz", dest="freq_hz", type=int, default=500)
    parser.add_argument("--retries", dest="max_retries", type=int, default=5, help="number of successive retries before exiting")
    parser.add_argument("--data-mode", dest="data_mode", type=str, default="random", choices=["csv", "random"], help="data mode to use")
    args = parser.parse_args()

    # Set up logger, defining minimum logging level
    logging.basicConfig(level=args.log_level.upper())
    logging.info("Logger has been initialized")

    # Determine sending frequency
    sleep_interval = 1.0 / args.freq_hz

    # Create the Unix Compatible Socket
    is_first_reconnect = True
    retries = 0
    count = 0

    try:
        # Load data from CSV file for faster processing
        if args.data_mode == "csv":
            data = dataloader("sensor_data.csv")

    # Retry loop for socket connection
        while retries <= args.max_retries:
            try:

                # Connect to the socket
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.connect(args.socket_path)
                is_first_reconnect = True
                retries = 0
                logging.info("Socket connected successfully")

                # Main loop to send data to the consumer
                while True:
                    try:
                        if args.data_mode == "csv":
                            # Simulate data from the CSV file
                            if count < len(data):
                                t, xG, yG, zG, xA, yA, zA, xM, yM, zM = data[count]

                                # Pack the data into the IMU class, converting units from the CSV to match the struct format provided
                                imu = IMU(
                                    xAcc=xA*1000, yAcc=yA*1000, zAcc=zA*1000, timestampAcc=int(t*1000),
                                    xGyro=int(xG*1000), yGyro=int(yG*1000), zGyro=int(zG*1000), timestampGyro=int(t*1000),
                                    xMag=xM*10, yMag=yM*10, zMag=zM*10, timestampMag=int(t*1000)
                                )
                                count += 1
                            else:
                                logging.info("End of data")
                                break # End of data, break the loop

                        elif args.data_mode == "random":
                            curr_time = int(time.time() * 1000) # Current time in milliseconds

                            # Generate random data for the IMU class, with somewhat realistic ranges based on the CSV file
                            imu = IMU(
                                xAcc=random.uniform(-1000,1000), yAcc=random.uniform(-1000,1000), zAcc=random.uniform(-1000,1000), timestampAcc=curr_time,
                                xGyro=random.randint(-135000, 135000), yGyro=random.randint(-135000, 135000), zGyro=random.randint(-135000, 135000), timestampGyro=curr_time,
                                xMag=random.uniform(-250, 250), yMag=random.uniform(-250, 250), zMag=random.uniform(-450, -320), timestampMag=curr_time
                            )
                        sock.sendall(imu.pack())
                        time.sleep(sleep_interval)

                    # If there is an issue with recieved data, log the error and continue
                    except ValueError as e:
                        logging.error(f"IMU Error: {e}")
                
                # If the data mode is CSV, check if all data has been sent and if so, exit
                if args.data_mode == "csv":
                    if count >= len(data):
                        logging.info("All data sent, exiting...")
                        break
            
            # If communication breaks, log the error and attempt to reconnect
            except socket.error as e:
                logging.error(f"Socket error: {e}")
                sock.close()
                if retries < args.max_retries:
                    if is_first_reconnect:
                        logging.info("Attempting to reconnect to socket...")
                        is_first_reconnect = False
                    else:
                        time.sleep(5)  # Wait before retrying
                retries += 1

        # Log exit in the basis of retries maxxing out        
        if retries >= args.max_retries:
            logging.critical("Max retries reached. Exiting...")

        # Close the socket
        sock.close() 
        logging.info("Socket successfully closed")

    except KeyboardInterrupt:
        print()
        logging.critical("Keyboard interrupt detected, forcing exiting")
        
        # Close the socket
        sock.close() 
        logging.info("Socket successfully closed")

    except Exception as e:
        logging.critical(f"An unexpected error occurred: {e}")
    