Welcome to flimp's documentation!
=================================

What is flimp?
--------------

The FLuiddb IMPorter (flimp) is a utility to help make it simple to import
data into FluidDB.

Given a source file (currently flimp handles json, csv or yaml file types) it
will create the necessary namespaces and tags and then import the records.

It assumes the following:

* The source file can be successfully translated into a list of Python dict
  objects to be converted into appropriately annotated FluidDB Objects. (How
  this is done for each file type is explained on each file type's page linked
  below.)
* The schema / structure of each record to be imported is the same (flimp uses
  the first record as a template in order to create the namespaces and tags)
* You have appropriate credentials for FluidDB and can provide meta-data about
  the data-set (name and description)

Usage
-----
::

  $ flimp -f source_file.yaml -i https://sandbox.fluidinfo.com
  FluidDB username: test
  FluidDB password: 
  Name of dataset (defaults to filename) [source_file]: my_dataset
  Description of the dataset: foobarbaz
  Key field for about tag value (if none given, will use anonymous objects): id
  Working... (this might take some time, why not: tail -f flimp.log)

The ``-i`` (instance) argument is optional and will default to
``https://fluiddb.fluidinfo.com``. Obviously, the ``-f`` option is used to
indicate the source file.

As shown above, flimp asks for some basic information and then runs
its course.

The *"Key field for about tag value"* question allows you to identify a field
in each record that contains a unique value within the dataset. These values
will be used as the basis of the about tag value. If no
value is given then flimp creates so-called anonymous objects without 
associated about tags. It is important to note that flimp *does not
check* that the field and associated values are unique. It assumes you know
what you're doing (you have been warned).

New namespaces and tags are created under the root namespace of the
user whose credentials you supplied. Flimp creates a namespace with the
same name as the dataset ("my_dataset" in the example above) and
generates all the other namespaces and tags underneath this.

Flimp keeps a log of what it's doing in the ``flimp.log`` file found in your
current working directory.

For more information about how each of the file types are processed, along
with examples, please see the pages linked below.

How flimp parses
----------------

.. toctree::
   :maxdepth: 3

   json
   csv
   yaml

Project Information
-------------------

To find out more about FluidDB visit `Fluidinfo's website 
<http://fluidinfo.com>`_.

This utility is hosted on `GitHub <http://github.com/fluidinfo/flimp>`_.
Feedback, bug reports, patches and ideas are most welcome.

The source code is available under the MIT open-source license.
