csvx: painless csv
==================

A Python csv library that supports 2 and 3, does the unicode thing properly, and lets you read rows as ordered dictionaries so that the ordering stays correct by default.

Which makes things pretty easy.

Example. You've got a csv you want to sanitize by removing a column of passwords.

Here's how that looks.

.. code-block:: python

    import csvx

    with csvx.OrderedDictReader('unsanitized.csv') as csv_in:
        rows = list(csv_in)

    for r in rows:
        del r['password']

    with csvx.DictWriter('sanitized.csv') as csv_out:
        csv_out.write_dicts(rows)

Simply install with `pip <https://pip.pypa.io>`_::

    $ pip install csvx

Unicode, encoding, blah blah...
-------------------------------

**tl;dr:** Just open files in text mode and everything will be fine.

Unlike `unicodecsv <https://pypi.python.org/pypi/unicodecsv>`_, which reads and writes to/from files in binary mode, csvx deals with files in *text mode*.

csvx reader and writer objects accept a file name (that file will be opened in text mode), but also file streams that you've already created. As long as those file streams are in text mode, everything should Just Work.

Tip: Always open files with the ``io`` module (which uses text mode by default in both Python 2 and 3) as opposed to the ``open(...`` builtin (whose behaviour differs between versions).


Contents:

.. toctree::
   :maxdepth: 2

   api.rst
