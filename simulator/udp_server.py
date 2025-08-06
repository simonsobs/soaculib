import time
import struct
import socket


UDP_KEYS = {
    'v2': [
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
        'Boresight Current 2',
    ],
    'vx2': [
        'Day', 'Time_UDP',
        'AzDesPos', 'AzActPos', 'AzPosErr',
        'AzActVel', 'AzVelFfw', 'AzAccFfw',
        'AzVelMot1', 'AzVelMot2', 'AzVelMot3', 'AzVelMot4']
}


class AcuUdpServer:
    """Class to produce UDP frames, simulating 200 Hz ACU
    PositionBroadcast and PositionBroadcastExt streams.  Frames are
    issued at up to 20 Hz, each containing 10 samples.

    args:
        write_port (int): Port to write UDP packets to
        data_object (DataMaster): ACU emulating data object
        keys (str or list of str): If a list of str, the data to
          populate for each sample.  If this is a str, it's a stream
          schema version code (e.g. "v2") that will be looked up in
          UDP_KEYS in this module.

    """
    def __init__(self, write_port, data_object, keys=None):
        if keys is None:
            keys = 'v2'
        if isinstance(keys, str):
            keys = UDP_KEYS[keys]

        self.keys = keys
        assert tuple(keys[:2]) == ('Day', 'Time_UDP')
        self.write_port = write_port
        self.data_object = data_object

        self.next_sample_time = None
        self.samples_per_packet = 10
        self.sample_interval = 0.005
        self.fmt = '<' + ('id' + 'd' * (len(keys) - 2)) * self.samples_per_packet

    def _build_udp_data(self):
        """Retrieve (and update) the values from the DataMaster. Any
        keys not present in DataMaster will return value 0.

        """
        all_data = self.data_object.values()
        return [all_data.get(key, 0.) for key in self.keys]

    def _collect_values(self):
        """Build the struct to send over UDP to the ACU Agent."""
        _values = []
        for i in range(self.samples_per_packet):
            # Wait until the next sample time.
            now = time.time()
            dt = self.next_sample_time - now
            if dt > 0:
                time.sleep(dt)
            self.next_sample_time += self.sample_interval
            sample = self._build_udp_data()
            _values.extend(sample)
        return struct.pack(self.fmt, *_values)

    def run(self):
        """Run the server.

        At 20 Hz we build a packet of 10 data points and send it out to the ACU Agent.

        """
        host = "localhost"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.next_sample_time = int(time.time() + 1)
        while True:
            pkt = self._collect_values()
            sock.sendto(pkt, (host, self.write_port))
