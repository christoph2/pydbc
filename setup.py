#!/bin/env/python

from distutils.core import setup, Extension
import os
import sys
from setuptools import find_packages
from glob import glob

ANTLR_VERSION = '4.7.2'


if os.environ.get("TRAVIS") or os.environ.get("APPVEYOR"):
    INSTALL_REQUIRES = ["antlr4-python3-runtime=={}".format(ANTLR_VERSION), 'mako', 'colorama', 'numpydoc', 'sphinxcontrib-napoleon']
else:
    INSTALL_REQUIRES = ["antlr4-python3-runtime=={}".format(ANTLR_VERSION), 'mako', 'wxPython>=4.0.0', 'colorama', 'numpydoc', 'sphinxcontrib-napoleon']


if (sys.version_info.major == 3 and sys.version_info.minor < 4) or (sys.version_info.minor < 3):
    print("ERROR: pyDBC requires at least Python 3.4")
    sys.exit(1)

setup(
    name = 'pydbc',
    version = '0.1.0',
    description = "DBC for Python",
    author = 'Christoph Schueler',
    author_email = 'cpu12.gems@googlemail.com',
    url = 'https://www.github.com/Christoph2/pydbc',
    packages = find_packages(),
    install_requires = INSTALL_REQUIRES,
    entry_points = {
        'console_scripts': [
                'vndb_importer = pydbc.scripts.vndb_importer:main'
        ],
    },
    data_files = [
        ('cgen/templates', glob('cgen/templates/*.tmpl')),
    ],
    test_suite="pydbc.tests"
)

