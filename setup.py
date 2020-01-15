#!/bin/env/python

import os
import sys
from setuptools import find_packages, setup, Extension
from glob import glob

ANTLR_VERSION = '4.7.2'

with open("README.md", "r") as fh:
    long_description = fh.read()

INSTALL_REQUIRES = ["antlr4-python3-runtime=={}".format(ANTLR_VERSION), 'mako', 'colorama', 'SQLAlchemy']


if (sys.version_info.major == 3 and sys.version_info.minor < 4) or (sys.version_info.minor < 3):
    print("ERROR: pyDBC requires at least Python 3.4")
    sys.exit(1)

setup(
    name = 'pydbc',
    version = '0.1.0',
    description = "Vehicle description file handling for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = 'Christoph Schueler',
    author_email = 'cpu12.gems@googlemail.com',
    url = 'https://www.github.com/Christoph2/pydbc',
    packages = find_packages(),
    install_requires = INSTALL_REQUIRES,
#    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-runner"],
    extras_require={
        "docs": [
            'sphinxcontrib-napoleon', 'numpydoc'
        ],
       "develop": [
            "bumpversion"
        ]
    },
    entry_points = {
        'console_scripts': [
                'vndb_importer = pydbc.scripts.vndb_importer:main'
        ],
    },
    include_package_data = True,
    package_data = {
        "templates": glob('cgen/templates/*.tmpl'),
    },
    test_suite="pydbc.tests",
    license='GPLv2',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

)

