#!/usr/bin/env python

import argparse
import socket
import struct
import time
import yaml

import soaculib as aculib

parser = argparse.ArgumentParser()
# Add global options here...

subparsers = parser.add_subparsers(dest='command')

# The bcast-* commands have a common set of options.
bcast_p = argparse.ArgumentParser(add_help=False)
bcast_p.add_argument('-s', '--stream', default=None)
bcast_p.add_argument('-f', '--force', default=False, action='store_true')

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

p = subparsers.add_parser('stop', help="Stop all axes.")



args = parser.parse_args()

acu = aculib.AcuControl()


# Functions defined below this point may freely use globals assigned
# above this point!

def get_target_streams():
    if args.stream is None:
        return False, acu.streams
    if not args.stream in acu.streams:
        parser.error('No stream "%s" found in ACU.' % args.stream)
    return True, {args.stream: acu.streams[args.stream]}


def stream_safe_enable(stream, print_func=print):
    for tries in range(6):
        cfg, raw = stream.get_status()
        print(tries, cfg, raw)
        if not cfg['target_ok']:
            if cfg['enabled']:
                print_func("disabling...")
                stream.disable()
            else:
                print_func("configuring...")
                stream.set_config()
        else:
             if cfg['enabled']:
                 print_func("stream is enabled.")
                 break
             else:
                print_func("enabling...")
                stream.enable()
    else:
        return False, "Failed to complete enabling of stream."
    return True, ""


if args.command == 'bcast':
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
        ok, msg = stream_safe_enable(
            stream, print_func=lambda x: print('    ' + x))
        if not ok:
            parser.error(msg)

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
                ok, msg = stream_safe_enable(
                    stream, print_func=lambda x: print(' '*8 + x))
                if not ok:
                    print('      -- not enabled!')
                # Refresh the config!
                cfg, raw = stream.get_status()
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
            if s['next_read'] > time.time():
                continue
            try:
                data, addr = s['sock'].recvfrom(64000)
            except socket.timeout:
                print(name, ' - timeout')
                s['next_read'] = time.time() + 1.
                s.pop('mark_time', None)
                continue

            now = time.time()
            if not 'mark_time' in s:
                print(name, ' - received %i bytes, starting rate counter.' % len(data))
                s['mark_time'] = now
                s['mark_bytes'] = 0
            else:
                s['mark_bytes'] += len(data)
                if now - s['mark_time'] > report_interval:
                    rate = s['mark_bytes'] / (now - s['mark_time'])
                    s['mark_time'] = now
                    s['mark_bytes'] = 0
                    # Unpack?
                    if s['schema'] is not None:
                        fmt = s['schema']['format']
                        n = struct.calcsize(fmt)
                        d = struct.unpack(fmt, data[-n:])
                    else:
                        d = '(unknown)'
                    print(name, ' - rate=%.2f bytes/s; data=' % rate, d)

            if len(data) and s.get('fout'):
                s['fout'].write(data)

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
    cfg = yaml.safe_load(open('acu_configs.yaml', 'r'))['platforms']['satp']
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
            print(f'# Using "{n}"')
            for k,v in t.items():
                print('%-30s : %s' % (k,repr(v)))
            print()

elif args.command == 'stop':
    print('Requesting stop...')
    acu.stop()

else:
    print('No action taken.')
