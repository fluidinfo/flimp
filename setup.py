#!/usr/bin/env python

from distutils.core import setup

setup(name='flimp',
      version='0.1',
      description='FLuiddb IMPorter - automates importing data into FluidDB',
      author='Nicholas H.Tollervey',
      author_email='ntoll@ntoll.org',
      url='http://github.com/fluidinfo/flimp',
      packages=['flimp', 'flimp.parser'],
      scripts=['bin/flimp'],
      requires=['fom', 'PyYaml'],
      license='MIT',
      long_description=open('README').read(),
     )
