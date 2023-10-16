import argparse
import socket
import time
import struct
import threading
from datetime import datetime

class Tracker:
    def __init__(self, filename, seq_no, hostname, port):
        self.filename = filename
        self.seq_no: int = seq_no
        self.hostname = hostname
        self.port: int = port

def write_to_file(file_name, payload):
    with open(file_name, 'a') as file:
        file.write(payload.decode())

def send_requests(trackers, sock, args):
    for tracker in trackers:
        packet_type = b'R'
        seq_num = socket.htonl(0)
        length = socket.htonl(0)
        
        packet = struct.pack("!cII", packet_type, seq_num, length) + tracker.filename.encode()
        sock.sendto(packet, (tracker.hostname, tracker.port))

def handle_packets(sock, args):
    total_packets_received = 0
    total_bytes_received = 0
    start_time = time.time()
    sender_stats = {}

    while True:
        data, addr = sock.recvfrom(65535)  # maximum UDP packet size
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        packet_type, seq_num, length = struct.unpack("!cII", data[:9])
        
        # Convert seq_num from network byte order to host byte order
        seq_num = socket.ntohl(seq_num)
        payload = data[9:]

        sender_addr = f"{addr[0]}:{addr[1]}"  # Using the actual sender's port
        key = f"{addr[0]}:{addr[1]}"
        
        if key not in sender_stats: #if this is the first packet sent update the dict
            sender_stats[key] = {
                "sender ip address":0,
                "sender port number": 0, 
                "total_packets": 0,
                "total_bytes": 0,
                "packets per second":0,
                "start_time": current_time,
                "end_time": None,
            }

        if packet_type == b'D':
            print("DATA Packet")
            # Print the sequence number as well
            print(f"recv time:\t{current_time}\nsender addr:\t{sender_addr}\nSequence num:\t{seq_num}\nlength:\t\t{len(payload)}\npayload:\t{payload[:4].decode('utf-8', 'ignore')}\n")
            total_packets_received += 1
            total_bytes_received += len(payload)
            sender_stats[key]["total_bytes"]+=1
            write_to_file(args.file, payload)

        elif packet_type == b'E':
            print("END Packet")
            # Print the sequence number for the END packet as well
            print(f"recv time:\t{current_time}\nsender addr:\t{sender_addr}\nSequence num:\t{seq_num}\nlength:\t\t0\npayload:\t0")

            end_time = time.time()
            duration = end_time - start_time
            duration_ms = duration * 1000

            print(f"\nSummary\nsender addr:\t\t{sender_addr}\nTotal Data packets:\t{total_packets_received}\nTotal Data bytes:\t{total_bytes_received}\nAverage packets/second:\t{round(total_packets_received / duration)}\nDuration of the test:\t{duration_ms:.2f} ms\n")
            
            break  # Assuming one 'END' packet ends the session. Adjust if needed.

def main():
    tracker_arr = []
    with open('tracker.txt', 'r') as file:
        content = file.readlines()
        content = [line.strip() for line in content if line.strip()]  # Avoid empty lines
        content.sort(key=lambda content: content[1])
        content = content[::-1]
        for i in content:
            filename, seq_no, hostname, port = i.split()
            tracker_arr.append(Tracker(filename, int(seq_no), hostname, int(port)))

    print('----------------------------')
    print("Requester’s print information:")

    parser = argparse.ArgumentParser(description="UDP File Requester")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port to bind to")
    parser.add_argument("-o", "--file", type=str, required=True, help="File to request")
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("", args.port))

        # Send requests in the main thread
        send_requests(tracker_arr, s, args)

        # Handling responses
        handle_packets(s, args)

if __name__ == "__main__":
    main()