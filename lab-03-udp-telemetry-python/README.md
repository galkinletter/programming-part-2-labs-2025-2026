# Laboratory Work No. 3  
## Programming Telemetry Data Transmission Using the UDP Protocol

![Laboratory Work 3 - Python UDP Telemetry](images/lab-03-poster.png)

## Purpose of the Work

The purpose of this laboratory work is to study the principles of network data exchange between software nodes using the UDP protocol and to gain practical skills in creating a UDP client and a UDP server in Python.

As part of this work, a software model for transmitting telemetry data from a simulated embedded or IoT device to a receiving server is developed.

---

## Task

Develop two Python programs:

1. **UDP Client** — simulates the operation of a device that generates and transmits telemetry data.
2. **UDP Server** — receives messages, analyzes the received data, and displays it in the console.

The client should transmit the following parameters:

- temperature;
- humidity;
- supply voltage;
- device status.

Example message:

```text
TEMP=24.6;HUM=51;VOLT=3.7;STATUS=OK
