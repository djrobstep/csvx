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
        if not six.PY2:
            return io.open(f, 'r', newline='')  # pragma: no cover
        else:
            return io.open(f, 'rb')  # pragma: no cover
    except TypeError:
        return f


def smart_openw(f):
    "Hi"
    try:
        if not six.PY2:
            return io.open(f, 'w', newline='')  # pragma: no cover
        else:
            return io.open(f, 'wb')  # pragma: no cover
    except TypeError:
        return f


def dictreader_from_fp(fp, dialect, **kwargs):
    return csv.DictReader(fp, dialect=dialect, **kwargs)


def reader_from_fp(fp, dialect, **kwargs):
    return csv.reader(fp, dialect=dialect, **kwargs)


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
        # self.encoding = encoding
        self.kw = kw

    def __enter__(self):
        self.f = smart_open(self.f)
        self.reader = reader_from_fp(self.f, self.dialect, **self.kw)
        return self

    def __exit__(self, type, value, traceback):
        self.f.close()

    def next(self):
        row = next(self.reader)
        return tuple([to_text(s) for s in row])

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
        # self.encoding = encoding
        self.kw = kw

    def __enter__(self):
        self.f = smart_open(self.f)

        self.reader = self.reader = dictreader_from_fp(self.f, self.dialect,
                                                       **self.kw)
        self._fieldnames = self.reader.fieldnames
        return self

    @property
    def fieldnames(self):
        """The field names as specified in the first row of the csv file.
        """
        return tuple(to_text(fn) for fn in self._fieldnames)

    def __exit__(self, type, value, traceback):
        self.f.close()

    def next(self):
        d = next(self.reader)
        return OrderedDict((to_text(k), to_text(d[k]))
                           for k in self._fieldnames)

    __next__ = next

    def __iter__(self):
        return self


class Writer(object):
    """A context manager that lets you write rows to a csv file by specifying
    each row as a tuple (or, in fact, any iterable of the correct length
    containing string contents).

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

    def __enter__(self):
        self.f = smart_openw(self.f)
        self.writer = csv.writer(self.f, dialect=self.dialect, **self.kw)
        return self

    def __exit__(self, type, value, traceback):
        self.f.flush()
        self.f.close()

    def write_row(self, row):
        """Write a row to the csv file. Row should be a tuple (or any
        iterable) containing the values as strings. Eg: ('a', 'b', '10')
        """
        r = [to_str(s) for s in row]
        self.writer.writerow(r)
        self.row_count += 1

    def write_rows(self, rows):
        """Write multiple rows at once. For only the most advanced of users!
        """
        for row in rows:
            self.write_row(row)


class DictWriter(object):
    """A context manager that lets you write rows to a csv file by
    specifying each row as a dictionary of values.

    Same args as for writer, with the addition of:

    Args:
        fieldnames: You can specify fieldnames explicitly here if you want. If
            you skip this, the writer will use the keys of the first dictionary
            you write as the field names. That's why it's a good idea to use
            OrderedDict-style ordered dictionaries to write to this, as then
            you can skip the tiresome step of specifying the fieldnames
            explicitly here.
    """
    def __init__(self, f, dialect=csv.excel, fieldnames=None, **kw):

        self.f = f
        self.dialect = dialect
        self.kw = kw
        self._initialized = False
        self.row_count = 0

        if fieldnames:
            self.initialize(fieldnames)

    def __enter__(self):
        self.f = smart_openw(self.f)
        return self

    @property
    def fieldnames(self):
        """Returns the fieldnames used in this csv file.
        """
        return tuple(to_str(fn) for fn in self._fieldnames)

    def initialize(self, fieldnames):
        self._fieldnames = fieldnames

        self.writer = csv.DictWriter(self.f,
                                     self.fieldnames,
                                     dialect=self.dialect,
                                     **self.kw)
        self.writer.writeheader()
        self._initialized = True

    def __exit__(self, type, value, traceback):
        self.f.flush()
        self.f.close()

    def write_dict(self, d):
        """Write a row to the csv file. Should be specified as a
        dictionary/mapping, eg: {'name': 'Fred', 'age': 23 }.

        If you didn't specify fieldnames in the constructor, the keys() of the
        first dict you write will be used as the field names.

        So make sure to either specify the field names explicitly, or use
        OrderedDict dictionaries with this method to guarantee predictable
        ordering.
        """
        if not self._initialized:
            self.initialize(d.keys())

        d = {to_str(k): to_str(v) for k, v in d.items()}
        self.writer.writerow(d)
        self.row_count += 1

    def write_dicts(self, rows):
        """Write multiple rows at once. For only the most sophisticated
        power users!
        """
        for row in rows:
            self.write_dict(row)
