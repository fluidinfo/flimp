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
from fom.errors import Fluid412Error
from fom.mapping import Namespace, Tag, Object, tag_value
from flimp import NAMESPACE_DESC, TAG_DESC

logger = logging.getLogger("flimp")

def process(root_dir, username, name, desc, uuid=None, about=None,
            preview=None):
    """
    Given a root directory will import the contents of the filesystem therein
    into FluidDB. Directories -> Namespaces, Files -> Tags, File-contents ->
    Tag Values on a single object.

    Returns the object id of the object that was tagged
    """
    logger.info('Directory: %s' % root_dir)
    abs_path = os.path.abspath(root_dir)
    logger.info('Absolute path: %s' % abs_path)
    if uuid:
        object_info = 'Tagging object with uuid: %s' % uuid
    elif about:
        object_info = 'Tagging object about: %s' % about
    else:
        object_info = 'Tagging a new anonymous object (no about or uuid given)'
    logger.info(object_info)

    if preview:
        logger.info('Generating preview...')
        output = list()
        output.append("Preview of processing %s\n" % root_dir)
        output.append(object_info + '\n')
        output.append("The following namespaces/tags will be generated.\n")
        output.extend(get_preview(abs_path, username, name))
        result = "\n".join(output)
        logger.info(result)
        print result
    else:
        return push_to_fluiddb(abs_path, username, name, desc, uuid, about)

def get_preview(directory, username, name):
    """
    Returns a list of the namespace/tag combinations that will be created
    """
    # Use split() to get *just* the name of the directory *NOT* including the
    # path that _might_ be in front of it
    head, tail = os.path.split(directory)
    head += '/'
    tag_paths = list()
    for path, children, files in os.walk(directory):
        # Not very pretty but it works...
        if not path.startswith('.'): # ignore hidden directories
            for f in files:
                if not f.startswith('.'): # ignore hidden files
                    tag_path = '/'.join([username, name,
                                         path.replace(head, ''), f])
                    content_type, encoding = guess_type(os.path.join(path,f))
                    if not content_type:
                        content_type = 'UNKNOWN'
                    tag_paths.append('%s CONTENT-TYPE: %s' % (tag_path,
                                                                  content_type))
    return tag_paths

def push_to_fluiddb(directory, username, name, desc, uuid=None, about=None):
    """
    Pushes the contents of the specified directory as tag-values on a
    specified object (if no uuid is given then it'll create a new object).

    Returns the object to which the tag-values have been added.
    """
    # get the object we'll be using
    obj = get_object(uuid, about)

    # make sure we have the appropriate "name" based namespace underneath the
    # user's root namespace
    name_ns = make_namespace("%s/%s" % (username, name), name, desc)

    # iterate over the filesystem creating the namespaces and tags (where
    # appropriate) and adding the tag value to the object
    head, tail = os.path.split(directory)
    head += '/'
    for path, children, files in os.walk(directory):
        # still not pretty
        if not path.startswith('.'): # ignore hidden directories
            # create/check the namespace from the directory
            ns_path = '/'.join([username, name, path.replace(head, '')])
            new_ns = make_namespace(ns_path, name, desc)
            for f in files:
                if not f.startswith('.'): # ignore hidden files
                    # create/check the tag from the filename
                    tag_path = os.path.join(new_ns.path, f)
                    try:
                        logger.info('Checking tag %s' % tag_path)
                        new_tag = new_ns.create_tag(f,
                                                    TAG_DESC % (f, name, desc),
                                                    False)
                        logger.info('Done')
                    except Fluid412Error:
                        # 412 simply means the tag already exists
                        new_tag = Tag(tag_path)
                        logger.info('(%s already existed)' % new_tag.path)
                    file_path = os.path.join(path, f)
                    logger.info('Preparing file %s for upload' % file_path)
                    content_type, encoding = guess_type(file_path)
                    logger.info('Content-Type of %s detected' % content_type)
                    # now attach it to the object
                    raw_file = open(file_path, 'r')
                    logger.info('Pushing file %s to object %s on tag %s' %
                                 (file_path, obj.uid, new_tag.path))
                    obj.set(new_tag.path, raw_file.read(), content_type)
                    logger.info('DONE!')
                    raw_file.close()
    logger.info('Finished tagging the object with the uuid %s' % obj.uid)
    return obj

def make_namespace(path, name, desc):
    """
    Given a path, name and description will attempt to create and return a new
    namespace
    """
    try:
        logger.info('Checking namespace %s' % path)
        ns_head, ns_tail = os.path.split(path)
        result = Namespace(path)
        result.create(NAMESPACE_DESC % (ns_tail, name, desc))
        logger.info('Done')
    except Fluid412Error:
        # 412 simply means the namespace already exists
        result = Namespace(path)
        logger.info('(%s already existed)' % result.path)
    return result

def get_object(uuid=None, about=None):
    """
    Will return the referenced object or a new object if uuid or about are not
    given.
    """
    logger.info("Getting object")
    if uuid:
        logger.info("Object with uuid %s" % uuid)
        return Object(uid=uuid)
    elif about:
        logger.info("Object with about tag value: %s" % about)
        return Object(about=about)
    else:
        o = Object()
        o.create()
        logger.info("New object with uuid %s" % o.uid)
        return o
