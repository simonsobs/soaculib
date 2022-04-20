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
        self.fmt = 'idddddddddddd'
        self.fmts = []
        for i in range(self.pkt_size):
            self.fmts.append(self.fmt)
        self.FMT = '<'+('').join(self.fmts)
        self.write_port = write_port
        self.read_port = read_port
        self.data = read_http()
    def set_values(self):
        pkt_values = {'Day': [],
                      'Time_UDP': [],
                      'Corrected Azimuth': [],
                      'Corrected Elevation': [],
                      'Corrected Boresight': [],
                      'Raw Azimuth': [],
                      'Raw Elevation': [],
                      'Raw Boresight': [],
                      'Azimuth Current 1': [],
                      'Azimuth Current 2': [],
                      'Elevation Current 1': [],
                      'Boresight Current 1': [],
                      'Boresight Current 2': []}
        for i in range(self.pkt_size):
            self.data = read_http()
            for key in self.data.keys():
                pkt_values[key].append(self.data[key])
            time.sleep(0.005)
        pack = struct.pack(self.FMT,
                           pkt_values['Day'][0],
                           pkt_values['Time_UDP'][0],
                           pkt_values['Corrected Azimuth'][0],
                           pkt_values['Corrected Elevation'][0],
                           pkt_values['Corrected Boresight'][0],
                           pkt_values['Raw Azimuth'][0],
                           pkt_values['Raw Elevation'][0],
                           pkt_values['Raw Boresight'][0],
                           pkt_values['Azimuth Current 1'][0],
                           pkt_values['Azimuth Current 2'][0],
                           pkt_values['Elevation Current 1'][0],
                           pkt_values['Boresight Current 1'][0],
                           pkt_values['Boresight Current 2'][0],
                           pkt_values['Day'][1],
                           pkt_values['Time_UDP'][1],
                           pkt_values['Corrected Azimuth'][1],
                           pkt_values['Corrected Elevation'][1],
                           pkt_values['Corrected Boresight'][1],
                           pkt_values['Raw Azimuth'][1],
                           pkt_values['Raw Elevation'][1],
                           pkt_values['Raw Boresight'][1],
                           pkt_values['Azimuth Current 1'][1],
                           pkt_values['Azimuth Current 2'][1],
                           pkt_values['Elevation Current 1'][1],
                           pkt_values['Boresight Current 1'][1],
                           pkt_values['Boresight Current 2'][1],
                           pkt_values['Day'][2],
                           pkt_values['Time_UDP'][2],
                           pkt_values['Corrected Azimuth'][2],
                           pkt_values['Corrected Elevation'][2],
                           pkt_values['Corrected Boresight'][2],
                           pkt_values['Raw Azimuth'][2],
                           pkt_values['Raw Elevation'][2],
                           pkt_values['Raw Boresight'][2],
                           pkt_values['Azimuth Current 1'][2],
                           pkt_values['Azimuth Current 2'][2],
                           pkt_values['Elevation Current 1'][2],
                           pkt_values['Boresight Current 1'][2],
                           pkt_values['Boresight Current 2'][2],
                           pkt_values['Day'][3],
                           pkt_values['Time_UDP'][3],
                           pkt_values['Corrected Azimuth'][3],
                           pkt_values['Corrected Elevation'][3],
                           pkt_values['Corrected Boresight'][3],
                           pkt_values['Raw Azimuth'][3],
                           pkt_values['Raw Elevation'][3],
                           pkt_values['Raw Boresight'][3],
                           pkt_values['Azimuth Current 1'][3],
                           pkt_values['Azimuth Current 2'][3],
                           pkt_values['Elevation Current 1'][3],
                           pkt_values['Boresight Current 1'][3],
                           pkt_values['Boresight Current 2'][3],
                           pkt_values['Day'][4],
                           pkt_values['Time_UDP'][4],
                           pkt_values['Corrected Azimuth'][4],
                           pkt_values['Corrected Elevation'][4],
                           pkt_values['Corrected Boresight'][4],
                           pkt_values['Raw Azimuth'][4],
                           pkt_values['Raw Elevation'][4],
                           pkt_values['Raw Boresight'][4],
                           pkt_values['Azimuth Current 1'][4],
                           pkt_values['Azimuth Current 2'][4],
                           pkt_values['Elevation Current 1'][4],
                           pkt_values['Boresight Current 1'][4],
                           pkt_values['Boresight Current 2'][4],
                           pkt_values['Day'][5],
                           pkt_values['Time_UDP'][5],
                           pkt_values['Corrected Azimuth'][5],
                           pkt_values['Corrected Elevation'][5],
                           pkt_values['Corrected Boresight'][5],
                           pkt_values['Raw Azimuth'][5],
                           pkt_values['Raw Elevation'][5],
                           pkt_values['Raw Boresight'][5],
                           pkt_values['Azimuth Current 1'][5],
                           pkt_values['Azimuth Current 2'][5],
                           pkt_values['Elevation Current 1'][5],
                           pkt_values['Boresight Current 1'][5],
                           pkt_values['Boresight Current 2'][5],
                           pkt_values['Day'][6],
                           pkt_values['Time_UDP'][6],
                           pkt_values['Corrected Azimuth'][6],
                           pkt_values['Corrected Elevation'][6],
                           pkt_values['Corrected Boresight'][6],
                           pkt_values['Raw Azimuth'][6],
                           pkt_values['Raw Elevation'][6],
                           pkt_values['Raw Boresight'][6],
                           pkt_values['Azimuth Current 1'][6],
                           pkt_values['Azimuth Current 2'][6],
                           pkt_values['Elevation Current 1'][6],
                           pkt_values['Boresight Current 1'][6],
                           pkt_values['Boresight Current 2'][6],
                           pkt_values['Day'][7],
                           pkt_values['Time_UDP'][7],
                           pkt_values['Corrected Azimuth'][7],
                           pkt_values['Corrected Elevation'][7],
                           pkt_values['Corrected Boresight'][7],
                           pkt_values['Raw Azimuth'][7],
                           pkt_values['Raw Elevation'][7],
                           pkt_values['Raw Boresight'][7],
                           pkt_values['Azimuth Current 1'][7],
                           pkt_values['Azimuth Current 2'][7],
                           pkt_values['Elevation Current 1'][7],
                           pkt_values['Boresight Current 1'][7],
                           pkt_values['Boresight Current 2'][7],
                           pkt_values['Day'][8],
                           pkt_values['Time_UDP'][8],
                           pkt_values['Corrected Azimuth'][8],
                           pkt_values['Corrected Elevation'][8],
                           pkt_values['Corrected Boresight'][8],
                           pkt_values['Raw Azimuth'][8],
                           pkt_values['Raw Elevation'][8],
                           pkt_values['Raw Boresight'][8],
                           pkt_values['Azimuth Current 1'][8],
                           pkt_values['Azimuth Current 2'][8],
                           pkt_values['Elevation Current 1'][8],
                           pkt_values['Boresight Current 1'][8],
                           pkt_values['Boresight Current 2'][8],
                           pkt_values['Day'][9],
                           pkt_values['Time_UDP'][9],
                           pkt_values['Corrected Azimuth'][9],
                           pkt_values['Corrected Elevation'][9],
                           pkt_values['Corrected Boresight'][9],
                           pkt_values['Raw Azimuth'][9],
                           pkt_values['Raw Elevation'][9],
                           pkt_values['Raw Boresight'][9],
                           pkt_values['Azimuth Current 1'][9],
                           pkt_values['Azimuth Current 2'][9],
                           pkt_values['Elevation Current 1'][9],
                           pkt_values['Boresight Current 1'][9],
                           pkt_values['Boresight Current 2'][9])
        return pack

    def run(self):
        host = "localhost"
        port = self.write_port
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        pkt = self.set_values()
        sock.sendto(pkt, (host, port))
        #time.sleep(0.05)
        return pkt

if __name__ == '__main__':
    udp = UDP_Sim(10008, 8102)
    while True:
        pkt = udp.run()
        time.sleep(0.05)
#        print(pkt)
