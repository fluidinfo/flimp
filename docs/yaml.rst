Processing YAML files with flimp
================================

How it works
------------

In the case of yaml, flimp is expecting a list of dictionary objects to parse
into objects in FluidDB.

Examples
--------

Good
++++

Consider the following yaml snippet::

  - cuisine: [chinese, indian, thai]
    description: The Royal Oak
    food: true
    id: 1
    location: {lat: 52.160454999999999, long: -0.87890599999999997}
    real ale: true
  - cuisine: null
    description: The King's Head
    food: false
    id: 2
    location: {lat: 52.669719999999998, long: -2.6367189999999998}
    real ale: false
  - cuisine: null
    description: The Bee Hive
    food: false
    id: 3
    location: {lat: 53.169826, long: -0.96679700000000002}
    real ale: true


If I gave this dataset the name "pubs" and indicated that the "id" field was
unique and to be used as the basis of the about tag value and that my username
was "ntoll" then we'd end up with the following namespaces/tags::

  ntoll/pubs/food
  ntoll/pubs/location/long
  ntoll/pubs/location/lat
  ntoll/pubs/real_ale
  ntoll/pubs/id
  ntoll/pubs/description
  ntoll/pubs/cuisine

Notice how the nested dictionary is translated into a new namespace. In
addition, if flimp encounters a nested list that contains values other than
strings then it will simply store the nested list as an application/json type
value within FluidDB (note *not* as application/yaml).

The about tag values would be the name of the dataset followed by a colon then
the unique value. So the about tag value for the first item in the example
above would be::

  pubs:1

Bad
+++

The following examples show what won't work and why.

You must supply the records in a list structure (even if there is only one
record). The following won't work::

  foo: bar
  baz: true

The records *must* have the same schema (the second record is missing the
``baz`` field)::

  - foo: bar
    baz: true
  - foo: qux
