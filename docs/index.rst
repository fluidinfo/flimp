Welcome to flimp's documentation!
=================================

What is flimp?
--------------

The FLuiddb IMPorter (flimp) aims to make it simple to import data into
FluidDB.

Flimp makes use of the brilliant `FOM (Fluid Object Mapper) 
<http://bitbucket.org/aafshar/fom-main/wiki/Home>`_ by Ali Afshar.

It currently works in two ways:

1. Given a source file (currently flimp handles json, csv or yaml file types) it
   will create the necessary namespaces and tags and then import the records.

2. Given a path on the filesystem it will create the necessary namespaces
   (based on directories) and tags (based on file names) and then import the
   file's contents as values tagged to a single object.

Flimp provides the "flimp" command line tool and has been written to make
it easy to use flimp's functionality in third-party Python projects.

Command Line flimp
------------------

When importing data from a source file flimp assumes the following:

* The source file can be successfully translated into a list of Python dict
  objects to be converted into appropriately annotated FluidDB Objects. (How
  this is done for each file type is explained on each file type's page linked
  below.)
* The schema / structure of each record to be imported is the same (flimp uses
  the first record as a template in order to create the namespaces and tags)
* You have appropriate credentials for FluidDB and can provide meta-data about
  the data-set (name and description)

When importing data from the filesystem flimp will map things like this:

* Directory -> Namespace
* Filename -> Tag
* File content -> A value tagged to an object

Flimp will ignore hidden files and directories (those starting with `'.'`).

It is possible to specify the object to be tagged with filesystem based data.
In fact, it's possible to customise most of the aspects of importing data into
FluidDB. See the example of the help message below for more information.

Usage
+++++

::

    $ flimp -h
    Usage: flimp [options]

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -f FILE, --file=FILE  The FILE to process (valid filetypes: yaml, json, csv)
      -d DIRECTORY, --dir=DIRECTORY
                            The root directory for a filesystem import into
                            FluidDB
      -u UUID, --uuid=UUID  The uuid of the object to which the filesystem import
                            is to attach its tags
      -a ABOUT, --about=ABOUT
                            The about value of the object to which the filesystem
                            import is to attach its tags
      -p, --preview         Show a preview of what will happen, don't import
                            anything
      -i INSTANCE, --instance=INSTANCE
                            The URI for the instance of FluidDB to use
      -l LOG, --log=LOG     The log file to write to (defaults to flimp.log)
      -v, --verbose         Display status messages to console

    $ flimp -f data.json
    FluidDB username: test
    FluidDB password: 
    Name of dataset (defaults to filename) [data]: test_data 
    Key field for about tag value (if none given, will use anonymous objects): 
    Description of the dataset: This is a test
    Working... (this might take some time, why not: tail -f the log?)
    Done

    $ flimp -d test_directory 
    FluidDB username: test
    FluidDB password: 
    Name of dataset: testdata
    Description of the dataset: This is some test data
    Working... (this might take some time, why not: tail -f the log?)
    Tags added to object with uuid: 4d21335a-d584-4db6-bed8-ac19cb75ee32

As shown above, flimp asks for some basic information and then runs its course.

Use the ``-p`` flag to generate a preview rather than import the actual data.

When importing data from a file the *"Key field for about tag value"* question 
allows you to identify a field in each record that contains a unique value
within the dataset. These values will be used as the basis of the about tag
value. If no value is given then flimp creates so-called anonymous objects
without associated about tags. It is important to note that flimp *does not
check* that the field and associated values are unique. It assumes you know
what you're doing (you have been warned).

New namespaces and tags are created under the root namespace of the
user whose credentials you supplied. Flimp creates a namespace with the
same name as the dataset and generates all the other namespaces and tags 
underneath this.

Flimp keeps a log of what it's doing in the ``flimp.log`` file found in your
current working directory (you can override this).

For more information about how things are processed, along with examples, 
please see the pages linked below.

How flimp parses
----------------

.. toctree::
   :maxdepth: 3

   json
   csv
   yaml
   filesystem

Using flimp in your project
---------------------------

The flimp command line is only a thin wrapper on top of several Python modules
that you can re-use in your own software projects.

To import data from a source file you'll want to do something like this:

.. include:: ../examples/file_import.py
    :literal:

Alternatively to import data from the filesystem you'll want to do something
like this:

.. include:: ../examples/directory_import.py
    :literal:

The source code is extensively commented and well covered by unit tests.
Please feel free to report bugs, patches and request features.

Project Information
-------------------

To find out more about FluidDB visit `Fluidinfo's website 
<http://fluidinfo.com>`_.

Flimp is hosted on `GitHub <http://github.com/fluidinfo/flimp>`_.
Feedback, bug reports, patches and ideas are most welcome.

:license: The source code is available under the MIT open-source license.
:copyright: 2010 Fluidinfo Inc.
