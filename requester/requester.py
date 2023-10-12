import argparse
import socket
import time
import struct

def main():
    parser = argparse.ArgumentParser(description="UDP File Requester")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port to bind to")
    parser.add_argument("-o", "--file", type=str, required=True, help="File to request")
    args = parser.parse_args()

    # Variables to hold statistics
    total_packets_received = 0
    total_bytes_received = 0
    start_time = time.time()

    # Set up the UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("", args.port))

        # Request file
        packet_type = b'R'
        seq_num = socket.htonl(0)
        length = socket.htonl(0)
        packet = struct.pack("!cII", packet_type, seq_num, length) + args.file.encode()
        s.sendto(packet, (socket.gethostbyname(socket.gethostname()), args.port))

        with open(args.file, "wb") as f:
            while True:
                data, addr = s.recvfrom(65535)  # maximum UDP packet size
                packet_type, seq_num, length = struct.unpack("!cII", data[:9])
                payload = data[9:]

                # Processing the packet and printing required details
                receipt_time = int(time.time() * 1000) % 1000  # receipt time in milliseconds
                print(f"{receipt_time}, {addr[0]}:{addr[1]}, {socket.ntohl(seq_num)}, {socket.ntohl(length)}, {payload[:4]}")

                if packet_type == b'D':
                    total_packets_received += 1
                    total_bytes_received += len(payload)
                    f.write(payload)

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

if __name__ == "__main__":
    main()
