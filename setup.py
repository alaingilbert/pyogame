#!/usr/bin/env python

from distutils.core import setup

setup(name='ogame',
      version='1.1.2',
      description='OGame wrapper.',
      author='Alain Gilbert',
      author_email='alain.gilbert.15@gmail.com',
      packages=['ogame'],
      url='https://github.com/alaingilbert/pyogame',
      install_requires=['requests',
                        'arrow',
                        'beautifulsoup4'],
      )
