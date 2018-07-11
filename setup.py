#!/bin/env/python

from distutils.core import setup, Extension
import os
import sys
from setuptools import find_packages
from glob import glob

ANTLR_VERSION = '=4.7.1'
ANTLR_RT = "{}".format("antlr4-python3-runtime" if sys.version_info.major == 3 
    else "antlr4-python2-runtime", ANTLR_VERSION)

print(ANTLR_RT)

setup(
    name = 'pydbc',
    version = '0.1.0',
    description = "DBC for Python",
    author = 'Christoph Schueler',
    author_email = 'cpu12.gems@googlemail.com',
    url = 'https://www.github.com/Christoph2/pydbc',
    packages = ['pydbc'],
    install_requires = [ANTLR_RT, 'enum34', 'mock', 'mako', 'wxPython>=4.0.0'],
    #entry_points = {
    #    'console_scripts': [
    #            'vd_exporter = pyA2L.catalogue.vd_exporter:main'
    #    ],
    #},
    #data_files = [
    #        ('pya2l/config', glob('pya2l/config/*.*')),
    #        ('pya2l/imagez', glob('pya2l/imagez/*.bin')),
    #],
    test_suite="pydbc.tests"
)

