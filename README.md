# Clone Robotics Coding Task: Driver for Custom Protocol

In this coding task, I have created a publisher and consumer using IPC socket communication. The publisher sends packed binary data of a custom `Payload_IMU` class to the consumer. The consumer unpacks this data and extracts rotation information from these sensors. 

## Getting Started

#### Basic Setup
Python 3.10.x was used to write the code in this repo. Please use the provided `requirements.txt` to install any or all dependencies you don't have already.

```
pip install -r requirements.txt
```

#### Setup with Conda

If using Conda you can create a new Conda Environment using the provided `environment.yml` file
```
conda env create -f environment.yml
```
After this completes you can open the Conda Environment by typing
```
conda activate clone_task
```

## Running the System

To run the system, in separate terminal windows first run the `consumer.py` then run `publisher.py`. Both programs have default values for all the arguments, so they can be run as-is:
```
python3 consumer.py
```

```
python3 publisher.py
```

### Consumer Arguments

* `--socket-path` - Default Value: `/tmp/imu_sensor_socket`
* `--log-level` - Default Value: `INFO`, Options: `[INFO, WARNING, ERROR, CRITICAL]`
* `--timeout-ms` - Default Value: `100`
* `--max-timeouts` - Default Value: `10`

Example:
```
python3 consumer.py --socket-path "/tmp/socket_stream" --log-level INFO --timeout-ms 100 
```
### Publisher Arguments

* `--socket-path` - Default Value: `/tmp/imu_sensor_socket`
* `--log-level` - Default Value: `INFO`, Options: `[INFO, WARNING, ERROR, CRITICAL]`
* `--frequency-hz` - Default Value: `500`
* `--retries` - Default: `10`
* `--data-mode` - Default: `random`, Options: `["csv", "random"]`

Example:

```
python3 publisher.py --socket-path "/tmp/socket_stream" --log-level INFO --frequency-hz 500
```
## Features

#### Extended Kalman Filter for Sensor Fusion

The accelerometer and magnetometer are combined using standard equations, as the accelerometer provides roll and pitch, and the magnetometer (adjusted by roll and pitch) provide the yaw. 

The gyroscope is updated iteratively with each dynamic timestep but can be prone to drift.

An Extended Kalman Filter has been implemented, using the Gyroscope as the prediction and the Fused Accelerometer + Magnetometer as the measurement. Since we assume that this Fused orientation is true, the EKF prioritizes alignment with the measurement but is smoothened by the gyroscope prediction. 

> **Note: The orientations are converted to quaternions to prevent gimble-locks**

#### Visualizer
The consumer's processing thread has a visualizer that updates live with the processed data. The visualizer is slower than the data being streamed and processed. To ensure real-time data sending, the visualizer runs on a separate thread.

The <span style="color:cyan"><b>blue arrow</b></span> is the fused orientation using EKF.

The <span style="color:green"><b>green arrow</b></span> is the raw orientation (quaternion) derived from the accelerometer and magnetometer fusion. This is just for visualization's sake.

The <span style="color:red"><b>red arrow</b></span> is the raw Gyroscope orientation updated on the first orientation as Euler Angles. This is just for visualization's sake.

> By watching the visualizer, it is evident that the CSV data for the accelerometer and magnetometer are noisy, but the gyroscope experiences drift over time. EKF helps fix these issues. 

## Changes Made

#### Impractical Timestamp

The suggested timestamp was a Unix Timestamp, an integer representing seconds since the Unix Epoch. However, this poses two issues: (1) Whole seconds does not provide enough fidelity for the gyroscope rotation and (2) expanding the unit to milliseconds or nanoseconds exceeds the limitations of an unsigned 32 bit integer. 

> **Solution:** Extend the timestamp to account for milliseconds as an unsigned long long in the data structure

## Authors

- **Madhusha Goonesekera** - A Masters in Robotic System Development graduate from Carnegie Mellon University, and holding Bachelors Degrees in Mechanical Engineering and Computer Science from the University of California - Davis. With a longstanding interest in applications of biomimicry for robotics, Madhusha hopes to work at Clone Robotics to develop software stacks for what he beleives is the most interesting humanoid robot on the market. 

## License

This project is licensed under the [MIT License](LICENSE)


## Acknowledgements

* **Clone Robotics** for the opportunity to solve this coding task and possibly work for this company.
* **Carnegie Mellon University and the MRSD program** for giving me the tools to make writing this repo possible.
* **iotaMotion Inc.**, where I developed a greater understanding of socket communication with tools such as gRPC and OpenIGTLink.

https://github.com/xioTechnologies/Fusion/blob/main/Python/sensor_data.csv

https://mwrona.com/posts/attitude-ekf/



### Artificial Intelligence & Integrity Statement

AI Tools such as ChatGPT were used for this Coding Task. AI Tools were used to look up syntax/functions within libraries used, debuggin, and to review and verify math / theory.

Beyond this, tools such as Google (including in part Gemini), and websites such as StackOverflow, and Reddit were used to get inspiration, especially for implementing EKF. 