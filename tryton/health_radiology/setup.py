#!/usr/bin/env python

# SPDX-FileCopyrightText:  2024 - Wei Zhao <wei.zhao@uclouvain.be>
# SPDX-License-Identifier: GPL-3.0-or-later
#
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                   HEALTH RADIOLOGY package                            #
#                   setup.py: Setuptools file                           #
#########################################################################

from setuptools import setup
import re
import os
import configparser

def read(fname):
    """
    Read the contents of a file.

    Args:
        fname (str): The name of the file to be read.

    Returns:
        str: The contents of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    return open(os.path.join(os.path.dirname(__file__), fname),
                encoding="UTF-8").read()
    
config = configparser.ConfigParser()
config.readfp(open('tryton.cfg'))
info = dict(config.items('tryton'))


for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()
major_version, minor_version = 6, 0

requires = []

for dep in info.get('depends', []):
    if (dep == 'health'):
        requires.append('gnuhealth == %s' % (info.get('version')))

    elif dep.startswith('health_'):
        health_package = dep.split('_', 1)[1]
        requires.append(
            'gnuhealth_%s == %s' %
            (health_package, info.get('version')))
    else:
        if not re.match(r'(ir|res|webdav)(\W|$)', dep):
            requires.append(
                'trytond_%s >= %s.%s, < %s.%s' %
                (dep, major_version, minor_version, major_version,
                    minor_version + 1))

setup(
    name='health_radiology',
    version=info.get('version', '0.0.1'),
    description=info.get(
        'description',
        'GNU Health Radiology package'),
    long_description=read('README.rst'),
    author='GNU Solidario',
    author_email='health@gnusolidario.org',
    url='https://www.gnuhealth.org',
    download_url='http://ftp.gnu.org/gnu/health/',
    package_dir={'trytond.modules.health_radiology': '.'},
    packages=[
        'trytond.modules.health_radiology',
        'trytond.modules.health_radiology.tests',
        'trytond.modules.health_radiology.wizard',
        ],

    package_data={
        'trytond.modules.health_radiology': info.get('xml', [])
        + info.get('translation', [])
        + ['tryton.cfg', 'view/*.xml', 'doc/*.rst', 'locale/*.po',
           'report/*.fodt', 'icons/*.svg'],
        },

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Framework :: Tryton',
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Natural Language :: Spanish',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        ],
    license='GPL-3',
    install_requires=requires,
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    health_radiology = trytond.modules.health_radiology
    """,
    test_suite='tests',
    test_loader='trytond.test_loader:Loader',
    )