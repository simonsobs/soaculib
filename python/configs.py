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
        # Address of the read-only "remote" interface.
        'readonly_url': 'http://172.16.5.95:8110',
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
                'schema': 'v2'
            },
            'ext': {
                'acu_name': 'PositionBroadcastExt',
                'port': 10001,
                'active': False,
            },
        },
        'status': {
            'status_name': 'Datasets.StatusSATPDetailed8100',
#            'status_name': 'Datasets.StatusCCATDetailed8100',
            },

        # For dataset description (see _platforms).
        'platform': 'satp',
        'motion_limits': {
            'azimuth': {
                'lower': -90.0,
                'upper': 480.0,
            },
            'elevation': {
                'lower': 20.0,
                'upper': 90.0,
            },
            'boresight': {
                'lower': 0.0,
                'upper': 360.,
            },
            'acc': (8./1.88),
        },

        # Deprecated stream configs...
        'broadcaster_url': 'http://172.16.5.95:8080',
        'PositionBroadcast_target': '172.16.5.10:10000',
        'PositionBroadcastExt_target': '172.16.5.10:10001',
    },

    # SATP1 ACU at Vertex.
    'satp1': {
        # Address of the "remote" interface.
        'base_url': 'http://192.168.1.111:8100',
        # Address of the read-only "remote" interface.
        'readonly_url': 'http://192.168.1.111:8110',
        # Address of the "developer" interface.
        'dev_url': 'http://192.168.1.111:8080',
        # Local interface IP.
        'interface_ip': '192.168.1.110',
        'motion_waittime': 5.0,
        # List of streams to configure.
        'streams': {
            'main': {
                'acu_name': 'PositionBroadcast',
                'port': 10004, #???
                'schema': 'v2'
            },
            'ext': {
                'acu_name': 'PositionBroadcastExt',
                'port': 10005, #???
                'active': False,
            },
        },
        'status': {
            'status_name': 'Datasets.StatusSATPDetailed8100',
            },

        # For dataset description (see _platforms).
        'platform': 'satp',
        'motion_limits': {
            'azimuth': {
                'lower': -90.0,
                'upper': 480.0,
            },
            'elevation': {
                'lower': 20.0,
                'upper': 50.0,
            },
            'boresight': {
                'lower': 0.0,
                'upper': 360.,
            },
            'acc': (8./1.88),
        },
        # Deprecated stream configs...
        'broadcaster_url': '192.168.1.111:8080',
        'PositionBroadcast_target': '192.168.1.111:10001',
        'PositionBroadcastExt_target': '192.168.1.111:10002',
    },

    # SATP2 ACU at Vertex.
    'satp2': {
        # Address of the "remote" interface.
        'base_url': 'http://192.168.1.109:8100',
        # Address of the read-only "remote" interface.
        'readonly_url': 'http://192.168.1.109:8110',
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
                'schema': 'v2'
            },
            'ext': {
                'acu_name': 'PositionBroadcastExt',
                'port': 10002,
                'active': False,
            },
        },
        'status': {
            'status_name': 'Datasets.StatusSATPDetailed8100',
            },

        # For dataset description (see _platforms).
        'platform': 'satp',
        'motion_limits': {
            'azimuth': {
                'lower': -90.0,
                'upper': 480.0,
            },
            'elevation': {
                'lower': 20.0,
                'upper': 50.0,
            },
            'boresight': {
                'lower': 0.0,
                'upper': 360.,
            },
            'acc': (8./1.88),
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
        'v1': {
            'format': '<iddddd',
            'fields': ['Day', 'Time', 'Corrected_Azimuth', 'Corrected_Elevation', 'Raw_Azimuth', 'Raw_Elevation']
            },
        'v2':{
            'format': '<idddddddddddd',
            'fields': ['Day', 'Time', 'Corrected_Azimuth', 'Corrected_Elevation', 'Corrected_Boresight', 'Raw_Azimuth', 'Raw_Elevation', 'Raw_Boresight', 'Azimuth_Current_1', 'Azimuth_Current_2', 'Elevation_Current_1', 'Boresight_Current_1', 'Boresight_Current_2']
            }
    },

    # This is not an ACU config.
    '_platforms': {
        'satp': {
            'default_dataset': 'satp',
            'datasets': [
                ('satp',       'DataSets.StatusSATPDetailed8100'),
                ('general',    'DataSets.StatusGeneral8100'),
                ('extra',      'DataSets.StatusExtra8100'),
                ('third',      'DataSets.Status3rdAxis'),
                ('faults',     'DataSets.StatusDetailedFaults'),
                ('pointing',   'DataSets.CmdPointingCorrection'),
                ('spem',       'DataSets.CmdSPEMParameter'),
                ('weather',    'DataSets.CmdWeatherStation'),
                ('azimuth',    'Antenna.SkyAxes.Azimuth'),
                ('elevation',  'Antenna.SkyAxes.Elevation'),
            ],
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
