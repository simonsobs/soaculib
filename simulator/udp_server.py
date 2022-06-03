import time
import struct
import socket


UDP_KEYS = [
    'Day',
    'Time_UDP',
    'Corrected Azimuth',
    'Corrected Elevation',
    'Corrected Boresight',
    'Raw Azimuth',
    'Raw Elevation',
    'Raw Boresight',
    'Azimuth Current 1',
    'Azimuth Current 2',
    'Elevation Current 1',
    'Boresight Current 1',
    'Boresight Current 2']


class AcuUdpServer:
    """Class meant to mimic the ACU UDP Server.

    args:
        write_port (int): Port to write UDP packets to
        data_object (DataMaster): ACU emulating data object

    """
    def __init__(self, write_port, data_object):
        self.pkt_size = 10
        self.fmt = '<' + 'idddddddddddd'*self.pkt_size
        self.write_port = write_port
        self.data_object = data_object
        self.data = data_object.data

    def _build_udp_data(self):
        """Retreive (and update) the values from the DataMaster.

        The full data from DataMaster is more than the UDP needs to report, so
        we then limit just to the info in UDP_KEYS.

        """
        all_data = self.data_object.values()
        udp_data = {}
        for key in UDP_KEYS:
            udp_data[key] = all_data[key]
        return udp_data

    def set_values(self):
        """Build the struct to send over UDP to the ACU Agent."""
        # Fetch values from DataMaster object
        pkt_values = {k: [] for k in UDP_KEYS}
        for i in range(self.pkt_size):
            self.data = self._build_udp_data()
            for key in self.data.keys():
                pkt_values[key].append(self.data[key])
            time.sleep(0.005)

        # Build list for struct
        _values = []
        for i in range(self.pkt_size):
            _values.extend([pkt_values[item][i] for item in UDP_KEYS])

        pack = struct.pack(self.fmt, *_values)

        return pack

    def run(self):
        """Run the server.

        At 20 Hz we build a packet of 10 data points and send it out to the ACU Agent.

        """
        host = "localhost"
        port = self.write_port
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            pkt = self.set_values()
            sock.sendto(pkt, (host, port))
            time.sleep(0.05)
