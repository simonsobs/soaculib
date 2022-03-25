import socket
import struct

port = 10008
FMT = '<idddddddddddd'
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", port))
print("waiting on port:", port)
while True:
    data, addr = s.recvfrom(1024)
    print("Received:", struct.unpack(FMT, data[:100]), "from", addr)
