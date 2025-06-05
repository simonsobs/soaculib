USAGE = """acu-headsup

This program queries a dataset from the ACU and renders the
information in a table.

"""


import curses
import time, calendar
import json

import soaculib


class Renderer(list):
    # Items in the list are actually formatting instructions for data;
    # tuples of the form:
    #    ('header', label, None)
    #    ('item', label, key)
    #
    def __init__(self, height, width):
        self.height = height -1
        self.scr_width = width
        self.width = min(80, self.scr_width)
        self.n_cols = int(self.scr_width / self.width)
        self.offset = 0
        self.truncate = True

    def render(self, w, data):
        if len(self) == 0:
            w.clear()
            groups = {'time': [], 'az': [], 'el': [], 'other': []}
            for k in data.keys():
                if k in ['Time', 'Year', 'human-time*', 'ctime*']:
                    groups['time'].append((k.lower(), k))
                elif k.startswith('Azimuth'):
                    groups['az'].append((k.lower().replace('azimuth ',''), k))
                elif k.startswith('Elevation'):
                    groups['el'].append((k.lower().replace('elevation ',''), k))
                else:
                    groups['other'].append((k.lower(), k))
            for k, label in [('time', 'Time Parameters'),
                             ('az', 'Azimuth'),
                             ('el', 'Elevation'),
                             ('other', 'Other')]:
                if len(groups[k]) == 0:
                    continue
                self.append(('header', label + ' '*(self.width-len(label)), None))
                for v in groups[k]:
                    self.append(('item', v[0], v[1]))
        col_i = 0
        for i, (type_, label, key) in enumerate(self[self.offset:]):
            col_i = i // self.height
            row = i - col_i*self.height
            col = col_i*self.width
            if col_i >= self.n_cols:
                break
            if type_ == 'header':
                w.addstr(row,col,label,curses.A_BOLD | curses.A_REVERSE)
            else:
                v = str(data[key])
                spaces = self.width - len(label) - len(v)
                if len(v) > self.width:
                    text = v[:self.width-3] + '...'
                elif spaces < 2:
                    text = ' ' + label[:spaces-2] + '|' + v
                else:
                    text = ' ' + label + ' ' * spaces + v
                w.addstr(row, col, text, curses.A_DIM)

    def update_view(self, step=None, page=None, home=None, end=None,
                    width=None, truncate=None):
        new_offset = self.offset
        if step is not None:
            new_offset += step
        if page is not None:
            new_offset += page * self.height
        if home:
            new_offset = 0
        if end:
            new_offset = len(self) - 1 - self.height
        if width is not None:
            self.width = max(1, self.width + width)
            self.n_cols = int(self.scr_width / self.width)
            self.clear()
        if truncate is not None and truncate != self.truncate:
            self.truncate = truncate
            self.clear()
        new_offset = max(0, min(new_offset, len(self)-1))
        if new_offset != self.offset:
            self.clear()
            self.offset = new_offset


class Recorder:
    filename, fout = None, None
    def __init__(self, filename=None):
        if filename is not None:
            self.filename = filename
            self.fout = open(filename, 'w')
            self.n = 0
    def __del__(self):
        if self.fout is not None:
            self.fout.write(']\n')
            self.fout.close()
    def save_block(self, data):
        if self.fout is not None:
            if self.n == 0:
                self.fout.write('[\n')
            else:
                self.fout.write(',\n')
            self.fout.write(json.dumps(data))
            self.n += 1
        

def time_code(t, fmt='upload'):
    if fmt == 'upload':
        fmt = '%j, %H:%M:%S'
        return time.strftime(fmt, time.gmtime(t)) + ('%.6f' % (t%1.))[1:]
    else:
        fmt = '%j'
        return time.strftime(fmt, time.gmtime(t)) + ('|%.6f' % (t % 86400))

    #day = time.gmtime(t).tm_yday
    #dayf = (t/86400.) % 1.
    #return (day, dayf)

def track_line(t, az, el, fmt='upload'):
    if fmt == 'upload':
        return '%s;%.4f;%.4f\r\n' % (time_code(t), az, el)
    if fmt == 'single':
        return '%s|%.4f|%.4f' % (time_code(t, 'single'), az, el)

def enrich(d, rec=None):
    if 'Year' in d and 'Time' in d:
        t = calendar.timegm(time.strptime('%i' % d['Year'], '%Y')) + 86400 * (d['Time'] - 1)
        d['ctime*'] = '%.6f' % t
        d['human-time*'] = time.strftime('%Y-%m-%d %H:%M:%%07.4f', time.gmtime(t)) % (t%60.)
    if rec is not None and rec.filename is not None:
        d['recording*'] = '+%s' % rec.filename
    else:
        d['recording*'] = 'no (r to start)'
    return d


def headsup(stdscr, acu, dataset='DataSets.StatusSATPDetailed8100'):
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)

    # Limit queries to 10 Hz.
    min_query_period = 0.1

    def quantize_future(t):
        # Returns t1, such that t1 > t and t1 - floor(t) is an integer
        # multiple of min_query_period.
        frac = (t % 1 + min_query_period) // min_query_period
        return t // 1 + frac * min_query_period

    next_query_t = quantize_future(time.time())

    stdscr.addstr(1,1, 'Loading acu-headsup ...')
    w = stdscr
    running = True
    R = None
    rec = Recorder()
    while running:
        now = time.time()
        if now >= next_query_t:
            v = acu.Values(dataset)
            if R is None:
                R = Renderer(*stdscr.getmaxyx())
            data = enrich(v, rec=rec)
            R.render(stdscr, data)
            rec.save_block(data)
            next_query_t += min_query_period
            if now > next_query_t:
                next_query_t = quantize_future(now)
        stdscr.refresh()
        while True:
            c = stdscr.getch()
            if c == -1:
                time.sleep(0.01)
                break
            if c == curses.KEY_RESIZE:
                R = None
            elif c in [ord('r'), ord('R')]:
                if rec.fout is None:
                    rec = Recorder('/home/simons/code/vertex-acu-agent/hacking/data/track_feb25_new.txt')
                else:
                    rec = Recorder()
            elif c in [ord('q'), 27]:
                running = False
            elif c == curses.KEY_UP:
                R.update_view(-1)
            elif c == curses.KEY_DOWN:
                R.update_view(1)
            elif c == curses.KEY_PPAGE:
                R.update_view(page=-1)
            elif c == curses.KEY_NPAGE:
                R.update_view(page=1)
            elif c == ord('+'):
                R.update_view(width=4)
            elif c == ord('-'):
                R.update_view(width=-4)
            elif c == curses.KEY_HOME:
                R.update_view(home=True)
            elif c == curses.KEY_END:
                R.update_view(end=True)
            elif c== ord('.'):
                R.update_view(truncate=not R.truncate)


def get_parser():
    from argparse import ArgumentParser
    parser = ArgumentParser(usage=USAGE)
#    parser.add_argument('-d', '--dataset', default='DataSets.StatusSATPDetailed8100', help='Dataset to monitor')
    parser.add_argument('-d', '--dataset', default='DataSets.StatusGeneral8100', help='Dataset to monitor')
    parser.add_argument('-c', '--config', default='guess', help=
                        "Config block to use.")
    return parser


def main(args=None):
    if args is None:
        parser = get_parser()
        args = parser.parse_args()
    args = parser.parse_args()

    acu = soaculib.AcuControl(args.config, persistent=True, readonly=True)

    if not args.dataset.lower().startswith('datasets.'):
        # Look it up ...
        platform = acu._config.get('platform')
        if platform is None:
            parser.error('ACU configuration does not specify a "platform".')
        if not isinstance(platform, dict):
            cfg = soaculib.configs.get_datasets(platform)
        if cfg is None:
            parser.error(f'aculib config does not describe datasets for '
                         f'platform "{platform}".')

        dataset_opts = {short: full_name for short, full_name in cfg['datasets']}
        if args.dataset == 'list':
            print('Datasets:')
            for k, v in dataset_opts.items():
                print(f'  {k:<20} : {v}')
            parser.exit(1)
        else:
            args.dataset = dataset_opts[args.dataset]

    curses.wrapper(headsup, acu, args.dataset)

if __name__ == '__main__':
    main()
