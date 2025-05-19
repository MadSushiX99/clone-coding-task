import argparse
import logging
import socket
import time
from payload_imu_class import Payload_IMU as IMU, STRUCT_SIZE

if __name__ == "__main__":
    # Initalize argument parser and define the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket-path", dest="socket_path", type=str, help="set socket path, match with consumer socket path")
    parser.add_argument("--log-level", dest="log_level", type=str, default="INFO", choices=["INFO", "WARNING", "ERROR", "CRITICAL"])
    parser.add_argument("--frequency-hz", dest="freq_hz", type=int, default=500)
    parser.add_argument("--retries", type=int, default=5, help="number of retries before exiting")
    args = parser.parse_args()

    # Set up logger, defining minimum logging level
    logging.basicConfig(level=args.log_level.upper())
    logging.info("Logger has been initialized")

    # Determine sending frequency
    # This initially assumes the data compilation and send operation take negligible time
    sleep_interval = 1.0 / args.freq_hz

    # Create the Unix Compatible Socket
    first_connection = True

    while True:
        try:
            # Connect to the socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(args.socket_path)
            first_connection = False
            logging.info("Socket connected successfully")

            # Send data to the socket
            while True:
                imu = IMU(
                    xAcc=0.0, yAcc=0.0, zAcc=0.0, timestampAcc=0,
                    xGyro=0.0, yGyro=0.0, zGyro=0.0, timestampGyro=0,
                    xMag=0.0, yMag=0.0, zMag=0.0, timestampMag=0
                )
                sock.sendall(imu.pack())
                time.sleep(sleep_interval)

        except socket.error as e:
            logging.error(f"Socket error: {e}")
            sock.close()
            if first_connection:
                logging.critical("Socket connection failed, exiting")
                exit(1)
            else:
                logging.info("Attempting to reconnect to socket...")
                time.sleep(1)