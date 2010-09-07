FLuid IMPorter
==============

This package provides a set of modules and a script that makes it easy to
import data into FluidDB.

It currently works with json, csv or yaml file formats. It can also import
files from the local filesystem so directories -> namespaces, filenames ->
tags and file content -> values tagged to an object.

Help can be obtained like this::

    flimp -h

Take a look in the docs directory for extensive help.

Importing Data Files
--------------------

Flimp assumes the following:

- You are providing a list of items to import into FluidDB
- The "shape" of each item is the same (conforms to the same schema)

In the case of json and yaml it simply attempts to parse the raw file into a
list of python dict objects before the import takes place.

In the case of a csv file it will assume the first line is a list of headers
and that each record is the same length as the headers. This will result in a
list of python dict objects that will form the basis of the import.

Once the list of items has been abstracted into a list of Python dicts the
script will use the first item as a "template" and create the appropriate
namespaces and tags to correspond to the keys in the dictionary.

Once this step is complete the script simply iterates over the items,
creates an object for each and tags it with the corresponding tag-values.

Example usage::

    flimp -f file.json

Importing from the Filesystem
-----------------------------

Pass a directory as an argument into flimp and it will attempt to import 
everything underneath the parent directory into FluidDB.

Directories become namesapces, files become tags and the content of the files
becomes a value tagged onto an object.

It is possible to specify the object to use if you provide the uuid or about
tag value.

Flimp attempts to guess the correct mime-type to use when importing the file
content.

Flimp ignores hidden files and directories (starting with `'.'`).

Example usage::

    flimp -d path

Credentials
-----------

Flimp uses an interactive prompt for you to supply the requested details
(such as your username and password etc...)

Logging
-------

You'll find a log of your session in the file flimp.log. If you encounter any
problems you should look in here first.

Code
----

Flimp can be imported into your own projects. Check the documention for details
and examples.

The source code is hosted here:

http://github.com/fluidinfo/flimp

You can find out more about FluidDB here:

http://fluidinfo.com/

Feedback welcome!
