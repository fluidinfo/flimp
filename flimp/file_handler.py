# -*- coding: utf-8 -*-
"""
Takes a file, and imports the data into FluidDB

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
import sys
import logging
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json
from fom.errors import Fluid412Error
from fom.mapping import Namespace, Tag, Object, tag_value
from flimp.parser import parse_json, parse_yaml, parse_csv
from flimp import NAMESPACE_DESC, TAG_DESC

VALID_FILETYPES = {
    'json': parse_json,
    'csv': parse_csv,
    'yaml': parse_yaml
}

logger = logging.getLogger("flimp")

def process(filename, username, name, desc, about, preview):
    """
    The recipe for grabbing the file and pushing it to FluidDB
    """
    # Turn the raw input file into a list data structure containing the items
    # to import into FluidDB
    raw_data = clean_data(filename)
    logger.info('Raw filename: %s' % filename)
    logger.info('About tag field key: %s' % about)
    logger.info('%d records found' % len(raw_data))

    if preview:
        # just print out/log a preview
        logger.info('Generating preview...')
        output = list()
        output.append("Preview of processing %s\n" % filename)
        output.append("The following namespaces/tags will be generated.\n")
        output.extend(get_preview(raw_data, username, name))
        result = "\n".join(output)
        logger.info(result)
        print result
    else:
        # Use the first item in the list of items 
        logger.info('Creating namespace/tag schema in FluidDB')
        tag_dict = create_schema(raw_data, username, name, desc)
        logger.info('Created %d new tag[s]' % len(tag_dict))
        logger.info(tag_dict.keys())

        # Create a FOM class that inherits from Object to use to interract with
        # FluidDB
        logger.info('Creating new FOM Object class')
        fom_class = create_class(tag_dict)
        logger.info(dir(fom_class))

        # Given the newly existing class push all the data to FluidDB
        logger.info('Starting to push records to FluidDB')
        push_to_fluiddb(raw_data, fom_class, about, name, username)

def get_preview(raw_data, username, name):
    """
    Returns a list of the namespace/tag combinations that will be created
    """
    template = raw_data[0]
    result = list()
    traverse_preview(template, '/'.join([username, name]), result)
    return result

def traverse_preview(template, parent, tags):
    """
    Does exactly what it says - traverses the preview dict and adds fully
    qualified tag paths to the result list
    """
    logger.info('Found namespace: %s' % parent)
    for key, value in template.iteritems():
        # lets see what's in here
        if isinstance(value, dict):
            # ok... we have another dict, so we're doing depth first traversal
            # and jump right in
            traverse_preview(value, '/'.join([parent, key]), tags)
        else:
            # Yay! it's a tag!
            logger.info('Found tag: %s' % key)
            tags.append('/'.join([parent, key]))

def clean_data(filename):
    """
    Given a filename will open it and pass it to the appropriate parser to
    turn it into a dictionary object for further processing
    """
    extension = filename.split('.')[-1:][0]
    if not extension in VALID_FILETYPES.keys():
        raise TypeError('Unknown file type to parse')

    f = open(filename, 'r')

    logger.info('Parsing %s' % extension)
    result = VALID_FILETYPES[extension].parse(f)
    f.close()
    return result

def create_schema(raw_data, username, name, desc):
    """
    Given the raw data, username, dataset name and description will use the
    first record in raw_data as a template for generating namespaces and tags
    underneath the user's root namespace.

    e.g. username/name/...

    Returns an appropriate dict object to use as the basis of generating the
    attributes on a new FOM Object class.
    """
    template = raw_data[0]
    root_ns = Namespace(username)
    tags = {}
    generate(root_ns, name, template, desc, name, tags)
    return tags

def generate(parent, child_name, template, description, name, tags):
    """
    A recursive function that traverses the "tree" in a dict to create new
    namespaces and/or tags as required.

    Populates the "tags" dict with tag_value instances so it's possible to
    generate FOM Object based classes based on the newly created tags.
    """
    try:
        # Create the child namespace
        logger.info('Creating new namespace "%s" under %s' % (child_name,
                                                               parent.path))
        ns = parent.create_namespace(child_name,
                                 NAMESPACE_DESC % (child_name, name, description))
        logger.info('Done.')
    except Fluid412Error:
        # 412 simply means the namespace already exists
        ns = Namespace(parent.path + '/' + child_name)
        logger.info('(%s already existed)' % ns.path)

    for key, value in template.iteritems():
        # lets see what's in here
        if isinstance(value, dict):
            # ok... we have another dict, so we're doing depth first traversal
            # and jump right in
            generate(ns, key, value, description, name, tags)
        else:
            try:
                # it must be a tag so create the tag within the current
                # namespace
                logger.info('Creating new tag "%s" under %s' % (key,
                                                                 ns.path))
                tag = ns.create_tag(key, TAG_DESC % (key, name, description),
                                    False)
            except Fluid412Error:
                # 412 simply means the namespace already exists
                tag = Tag(parent.path + '/' + child_name + '/' + key)
                logger.info('(%s already existed)' % tag.path)
            # Create the tag_value instance...
            # Lets make sure we specify the right sort of mime
            defaultType = None
            if isinstance(value, list) and not all(isinstance(x, basestring) for
                                                 x in value):
                defaultType = 'application/json'
            # the attribute will be named after the tag's path with slash
            # replaced by underscode. e.g. 'foo/bar' -> 'foo_bar'
            tags[tag.path.replace('/', '_')] = tag_value(tag.path, defaultType)

def create_class(tags):
    """
    Simply creates a new class that inherits from FOM's Object class with the
    attributes based upon the tag_value instances passed in.
    """
    return type('fom_class', (Object, ), tags)

def push_to_fluiddb(raw_data, klass, about, name, username):
    """
    Given the raw data and a class derived from FOM's Object class will import
    the data into FluidDB. Each item in the list mapping to a new object in
    FluidDB. The 'about' and 'name' arguments are used to automate the
    generation of the about tag and associated value. The 'name' and
    'username' arguments are used to build the root path
    """
    length = len(raw_data)
    counter = 1
    for item in raw_data:
        logger.info("Processing record %d of %d" % (counter, length))
        counter += 1
        # create the object
        if about:
            about_value = "%s:%s" % (name, item[about])
            logger.info('Creating new object with about tag value: %s' %
                     about_value)
            obj = klass(about=about_value)
        else:
            logger.info('Creating a new anonymous object')
            obj = klass()
            obj.create()
        logger.info('Object %s successfully created' % obj.uid)
        # annotate it
        tag_values = get_values(item, build_attribute_name([username, name,]))
        for key, value in tag_values.iteritems():
            if (key in klass.__dict__.keys()):
                if value:
                    setattr(obj, key, value)
                    logger.info('Set: %s to: %s' % (key, value))
            else:
                logger.error('Unable to set %s (unknown attribute)' % key)
        if about:
            logger.info('Finished annotating Object about "%s" with id: %s' %
                         (about_value, obj.uid))
        else:
            logger.info('Finished annotating anonymous Object with id: %s' %
                         obj.uid)

def get_values(item, parent):
    """
    Given a dictionary that represents data to import into FluidDB this method
    (recursively) builds a dict where the key is the attribute name on the
    Object class and the value is the value to import into FluidDB.
    """
    vals = {}
    for key, value in item.iteritems():
        if isinstance(value, dict):
            vals.update(get_values(value, build_attribute_name([parent, key])))
        else:
            vals[build_attribute_name([parent, key])] = value
    return vals

def build_attribute_name(items):
    """
    Turns a list into a something that will be a "valid" attribute name
    """
    return '_'.join([item for item in items if item])
