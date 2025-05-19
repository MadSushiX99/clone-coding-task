# Clone Robotics Coding Task: Driver for Custom Protocol

In this coding task, I have created a publisher and consumer using IPC socket communication. The publisher sends packed binary data of a custom `Payload_IMU` class to the consumer. The consumer unpacks this data and extracts rotation information from these sensors. 

## Getting Started

All the libraries used in this repository should be part of vanilla Python3. However, if there are any missing libraries, a `requirements.txt` has been included for your convenience.

```python
pip install -r requirements.txt
```

## Running the System

## Built With

## Future Work

## Authors

- **Madhusha Goonesekera** - A Masters in Robotic System Development graduate from Carnegie Mellon University, and holding Bachelors Degrees in Mechanical Engineering and Computer Science from the University of California - Davis. With a longstanding interest in applications of biomimicry for robotics, Madhusha hopes to work at Clone Robotics to develop software stacks for the most interesting humanoid robot on the market. 

## License

## Acknowledgements

* **Clone Robotics** for the opportunity to solve this coding task and possibly work for this company.
* **Carnegie Mellon University and the MRSD program** for giving me the tools to make writing this repo possible.
* **iotaMotion Inc.**, where I developed a greater understanding of socket communication with tools such as gRPC and OpenIGTLink.