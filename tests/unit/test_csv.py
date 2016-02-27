from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from csvx import Reader, OrderedDictReader, Writer, DictWriter, to_text

COL_NAMES = ('id', b'account', b'active', 'start_time', 'end_time', 'amount',
             'credit_limit', 'deposited', 'des\u00e7ription')

FIRST_ROW = (490, 248, 'False', '2012-10-01 00:00:00.000000',
             '2013-01-02 00:00:00.000000', 72000000, 216000000, 72000000,
             'Fran\u00e7ois')

SECOND_ROW = (490, 248.0, b'False', b'-infinity', '', 72000000, 216000000,
              72000000, 'Fran\u00e7ois')


def test_csv(tmpdir):
    csvout = tmpdir / 'test.csv'

    with Writer(str(csvout)) as out:
        out.write_rows([COL_NAMES, FIRST_ROW, SECOND_ROW])

    with Reader(str(csvout)) as csvin:
        rows = list(csvin)
        assert rows[1] == tuple(to_text(x) for x in FIRST_ROW)
        assert len(rows) == 3

    with Reader(csvout.open()) as csvin:
        rows = list(csvin)
        assert rows[1] == tuple(to_text(x) for x in FIRST_ROW)
        assert len(rows) == 3

    with OrderedDictReader(str(csvout)) as csvin:
        rows = list(csvin)
        assert csvin.fieldnames == tuple(to_text(x) for x in COL_NAMES)
        assert len(rows) == 2

    with OrderedDictReader(csvout.open()) as csvin:
        rows = list(csvin)
        assert csvin.fieldnames == tuple(to_text(x) for x in COL_NAMES)

    with DictWriter(str(csvout)) as out:
        rows = [dict(zip(COL_NAMES, row)) for row in [FIRST_ROW, SECOND_ROW]]
        out.write_dicts(rows)

    with DictWriter(csvout.open('w'), fieldnames=COL_NAMES) as out:
        rows = [dict(zip(COL_NAMES, row)) for row in [FIRST_ROW, SECOND_ROW]]
        out.write_dicts(rows)

    with OrderedDictReader(str(csvout), fieldnames=COL_NAMES) as csvin:
        rows = list(csvin)
        assert csvin.fieldnames == tuple(to_text(x) for x in COL_NAMES)
