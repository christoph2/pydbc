#!/bin/env/python

from distutils.core import setup, Extension
import os
import sys
from setuptools import find_packages
from glob import glob

ANTLR_VERSION = '4.7.1'

setup(
    name = 'pydbc',
    version = '0.1.0',
    description = "DBC for Python",
    author = 'Christoph Schueler',
    author_email = 'cpu12.gems@googlemail.com',
    url = 'https://www.github.com/Christoph2/pydbc',
    packages = ['pydbc'],
    install_requires = ["antlr4-python3-runtime=={}".format(ANTLR_VERSION),
        'mock', 'mako', 'wxPython>=4.0.0', 'colorama'
    ],
    entry_points = {
        'console_scripts': [
                'dbc_importer = pydbc.scripts.dbc_importer:main'
        ],
    },
    data_files = [
        ('cgen/templates/', glob('cgen/templates/*.tmpl')),
    ],
    test_suite="pydbc.tests"
)

