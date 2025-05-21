import argparse
import logging
import socket
import time
from payload_imu_class import Payload_IMU as IMU, STRUCT_SIZE

if __name__ == "__main__":
    # Initalize argument parser and define the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket-path", dest="socket_path", type=str, default="/tmp/imu_sensor_socket", help="set socket path, match with consumer socket path")
    parser.add_argument("--log-level", dest="log_level", type=str, default="INFO", choices=["INFO", "WARNING", "ERROR", "CRITICAL"])
    parser.add_argument("--frequency-hz", dest="freq_hz", type=int, default=500)
    parser.add_argument("--retries", dest="max_retries", type=int, default=5, help="number of retries before exiting")
    args = parser.parse_args()

    # Set up logger, defining minimum logging level
    logging.basicConfig(level=args.log_level.upper())
    logging.info("Logger has been initialized")

    # Determine sending frequency
    # This initially assumes the data compilation and send operation take negligible time
    sleep_interval = 1.0 / args.freq_hz
    # start_time = int(time.time() * 1000)

    # Create the Unix Compatible Socket
    is_first_reconnect = True
    retries = 0

    while retries <= args.max_retries:
        try:
            # Connect to the socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(args.socket_path)
            is_first_reconnect = True
            retries = 0 

            logging.info("Socket connected successfully")

            # Send data to the socket
            while True:
                try:
                    curr_time = int(time.time() * 1000) # - start_time  # Current time in milliseconds
                    imu = IMU(
                        xAcc=0.0, yAcc=0.0, zAcc=0.0, timestampAcc=curr_time,
                        xGyro=0, yGyro=0, zGyro=0, timestampGyro=curr_time,
                        xMag=0.0, yMag=0.0, zMag=0.0, timestampMag=curr_time
                    )
                    sock.sendall(imu.pack())
                    time.sleep(sleep_interval)

                except ValueError as e:
                    logging.error(f"IMU Error: {e}")
            
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

    if retries >= args.max_retries:
        logging.critical("Max retries reached. Exiting...")
    
    sock.close() # Close the socket
    logging.info("Socket successfully closed")