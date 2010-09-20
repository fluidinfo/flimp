#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Handles the command-line arguments and kicks off the import of data.

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
import os
import sys
from traceback import format_exception
from optparse import OptionParser
from getpass import getpass
from file_handler import VALID_FILETYPES, process as process_file
from directory_handler import process as process_directory
from fom.session import Fluid
import flimp

def execute():
    """
    Grab a bunch of args from the command line, verify and get the show on the
    road
    """
    parser = OptionParser(version="%prog " + flimp.VERSION)
    parser.add_option('-f', '--file', dest='filename',
                      help='The FILE to process (valid filetypes: %s)' %
                      ', '.join(VALID_FILETYPES.keys()), metavar="FILE")
    parser.add_option('-d', '--dir', dest='directory',
                      help="The root directory for a filesystem import into"\
                      " FluidDB")
    parser.add_option('-u', '--uuid', dest="uuid", default="",
                      help="The uuid of the object to which the filesystem"\
                      " import is to attach its tags")
    parser.add_option('-a', '--about', dest="about", default="",
                      help="The about value of the object to which the"\
                      " filesystem import is to attach its tags")
    parser.add_option('-p', '--preview', action="store_true", dest="preview",
                      help="Show a preview of what will happen, don't import"\
                      " anything", default=False)
    parser.add_option('-i', '--instance', dest='instance',
                      default="https://fluiddb.fluidinfo.com",
                      help="The URI for the instance of FluidDB to use")
    parser.add_option('-l', '--log', dest='log', default="flimp.log",
                      help="The log file to write to (defaults to flimp.log)")
    parser.add_option('-v', '--verbose', dest='verbose', default=False,
                      action="store_true", help="Display status messages to"\
                      " console")
    parser.add_option('-c', '--check', dest='check', default=False,
                      action="store_true", help="Validate the data file"\
                      " containing the data to import into FluidDB - don't"\
                      " import anything")
    options, args = parser.parse_args()

    # Some options validation
    if not (options.filename or options.directory):
        parser.error("You must supply either a source file or root directory"\
                     " to import.")
    if options.filename and options.directory:
        parser.error("You may only supply either a source file OR root"\
                     " directory to import (not both).")
    if options.uuid and options.about:
        parser.error("You may only supply either an object's uuid OR its"\
                     " about tag value (not both).")

    # Setup logging properly
    logger = logging.getLogger("flimp")
    logger.setLevel(logging.DEBUG)
    logfile_handler = logging.FileHandler(options.log)
    logfile_handler.setLevel(logging.DEBUG)
    log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logfile_handler.setFormatter(log_format)
    logger.addHandler(logfile_handler)
    # verbose..?
    if options.verbose:
        # console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(log_format)
        logger.addHandler(ch)

    if options.check:
        # No need to get information from the user if we're just validating
        # the file. A bit hacky!
        username = password = root_path = name = desc = about = ""
    else:
        # In the same way that sphinx interrogates the user using q&a we need to
        # assemble some more data that is probably not so easy to grab from the
        # arguments of the command
        username = get_argument('FluidDB username')
        password = get_argument('FluidDB password', password=True)
        root_path = get_argument('Absolute Namespace path (under which imported'\
                                 ' namespaces and tags will be created)')
        if options.filename:
            name = get_argument('Name of dataset (defaults to filename)',
                            os.path.basename(options.filename).split('.')[0])
            about = get_argument('Key field for about tag value (if none given,'\
                                 ' will use anonymous objects)', required=False)
        else:
            name = get_argument('Name of dataset')
        desc = get_argument('Description of the dataset')

        # Dump the recently collected information into the log file
        logger.info('FluidDB instance: %r' % options.instance)
        logger.info('Username: %r' % username)
        logger.info('Absolute Namespace path: %r' % root_path)
        logger.info('Dataset name: %r' % name)
        logger.info('Dataset description: %r' % desc)

    # Log into FluidDB
    fdb = Fluid(options.instance)
    fdb.bind()
    fdb.login(username, password)

    # Process the file or directory
    try:
        print "Working... (this might take some time, why not: tail -f the"\
            " log?)"
        if options.filename:
            process_file(options.filename, root_path, name, desc, about,
                         options.preview, options.check)
            print "Done"
        else:
            obj = process_directory(options.directory, root_path, username,
                                    name, desc, options.uuid, options.about,
                                    options.preview)
            msg = 'Tags added to object with uuid: %s' % obj.uid
            logger.info(msg)
            print msg
    except Exception, e:
        # We want to catch all exceptions so we can log them nicely
        ex_type, ex_val, ex_trace = sys.exc_info()
        for msg in format_exception(ex_type, ex_val, ex_trace):
            logger.critical(msg)
        # this will be handled nicely by the try of last resort in the
        # flimp command line tool
        raise e
    finally:
        logger.info('FINISHED!') # :-)

def get_argument(description, default_value=None, required=True,
                 password=False):
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
    if required and not default_value:
        user_val = None
        while not user_val:
            if password:
                user_val = getpass("%s: " % desc)
            else:
                user_val = raw_input("%s: " % desc)
            if not user_val:
                print "This field is required!"
        val = user_val
    else:
        if password:
            val = getpass("%s: " % desc)
        else:
            val = raw_input("%s: " % desc)
    if default_value and not val:
        val = default_value
    return val
