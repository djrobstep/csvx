from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from csvx import Reader, OrderedDictReader, Writer, DictWriter, \
    to_text, to_str, ordereddicts_from_text, text_from_dicts, sniff_text

from collections import OrderedDict
import io
from six import StringIO as sio
import csv


def unicode_list(t):
    return list(to_text(x) for x in t)


COL_NAMES = ('id', b'account', b'active', 'start_time', 'end_time', 'amount',
             'credit_limit', 'deposited', 'des\u00e7ription')

FIRST_ROW = (490, 248, 'False', '2012-10-01 00:00:00.000000',
             '2013-01-02 00:00:00.000000', 72000000, 216000000, 72000000,
             'Fran\u00e7ois')

SECOND_ROW = (490, 248.0, b'False', b'-infinity', '', 72000000, 216000000,
              72000000, 'Fran\u00e7ois')

COL_NAMES_U = unicode_list(COL_NAMES)
FIRST_ROW_U = unicode_list(FIRST_ROW)
SECOND_ROW_U = unicode_list(SECOND_ROW)

ROWS_FOR_WRITING = [COL_NAMES, FIRST_ROW, SECOND_ROW]

ALL_ROW_ROWS = [COL_NAMES_U, FIRST_ROW_U, SECOND_ROW_U]
ROW_ROWS = [FIRST_ROW_U, SECOND_ROW_U]
ROW_ODS = [OrderedDict(zip(COL_NAMES_U, row)) for row in ROW_ROWS]


def test_csv(tmpdir):
    csvout = tmpdir / 'test.csv'
    path = str(csvout)

    with Writer(path) as w:
        w.write_rows(ROWS_FOR_WRITING)

    with Reader(path) as r:
        assert list(r) == ALL_ROW_ROWS

    with Reader(io.open(path)) as r:
        assert list(r) == ALL_ROW_ROWS

    with OrderedDictReader(path) as odr:
        assert odr.fieldnames == COL_NAMES_U
        assert list(odr) == ROW_ODS

    with DictWriter(path) as dw:
        dw.write_dicts(ROW_ODS)

    with DictWriter(io.open(path, 'w'), fieldnames=COL_NAMES) as dw:
        dw.write_dicts(ROW_ODS)

    with OrderedDictReader(io.open(path)) as odr:
        assert odr.fieldnames == COL_NAMES_U
        assert list(odr) == ROW_ODS

    # test non context usage
    w = OrderedDictReader(path)
    assert list(w) == ROW_ODS
    w.close()

    # test convenience methods
    t = text_from_dicts(ROW_ODS)
    assert list(ordereddicts_from_text(t)) == ROW_ODS

    sniffed = sniff_text(t)
    assert sniffed.delimiter == ','

    # test handling of incomplete rows

    t = 'a,b\n1\n1,\n,1\n\n1,2,3,4\n1,2,3\n'
    as_str = to_str(t)

    stdlib_rows = list(csv.reader(sio(as_str)))

    with Reader(sio(as_str)) as r:
        csvx_rows = list(r)

    assert stdlib_rows == csvx_rows

    stdlib_out = sio('')

    w = csv.writer(stdlib_out)
    w.writerows(stdlib_rows)
    stdlib_out = stdlib_out.getvalue()
    csvx_out = sio('')

    with Writer(csvx_out) as w:
        w.write_rows(csvx_rows)
        csvx_out = csvx_out.getvalue()

    assert stdlib_out == csvx_out

    # now with dicts...
    stdlib_dicts = list(csv.DictReader(sio(as_str)))

    with OrderedDictReader(sio(as_str)) as r:
        csvx_ordereddicts = list(r)
        csvx_dicts = [dict(d) for d in csvx_ordereddicts]

    assert stdlib_dicts == csvx_dicts

    stdlib_out = sio('')

    # remove None keys because DictWriter won't accept them
    def cleanse(dicts):
        for d in dicts:
            if None in d:
                del d[None]

    cleanse(stdlib_dicts)
    cleanse(csvx_ordereddicts)
    cleanse(csvx_dicts)

    w = csv.DictWriter(stdlib_out, fieldnames=stdlib_rows[0])
    w.writeheader()
    w.writerows(stdlib_dicts)
    stdlib_out = stdlib_out.getvalue()

    csvx_out = sio('')

    with DictWriter(csvx_out) as w:
        w.write_dicts(csvx_ordereddicts)
        csvx_out = csvx_out.getvalue()
    print(stdlib_out)
    assert stdlib_out == csvx_out
