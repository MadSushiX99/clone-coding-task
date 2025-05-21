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
from visualizer import Visualizer

def processing_thread(event, queue):
    """
    Thread to handle conversion of raw data to euler angles and quaternions.
    This thread will run in parallel to the main thread and will process data from the queue.

    Args:
        event: Event object to signal when to stop the thread.
        queue: Queue object to get data from the main thread.
    """

    # Initialize Visualizer if enabled
    if args.visualize:
        plotter = Visualizer()
        logging.info("Visualizer Enabled")

    # Define Flags and Initial State
    is_first_data = True
    is_first_queue_empty = True
    counter = 0
    gyro_state = np.array([0, 0, 0])

    while not event.is_set():
        try:
            result = queue.get(timeout=1) # wait for data to be available in the q
            accel, gyro, mag, dt = result

            if is_first_data:
                # Initialize the Extended Kalman Filter with the first data
                gyro_state = acc_mag_to_euler(accel, mag)
                ekf = EKF(quaternion.from_euler_angles(gyro_state))
                is_first_data = False

            # Convert gyro data to delta rotation in radians
            delta_gyro = gyro_to_delta_rot(gyro, dt)
            gyro_state = gyro_state + np.array(delta_gyro)

            # Convert accelerometer and magnetometer data to euler angles in radians
            euler_rotation = acc_mag_to_euler(accel, mag)
            
            # Do Prediction and Update with the Extended Kalman Filter
            ekf.predict(delta_gyro) # Predict the next state using the gyroscope data
            ekf.update(euler_rotation) # Update the state with the accelerometer and magnetometer data

            # Print the quaternions at the specified verbosity rate
            if counter % args.verbosity_rate == 0:
                gyro_norm = quaternion.from_euler_angles(gyro_state).normalized()
                acc_mag_norm = quaternion.from_euler_angles(euler_rotation).normalized() 
                fusion_norm = ekf.q.normalized() 
                logging.info(f"Gyro:          W:{gyro_norm.w:.3} X:{gyro_norm.x:.3} Y:{gyro_norm.y:.3} Z:{gyro_norm.z:.3}")
                logging.info(f"Accel & Mag:   W:{acc_mag_norm.w:.3} X:{acc_mag_norm.x:.3} Y:{acc_mag_norm.y:.3} Z:{acc_mag_norm.z:.3}")
                logging.info(f"Fused Result:  W:{fusion_norm.w:.3} X:{fusion_norm.x:.3} Y:{fusion_norm.y:.3} Z:{fusion_norm.z:.3}")
                counter = 0
            counter += 1

            # Update plot with the new data if visualization is enabled
            if args.visualize:
                plotter.update_plot(gyro_state, euler_rotation, ekf.q) # Update the plot with the new data

        # If Queue is empty, wait for data to be available
        except QueueEmpty:
            if is_first_queue_empty:
                logging.warning("Queue is empty, waiting for data...")
                is_first_queue_empty = False

    # If visualization is enabled, close the plot when the thread is stopped
    if args.visualize:
        plotter.close() # Close the plot when the thread is stopped




if __name__ == "__main__":
    # Initalize argument parser and define the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket-path", dest="socket_path", type=str, default="/tmp/imu_sensor_socket", help="set socket path, match with publisher socket path")
    parser.add_argument("--log-level", dest="log_level", type=str, default="INFO", choices=["INFO", "WARNING", "ERROR", "CRITICAL"])
    parser.add_argument("--timeout-ms", dest="timeout_ms", type=int, default=100)
    parser.add_argument("--max-timeouts", dest="max_timeouts", type=int, default=10, help="number of timeouts before exiting")
    parser.add_argument("--visualize", dest="visualize", action="store_true", help="enable visualization of the data")
    parser.add_argument("--no-visualize", dest="visualize", action="store_false", help="disable visualization of the data")
    parser.add_argument("--verbosity-rate", dest="verbosity_rate", type=int, default=500, help="rate of verbosity for the logger")
    parser.set_defaults(visualize=True)

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

        # Set the socket and connection timeouts
        sock.settimeout(60)
        conn.settimeout(float(args.timeout_ms / 1000))

        # Start the processing thread
        process_thread = threading.Thread(target=processing_thread, args=(event,queue,))
        process_thread.start()
        logging.info("Processing thread started")

        # Initialize variables for last state and current state
        timeouts = 0
        prev_timestamp = 0
        euler_state = [0, 0, 0]
        is_first_data = True
        
        while timeouts < args.max_timeouts:
            try:
                data, _ = conn.recvfrom(STRUCT_SIZE) # receive data from the socket

                # If data is received, unpack it and process it
                if data:
                    result = IMU.unpack(data) # unpack the data and print it

                    if is_first_data:
                        prev_timestamp = result.timestampGyro
                        euler_state = acc_mag_to_euler([result.xAcc, result.yAcc, result.zAcc], [result.xMag, result.yMag, result.zMag])
                        is_first_data = False

                    # Unpack Data into the respective variables
                    accel = [result.xAcc, result.yAcc, result.zAcc]
                    gyro = [result.xGyro, result.yGyro, result.zGyro]
                    mag = [result.xMag, result.yMag, result.zMag]
                    dt = float(result.timestampGyro - prev_timestamp) / 1000 # convert to seconds
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

    # Force exit with keyboard interrupt
    except KeyboardInterrupt:
        print()
        logging.critical("Keyboard interrupt detected, forcing exiting")

    # Log exit based on timeout if max timeouts is reached
    if timeouts >= args.max_timeouts:
        logging.critical("Max timeouts reached, consider checcking the connection or changing the (1) publisher frequency or (2) timeout-ms. Now exiting...")


    # Close everything and log it
    
    event.set() # set the event to stop the printing thread
    process_thread.join() # wait for the printing thread to finish
    logging.info("Process thread successfully stopped")

    conn.close() # close the connection
    logging.info("Socket connection successfully closed")

    sock.close() # close the socket
    logging.info("Socket successfully closed")

    os.remove(args.socket_path) # remove the socket path
    logging.info("Socket path successfully removed")
        

    