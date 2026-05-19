"""
Laboratory Work 3
Telemetry Data Transmission Using the UDP Protocol

Course:
    Programming. Part 2

Topic:
    Development of a Python UDP client for generating and transmitting
    telemetry data to a UDP server.

Description:
    This program simulates a network, IoT, or embedded device that
    periodically generates telemetry data and sends it to a UDP server.

    The transmitted telemetry data includes:
        - temperature;
        - humidity;
        - supply voltage;
        - device status.

    Example telemetry message:
        TEMP=24.6;HUM=51;VOLT=3.7;STATUS=OK

University:
    Kharkiv National University of Radio Electronics (NURE)

Author:
    Pavlo Galkin

Academic years:
    2025–2026

Language:
    Python 3

Required libraries:
    No external libraries are required.
    The program uses only standard Python modules:
        socket
        random
        time
        sys

Run examples:
    python udp_client.py
    python udp_client.py 127.0.0.1 5005
    python udp_client.py 192.168.1.100 5005

Note:
    The program is designed for educational purposes as part of
    Laboratory Work 3 for the course "Programming. Part 2".
"""

import socket
import random
import time
import sys
from datetime import datetime


DEFAULT_SERVER_IP = "127.0.0.1"
DEFAULT_SERVER_PORT = 5005
SEND_INTERVAL = 2


def show_start_message(server_ip, server_port):
    """
    Displays information about the UDP client startup.
    """

    print("=" * 70)
    print("Laboratory Work 3")
    print("UDP Telemetry Client")
    print("=" * 70)
    print(f"Server IP:       {server_ip}")
    print(f"Server port:     {server_port}")
    print(f"Send interval:   {SEND_INTERVAL} seconds")
    print("Status:          sending telemetry data...")
    print("=" * 70)
    print()


def generate_telemetry(packet_id):
    """
    Generates simulated telemetry data.

    Returns a dictionary with telemetry parameters.
    """

    telemetry = {
        "ID": packet_id,
        "TEMP": round(random.uniform(20.0, 50.0), 1),
        "HUM": random.randint(30, 80),
        "VOLT": round(random.uniform(3.0, 4.2), 2),
        "STATUS": random.choice(["OK", "OK", "OK", "ERROR"])
    }

    return telemetry


def create_telemetry_message(telemetry):
    """
    Converts telemetry dictionary into a text message.

    Message format:
        ID=1;TEMP=24.6;HUM=51;VOLT=3.7;STATUS=OK
    """

    message = (
        f"ID={telemetry['ID']};"
        f"TEMP={telemetry['TEMP']};"
        f"HUM={telemetry['HUM']};"
        f"VOLT={telemetry['VOLT']};"
        f"STATUS={telemetry['STATUS']}"
    )

    return message


def run_udp_client(server_ip, server_port):
    """
    Starts the UDP client and periodically sends telemetry messages.
    """

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    show_start_message(server_ip, server_port)

    packet_id = 1

    while True:
        try:
            telemetry = generate_telemetry(packet_id)
            message = create_telemetry_message(telemetry)

            client_socket.sendto(
                message.encode("utf-8"),
                (server_ip, server_port)
            )

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"[{timestamp}] Packet #{packet_id} sent:")
            print(message)
            print("-" * 70)

            packet_id += 1

            time.sleep(SEND_INTERVAL)

        except KeyboardInterrupt:
            print()
            print("UDP client stopped by user.")
            break

        except Exception as error:
            print(f"Client error: {error}")
            break

    client_socket.close()


def main():
    """
    Main function. Reads command-line arguments and starts the client.

    Usage:
        python udp_client.py
        python udp_client.py 127.0.0.1 5005
        python udp_client.py 192.168.1.100 5005
    """

    server_ip = DEFAULT_SERVER_IP
    server_port = DEFAULT_SERVER_PORT

    if len(sys.argv) >= 2:
        server_ip = sys.argv[1]

    if len(sys.argv) >= 3:
        try:
            server_port = int(sys.argv[2])
        except ValueError:
            print("Error: server port must be an integer.")
            print("Example:")
            print("python udp_client.py 127.0.0.1 5005")
            return

    run_udp_client(server_ip, server_port)


if __name__ == "__main__":
    main()