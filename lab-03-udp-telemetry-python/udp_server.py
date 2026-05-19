"""
Laboratory Work 3
Telemetry Data Reception Using the UDP Protocol

Course:
    Programming. Part 2

Topic:
    Development of a Python UDP server for receiving and processing
    telemetry data from a simulated network or embedded device.

Description:
    This program runs a UDP server that receives telemetry messages
    from a UDP client. The received data may include temperature,
    humidity, supply voltage, and device status. The server analyzes
    the telemetry values and displays warning messages if emergency
    conditions are detected.

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
    The program uses the standard Python socket module.

Run examples:
    python udp_server.py
    python udp_server.py 127.0.0.1 5005
    python udp_server.py 0.0.0.0 5005

Note:
    The program is designed for educational purposes as part of
    Laboratory Work 3 for the course "Programming. Part 2".
"""

import socket
import sys
from datetime import datetime


DEFAULT_SERVER_IP = "127.0.0.1"
DEFAULT_SERVER_PORT = 5005
BUFFER_SIZE = 1024


def show_start_message(server_ip, server_port):
    """
    Displays information about the UDP server startup.
    """

    print("=" * 70)
    print("Laboratory Work 3")
    print("UDP Telemetry Server")
    print("=" * 70)
    print(f"Server IP:   {server_ip}")
    print(f"Server port: {server_port}")
    print("Status:      waiting for telemetry data...")
    print("=" * 70)
    print()


def parse_telemetry_message(message):
    """
    Parses a telemetry message in the following format:

        TEMP=24.6;HUM=51;VOLT=3.7;STATUS=OK

    Returns a dictionary with telemetry parameters.
    """

    telemetry = {}

    try:
        pairs = message.split(";")

        for pair in pairs:
            if "=" in pair:
                key, value = pair.split("=", 1)
                telemetry[key.strip().upper()] = value.strip()

    except Exception as error:
        print(f"Error while parsing message: {error}")

    return telemetry


def analyze_telemetry(telemetry):
    """
    Analyzes telemetry values and displays warning messages
    if emergency conditions are detected.
    """

    warnings = []

    try:
        if "TEMP" in telemetry:
            temperature = float(telemetry["TEMP"])

            if temperature > 45:
                warnings.append("WARNING! Device overheating.")

        if "VOLT" in telemetry:
            voltage = float(telemetry["VOLT"])

            if voltage < 3.3:
                warnings.append("WARNING! Low supply voltage.")

        if "STATUS" in telemetry:
            status = telemetry["STATUS"].upper()

            if status == "ERROR":
                warnings.append("WARNING! Device emergency state.")

    except ValueError:
        warnings.append("WARNING! Incorrect telemetry data format.")

    return warnings


def print_telemetry(telemetry):
    """
    Displays telemetry data in a readable format.
    """

    if "TEMP" in telemetry:
        print(f"Temperature:     {telemetry['TEMP']} °C")

    if "HUM" in telemetry:
        print(f"Humidity:        {telemetry['HUM']} %")

    if "VOLT" in telemetry:
        print(f"Supply voltage:  {telemetry['VOLT']} V")

    if "STATUS" in telemetry:
        print(f"Device status:   {telemetry['STATUS']}")


def run_udp_server(server_ip, server_port):
    """
    Starts the UDP server and processes incoming telemetry messages.
    """

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((server_ip, server_port))

    show_start_message(server_ip, server_port)

    packet_counter = 0

    while True:
        try:
            data, address = server_socket.recvfrom(BUFFER_SIZE)
            packet_counter += 1

            message = data.decode("utf-8")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"[{timestamp}] Packet #{packet_counter}")
            print(f"Message received from {address}:")
            print(message)
            print()

            telemetry = parse_telemetry_message(message)

            if telemetry:
                print_telemetry(telemetry)

                warnings = analyze_telemetry(telemetry)

                if warnings:
                    print()
                    for warning in warnings:
                        print(warning)
                else:
                    print()
                    print("Telemetry status: OK")
            else:
                print("No valid telemetry data found.")

            print("-" * 70)

        except KeyboardInterrupt:
            print()
            print("UDP server stopped by user.")
            break

        except Exception as error:
            print(f"Server error: {error}")

    server_socket.close()


def main():
    """
    Main function. Reads command-line arguments and starts the server.

    Usage:
        python udp_server.py
        python udp_server.py 127.0.0.1 5005
        python udp_server.py 0.0.0.0 5005
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
            print("python udp_server.py 127.0.0.1 5005")
            return

    run_udp_server(server_ip, server_port)


if __name__ == "__main__":
    main()