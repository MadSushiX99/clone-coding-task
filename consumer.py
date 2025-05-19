import argparse
import logging
import socket
import os
from payload_imu_class import Payload_IMU as IMU, STRUCT_SIZE

def accel_to_rot():
    """
    Convert acceleration to rotation.
    """
    pass

def gyro_to_rot():
    """
    Convert gyroscope data to rotation.
    """
    pass

def mag_to_rot():
    """
    Convert magnetometer data to rotation.
    """
    pass

def calc_confidence():
    """
    Calculate confidence level.
    """
    pass

def sensor_fusion():
    """
    Perform sensor fusion.
    """
    pass

if __name__ == "__main__":
    # Initalize argument parser and define the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket-path", dest="socket_path", type=str, help="set socket path, match with publisher socket path")
    parser.add_argument("--log-level", dest="log_level", type=str, default="INFO", choices=["INFO", "WARNING", "ERROR", "CRITICAL"])
    parser.add_argument("--timeout-ms", dest="timeout_ms", type=int, default=100)
    args = parser.parse_args()


    # Set up logger, defining minimum logging level
    logging.basicConfig(level=args.log_level.upper())
    logging.info("Logger successfully initialized")

    # Create the Unix Compatible Socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    # Check socket path and link to socket
    if os.path.exists(args.socket_path):
        os.remove(args.socket_path)
        logging.info("Socket Path already existed. It has been removed")
    
    sock.bind(args.socket_path)
    sock.listen(1) # listen for incoming connections
    logging.info("Socket path successfully created and binded")
    logging.info("Waiting for incoming connection...")

    try:
        conn, _ = sock.accept() # accept incoming connection
        logging.info("Socket connection successfully accepted")
        conn.settimeout(float(args.timeout_ms / 1000)) # settimeout is in seconds, converting ms to seconds as type float
        
        while True:
            try:
                data, addr = conn.recvfrom(STRUCT_SIZE) # receive data from the socket
                if data:
                    print(IMU.unpack(data).xAcc) # unpack the data and print it
                
                else:
                    # No data means the publisher has disconnected, so only need to accept a new connection
                    logging.info("Publisher disconnected, attempting reconnect")
                    conn, _ = sock.accept() # accept incoming connection
            
            except socket.timeout:
                # Publisher may still be connected, so kill the connection and try again
                logging.warning("Socket timeout")
                conn.close()
                conn, _ = sock.accept()
                conn.settimeout(float(args.timeout_ms / 1000))

    except KeyboardInterrupt:
        logging.critical("\nKeyboard interrupt detected, forcing exiting")

    conn.close() # close the connection
    sock.close() # close the socket
    os.remove(args.socket_path) # remove the socket path
    logging.info("Socket path successfully removed")
        

    