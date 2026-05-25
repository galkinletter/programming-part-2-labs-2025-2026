"""
Laboratory Work 4
MPEG-TS Transport Stream Parser

Course:
    Programming. Part 2

Topic:
    Development of a Python tool for analyzing MPEG-TS transport stream packets
    used in digital television systems.

Description:
    This program reads an MPEG-TS file, splits it into 188-byte transport stream
    packets, checks the synchronization byte, extracts MPEG-TS header fields,
    analyzes PID statistics, detects basic continuity counter errors, and saves
    the result to a CSV file.

University:
    Kharkiv National University of Radio Electronics (NURE)

Author:
    Pavlo Galkin

Academic years:
    2025–2026

Language:
    Python 3

Run examples:
    python mpeg_ts_parser.py sample.ts
    python mpeg_ts_parser.py sample.ts --csv pid_statistics.csv

Input:
    MPEG-TS file with .ts extension

Output:
    Console statistics and CSV report with PID information
"""

import argparse
import csv
import os
from collections import defaultdict


TS_PACKET_SIZE = 188
SYNC_BYTE = 0x47


# Known MPEG-TS service PIDs
KNOWN_PIDS = {
    0x0000: "PAT - Program Association Table",
    0x0001: "CAT - Conditional Access Table",
    0x0010: "NIT - Network Information Table",
    0x0011: "SDT/BAT - Service Description Table",
    0x0012: "EIT - Event Information Table",
    0x0014: "TDT/TOT - Time and Date / Time Offset Table",
    0x1FFF: "Null Packet",
}


def get_pid_type(pid):
    """
    Return a short description for known MPEG-TS PIDs.
    """
    return KNOWN_PIDS.get(pid, "Unknown / Elementary Stream")


def parse_ts_header(packet):
    """
    Parse the 4-byte MPEG-TS packet header.

    MPEG-TS packet header structure:
        Byte 0:
            sync_byte

        Byte 1:
            transport_error_indicator        - 1 bit
            payload_unit_start_indicator     - 1 bit
            transport_priority               - 1 bit
            PID high bits                     - 5 bits

        Byte 2:
            PID low bits                      - 8 bits

        Byte 3:
            transport_scrambling_control     - 2 bits
            adaptation_field_control         - 2 bits
            continuity_counter               - 4 bits
    """

    sync_byte = packet[0]

    transport_error_indicator = (packet[1] & 0x80) >> 7
    payload_unit_start_indicator = (packet[1] & 0x40) >> 6
    transport_priority = (packet[1] & 0x20) >> 5

    pid = ((packet[1] & 0x1F) << 8) | packet[2]

    transport_scrambling_control = (packet[3] & 0xC0) >> 6
    adaptation_field_control = (packet[3] & 0x30) >> 4
    continuity_counter = packet[3] & 0x0F

    return {
        "sync_byte": sync_byte,
        "transport_error_indicator": transport_error_indicator,
        "payload_unit_start_indicator": payload_unit_start_indicator,
        "transport_priority": transport_priority,
        "pid": pid,
        "transport_scrambling_control": transport_scrambling_control,
        "adaptation_field_control": adaptation_field_control,
        "continuity_counter": continuity_counter,
    }


def analyze_ts_file(filename):
    """
    Analyze MPEG-TS packets from a file.
    """

    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")

    file_size = os.path.getsize(filename)

    if file_size < TS_PACKET_SIZE:
        raise ValueError("File is too small to be a valid MPEG-TS stream.")

    total_packets = 0
    sync_errors = 0
    transport_errors = 0

    pid_stats = defaultdict(int)
    pid_payload_start = defaultdict(int)
    pid_scrambled = defaultdict(int)
    continuity_errors = defaultdict(int)

    last_continuity_counter = {}

    with open(filename, "rb") as file:
        packet_index = 0

        while True:
            packet = file.read(TS_PACKET_SIZE)

            if not packet:
                break

            if len(packet) != TS_PACKET_SIZE:
                print(
                    f"[WARNING] Incomplete packet at the end of file. "
                    f"Size: {len(packet)} bytes"
                )
                break

            total_packets += 1

            header = parse_ts_header(packet)

            if header["sync_byte"] != SYNC_BYTE:
                sync_errors += 1
                print(
                    f"[ERROR] Sync byte error at packet {packet_index}: "
                    f"found 0x{header['sync_byte']:02X}, expected 0x47"
                )
                packet_index += 1
                continue

            pid = header["pid"]
            continuity_counter = header["continuity_counter"]
            adaptation_field_control = header["adaptation_field_control"]

            pid_stats[pid] += 1

            if header["payload_unit_start_indicator"]:
                pid_payload_start[pid] += 1

            if header["transport_error_indicator"]:
                transport_errors += 1

            if header["transport_scrambling_control"] != 0:
                pid_scrambled[pid] += 1

            """
            Continuity Counter check:
            It is meaningful mainly when the packet contains payload.

            adaptation_field_control:
                00 - reserved
                01 - payload only
                10 - adaptation field only
                11 - adaptation field followed by payload

            Continuity counter should increment only for packets with payload.
            """
            has_payload = adaptation_field_control in (1, 3)

            if has_payload and pid != 0x1FFF:
                if pid in last_continuity_counter:
                    expected_counter = (last_continuity_counter[pid] + 1) % 16

                    if continuity_counter != expected_counter:
                        continuity_errors[pid] += 1

                last_continuity_counter[pid] = continuity_counter

            packet_index += 1

    return {
        "filename": filename,
        "file_size": file_size,
        "total_packets": total_packets,
        "sync_errors": sync_errors,
        "transport_errors": transport_errors,
        "pid_stats": dict(pid_stats),
        "pid_payload_start": dict(pid_payload_start),
        "pid_scrambled": dict(pid_scrambled),
        "continuity_errors": dict(continuity_errors),
    }


def print_report(result):
    """
    Print MPEG-TS analysis report to console.
    """

    print()
    print("=" * 70)
    print("MPEG-TS TRANSPORT STREAM PARSER")
    print("=" * 70)

    print(f"File: {result['filename']}")
    print(f"File size: {result['file_size']} bytes")
    print(f"Packet size: {TS_PACKET_SIZE} bytes")
    print(f"Total packets: {result['total_packets']}")
    print(f"Sync errors: {result['sync_errors']}")
    print(f"Transport error indicator packets: {result['transport_errors']}")

    print()
    print("-" * 70)
    print("PID STATISTICS")
    print("-" * 70)

    print(
        f"{'PID HEX':<10} "
        f"{'PID DEC':<10} "
        f"{'PACKETS':<12} "
        f"{'PAYLOAD START':<15} "
        f"{'CC ERRORS':<12} "
        f"{'TYPE'}"
    )

    print("-" * 70)

    pid_stats = result["pid_stats"]
    pid_payload_start = result["pid_payload_start"]
    continuity_errors = result["continuity_errors"]

    for pid, count in sorted(pid_stats.items()):
        print(
            f"0x{pid:04X}     "
            f"{pid:<10} "
            f"{count:<12} "
            f"{pid_payload_start.get(pid, 0):<15} "
            f"{continuity_errors.get(pid, 0):<12} "
            f"{get_pid_type(pid)}"
        )

    print("-" * 70)

    if 0x0000 in pid_stats:
        print("[OK] PAT table detected: PID 0x0000")
    else:
        print("[WARNING] PAT table was not detected.")

    if result["sync_errors"] == 0:
        print("[OK] No synchronization errors detected.")
    else:
        print(f"[WARNING] Synchronization errors detected: {result['sync_errors']}")

    total_cc_errors = sum(continuity_errors.values())

    if total_cc_errors == 0:
        print("[OK] No continuity counter errors detected.")
    else:
        print(f"[WARNING] Continuity counter errors detected: {total_cc_errors}")

    print("=" * 70)
    print()


def save_pid_statistics_to_csv(result, csv_filename):
    """
    Save PID statistics to CSV file.
    """

    pid_stats = result["pid_stats"]
    pid_payload_start = result["pid_payload_start"]
    pid_scrambled = result["pid_scrambled"]
    continuity_errors = result["continuity_errors"]

    with open(csv_filename, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow(
            [
                "PID_HEX",
                "PID_DEC",
                "PACKETS",
                "PAYLOAD_UNIT_START_COUNT",
                "SCRAMBLED_PACKETS",
                "CONTINUITY_COUNTER_ERRORS",
                "TYPE",
            ]
        )

        for pid, count in sorted(pid_stats.items()):
            writer.writerow(
                [
                    f"0x{pid:04X}",
                    pid,
                    count,
                    pid_payload_start.get(pid, 0),
                    pid_scrambled.get(pid, 0),
                    continuity_errors.get(pid, 0),
                    get_pid_type(pid),
                ]
            )

    print(f"[INFO] CSV report saved to: {csv_filename}")


def main():
    parser = argparse.ArgumentParser(
        description="MPEG-TS Transport Stream Parser"
    )

    parser.add_argument(
        "filename",
        help="Path to MPEG-TS file, for example sample.ts"
    )

    parser.add_argument(
        "--csv",
        default="pid_statistics.csv",
        help="CSV output file name. Default: pid_statistics.csv"
    )

    args = parser.parse_args()

    try:
        result = analyze_ts_file(args.filename)
        print_report(result)
        save_pid_statistics_to_csv(result, args.csv)

    except FileNotFoundError as error:
        print(f"[ERROR] {error}")

    except ValueError as error:
        print(f"[ERROR] {error}")

    except Exception as error:
        print(f"[ERROR] Unexpected error: {error}")


if __name__ == "__main__":
    main()