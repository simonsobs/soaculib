import calendar
import time
from html.parser import HTMLParser


class Timestamp:
    """Store a UTC timestamp, unix style."""

    def __init__(self, t=0.):
        self.t = t

    @classmethod
    def from_acu(cls, year_int, day_float):
        return cls(calendar.timegm(time.strptime('%i' % year_int, '%Y')) + 
                   86400 * day_float)

    @classmethod
    def from_human(cls, timestr):
        for fmt in [
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M',
                '%Y-%m-%d %H:%M',
                '%Y-%m-%d',
        ]:
            try:
                t =  calendar.timegm(time.strptime(timestr, fmt))
                break
            except:
                pass
        else:
            raise ValueError('Could not decode "{}" as a human time.'.format(timestr))
        return cls(t)

    def human(self):
        return time.strftime('%Y-%m-%d %H:%M:%%07.4f', time.gmtime(self.t)) % (self.t%60.)

    def __repr__(self):
        return '%+018.6f|%s' % (self.t, self.human())

    def __add__(self, t):
        if isinstance(t, Timestamp):
            return Timestamp(self.t + t.t)
        return Timestamp(self.t + t)


class TableExtractor(HTMLParser):
    """HTMLParser specializing in extracting data from HTML tables.

    This is targeting the ACU "developer" interface, for
    PositionBroadcast stream configuration information.

    Suppose you expect Port/Destination to be in columns 0 and 1 of
    some table in output.html::

        te = TableExtractor()
        te.feed(open('output.html').read())
        result = te.simple_search(['Port', 'Destination'], 0, 1)

    """

    def __init__(self):
        super().__init__()

        # The table data dictionaries, in the order encountered.  Each
        # dict has entries:
        #  - rows: list of lists of row data
        #  - 'index': the index of this table in self.tables.
        #  - lineage: the index in self.tables of the sequence of
        #    parent tables; will be [] for unnested tables.
        #
        # Once the page has been parsed, this should be all you need.
        self.tables = []

        # During parsing, the current table data dictionary.
        self.active = None

        # During parsing, a "reference" to a list (i.e. one of the
        # lists in self.active['rows'] where "data" should be
        # appended, or is None if we're not inside a td or th element.
        self.dest = None

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            if self.active:
                lineage = self.active['lineage'] + [self.active['index']]
            else:
                lineage = []
            self.active = {'rows': [],
                           'lineage': lineage,
                           'index': len(self.tables)}
            self.tables.append(self.active)
        if self.active is None:
            return
        if tag == 'tr':
            self.active['rows'].append([])
        elif tag in ['td', 'th']:
            if 'rows' in self.active:
                self.dest = self.active['rows'][-1]

    def handle_endtag(self, tag):
        if tag == 'table':
            if len(self.active['lineage']):
                self.active = self.tables[self.active['lineage'][-1]]
            else:
                self.active = None
        if tag in ['td', 'th']:
            self.dest = None

    def handle_data(self, data):
        if self.dest is not None:
            self.dest.append(data)

    def simple_search(self, keys, index_col, data_col):
        """Look in all tables for places where value in column index_col (int)
        matches an entry in keys (list of str); if found, grab the
        value from that row in column data_col (int) and return all
        the results as a dict.

        """
        output = {k: None for k in keys}
        for t in self.tables:
            for row in t['rows']:
                if len(row) <= max(index_col,data_col):
                    continue
                k, v = row[index_col], row[data_col]
                if k in keys:
                    output[k] = v
        return output
