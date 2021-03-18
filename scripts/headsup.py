#!/usr/bin/env python3
import curses
import time, calendar
import json

import soaculib

class Renderer(list):
    def __init__(self, height, width):
        self.height = height
        self.width = min(40, width)
        self.n_cols = int(width / self.width)
    def render(self, w, data):
        if len(self) == 0:
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
                self.append(('header', label + ' '*(self.width-len(label)), None))
                for v in groups[k]:
                    fmt = '  %s %%%is' % (v[0], self.width - len(v[0]) - 3)
                    self.append(('item', fmt, v[1]))
        col_i = 0
        for i, (type_, fmt, key) in enumerate(self):
            col_i = i // self.height
            row = i - col_i*self.height
            col = col_i*self.width
            if col_i > self.n_cols:
                break
            if type_ == 'header':
                w.addstr(row,col,fmt,curses.A_BOLD | curses.A_REVERSE)
            else:
                w.addstr(row,col,fmt % data[key], curses.A_DIM)

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

#def main(stdscr, dataset='DataSets.StatusGeneral8100'):
def main(stdscr, acu, dataset='DataSets.StatusSATPDetailed8100'):
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)
    
    # ACU limits requests to 5 Hz (10 Hz according to docs...)
    min_query_period = 0.05   # Limit to 20 Hz.
    query_t = 0

    stdscr.addstr(1,1, 'blech')
    w = stdscr
    running = True
    R = None
    rec = Recorder()
    while running:
        now = time.time()
        if now - query_t > min_query_period:
            v = acu.Values(dataset)
            if R is None:
                R = Renderer(*stdscr.getmaxyx())
            data = enrich(v, rec=rec)
            R.render(stdscr, data)
            rec.save_block(data)
            query_t = now
        stdscr.refresh()
        while True:
            c = stdscr.getch()
            if c == -1:
                #time.sleep(.05)
                break
            if c == curses.KEY_RESIZE:
                stdscr.clear()
                R = None
            if c in [ord('r'), ord('R')]:
                if rec.fout is None:
                    rec = Recorder('/home/simons/code/vertex-acu-agent/hacking/data/track_feb25_new.txt')
                else:
                    rec = Recorder()
            if c in [ord('q'), 27]:
                running = False

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
#    parser.add_argument('-d', '--dataset', default='DataSets.StatusSATPDetailed8100', help='Dataset to monitor')
    parser.add_argument('-d', '--dataset', default='DataSets.StatusGeneral8100', help='Dataset to monitor')
    args = parser.parse_args()

    acu = soaculib.AcuControl()
    curses.wrapper(main, acu, args.dataset)
