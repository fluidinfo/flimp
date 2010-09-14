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
import logging
logger = logging.getLogger("flimp")
from fom.errors import Fluid412Error
from fom.mapping import Namespace, Tag
from flimp import NAMESPACE_DESC, TAG_DESC

def make_namespace(path, name, desc):
    """
    Given a path, name and description will attempt to create and return a new
    namespace.

    path - the path to the new namespace

    name - the name of the dataset that's causing this namespace to be created
    (used when setting the description of the new namespace)

    desc - the description of the dataset that's causing the namespace to be
    create (used when setting the description of the new namespace)
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

def make_tag(parent_ns, name, dataset, desc, indexed=False):
    """
    Given a parent namespace, name, description and optional indexed flag will
    create and return the resulting tag

    parent_ns - the parent namespace under which the tag will be created

    name - the name of the new tag

    dataset - the title of the dataset that is causing this tag to be created
    (used when setting the description of the new tag)

    desc - the description of the dataset that's causing the tag to be created
    (used when setting the description of the new tag)

    indexed - flag to indicate if the tag is to be indexed for full text
    search
    """
    try:
        # it must be a tag so create the tag within the current
        # namespace
        logger.info('Creating new tag "%s" under %s' % (name, parent_ns.path))
        tag = parent_ns.create_tag(name, TAG_DESC % (name, dataset, desc), False)
        logger.info('Tag %s created' % tag.path)
    except Fluid412Error:
        # 412 simply means the tag already exists
        tag = Tag(parent_ns.path + '/' + name)
        logger.info('%s already existed' % tag.path)
    return tag

def make_namespace_path(path, name, desc):
    """
    Given an absolute namespace path (e.g. "foo/bar/baz") will check all the
    namespaces exist or else create them. Will return the final namespace
    (referring to "baz" in the example given just now).

    path - the path to be checked/created

    name - the name of the dataset that is causing the namespaces to be
    created (used when setting the description of the new namespace)

    desc - the description of the dataset that's causing the namespace to be
    created (used when setting the description of the new tag)
    """
    namespace_path = path.split('/')
    # put the user's root namespace in the checked_namespaces since it will
    # (should) already exist and we can't create it anyway!
    checked_namespaces = namespace_path[0]
    for namespace in namespace_path[1:]:
        if checked_namespaces:
            ns_path = os.path.join(checked_namespaces, namespace)
        else:
            ns_path = namespace
        ns = make_namespace(ns_path, name, desc)
        checked_namespaces = ns.path
    return ns
