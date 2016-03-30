from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from csvx import Reader, OrderedDictReader, Writer, DictWriter, \
    to_text, ordereddicts_from_text, text_from_dicts, sniff_text

from collections import OrderedDict
import io


def unicode_tuple(t):
    return tuple(to_text(x) for x in t)


COL_NAMES = ('id', b'account', b'active', 'start_time', 'end_time', 'amount',
             'credit_limit', 'deposited', 'des\u00e7ription')

FIRST_ROW = (490, 248, 'False', '2012-10-01 00:00:00.000000',
             '2013-01-02 00:00:00.000000', 72000000, 216000000, 72000000,
             'Fran\u00e7ois')

SECOND_ROW = (490, 248.0, b'False', b'-infinity', '', 72000000, 216000000,
              72000000, 'Fran\u00e7ois')

COL_NAMES_U = unicode_tuple(COL_NAMES)
FIRST_ROW_U = unicode_tuple(FIRST_ROW)
SECOND_ROW_U = unicode_tuple(SECOND_ROW)

ROWS_FOR_WRITING = [COL_NAMES, FIRST_ROW, SECOND_ROW]

ALL_ROW_TUPLES = [COL_NAMES_U, FIRST_ROW_U, SECOND_ROW_U]
ROW_TUPLES = [FIRST_ROW_U, SECOND_ROW_U]
ROW_ODS = [OrderedDict(zip(COL_NAMES_U, row)) for row in ROW_TUPLES]


def test_csv(tmpdir):
    csvout = tmpdir / 'test.csv'
    path = str(csvout)

    with Writer(path) as w:
        w.write_rows(ROWS_FOR_WRITING)

    with Reader(path) as r:
        assert list(r) == ALL_ROW_TUPLES

    with Reader(io.open(path)) as r:
        assert list(r) == ALL_ROW_TUPLES

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
