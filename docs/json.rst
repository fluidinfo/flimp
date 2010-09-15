Processing JSON files with flimp
================================

How it works
------------

In the case of json, flimp expects a list of dictionary objects to turn
into objects in FluidDB.

Examples
--------

Good
++++

Consider the following json snippet::

  [
    {
      "cuisine": [
        "chinese", 
        "indian", 
        "thai"
      ], 
      "real ale": true, 
      "description": "The Royal Oak", 
      "food": true, 
      "location": {
        "lat": 52.160454999999999, 
        "long": -0.87890599999999997
      }, 
      "id": 1
    }, 
    {
      "cuisine": null,
      "food": false, 
      "location": {
        "lat": 52.669719999999998, 
        "long": -2.6367189999999998
      }, 
      "real ale": false, 
      "id": 2, 
      "description": "The King's Head"
    }, 
    {
      "cuisine": null,
      "food": false, 
      "location":
      {
        "lat": 53.169826, 
        "long": -0.96679700000000002
      }, 
      "real ale": true, 
      "id": 3, 
      "description": "The Bee Hive"
    }
  ]

If I provided the root namespace "ntoll/pubs", indicated that the "id" field was
unique and to be used as the basis of the about tag value, and that the name of
the dataset was "pubs" then we'd end up with the following namespaces/tags::

  ntoll/pubs/cuisine
  ntoll/pubs/food
  ntoll/pubs/location/long
  ntoll/pubs/location/lat
  ntoll/pubs/real_ale
  ntoll/pubs/id
  ntoll/pubs/description

Notice how the nested dictionary is translated into a new namespace.
If flimp encounters a nested list that contains values other than just
strings then it attempts to store the nested list as an application/json type
value within FluidDB.

About tag values are the name of the dataset followed by a colon then
the unique value. For instance the about tag value for the first item in the 
example above would be::

  pubs:1

Bad
+++

The following examples show what won't work and why.

You must supply the records in a list structure (even if there is only one
record). The following won't work::

  {
    "foo": "bar",
    "baz": true
  }

The records *must* have the same schema (the second record is missing the
``baz`` field)::

  [
      {
        "foo": "bar",
        "baz": true
      },
      {
        "foo": "qux"
      }
  ]

Supplying just an empty list is not a good idea::

  []
