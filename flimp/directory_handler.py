# -*- coding: utf-8 -*-
"""
Given a root directory will import the directories and files therin into
FluidDB. Directories -> Namespaces, Files -> Tags, File-contents -> Tag values
on a single object.

Please feel free to adapt and change.

Copyright (c) 2010 Fluidinfo Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import os
import sys
import logging
from mimetypes import guess_type
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json
from fom.mapping import Object
from flimp.utils import make_namespace, make_tag, make_namespace_path

logger = logging.getLogger("flimp")

def process(root_dir, fluiddb_path, name, desc, uuid=None, about=None,
            preview=None):
    """
    Given a root directory will import the contents of the filesystem therein
    into FluidDB. Directories -> Namespaces, Files -> Tags, File-contents ->
    Tag Values on a single object.

    Returns the object id of the object that was tagged.

    root_dir - the path to the directory on the filesystem that will act as
    the root of the import

    fluiddb_path - the path to locate the namespace that maps to root_dir

    name - the name of the data that's being imported into FluidDB

    desc - a description of the data that's being imported into FluidDB

    uuid - the UUID to identify the object to be tagged

    about - the fluiddb/about tag value of the object to be tagged

    preview - If true, will print out a preview and not import the data
    """
    logger.info('Directory: %r' % root_dir)
    abs_path = os.path.abspath(root_dir)
    logger.info('Absolute path: %r' % abs_path)
    if uuid:
        object_info = 'Tagging object with uuid: %r' % uuid
    elif about:
        object_info = 'Tagging object about: %r' % about
    else:
        object_info = 'Tagging a new anonymous object (no about or uuid given)'
    logger.info(object_info)

    if preview:
        logger.info('Generating preview...')
        output = list()
        output.append("Preview of processing %r\n" % root_dir)
        output.append(object_info + '\n')
        output.append("The following namespaces/tags will be generated.\n")
        output.extend(get_preview(abs_path, fluiddb_path))
        result = "\n".join(output)
        logger.info(result)
        print result
    else:
        return push_to_fluiddb(abs_path, fluiddb_path, name, desc, uuid, about)

def get_preview(directory, fluiddb_path):
    """
    Returns a list of the namespace/tag combinations that will be created
    """
    # Use split() to get *just* the name of the directory *NOT* including the
    # path that _might_ be in front of it
    tag_paths = list()
    for path, children, files in os.walk(directory):
        # Not very pretty but it works... (ignores hidden directories)
        for child in children:
            if os.path.basename(child).startswith('.'):
                children.remove(child)
        for f in files:
            if not f.startswith('.'): # ignore hidden files
                relative_path = path.replace(directory, '')
                if relative_path:
                    # build the full path remembering to knock off the
                    # slash from the relative path
                    tag_path = '/'.join([fluiddb_path,
                                         relative_path[1:], f])
                else:
                    tag_path = '/'.join([fluiddb_path, f])
                content_type, encoding = guess_type(os.path.join(path,f))
                if not content_type:
                    content_type = 'UNKNOWN'
                tag_paths.append('%s CONTENT-TYPE: %s' % (tag_path,
                                                          content_type))
    return tag_paths

def push_to_fluiddb(directory, fluiddb_path, name, desc, uuid=None,
                    about=None):
    """
    Pushes the contents of the specified directory as tag-values on a
    specified object (if no uuid is given then it'll create a new object).

    Returns the object to which the tag-values have been added.

    root_dir - the path to the directory on the filesystem that will act as
    the root of the import

    fluiddb_path - the path to locate the namespace that maps to root_dir

    name - the name of the data that's being imported into FluidDB

    desc - a description of the data that's being imported into FluidDB

    uuid - the UUID to identify the object to be tagged

    about - the fluiddb/about tag value of the object to be tagged
    """
    # get the object we'll be using
    obj = get_object(uuid, about)

    # make sure we have the appropriate "fluidinfo_path" based namespaces
    # underneath the user's root namespace
    root_namespace = make_namespace_path(fluiddb_path, name, desc)

    # iterate over the filesystem creating the namespaces and tags (where
    # appropriate) and adding the tag value to the object
    for path, children, files in os.walk(directory):
        # still not pretty (ignoring hidden directories)
        for child in children:
            if os.path.basename(child).startswith('.'):
                children.remove(child)
        # create/check the namespace from the directory
        new_ns_name = path.replace(directory, '')
        if new_ns_name:
            # join the paths whilst remember to knock off the leading
            # slash from the new_ns_name
            ns_path = '/'.join([root_namespace.path, new_ns_name[1:]])
            new_ns = make_namespace(ns_path, name, desc)
        else:
            new_ns = root_namespace
        for f in files:
            if not f.startswith('.'): # ignore hidden files
                # create/check the tag from the filename
                # TODO: tag_path is not used.
                tag_path = os.path.join(new_ns.path, f)
                new_tag = make_tag(new_ns, f, name, desc, False)
                file_path = os.path.join(path, f)
                logger.info('Preparing file %r for upload' % file_path)
                content_type, encoding = guess_type(file_path)
                logger.info('Content-Type of %r detected' % content_type)
                # now attach it to the object
                raw_file = open(file_path, 'r')
                logger.info('Pushing file %r to object %r on tag %r' %
                            (file_path, obj.uid, new_tag.path))
                obj.set(new_tag.path, raw_file.read(), content_type)
                logger.info('DONE!')
                raw_file.close()
    logger.info('Finished tagging the object with the uuid %r' % obj.uid)
    return obj

def get_object(uuid=None, about=None):
    """
    Returns the referenced object or a new object if uuid or about are not
    given.
    """
    logger.info("Getting object")
    if uuid:
        logger.info("Object with uuid %r" % uuid)
        return Object(uid=uuid)
    elif about:
        logger.info("Object with about tag value: %r" % about)
        return Object(about=about)
    else:
        o = Object()
        o.create()
        logger.info("New object with uuid %r" % o.uid)
        return o
