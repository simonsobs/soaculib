import soaculib
import argparse

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', default='guess',
                        help="Config block name to use.  Will default to "
                        "'guess', triggering a lookup based on hostname.")
    return parser

def get_acu():
    import util
    parser = util.get_parser()
    args = parser.parse_args()
    return soaculib.AcuControl(args.config)
