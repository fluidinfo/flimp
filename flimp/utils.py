# -*- coding: utf-8 -*-
"""
Utility functions used by flimp.

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
from fom.mapping import Namespace, Tag, Object, tag_value
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
        logger.info('Checking namespace %r' % path)
        ns_head, ns_tail = os.path.split(path)
        result = Namespace(path)
        result.create(NAMESPACE_DESC % (ns_tail, name, desc))
        logger.info('Done')
    except Fluid412Error:
        # 412 simply means the namespace already exists
        result = Namespace(path)
        logger.info('%r already existed' % result.path)
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
        logger.info('Creating new tag "%r" under %r' % (name, parent_ns.path))
        tag = parent_ns.create_tag(name, TAG_DESC % (name, dataset, desc), False)
        logger.info('Tag %r created' % tag.path)
    except Fluid412Error:
        # 412 simply means the tag already exists
        tag = Tag(parent_ns.path + '/' + name)
        logger.info('%r already existed' % tag.path)
    return tag

def make_namespace_path(path, name, desc):
    """
    Given an absolute namespace path (e.g. "foo/bar/baz") will check all the
    namespaces exist or else create them. Will return the final namespace
    (referring to "baz" in the example given just now).

    path - the path to be checked/created

    name - the name of the dataset that is causing the namespaces to be
    created (used when setting the description of the new namespace)

    desc - the description of the dataset that's causing the namespace to
    be created (used when setting the description of the new tag)
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

def process_data_list(raw_data, root_path, name, desc, about, allowEmpty=True):
    """
    Given a raw-data list of dictionaries that represent objects to be tagged
    in FluidDB this function will create the required tags and namespaces,
    create the FOM class and then use it to push the data to FluidDB
    """
    # Use the first item in the list of items
    logger.info('Creating namespace/tag schema in FluidDB')
    tag_dict = create_schema(raw_data, root_path, name, desc)
    logger.info('Created %d new tag[s]' % len(tag_dict))
    logger.info(tag_dict.keys())

    # Create a FOM class that inherits from Object to use to interact with
    # FluidDB
    logger.info('Creating new FOM Object class')
    fom_class = create_class(tag_dict)
    logger.info(dir(fom_class))

    # Given the newly existing class push all the data to FluidDB
    logger.info('Starting to push records to FluidDB')
    push_to_fluiddb(raw_data, root_path, fom_class, about, name, allowEmpty)

def validate(raw_data):
    """
    Given the raw data as a list of dictionaries this function will check
    each record to make sure it is valid. "Valid" in this case means that the
    shape of each dictionary is the same - they have the same keys.

    Returns lists indicating location of missing and extra fields.
    """
    # We use the first record as the template
    default = raw_data[0]
    # To store the results of the validation
    missing_log = []
    extras_log = []
    for record in raw_data[1:]:
        validate_dict(default, record, record, missing_log, extras_log)
    # return the correct response
    return missing_log, extras_log

def validate_dict(template, to_be_checked, parent, missing_log, extras_log):
    """
    Given a dictionary as a template will check that the to_be_checked
    dictionary.
    """
    for k in to_be_checked:
        k = k.strip()
        if not k in template:
            extras_log.append("Field %r in record %r" % (k, parent))
    for k in template:
        k = k.strip()
        if not k in to_be_checked:
            missing_log.append("Field %r in record %r" % (k, parent))
    for key, val in template.iteritems():
        if isinstance(val, dict):
            # check the inner dictionary
            validate_dict(val, to_be_checked[key], parent, missing_log, extras_log)

def create_schema(raw_data, root_path, name, desc):
    """
    Given the raw data, root_path, dataset name and description will use the
    first record in raw_data as a template for generating namespaces and tags
    underneath the user's root namespace.

    e.g. username/name/...

    Returns an appropriate dict object to use as the basis of generating the
    attributes on a new FOM Object class.
    """
    template = raw_data[0]
    root_ns = make_namespace_path(root_path, name, desc)
    tags = {}
    generate(root_ns, None, template, desc, name, tags)
    return tags

def generate(parent, child_name, template, description, name, tags):
    """
    A recursive function that traverses the "tree" in a dict to create new
    namespaces and/or tags as required.

    Populates the "tags" dict with tag_value instances so it's possible to
    generate FOM Object based classes based on the newly created tags.
    """
    # Create the child namespace
    if child_name:
        ns = make_namespace('/'.join([parent.path, child_name]), name, description)
    else:
        ns = parent

    for key, value in template.iteritems():
        # drop all the white space
        key = key.strip()
        # lets see what's in here
        if isinstance(value, dict):
            # ok... we have another dict, so we're doing depth first traversal
            # and jump right in
            generate(ns, key, value, description, name, tags)
        else:
            # it must be a tag so create the tag within the current namespace
            tag = make_tag(ns, key, description, False)
            # Create the tag_value instance...
            # Lets make sure we specify the right sort of mime
            defaultType = None
            if isinstance(value, list) and not all(isinstance(x, basestring) for
                                                 x in value):
                defaultType = 'application/json'
                logger.info("Found list that's not all strings, setting JSON tag value "
                            "with MIME type %r" % defaultType)
            attribute_name = tag.path
            logger.info('Mapping tag: %r to attribute: %r' % (tag.path, attribute_name))
            tags[attribute_name] = tag_value(tag.path, defaultType)

def create_class(tags):
    """
    Simply creates a new class that inherits from FOM's Object class with the
    attributes based upon the tag_value instances passed in.
    """
    return type('fom_class', (Object, ), tags)

def push_to_fluiddb(raw_data, root_path, klass, about, name, allowEmpty=True):
    """
    Given the raw data and a class derived from FOM's Object class will import
    the data into FluidDB. Each item in the list mapping to a new object in
    FluidDB. The 'about' and 'name' arguments are used to automate the
    generation of the about tag and associated value.
    """
    length = len(raw_data)
    for counter, item in enumerate(raw_data):
        logger.info("Processing record %d of %d" % (counter + 1, length))
        # create the object
        if about:
            about_value = "%s:%s" % (name, item[about])
            logger.info('Creating new object with about tag value: %r' %
                     about_value)
            obj = klass(about=about_value)
        else:
            logger.info('Creating a new anonymous object')
            obj = klass()
            obj.create()
        logger.info('Object %r successfully created' % obj.uid)
        # annotate it
        tag_values = get_values(item, root_path)
        for key, value in tag_values.iteritems():
            set_tag_value(klass, obj, key, value, allowEmpty)
        if about:
            logger.info('Finished annotating Object about %r with id: %r' %
                         (about_value, obj.uid))
        else:
            logger.info('Finished annotating anonymous Object with id: %r' %
                         obj.uid)

def set_tag_value(klass, obj, key, value, allowEmpty):
    if key in klass.__dict__:
        # check if we're allowed to set empty values
        if allowEmpty or not value is None:
            setattr(obj, key, value)
            logger.info('Set: %r to: %r' % (key, value))
        else:
            logger.info('%r ignored because it was empty' % key)
    else:
        # ToDo: Do we want to handle unknown tag values..?
        logger.error('Unable to set %r (unknown attribute)' % key)

def get_values(item, parent):
    """
    Given a dictionary that represents data to import into FluidDB this method
    (recursively) builds a dict where the key is the attribute name on the
    Object class and the value is the value to import into FluidDB.
    """
    vals = {}
    for key, value in item.iteritems():
        if isinstance(value, dict):
            vals.update(get_values(value, os.path.join(parent, key)))
        else:
            vals[os.path.join(parent, key)] = value
    return vals
