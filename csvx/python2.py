from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import io
import csv


def decode(x):
    if x is None:
        return x
    return x.decode('utf-8')


def encode(x):
    if x is None:
        return x
    return x.encode('utf-8')


class UTF8Recoder(object):
    """
    Iterator that reads a text stream and reencodes the input to UTF-8
    """

    def __init__(self, f):
        self.f = f

    def __iter__(self):
        return self

    def next(self):
        x = self.f.next()
        return x.encode("utf-8")


class TextReader(object):
    """
    Accepts text streams. Used for wrapping a python-2 csv `reader`
    (which reads bytes).
    """

    def __init__(self, f, dialect=csv.excel, **kwds):
        f = UTF8Recoder(f)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return list(r.decode('utf-8') for r in row)

    __next__ = next

    def __iter__(self):
        return self


class TextDictReader(object):
    """
    Same as TextReader, but wrapping DictReader
    """

    def __init__(self, f, dialect=csv.excel, **kwds):
        f = UTF8Recoder(f)
        self.reader = csv.DictReader(f, dialect=dialect, **kwds)
        self.fieldnames = self.reader.fieldnames
        self.fieldnames = list(r.decode('utf-8')
                               for r in self.reader.fieldnames)

    def next(self):
        row = self.reader.next()

        def decode_value(k, v):
            if k is None:
                return [x.decode('utf-8') for x in v]

            if v is None:
                return v
            return v.decode('utf-8')

        return {decode(k): decode_value(k, v) for k, v in row.items()}

    __next__ = next

    def __iter__(self):
        return self


class TextWriter(object):
    """Wraps a python2 csv writer for writing to text streams
    """

    def __init__(self, f, dialect=csv.excel, **kwds):
        self.queue = io.BytesIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f

    def writerow(self, row):
        e = [s.encode('utf-8') for s in row]
        self.writer.writerow(e)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()

        data = data.decode('utf-8')
        # ... and reencode it into the target encoding
        self.stream.write(data)
        # empty queue
        self.queue.seek(0)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class TextDictWriter(object):
    """Same as TextWriter, but for DictWriter
    """

    def __init__(self, f, fieldnames, **kwds):
        self.queue = io.BytesIO()
        _fieldnames = [fn.encode('utf-8') for fn in fieldnames]
        self._fieldnames = _fieldnames
        self.writer = csv.DictWriter(self.queue,
                                     fieldnames=_fieldnames,
                                     **kwds)
        self.stream = f

    def writeheader(self):
        self.writer.writeheader()

    def writerow(self, row):
        e = {encode(k): encode(v) for k, v in row.items()}
        self.writer.writerow(e)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()

        data = data.decode('utf-8')
        # ... and reencode it into the target encoding
        self.stream.write(data)
        # empty queue
        self.queue.seek(0)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
