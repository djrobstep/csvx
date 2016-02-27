csvx: painless csv
==================

A csv library that supports 2 and 3, does the unicode thing properly, and lets you read rows as ordered dictionaries so that the ordering stays correct by default.

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


Documentation
-------------

Full documentation is at `https://csvx.readthedocs.org <https://csvx.readthedocs.org>`_.


Install
-------

Simply install with `pip <https://pip.pypa.io>`_::

    $ pip install csvx
