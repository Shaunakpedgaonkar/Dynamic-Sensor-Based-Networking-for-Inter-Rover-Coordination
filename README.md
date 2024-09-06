Dynamic-Sensor-Based-Networking-for-Inter-Rover-Coordination
Project Overview
This project simulates a distributed network of Mars rovers designed to collaborate and complete various tasks, such as data collection across Mars. The system is decentralized, secure, and scalable, allowing multiple rovers to communicate in real-time. Each rover is equipped with different sensors, and communication between them ensures task coordination, data exchange, and decision-making based on rover health status and sensor data.

The core of the project is a peer-to-peer network architecture that handles secure communication and data requests using asynchronous programming and network protocols like UDP and TCP. The system also implements data encryption for secure transmission.
Use Case
In this project, a scenario is executed where a network of Mars rovers collaborates to collect and share data. Each network consists of multiple rovers, with each rover equipped with different sensors for specialized tasks, such as detecting atmospheric gas, analyzing soil composition, or tracking weather patterns.

Example:
Rover-to-Rover Health Monitoring:
Rover A requests the health status of Rover B. If Rover B's health is deemed "unhealthy" (i.e., below a certain threshold), Rover A takes action and moves to Rover B's location to assist. Rover A also uses the location sensor of Rover B to retrieve its current position.

Similarly, in another use case, a Biological Rover requests data from the Mineralogy camera sensor of a Geological Rover to detect minerals that could indicate the presence of life. Based on the data, the Biological Rover moves to investigate further.

This flexible architecture enables various use cases, where different rovers share sensor data based on task requirements.

Project Structure
An overview of the project files is as follows:

connection.py:

Handles asynchronous communication between the rovers using UDP for broadcasting and TCP for secure, point-to-point communication. This script simulates sensor data generation (e.g., health, pressure, GPS location, and humidity) for the rovers.
final (1).py:

The main control script that coordinates rover communication and handles data exchange requests. The script manages UDP and TCP communication, starts servers, and executes tasks related to rover data sharing.
import base64.py:

Implements encryption and decryption functionality using base64 encoding and XOR encryption. This ensures that any data exchanged between rovers is securely encrypted.
Sensors and Rover Types
Each rover is equipped with specialized sensors for data collection. Below is an overview of the different types of rovers and their sensors:

## Sensors and Rover Types

| **Rover**           | **Sensors**                                                                                                                                           |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Atmospheric Rover** | Health, Location, Atmospheric Gas, Wind Speed, Temperature, Humidity, UV Radiation, Dust Particles, Barometer                                       |
| **Biological Rover**  | Health, Location, Microbial Detection, UV Light, Organic Compound, Fluorescence, Regolith, Thermal Gradient                                         |
| **Geological Rover**  | Health, Location, Rock Spectrometer, Soil Composition, Subsurface Radar, Seismic Vibration, Mineralogy Camera, Magnetic Field                      |
| **Navigation Rover**  | Health, Location, High Gain Antenna, Optical Navigation Camera, Star Tracker, Radar Altimeter, Environmental Sensors                               |
| **Weather Rover**     | Health, Location, Weather Station, Thermal Imaging, Infrared Spectrometer, Cloud Particle Analysis, Solar Irradiance, Atmospheric Electricity       |

Network topology
This project transitioned from a centralized server model to a decentralized, peer-to-peer network due to concerns about a single point of failure, scalability issues, and latency.

Within a Network:
Nodes communicate via UDP broadcasting to simulate real-time sensor data sharing.
Secure point-to-point communication is achieved via TCP connections, ensuring the integrity and confidentiality of transmitted data.
Between Networks:
Networks communicate with each other using one-to-one TCP connections. When rovers from different networks need to exchange data, they establish direct communication through a decentralized FIB-based system.
