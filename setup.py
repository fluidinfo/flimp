#!/usr/bin/env python

from distutils.core import setup

setup(name='flimp',
      version='0.1',
      description='FluidDB json importer',
      author='Nicholas H.Tollervey',
      author_email='ntoll@ntoll.org',
      url='http://github.com/fluidinfo/flimp',
      packages=['flimp'],
      scripts=['bin/flimp'],
     )
