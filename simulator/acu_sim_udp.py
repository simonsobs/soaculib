import time
import struct
import socket
import requests

def read_http(read_port=8102):
    r = requests.get('http://localhost:'+str(read_port)+'/Values')
    all_data = r.json()
    udp_data = {}
    udp_keys = ['Day', 'Time_UDP', 'Corrected Azimuth', 'Corrected Elevation', 'Corrected Boresight', 'Raw Azimuth', 'Raw Elevation', 'Raw Boresight', 'Azimuth Current 1', 'Azimuth Current 2', 'Elevation Current 1', 'Boresight Current 1', 'Boresight Current 2']
    for key in udp_keys:
        udp_data[key] = all_data[key]
    return udp_data

class UDP_Sim:
    def __init__(self, write_port, read_port):
        self.pkt_size = 10
        self.FMT = '<idddddddddddd'
        self.write_port = write_port
        self.read_port = read_port
        self.data = read_http()
    def set_values(self):
        self.data = read_http()
        pack = struct.pack(self.FMT,
                           self.data['Day'],
                           self.data['Time_UDP'],
                           self.data['Corrected Azimuth'],
                           self.data['Corrected Elevation'],
                           self.data['Corrected Boresight'],
                           self.data['Raw Azimuth'],
                           self.data['Raw Elevation'],
                           self.data['Raw Boresight'],
                           self.data['Azimuth Current 1'],
                           self.data['Azimuth Current 2'],
                           self.data['Elevation Current 1'],
                           self.data['Boresight Current 1'],
                           self.data['Boresight Current 2'])
        return pack

    def run(self):
        host = "localhost"
        port = self.write_port
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        pkt = self.set_values()
        sock.sendto(pkt, (host, port))
        time.sleep(0.005)
        return pkt

if __name__ == '__main__':
    udp = UDP_Sim(10008, 8102)
    while True:
        pkt = udp.run()
#        print(pkt)
