# Clone Robotics Coding Task: Driver for Custom Protocol

In this coding task, I have created a publisher and consumer using IPC socket communication. The publisher sends packed binary data of a custom `Payload_IMU` class to the consumer. The consumer unpacks this data and extracts rotation information from these sensors. 

## Getting Started

All the libraries used in this repository should be part of vanilla Python 3.10.x. However, if there are any missing libraries, a `requirements.txt` has been included for your convenience.

```
pip install -r requirements.txt
```
Alternatively, if using Conda you can create a new Conda Environment using the provided `environment.yml` file
```
conda env create -f environment.yml
```
After this completes you can open the Conda Environment by typing
```
conda activate clone_task
```

## Running the System

## Features

## Changes Made

#### Impractical Timestamp

The suggested timestamp was a Unix Timestamp, an integer representing seconds since the Unix Epoch. However, this poses two issues: (1) Whole seconds does not provide enough fidelity for the gyroscope rotation and (2) expanding the unit to milliseconds or nanoseconds exceeds the limitations of an unsigned 32 bit integer. 

> **Solution:** Extend the timestamp to account for milliseconds as an unsigned long long in the data structure

## Authors

- **Madhusha Goonesekera** - A Masters in Robotic System Development graduate from Carnegie Mellon University, and holding Bachelors Degrees in Mechanical Engineering and Computer Science from the University of California - Davis. With a longstanding interest in applications of biomimicry for robotics, Madhusha hopes to work at Clone Robotics to develop software stacks for the most interesting humanoid robot on the market. 

## License

This project is licensed under the [MIT License](LICENSE)


## Acknowledgements

* **Clone Robotics** for the opportunity to solve this coding task and possibly work for this company.
* **Carnegie Mellon University and the MRSD program** for giving me the tools to make writing this repo possible.
* **iotaMotion Inc.**, where I developed a greater understanding of socket communication with tools such as gRPC and OpenIGTLink.

https://github.com/xioTechnologies/Fusion/blob/main/Python/sensor_data.csv


### Artificial Intelligence Statement

