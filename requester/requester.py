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


    print('----------------------------')
    print("Requester’s print information:")

    parser = argparse.ArgumentParser(description="UDP File Requester")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port to bind to")
    parser.add_argument("-o", "--file", type=str, required=True, help="File to request")
    args = parser.parse_args()

    # Variables to hold statistics
    total_packets_received = 0
    total_bytes_received = 0
    start_time = time.time()


    

    # TODO be able to receive 2+ packets concurrently if same sequence number
    #  currently in a linear flow model
    #  data packet from sender 1 -> end packet from sender 1 -> Summary2
    #  -> data packet from sender2 -> end packet from sender2 -> Summary2
    # 
    # IDEAS:
    # - setup threads for multiple packets to be accepted from senders (2 while loops below running concurrently)
    # - sequence numbers determine order of packets (if same # accept at same time)

    # Set up the UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("", args.port))

        for tracker in tracker_arr: # if sequence number the same in the array create threads to run below while loop at the same time
            packet_type = b'R'
            seq_num = socket.htonl(0)
            length = socket.htonl(0)
            
            packet = struct.pack("!cII", packet_type, seq_num, length) + tracker.filename.encode()
            s.sendto(packet, (tracker.hostname, tracker.port))


            while True:
                data, addr = s.recvfrom(65535)  # maximum UDP packet size
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                packet_type, seq_num, length = struct.unpack("!cII", data[:9])
                payload = data[9:]

                sender_addr = f"{addr[0]}:{tracker.port}"

                if packet_type == b'D':
                    print("DATA Packet")
                    print(f"recv time:\t{current_time}\nsender addr:\t{sender_addr}\nSequence num::\t{tracker.seq_no}\nlength:\t\t{len(payload)}\npayload:\t{payload[:4].decode('utf-8', 'ignore')}\n")
                    total_packets_received += 1
                    total_bytes_received += len(payload)

                    t = threading.Thread(target=write_to_file, args=(args.file, payload))
                    t.start()
                    t.join()

                elif packet_type == b'E':
                    print("END Packet")
                    print(f"recv time:\t{current_time}\nsender addr:\t{sender_addr}\nSequence num::\t{tracker.seq_no}\nlength:\t\t0\npayload:\t0")
                    
                    # Print the summary for the sender:
                    duration = time.time() - start_time
                    duration_ms = duration * 1000
                    print(f"\nSummary\nsender addr:\t\t{sender_addr}\nTotal Data packets:\t{total_packets_received}\nTotal Data bytes:\t{total_bytes_received}\nAverage packets/second:\t{round(total_packets_received / duration)}\nDuration of the test:\t{duration_ms:.2f} ms\n")
                    # print(f"Total data packets received: {total_packets_received}")
                    # print(f"Total data bytes received: {total_bytes_received}")
                    # print(f"Average packets/second: {total_packets_received / duration}")
                    # print(f"Duration of the test: {duration:.2f} seconds\n")

                    # Reset counters if you are expecting data from another sender after an END packet
                    total_packets_received = 0
                    total_bytes_received = 0
                    start_time = time.time()
                    break

if __name__ == "__main__":
    main()
