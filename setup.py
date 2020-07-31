#!/usr/bin/env python
#
# Copyright 2012-2017 BigML, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import re

import setuptools

# Get the path to this project
project_path = os.path.dirname(__file__)

# Read the version from bigml.__version__ without importing the package
# (and thus attempting to import packages it depends on that may not be
# installed yet)
init_py_path = os.path.join(project_path, 'bigmler', '__init__.py')
version = re.search("__version__ = '([^']+)'",
                    open(init_py_path).read()).group(1)

# Concatenate files into the long description
file_contents = []
for file_name in ('README.rst', 'HISTORY.rst'):
    path = os.path.join(os.path.dirname(__file__), file_name)
    file_contents.append(open(path).read())
long_description = '\n\n'.join(file_contents)


setuptools.setup(
    name="bigmler",
    description="A command-line tool for BigML.io, the public BigML API",
    long_description=long_description,
    version=version,
    author="The BigML Team",
    author_email="bigml@bigml.com",
    url="https://bigml.com/developers",
    download_url="https://github.com/bigmlcom/bigmler",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    setup_requires = ['nose'],
    packages = ['bigmler', 'bigmler.processing', 'bigmler.analyze',
                'bigmler.cluster', 'bigmler.anomaly', 'bigmler.report',
                'bigmler.options', 'bigmler.delete', 'bigmler.sample',
                'bigmler.tests', 'bigmler.reify', 'bigmler.project',
                'bigmler.association', 'bigmler.logisticregression',
                'bigmler.execute', 'bigmler.whizzml', 'bigmler.topicmodel',
                'bigmler.timeseries', 'bigmler.deepnet', 'bigmler.retrain',
                'bigmler.export', 'bigmler.export.out_model',
                'bigmler.resourcesapi',
                'bigmler.linearregression', 'bigmler.pca', 'bigmler.fusion',
                'bigmler.dataset', 'bigmler.externalconnector',
                'bigmler.export.out_tree'],
    install_requires = ['bigml>=5.0.0, <6.0.0',
                        'jsonschema==2.6.0',
                        'nbformat>=4.4.0'],
    package_data={'bigmler':['static/*.json',
                             'static/*.html',
                             'static/out_model/*',
                             'static/scripts/incremental/*.json',
                             'static/scripts/incremental/retrain/*',
                             'static/scripts/incremental/reify/*',
                             'static/scripts/incremental/generate_whizzml/*',
                             'static/scripts/reify/python/*',
                             'static/scripts/reify/whizzml/*',
                             'static/scripts/reify/*.json']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='bigmler.tests',
    entry_points={
        'console_scripts': [
            'bigmler = bigmler.bigmler:main',
        ]
    }
)
