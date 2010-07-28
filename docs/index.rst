Welcome to flimp's documentation!
=================================

Contents
--------

.. toctree::
   :maxdepth: 2

   json
   csv
   yaml

What is flimp?
--------------

The FLuiddb IMPorter (flimp) is a utility to help make it simple to import
data into FluidDB.

Given a source file (currently flimp handles json, csv and yaml file types) it
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

As shown above, you are asked for some basic information and the utility runs
its course.

The ``Key field for about tag value`` question is important because this
allows you to identify a field in each record that contains a unique value
within the dataset that can be used as the basis of the about tag value. If no
value is given then flimp will create so-called anonymous objects without an
associated about tag value. It is important to note that flimp *does not
check* that the field and associated values are unique. It assumes you know
what you're doing (you have been warned).

The new namespaces and tags will be created under the root namespace of the
user whose credentials you supplied. Flimp will create a namespace with the
same name as the dataset ("my_dataset" in the example usage above) and
generate all the other namespaces and tags underneath this.

You can find a log of what it's doing in the ``flimp.log`` file found in the
current directory.

For more information about how each of the file types are processed, along
with examples, please see the file type's page within this documentation.

Project Information
-------------------

To find out more about FluidDB please visit `Fluidinfo's website 
<http://fluidinfo.com>`_.

This utility is hosted on `GitHub <http://github.com/fluidinfo/flimp>`_.
Feedback, bug reports, patches and ideas are most welcome.

The source code is available under the MIT open-source license.
