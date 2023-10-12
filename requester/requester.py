import argparse
import socket
import time
import struct
import threading

class Tracker:
    def __init__(self, filename, seq_no, hostname, port):
        self.filename = filename
        self.seq_no: int = seq_no
        self.hostname = hostname
        self.port: int = port


def write_to_file(file_name, payload):
    with open(file_name, 'a') as file:
        file.write(payload.decode())

def main():
    tracker_arr = []
    # read the tracker
    with open('tracker.txt', 'r') as file:
        content = file.readlines()
        content.sort(key=lambda content: content[1])
        content = content[::-1]
        for i in content:
            filename, seq_no, hostname, port = i.split()
            tracker_arr.append(Tracker(filename, int(seq_no), hostname, int(port)))




    parser = argparse.ArgumentParser(description="UDP File Requester")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port to bind to")
    parser.add_argument("-o", "--file", type=str, required=True, help="File to request")
    args = parser.parse_args()

    # Variables to hold statistics
    total_packets_received = 0
    total_bytes_received = 0
    start_time = time.time()
    sender_ip = 'localhost'


    # Set up the UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("", args.port))
        
        # # # Request file
        # packet_type = b'R'
        # seq_num = socket.htonl(0)
        # length = socket.htonl(0)

        # for tracker in tracker_arr:
        #     print(tracker.filename)
        #     packet = struct.pack("!cII", packet_type, seq_num, length) + tracker.filename.encode()
        #     s.sendto(packet, (tracker.hostname, tracker.port))
        for tracker in tracker_arr:
            packet_type = b'R'
            seq_num = socket.htonl(0)
            length = socket.htonl(0)
            
            packet = struct.pack("!cII", packet_type, seq_num, length) + tracker.filename.encode()
            s.sendto(packet, (tracker.hostname, tracker.port))

            while True:
                data, addr = s.recvfrom(65535)  # maximum UDP packet size
                packet_type, seq_num, length = struct.unpack("!cII", data[:9])
                payload = data[9:]

                # Processing the packet and printing required details
                receipt_time = int(time.time() * 1000) % 1000  # receipt time in milliseconds
                print(f"{receipt_time}, {addr[0]}:{addr[1]}, {socket.ntohl(tracker.seq_no)}, {socket.ntohl(length)}, {payload[:4]}")

                if packet_type == b'D':
                    total_packets_received += 1
                    total_bytes_received += len(payload)

                    t = threading.Thread(target=write_to_file, args=(args.file, payload))
                    t.start()
                    t.join()

                elif packet_type == b'E':
                    # Print the summary for the sender:
                    duration = time.time() - start_time
                    print(f"\nSummary for Sender {addr[0]}:{addr[1]}")
                    print(f"Total data packets received: {total_packets_received}")
                    print(f"Total data bytes received: {total_bytes_received}")
                    print(f"Average packets/second: {total_packets_received / duration}")
                    print(f"Duration of the test: {duration:.2f} seconds\n")

                    # Reset counters if you are expecting data from another sender after an END packet
                    total_packets_received = 0
                    total_bytes_received = 0
                    start_time = time.time()
                    break

if __name__ == "__main__":
    main()
