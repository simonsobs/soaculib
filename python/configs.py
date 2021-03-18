import socket

"""Library of basic configurations for ACUs.

When you 'guess' the config, it will be loaded from the CONFIGS dict
based on socket.gethostname().

"""

CONFIGS = {

    # Simulator ACU at UCologne.
    'nanten-db':   {
        # Address of the "remote" interface.
        'base_url': 'http://172.16.5.95:8100',
        # Address of the "developer" interface.
        'dev_url': 'http://172.16.5.95:8080',
        # Local interface IP.
        'interface_ip': '172.16.5.10',
        # Sleep time to wait for motion to end.
        'motion_waittime': 1.0,
        # List of streams to configure.
        'streams': {
            'main': {
                'acu_name': 'PositionBroadcast',
                'port': 10000,
                'schema': 'v0'
            },
            'ext': {
                'acu_name': 'PositionBroadcastExt',
                'port': 10001,
                'active': False,
            },
        },
        # Deprecated stream configs...
        'broadcaster_url': 'http://172.16.5.95:8080',
        'PositionBroadcast_target': '172.16.5.10:10000',
        'PositionBroadcastExt_target': '172.16.5.10:10001',
    },

    # SATP ACU at Vertex.
    'ocs-acu-1': {
        # Address of the "remote" interface.
        'base_url': 'http://192.168.1.109:8100',
        # Address of the "developer" interface.
        'dev_url': 'http://192.168.1.109:8080',
        # Local interface IP.
        'interface_ip': '192.168.1.110',
        'motion_waittime': 5.0,
        # List of streams to configure.
        'streams': {
            'main': {
                'acu_name': 'PositionBroadcast',
                'port': 10001,
                'schema': 'v0'
            },
            'ext': {
                'acu_name': 'PositionBroadcastExt',
                'port': 10002,
                'active': False,
            },
        },
        # Deprecated stream configs...
        'broadcaster_url': '192.168.1.109:8080',
        'PositionBroadcast_target': '192.168.1.109:10001',
        'PositionBroadcastExt_target': '192.168.1.109:10002',
    },

    # This is not an ACU config.
    '_stream_schemas': {
        'v0': {
            'format': '<iddd',
            'fields': ['Day', 'Time', 'Azimuth', 'Elevation']
            },
    },
}

def guess_config(hostname):
    """Return an ACU config block.  The "hostname" argument can be any
    of:
    - a dict, in which case it is simply returned to the user.
    - a string giving a hostname in CONFIGS, in which case
      CONFIGS[hostname] is returned.
    - the string 'guess', in which case the current system hostname is
      determined and the config looked up in CONFIGS.

    """
    if isinstance(hostname, dict):
        return hostname
    if hostname == 'guess':
        hostname = socket.gethostname()
    if not hostname in CONFIGS:
        raise ValueError('No block for system "%s" in CONFIGS!' % hostname)
    return CONFIGS[hostname]

def get_stream_schema(name):
    """
    Returns the _stream_schemas entry for name.
    """
    return CONFIGS['_stream_schemas'][name]
