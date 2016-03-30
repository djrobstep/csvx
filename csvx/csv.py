from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import csv
from collections import OrderedDict
import io

import six

if not six.PY2:
    unicode = str  # pragma: no cover


def to_text(x):  # pragma: no cover
    if isinstance(x, six.text_type):
        return x

    elif isinstance(x, six.binary_type):
        return x.decode('utf-8')

    else:
        return unicode(x)


def to_bytes(x):  # pragma: no cover
    if isinstance(x, six.text_type):
        return x.encode('utf-8')

    elif isinstance(x, six.binary_type):
        return x

    else:
        return unicode(x).encode('utf-8')


if not six.PY2:
    to_str = to_text  # pragma: no cover
    from_str = to_bytes  # pragma: no cover
else:
    to_str = to_bytes  # pragma: no cover
    from_str = to_text  # pragma: no cover


def smart_open(f):
    try:
        return io.open(f)
    except TypeError:
        return f


def smart_openw(f):
    try:
        return io.open(f, 'w')
    except TypeError:
        return f


if six.PY2:
    from .python2 import TextReader, TextDictReader, \
                        TextWriter, TextDictWriter
    writer = TextWriter
    reader = TextReader
    dictreader = TextDictReader
    dictwriter = TextDictWriter
else:
    writer = csv.writer
    reader = csv.reader
    dictreader = csv.DictReader
    dictwriter = csv.DictWriter


class Reader(object):
    """A context manager that helps you read a csv file by iterating over the
    rows as tuples.

    Args:
        f (filename or file-like object): The path of the file, or an already
            opened file. The file should be opened in text mode (using
            io.open(... is always a good idea).
        dialect: Dialect of the csv file. Defaults to csv.excel from the stdlib
            which should be usually what you want.
        kw (kwargs): Additional arguments, passed through to the constructor of
            the stdlib reader object used under the hood.
    """

    def __init__(self, f, dialect=csv.excel, **kw):
        self.f = f
        self.dialect = dialect
        self.kw = kw
        self.f = smart_open(self.f)
        self.reader = reader(self.f, self.dialect, **self.kw)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.f.close()

    def next(self):
        return tuple(next(self.reader))

    __next__ = next

    def __iter__(self):
        return self


class OrderedDictReader(object):
    """A context manager that helps you read a csv file by iterating over the
    rows as (ordered) dictionaries (ie OrderedDicts).

    Arguments are the same as for Reader.
    """

    def __init__(self, f, dialect=csv.excel, **kw):
        self.f = f
        self.dialect = dialect
        self.kw = kw

        self.f = smart_open(self.f)

        b = dictreader(self.f, dialect=self.dialect, **self.kw)
        self.reader = b
        self.fieldnames = tuple(self.reader.fieldnames)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.f.close()

    def next(self):
        d = next(self.reader)
        tups = [(k, d[k]) for k in self.fieldnames]
        return OrderedDict(tups)

    __next__ = next

    def __iter__(self):
        return self


class Writer(object):
    """A context manager that lets you write rows to a csv file by
    specifying each row as a tuple (or, in fact, any iterable of the
    correct length containing string contents).

    Args are the same as for the reader classes.

    If you're passing in an already open file, it should be in write mode
    (and text mode). If you're passing in a file name, this file will be
    *truncated* and then written to (as per normal 'w' mode behaviour).
    """

    def __init__(self, f, dialect=csv.excel, **kw):
        self.f = f
        self.dialect = dialect
        self.kw = kw
        self.row_count = 0

        self.f = smart_openw(self.f)

        self.writer = writer(self.f, dialect=self.dialect, **self.kw)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.f.flush()
        self.f.close()

    def write_row(self, row):
        """Write a row to the csv file. Row should be a tuple (or any
        iterable) containing the values, preferably as text. Non-text
        values will be converted to text with the `unicode` method
        (byte sequences are assumed to be utf-8). For instance:
        ('text', b'bytes', 10) will become ('text', 'bytes', '10').
        """
        r = [to_text(s) for s in row]
        self.writer.writerow(r)
        self.row_count += 1

    def write_rows(self, rows):
        """Write multiple rows at once. For only the most advanced
        of users!
        """
        for row in rows:
            self.write_row(row)


class DictWriter(object):
    """A context manager that lets you write rows to a csv file by
    specifying each row as a dictionary of values.

    Same args as for writer, with the addition of:

    Args:
        fieldnames: You can specify fieldnames explicitly here if
            you want. If you skip this, the writer will use the keys
            of the first dictionary you write as the field names. That's
            why it's a good idea to use OrderedDict-style ordered
            dictionaries to write to this, as then you can skip the
            tiresome step of specifying the fieldnames explicitly here.
    """

    def __init__(self, f, **kw):
        self.f = smart_openw(f)
        self.kw = kw
        self._initialized = False
        self.row_count = 0

        if 'fieldnames' in kw:
            self.initialize()

    def __enter__(self):
        return self

    def initialize(self):
        fieldnames = self.kw['fieldnames']
        self.fieldnames = tuple(to_text(fn) for fn in fieldnames)
        self.kw['fieldnames'] = self.fieldnames
        self.writer = dictwriter(self.f, **self.kw)
        self.writer.writeheader()
        self._initialized = True

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.f.flush()
        self.f.close()

    def write_dict(self, d):
        """Write a row to the csv file. Should be specified as a
        dictionary/mapping, eg: { 'name': 'Fred', 'age': 23 }.

        If you didn't specify fieldnames in the constructor, the keys()
        of the first dict you write will be used as the field names.

        So make sure to either specify the field names explicitly, or use
        OrderedDict dictionaries with this method to guarantee predictable
        ordering.
        """

        if not self._initialized:
            self.kw[to_str('fieldnames')] = d.keys()
            self.initialize()

        d = {to_text(k): to_text(v) for k, v in d.items()}
        self.writer.writerow(d)
        self.row_count += 1

    def write_dicts(self, rows):
        """Write multiple rows at once. For only the most sophisticated
        power users!
        """
        for row in rows:
            self.write_dict(row)


def ordereddicts_from_text(t):
    """Convenience method. Got some csv text? Get some dicts.
    """
    t = to_text(t)
    s = io.StringIO(t)

    with OrderedDictReader(s) as odr:
        for od in odr:
            yield od


def text_from_dicts(iterable_of_dicts):
    """Convenience method, the inverse of
    ordereddicts_from_text (sorta).
    """
    s = io.StringIO()

    with DictWriter(s) as w:
        w.write_dicts(iterable_of_dicts)
        return s.getvalue()


def sniff_text(text):
    """Sniff some csv text to determine format. Returns a Dialect object
    as per the stdlib csv module.
    """
    sniffer = csv.Sniffer()
    sniffed = sniffer.sniff(text)
    return sniffed
