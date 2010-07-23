#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Takes a json file, and imports the data into FluidDB

Please feel free to adapt and change. Hacky... you have been warned! ;-)

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

import logging
import sys
from optparse import OptionParser
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json
from fom.errors import Fluid412Error
from fom.session import Fluid
from fom.mapping import Namespace, Tag, Object, tag_value
from parser import parse_json, parse_yaml, parse_csv

NAMESPACE_DESC = "%s namespace derived from %s.\n\n%s"
TAG_DESC = "%s tag derived from %s.\n\n%s"

LOG_FILENAME = 'flimp.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def clean_data(filename):
    """
    Given a filename will open it and pass it to the appropriate parser to
    turn it into a dictionary object for further processing
    """
    extension = filename.split('.')[-1:][0]
    if not extension in ('json', ):
        raise TypeError('Unknown file type to parse')

    f = open(filename, 'r')

    if extension == 'json':
        logging.info('Parsing json')
        return parse_json.parse(f)

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
        ns = parent.create_namespace(child_name,
                                 NAMESPACE_DESC % (child_name, name, description))
    except Fluid412Error:
        # 412 simply means the namespace already exists
        ns = Namespace(parent.path + '/' + child_name)

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
                tag = ns.create_tag(key, TAG_DESC % (key, name, description), False)
            except Fluid412Error:
                # 412 simply means the namespace already exists
                tag = Tag(parent.path + '/' + child_name + '/' + key)
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

"""
def annotate(item, fom_class, about, name, base_namespace):
    about_val, tag_values = get_values(item, about, name, base_namespace)
    obj = fom_class(about=about_val)
    for key, value in tag_values.iteritems():
        if (key in fom_class.__dict__.keys()):
            if value:
                setattr(obj, key, value)
        else:
            raise ValueError('No such attribute %s' % key)
    print obj.uid
    print obj.about

def get_values(item, about, name, parent):
    about_val = ''
    vals = {}
    for key, value in item.iteritems():
        if key == about:
            about_val = '%s:%s' % (name, value)
        if isinstance(value, dict):
            a, v = get_values(value, about, name, build_path([parent, key]))
            if a and not about_val:
                about_val = a
            vals.update(v)
        else:
            vals[build_path([parent, key])] = value
    return about_val, vals

def build_path(items):
    return '_'.join([item for item in items if item])
"""

def execute():
    """
    Grab a bunch of args from the command line, verify and get the show on the
    road
    """
    # get the filename of the json to import and (optionally) the instance of
    # FluidDB to connect to.
    instance = 'https://fluiddb.fluidinfo.com'
    parser = OptionParser()
    parser.add_option('-f', '--file', dest='filename',
                      help='The json FILE to process', metavar="FILE")
    parser.add_option('-i', '--instance', dest='instance',
                      help="The URI for the instance of FluidDB to use")
    options, args = parser.parse_args()
    if not options.filename:
        parser.error("You must supply a source file to import.")
    if options.instance:
        instance = options.instance

    logging.info('FluidDB instance: %s' % instance)
    logging.info('Raw filename: %s' % options.filename)
    # In the same way that sphinx interrogates the user using q&a we need to
    # assemble some more data that is probably not so easy to 
    username = get_argument('FluidDB username')
    password = get_argument('FluidDB password')
    name = get_argument('Name of dataset (defaults to filename)',
                        parser.filename)
    desc = get_argument('Description of the dataset')
    about = get_argument('Key field for about tag value (defaults to "id")',
                         'id')
    logging.info('Username: %s' % username)
    logging.info('Dataset name: %s' % name)
    logging.info('Dataset description: %s' % desc)
    logging.info('About tag field key: %s' % about)

    # Log into FluidDB
    fdb = Fluid(instance)
    fdb.bind()
    fdb.login(username, password)

    # Turn the raw input file into a list data structure containing the items
    # to import into FluidDB
    raw_data = clean_data(options.filename)
    logging.info('%d records found' % len(raw_data))

    # Use the first item in the list of items 
    tag_list = create_schema(raw_data, name, desc)

    # Create a FOM class that inherits from Object to use to interract with
    # FluidDB
    fom_class = create_class(tag_list)

    # Given the newly existing class push all the data to FluidDB
    push_to_fluiddb(raw_data, fom_class, about)

def get_argument(description, default_value=None, required=True):
    """
    Will return a string value obtained from the user given the description
    and other stuff so that arguments for importing data into FluidDB can be
    built.
    """
    if default_value:
        desc = "%s [%s]" % (description, str(default_value))
    else:
        desc = description
    val = default_value
    if required:
        user_val
        while not user_val:
            user_val = raw_input("%s: " % desc)
            if not user_val:
                print "This field is required!"
        val = user_val
    else:
        val = raw_input("%s: " % desc)
    return val
