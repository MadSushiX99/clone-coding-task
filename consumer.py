import argparse
import logging
import socket
import os
import time
from payload_imu_class import Payload_IMU as IMU, STRUCT_SIZE
import threading
from queue import Queue, Empty as QueueEmpty
import quaternion
import numpy as np
from sensor_processing import Extended_Kalman_Filter as EKF, gyro_to_delta_rot, acc_mag_to_euler

def processing_thread(event, queue):
    """
    Thread to handle printing of data.
    """
    is_first_data = True
    is_first_queue_empty = True
    while not event.is_set():
        try:
            result = queue.get(timeout=1) # wait for data to be available in the q
            accel, gyro, mag, dt = result

            if is_first_data:
                # Initialize the Extended Kalman Filter with the first data
                ekf = EKF(quaternion.from_euler_angles(acc_mag_to_euler(accel, mag)))
                is_first_data = False

            # Convert gyro data to delta rotation in radians
            delta_gyro = gyro_to_delta_rot(gyro, dt)

            # Convert accelerometer and magnetometer data to euler angles in radians
            euler_rotation = acc_mag_to_euler(accel, mag)
            
            ekf.predict(delta_gyro) # Predict the next state using the gyroscope data
            ekf.update(euler_rotation) # Update the state with the accelerometer and magnetometer data
            print(ekf.q)

        except QueueEmpty:
            if is_first_queue_empty:
                logging.warning("Queue is empty, waiting for data...")
                is_first_queue_empty = False

if __name__ == "__main__":
    # Initalize argument parser and define the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket-path", dest="socket_path", type=str, default="/tmp/imu_sensor_socket", help="set socket path, match with publisher socket path")
    parser.add_argument("--log-level", dest="log_level", type=str, default="INFO", choices=["INFO", "WARNING", "ERROR", "CRITICAL"])
    parser.add_argument("--timeout-ms", dest="timeout_ms", type=int, default=100)
    parser.add_argument("--max-timeouts", dest="max_timeouts", type=int, default=10, help="number of timeouts before exiting")

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
    sock.listen(1) # listen for 1 incoming connection
    logging.info("Socket path successfully created and binded")

    # Create thread to handle printing of data
    event = threading.Event()
    queue = Queue()

    try:
        logging.info("Waiting for incoming connection...")
        conn, _ = sock.accept() # accept incoming connection

        logging.info("Socket connection successfully accepted")
        sock.settimeout(60)
        conn.settimeout(float(args.timeout_ms / 1000))

        process_thread = threading.Thread(target=processing_thread, args=(event,queue,))
        process_thread.start()

        # Initialize variables for last state and current state
        timeouts = 0
        prev_timestamp = 0
        euler_state = [0, 0, 0]
        is_first_data = True
        
        while timeouts < args.max_timeouts:
            try:
                data, _ = conn.recvfrom(STRUCT_SIZE) # receive data from the socket
                if data:
                    result = IMU.unpack(data) # unpack the data and print it

                    if is_first_data:
                        prev_timestamp = result.timestampGyro
                        euler_state = acc_mag_to_euler([result.xAcc, result.yAcc, result.zAcc], [result.xMag, result.yMag, result.zMag])
                        is_first_data = False

                    accel = [result.xAcc, result.yAcc, result.zAcc]
                    gyro = [result.xGyro, result.yGyro, result.zGyro]
                    mag = [result.xMag, result.yMag, result.zMag]
                    dt = float(result.timestampGyro - prev_timestamp) / 1000 # convert to milliseconds
                    prev_timestamp = result.timestampGyro
                    
                    # Perform Processing in a thread to preserve real-time data capture
                    queue.put([accel, gyro, mag, dt])

                else:
                    # No data means the publisher has disconnected, so only need to accept a new connection
                    try:
                        logging.info("Publisher disconnected, attempting reconnect")
                        conn, _ = sock.accept() # accept incoming connection
                        conn.settimeout(float(args.timeout_ms / 1000))
                    except socket.timeout:
                        logging.critical("Publisher disconnected for over a minute, unable to reconnect")
                        break

            except socket.timeout:
                # Publisher may still be connected, so kill the connection and try again
                timeouts += 1
                logging.warning(f"Socket timed out, total timeouts: {timeouts}")
                time.sleep(1)

    except KeyboardInterrupt:
        print()
        logging.critical("Keyboard interrupt detected, forcing exiting")

    if timeouts >= args.max_timeouts:
        logging.critical("Max timeouts reached, consider checcking the connection or changing the (1) publisher frequency or (2) timeout-ms. Now exiting...")

    event.set() # set the event to stop the printing thread
    process_thread.join() # wait for the printing thread to finish
    logging.info("Process thread successfully stopped")

    conn.close() # close the connection
    logging.info("Socket connection successfully closed")

    sock.close() # close the socket
    logging.info("Socket successfully closed")

    os.remove(args.socket_path) # remove the socket path
    logging.info("Socket path successfully removed")
        

    