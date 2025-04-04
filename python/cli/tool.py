USAGE = """acu-special

This program may be used to perform various operations on the ACU,
including setting up and testing the UDP broadcast streams, dumping
datasets, and querying version information.

"""

import argparse
import requests
import socket
import struct
import subprocess
import time
import urllib
import yaml


import soaculib as aculib
from soaculib.status_keys import status_fields

def get_parser():
    parser = argparse.ArgumentParser(usage=USAGE)
    # Add global options here...

    parser.add_argument('--readonly', default=False, action='store_true', help=
                        "Use the 'readonly' interface instead of the main "
                        "read/write interface.")
    parser.add_argument('-c', '--config', default='guess', help=
                        "Config block name to use.")
    subparsers = parser.add_subparsers(dest='command')

    # The bcast-* commands have a common set of options.
    bcast_p = argparse.ArgumentParser(add_help=False)
    bcast_p.add_argument('-s', '--stream', default=None)
    bcast_p.add_argument('-f', '--force', default=False, action='store_true')

    p = subparsers.add_parser('ping', help=
                              "Check connections to the ACU.")

    p = subparsers.add_parser('bcast', help=
                              "Inspect current broadcast stream configs, "
                              "a.k.a UDP, PositionBroadcast, etc.",
                              parents=[bcast_p])
    p = subparsers.add_parser('enable-bcast', help=
                              "Get the PositionBroadcast stream enabled, "
                              "in a safe way.",
                              parents=[bcast_p])
    p = subparsers.add_parser('disable-bcast', help=
                              "Disable the PositionBroadcast stream, if it is "
                              "currently enabled (--force to do so regardless).",
                              parents=[bcast_p])
    p = subparsers.add_parser('listen-bcast', help=
                              "Monitor the PositionBroadcast stream(s).",
                              parents=[bcast_p])
    p.add_argument('-e', '--enable', action='store_true', help="Enable the stream, too.")
    p.add_argument('-o', '--output', help=
                   "Record the stream to file.")

    p = subparsers.add_parser('meta', help=
                              "Query the Meta plugin.  Prints a huge XML tree.")
    p = subparsers.add_parser('version', help=
                              "Query the Version plugin.  Prints a short text listing.")
    p = subparsers.add_parser('docs', help=
                              "Query the Documentation plugin for some identifier. "
                              "Prints HTML.")
    p.add_argument('target', help=
                   "The identifier to get docs for; e.g. Antenna.SkyAxes.Azimuth")
    p.add_argument('type', default='actual',
                   choices=['actual', 'target', 'parameter', 'commands'],
                   help="Specifies which aspect of the module to describe.")

    p = subparsers.add_parser('dataset', help=
                              "Query a dataset and print results to terminal.")
    p.add_argument('datasets', default=None, nargs='*',
                   help="Zero or more dataset names or short names.")
    p.add_argument('--list', action='store_true',
                   help="Show list of known datasets.")
    p.add_argument('--check', action='store_true',
                   help="Check each listed item.")
    p.add_argument('--reconcile', action='store_true',
                   help="Verify the mapping between fields found in dataset "
                   "and fields enumerated internally for reporting.")

    p = subparsers.add_parser('stop', help="Stop all axes.")

    return parser


def main(args=None):
    if args is None:
        parser = get_parser()
        args = parser.parse_args()

    acu = aculib.AcuControl(args.config, readonly=args.readonly)

    def get_target_streams():
        if args.stream is None:
            return False, acu.streams
        if not args.stream in acu.streams:
            parser.error('No stream "%s" found in ACU.' % args.stream)
        return True, {args.stream: acu.streams[args.stream]}


    if args.command == 'ping':
        acu_config = aculib.guess_config(args.config)
        print('Using config block "{}" from {}\n'.format(
            acu_config['_name'], acu_config['_filename']))
        url = acu_config['base_url'] # e.g. 'http://172.16.5.95:8100']

        host = urllib.parse.urlparse(url).hostname
        print(f'Pinging host at {host}')
        p = subprocess.Popen(["/bin/ping", "-c1", "-w2", host],
                             stdout=subprocess.PIPE)
        p.communicate()
        if p.returncode == 0:
            print(f' -- host responded to ping.')
        else:
            print(f' -- WARNING - host did not respond to ping.')
        print()

        # Check main, readonly,  API.
        for key, expected in [('base_url', 400),
                              ('readonly_url', 400),
                              ('dev_url', 200)]:
            print(f'Trying http on {key} ...')
            url = acu_config.get(key)
            if url is None:
                print(f' -- (url not configured)')
                continue
            print(f' -- trying {url}')
            try:
                t = requests.get(url + '/')
            except requests.ConnectionError:
                t = None
            if t is None:
                print(f' -- WARNING - could not connect.')
            elif t.status_code == expected:
                print(f' -- got expected HTTP response {t.status_code}')
            else:
                print(f' -- WARNING - got unexpected HTTP response {t.status_code}')
            print()

    elif args.command == 'bcast':
        is_all_streams, target_streams = get_target_streams()
        if is_all_streams:
            print('Here is a summary of the %i known streams:\n' %
                  len(target_streams))
        for name, stream in target_streams.items():
            print(f"  stream:        '{name}' @{stream.p['module']}")
            cfg, raw = stream.get_status()
            print(f"    target_ok:   {cfg['target_ok']}")
            print(f"    enabled:     {cfg['enabled']}")
            print()

    elif args.command == 'enable-bcast':
        is_all_streams, target_streams = get_target_streams()
        for name, stream in target_streams.items():
            print(f"  stream:        '{name}' @{stream.p['module']}")
            print(f"    enabling stream")
            cfg, raw = stream.safe_enable()
            if not cfg['enabled'] or not cfg['target_ok']:
                print(f"    -- stream not successfully enabled!")

    elif args.command == 'disable-bcast':
        is_all_streams, target_streams = get_target_streams()
        for name, stream in target_streams.items():
            print(f"  stream:        '{name}' @{stream.p['module']}")
            cfg, raw = stream.get_status()
            if cfg['enabled'] or args.force:
                print("    disabling...")
                stream.disable()
            else:
                print("    stream already disabled, no action.")

    elif args.command == 'listen-bcast':
        socks = {}
        report_interval = 1.
        socket_timeout = 0.3

        is_all_streams, target_streams = get_target_streams()
        for name, stream in target_streams.items():
            print(f"  stream:        '{name}' @{stream.p['module']}")
            cfg, raw = stream.get_status()
            print(f"    target_ok:   {cfg['target_ok']}")
            print(f"    enabled:     {cfg['enabled']}")
            if not cfg['target_ok'] or not cfg['enabled']:
                if args.enable:
                    print('      -- enabling the stream safely')
                    cfg, raw = stream.safe_enable()
                    if not cfg['enabled'] or not cfg['target_ok']:
                        sprint(f"    -- stream not successfully enabled!")
                else:
                    print("    -- note you can pass --enable to re-configure "
                          "       and enable the stream now.")
            print()
            raw['schema'] = stream.p['schema']
            socks[name] = raw

        if args.output:
            if len(target_streams) != 1:
                parser.error("Pick a single stream with -s to output.")
            print('Saving stream to %s' % args.output)
            list(socks.values())[0]['fout'] = open(args.output, 'wb')

        for name, s in socks.items():
            sock = socket.socket(socket.AF_INET,
                                 socket.SOCK_DGRAM)
            sock.bind((s['Destination'], int(s['Port'])))
            sock.settimeout(socket_timeout)
            socks[name]['sock'] = sock
            socks[name]['next_read'] = time.time()

        while True:
            for name, s in socks.items():
                now = time.time()

                if s['next_read'] > now:
                    continue

                try:
                    data, addr = s['sock'].recvfrom(64000)
                except socket.timeout:
                    print(name, '  -- timeout')
                    s['next_read'] = now + 1.
                    s.pop('mark_time', None)
                    continue

                if len(data) and s.get('fout'):
                    s['fout'].write(data)

                if not 'mark_time' in s:
                    s['mark_time'] = now
                    s['mark_bytes'] = 0
                    s['mark_frames'] = 0

                else:
                    s['mark_bytes'] += len(data)
                    s['mark_frames'] += 1

                if now - s['mark_time'] < report_interval:
                    continue

                # Compute rates and reset counter
                byte_rate = s['mark_bytes'] / (now - s['mark_time'])
                frame_rate = s['mark_frames'] / (now - s['mark_time'])
                del s['mark_time']

                frame_size = len(data)
                bytes_per_sample = frame_size / 10

                print(f'{name}: frame_rate={frame_rate:.3f}, data_rate={byte_rate:.3f}, '
                      f'frame_size={frame_size} '
                      f'({bytes_per_sample:.1f} bytes per sample)')

                if s['schema'] is not None:
                    fmt = s['schema']['format']
                    n = struct.calcsize(fmt)
                    if n != bytes_per_sample:
                        print(f'  -- schema struct size mismatch ({n} vs {bytes_per_sample})!')
                    vals = struct.unpack(fmt, data[-n:])
                    for f, v in zip(s['schema']['fields'], vals):
                        print(f'  {f:<25}: {v}')
                print()


    elif args.command == 'meta':
        output = next(acu.http.Meta())
        print(output)

    elif args.command == 'version':
        output = next(acu.http.Version())
        print(output)

    elif args.command == 'docs':
        output = next(acu.http.Documentation(args.target, args.type))
        print(output)

    elif args.command == 'dataset':
        platform = acu._config.get('platform')
        if platform is None:
            parser.error('ACU configuration does not specify a "platform".')
        if not isinstance(platform, dict):
            cfg = aculib.configs.get_datasets(platform)
            if cfg is None:
                parser.error(f'The loaded config does not list datasets for platform "{platform}".')

        dataset_opts = {short: full_name for short, full_name in cfg['datasets']}
        if args.list:
            print('Known datasets:')
            for short, full_name in dataset_opts.items():
                print('  %-20s: %s' % (short, full_name))
                if args.check:
                    try:
                        data = acu.Values(full_name)
                    except aculib.http.HttpError as e:
                        print('    error requesting dataset "%s"!' % full_name)
                        continue
                    print('    loaded values for %i items' % len(data))
            print()
        else:
            if len(args.datasets) == 0:
                args.datasets = [cfg['default_dataset']]
            for n in args.datasets:
                n = dataset_opts.get(n, n)
                try:
                    t = acu.Values(n)
                except aculib.http.HttpError as e:
                    print('#  error requesting dataset "%s"!' % n)
                    continue
                if args.reconcile:
                    internal_map = {}
                    for group, items in status_fields[platform]['status_fields'].items():
                        for field, alias in items.items():
                            internal_map[field] = f'{group}.{alias}'
                    print('Items not found in internal map:')
                    for k, v in t.items():
                        if internal_map.pop(k, None) is None:
                            print(f'  "{k}" (current value: {v})')
                    print()
                    print('Items in internal map not found in dataset:')
                    for k, v in internal_map.items():
                        print(f'  "{k}"')
                    print()
                else:
                    print(f'# Using "{n}"')
                    for k, v in t.items():
                        print('%-30s : %s' % (k,repr(v)))
                    print()

    elif args.command == 'stop':
        print('Requesting stop...')
        acu.stop()

    else:
        print('No action taken.')
