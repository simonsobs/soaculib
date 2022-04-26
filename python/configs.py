import os
import socket
import yaml

"""Support for loading ACU configs.

The soaculib config file is a yaml file describing one or more ACUs.
See the load() function for the list of filenames that will be tried.
If you want the envvar, it's ACU_CONFIG.

See acu-configs.yaml, in the package directory, for example syntax.

"""

cache = None

def load(config_file=None, update_cache=True):
    """Load ACU configuration file and return the contents (as a dict).
    By default, this will also update (replace) the internal
    configuration cache.

    If the config_file argument is passed, that file will be used.  If
    not, then the value of the ACU_CONFIG environment variable is
    used.  If that envvar is not set, then ~/.acu.yaml and
    /etc/acu.yaml are tried.

    Finally, the acu-configs.yaml in the installed module is loaded.
    This is likely to go away soon.

    If none of those exist, an exception is raised.

    """
    global cache
    things_to_try = [
        (config_file, True, 'user-specified file "{filename}"'),
        (os.getenv('ACU_CONFIG'), True, 'environment variable ACU_CONFIG="{filename}"'),
        (os.path.expanduser('~/.acu.yaml'), False, 'local user config file "{filename}"'),
        ('/etc/acu.yaml', False, 'global config file "{filename}"'),
        (os.path.join(os.path.split(__file__)[0], 'acu-configs.yaml'), False, 'acu-configs.yaml'),
    ]
    for filename, fail_on_missing, desc_format in things_to_try:
        if filename is None:
            continue
        if os.path.exists(filename):
            config = yaml.safe_load(open(filename, 'r').read())
            break
        if fail_on_missing:
            raise RuntimeError("Config file not found; " +
                               desc_format.format(filename=filename))
    else:
        raise RuntimeError("Could not find an ACU config file.  See docs "
                           "or try putting one in ~/.acu.yaml or /etc/acu.yaml.")
    # Process config...
    if update_cache:
        cache = config
    return config


def guess_config(hostname):
    """Return an ACU config block.  The "hostname" argument can be any
    of:
    - a dict, in which case it is simply returned to the user.
    - a string giving a hostname in CONFIGS, in which case
      CONFIGS[hostname] is returned.
    - the string 'guess', in which case the current system hostname is
      determined and the config looked up in CONFIGS.

    """
    if cache is None:
        load()

    devices = cache.get('devices', {})

    if isinstance(hostname, dict):
        return hostname
    if hostname == 'guess':
        hostname = socket.gethostname()
    if not hostname in devices:
        if '_default' in devices:
            hostname = default
        else:
            raise ValueError('No block for system "%s" (and no _default) in config!' % hostname)
    return devices[hostname]

def get_stream_schema(name):
    """
    Returns the _stream_schemas entry for name.
    """
    return cache['stream_schemas'][name]

def get_datasets(platform):
    """
    Returns the datasets entry for the given platform.
    """
    return cache['datasets'][platform]
