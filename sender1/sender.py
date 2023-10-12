import argparse
import socket
import time
import struct
import os

def send_file(s, filename, dest_addr, rate, seq_no, length):
    if not os.path.exists(filename):
        print(f"File {filename} not found!")
        return

    with open(filename, 'rb') as file:
        while True:
            data = file.read(length)
            print(data)
            if not data:
                print("end packet send")
                # Sending the END packet
                header = struct.pack('!cII', b'E', socket.htonl(seq_no), 0)
                s.sendto(header, dest_addr)
                break
            
            header = struct.pack('!cII', b'D', socket.htonl(seq_no), len(data))
            packet = header + data
            s.sendto(packet, dest_addr)

            # Print the sender's log
            print(f"{time.time()*1000:.0f} {dest_addr[0]} {seq_no} {data.decode('utf-8', 'ignore')}")
            
            seq_no += len(data)
            time.sleep(1.0/rate)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', type=int, required=True, help='Port for the sender to listen on.')
    parser.add_argument('-g', type=int, required=True, help='Port for the requester.')
    parser.add_argument('-r', type=int, required=True, help='Rate of sending packets.')
    parser.add_argument('-q', type=int, required=True, help='Initial sequence number.')
    parser.add_argument('-l', type=int, required=True, help='Length of the payload in bytes.')
    args = parser.parse_args()

    # Check port range validity
    if not (2049 < args.p < 65536) or not (2049 < args.g < 65536):
        print("Error: Port number must be in the range 2050 to 65535.")
        exit(1)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('0.0.0.0', args.p))
        print(args.p)

        try:
            while True:
                # Listen for incoming request packets
                data, addr = s.recvfrom(4096)
                print(data)
                print(addr)
                packet_type, _, _ = struct.unpack('!cII', data[:9])

                print(packet_type)
                if packet_type == b'R':
                    requested_file = data[9:].decode()
                    send_file(s, requested_file, (addr[0], args.g), args.r, args.q, args.l)

        except KeyboardInterrupt:
            print("\nShutting down sender...")
        finally:
            s.close()
