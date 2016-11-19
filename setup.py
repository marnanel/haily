#!/usr/bin/env python

from distutils.core import setup

setup(name='Haily',
                version='0.1',
                description='Tomboy server',
                author='Thomas Thurman',
                author_email='thomas@thurman.org.uk',
                url='https://github.com/tthurman/haily',
                packages=['haily'],
                requires=[
                        'dulwich',
                        ],
     )
