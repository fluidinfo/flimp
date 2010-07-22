#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Takes a json file, and imports the data into FluidDB

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
from optparse import OptionParser
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json
from fom.errors import Fluid412Error
from fom.session import Fluid
from fom.mapping import Namespace, Tag, Object, tag_value

NAMESPACE_DESC = "%s namespace derived from %s.\n\n%s"
TAG_DESC = "%s tag derived from %s.\n\n%s"

def clean_data(username, password, filename, description, name, about):
    fdb = Fluid('http://sandbox.fluidinfo.com')
    fdb.bind()
    fdb.login(username, password)
    f = open(filename, 'r')
    data = json.loads(f.read())
    assert isinstance(data, list), "The json file must provide a list of"\
        " dict records"
    if len(data) > 0:
        template = data[0]
        root_ns = Namespace(username)
        tags = {}
        generate(root_ns, name, template, description, name, tags)
        fom_class = create_class(tags)
        for item in data[:10]:
            annotate(item, fom_class, about, name, "%s_%s" % (root_ns.path, name))
    else:
        print "No records found"
        return

def generate(parent, child_name, template, description, name, tags):
    try:
        ns = parent.create_namespace(child_name,
                                 NAMESPACE_DESC % (child_name, name, description))
    except Fluid412Error:
        ns = Namespace(parent.path + '/' + child_name)
    for key, value in template.iteritems():
        if isinstance(value, dict):
            generate(ns, key, value, description, name, tags)
        else:
            try:
                tag = ns.create_tag(key, TAG_DESC % (key, name, description), False)
            except Fluid412Error:
                tag = Tag(parent.path + '/' + child_name + '/' + key)
            defaultType = None
            if isinstance(value, list) and not all(isinstance(x, basestring) for
                                                 x in value):
                defaultType = 'application/json'
            tags[tag.path.replace('/', '_')] = tag_value(tag.path, defaultType)

def create_class(tags):
    return type('fom_class', (Object, ), tags)

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

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-u', '--username', dest='username',
                      help='FluidDB username')
    parser.add_option('-p', '--password', dest='password',
                      help='FluidDB password')
    parser.add_option('-f', '--file', dest='filename',
                      help='The json FILE to process', metavar="FILE")
    parser.add_option('-d', '--description', dest='description',
                      help='A description of the data')
    parser.add_option('-n', '--name', dest='name',
                      help='A name for this dataset')
    parser.add_option('-a', '--about', dest='about',
                      help='The field to use as the basis for the about'\
                      ' tag value (defaults to "id")', default='id')
    options, args = parser.parse_args()
    if (options.username and options.password and options.filename and
        options.description and options.name):
        clean_data(options.username, options.password, options.filename,
                   options.description, options.name, options.about)
    else:
        parser.error("You must supply a username, password, source file,"\
                    " description and name")
