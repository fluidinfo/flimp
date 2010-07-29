Processing CSV files with flimp
===============================

How it works
------------

Flimp expects that the first line will be a list of column
headers. It attempts to detect these headers and uses them as the basis for 
creating the tags used to annotate the objects within FluidDB. It also
attempts to make a good guess at the dialect used to format the CSV file.

Each of the remaining lines in the CSV file will be treated as the basis for
new objects in FluidDB.

Examples
--------

Good
++++

Consider the following CSV file::

  'header 1', 'header 2', 'header 3'
  'foo', 'bar', 'baz'
  'qux', 'quux', 'corge',
  1, 2, 3

Internally, flimp translates it into::

  [
    {
      'header 1': 'foo',
      'header 2': 'bar',
      'header 3': 'baz'
    },
    {
      'header 1': 'qux',
      'header 2': 'quux',
      'header 3': 'corge'
    },
    {
      'header 1': 1,
      'header 2': 2,
      'header 3': 3
    }
  ]

The records are turned into dictionary that
will be used to generate the objects and associated tags (whitespace is
translated to underscores so the tag names will, in fact, be something like
``header_1``).

Bad
+++

Here are some examples of what won't work.

The following won't work because there are *no headers*::

  1, 2, 3
  4, 5, 6
  7, 8, 9

Obviously, just supplying headers is not enough::

  'header 1', 'header 2', 'header 3'

This example fails because one of the records doesn't have the right number of
fields (too few)::

  'header 1', 'header 2', 'header 3'
  'foo', 'bar', 'baz'
  'qux', 'corge'
  'ham', 'and', 'eggs'

If you need to supply an empty value please make sure you specify it using the
correct delimeter and/or quote character.
