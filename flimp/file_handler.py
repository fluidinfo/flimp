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
import os
import logging
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json
from flimp.utils import process_data_list, validate
from flimp.parser import parse_json, parse_yaml, parse_csv

VALID_FILETYPES = {
    '.json': parse_json,
    '.csv': parse_csv,
    '.yaml': parse_yaml
}

logger = logging.getLogger("flimp")

def process(filename, root_path, name, desc, about, preview=False,
            check=False):
    """
    The recipe for grabbing the file and pushing it to FluidDB
    """
    # Turn the raw input file into a list data structure containing the items
    # to import into FluidDB
    raw_data = clean_data(filename)
    logger.info('Raw filename: %r' % filename)
    logger.info('Root namespace path: %r' % root_path)
    logger.info('About tag field key: %r' % about)
    logger.info('%d records found' % len(raw_data))

    if preview or check:
        if preview:
            # just print out/log a preview
            logger.info('Generating preview...')
            output = list()
            output.append("Preview of processing %r\n" % filename)
            output.append("The following namespaces/tags will be generated.\n")
            output.extend(get_preview(raw_data, root_path))
            output.append("\n%d records will be imported into FluidDB\n" %
                          len(raw_data))
            result = "\n".join(output)
            logger.info(result)
            print result
        else:
            # check the file and display the results
            logger.info('Validating %r\n' % filename)
            output = list()
            errors, warnings = validate(raw_data)
            if errors:
                output.append("The following ERRORS were found:\n")
                output.extend(errors)
                output.append('\n')
            if warnings:
                output.append("The following WARNINGS were generated:\n")
                output.extend(warnings)
            if output:
                result = "\n".join(output)
            else:
                result = "Validation passed ok"
            logger.info(result)
            print result
    else:
        process_data_list(raw_data, root_path, name, desc, about)

def get_preview(raw_data, root_path):
    """
    Returns a list of the namespace/tag combinations that will be created
    """
    template = raw_data[0]
    result = list()
    traverse_preview(template, root_path, result)
    return result

def traverse_preview(template, parent, tags):
    """
    Does exactly what it says - traverses the preview dict and adds fully
    qualified tag paths to the result list
    """
    logger.info('Found namespace: %r' % parent)
    for key, value in template.iteritems():
        # lets see what's in here
        if isinstance(value, dict):
            # ok... we have another dict, so we're doing depth first traversal
            # and jump right in
            traverse_preview(value, '/'.join([parent, key]), tags)
        else:
            # Yay! it's a tag!
            logger.info('Found tag: %r' % key)
            tags.append('/'.join([parent, key]))

def clean_data(filename):
    """
    Given a filename will open it and pass it to the appropriate parser to
    turn it into a dictionary object for further processing
    """
    extension = os.path.splitext(filename)[1]
    try:
        parser = VALID_FILETYPES[extension]
    except KeyError:
        raise TypeError('Unknown file extension %r to parse' % extension)
    else:
        f = open(filename, 'r')
        logger.info('Parsing %r' % extension)
        result = parser.parse(f)
        f.close()
        return result

