"""
Measure response rate for some dataset from ACU.
"""

import soaculib
import argparse
import time

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', default='guess',
                        help="Config block name to use.  Will default to "
                        "'guess', triggering a lookup based on hostname.")
    parser.add_argument('--persistent', action='store_true',
                        help="Request use of persistent HTTP connection.")
    parser.add_argument('--count', type=int)
    return parser

def tod(t):
    return t % 86400

parser = get_parser()
args = parser.parse_args()
acu = soaculib.AcuControl(args.config, persistent=args.persistent,
                          readonly=True)

dset = 'Datasets.StatusCCATDetailed8100'

bad_delay_thresh = .3   # typical is 0.2
if args.persistent:
    bad_delay_thresh = .01   # typical is ... fast

count = 0
dt_sum = 0

while True:
    tstart = time.time()
    v = acu.Values(dset)
    tend = time.time()
    dt = (tend - tstart)
    if dt < bad_delay_thresh:
        count += 1
        dt_sum += dt
    else:
        print('After %i good packets, response time is %f' % (count, dt))
        print('  Request issued at  %.3f' % tod(tstart))
        print('  Response recd at   %.3f' % tod(tend))
        print('  ACU timestamp is   %.3f' % tod((v['Time'] * 86400)))
        if count > 0:
            print('  (Average response time was %.6f)' % (dt_sum / count))
        count = 0
        dt_sum = 0
    if count > 100:
        print('Average response rate is', (dt_sum / count))
        count = 0
        dt_sum = 0
    if args.count is not None:
        args.count -= 1
        if args.count == 0:
            break
