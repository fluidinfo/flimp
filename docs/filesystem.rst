Importing from the filesystem with flimp
========================================

How it works
------------

Flimp traverses the filesystem below the given directory and performs the
following operations:

* Directories become namespaces
* Filenames become tags
* The content of files are tagged to an object.

Flimp ignores hidden directories and files (beginning with '.'). A future
enhancement will be something akin to GIT's .gitignore file to specify
patterns for ignoring files and directories.

Flimp makes an educated guess at the mime-type to use when tagging values to
the object in FluidDB.

If no UUID or fluiddb/about tag value is specified then a new object is
created.

Examples
--------

Consider the following directory tree::

    test_directory/
    |
    +- readme.txt
    |
    +- foo/
    |  |
    |  +- foo_child.jpg
    |
    +- bar/
       |
       +- bar_child.pdf

Then if we provide the root namespace 'test/my_data' the following tags
will be created::

    test/my_data/test_directory/readme.txt
    test/my_data/test_directory/foo/foo_child.jpg
    test/my_data/test_directory/bar/bar_child.pdf

Furthermore, the Content-Type for each of the values tagged to the object in
FluidDB will be `text/plain`, `image/jpg` and `application/pdf` respectively.

If you were to GET the newly created tag-values they will be returned by
FluidDB with the correct mime-type.
