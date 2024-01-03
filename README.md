This project emulates a distributed file transfer between sender and reciever. 

Run the project using the following syntax: 

python3 sender.py -p <port> -g <requester port> -r <rate> -q <seq_no> -l <length>
  port is the port on which the sender waits for requests,
  requester port is the port on which the requester is waiting,
  rate is the number of packets to be sent per second,
  seq_no is the initial sequence of the packet exchange,
  length is the length of the payload (in bytes) in the packets
  
python3 requester.py -p <port> -o <file option>
  port is the port on which the requester waits for packets,
  file option is the name of the file that is being requested.

This implementation suppports multiple senders and recievers 
