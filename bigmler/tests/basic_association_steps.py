# -*- coding: utf-8 -*-
#
# Copyright 2015-2017 BigML
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
from __future__ import absolute_import


import os
import time
import csv
import json

from nose.tools import assert_equal, assert_not_equal, ok_
from bigmler.tests.world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigml.api import check_resource
from bigmler.utils import storage_file_name
from bigmler.checkpoint import file_number_of_lines
from bigmler.tests.common_steps import check_debug


def shell_execute(command, output, test=None, options=None,
                  data=None, test_split=None):
    """Excute bigmler command in shell

    """
    command = check_debug(command)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            if test is not None:
                world.test_lines = file_number_of_lines(test)
                world.test_lines -= 1
                # prediction file has headers in it,
                # so first line must be ignored
                world.prediction_header = options is not None and \
                    options.find('--prediction-header') > -1
            if test_split is not None:
                data_lines = file_number_of_lines(data) - 1
                world.test_lines = int(data_lines * float(test_split))
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML association uploading train "(.*?)" file and log resources in "([^"]*)"$')
def i_create_association(step, data=None, output_dir=None):
    ok_(data is not None and output_dir is not None)
    command = ("bigmler association --train " + res_filename(data) +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "x.tmp"))


#@step(r'I check that the association has been created')
def i_check_create_association(step):
    association_file = os.path.join(world.directory, "associations")
    try:
        association_file = open(association_file, "r")
        association = check_resource(association_file.readline().strip(),
                                     world.api.get_association)
        world.associations.append(association['resource'])
        world.association = association
        association_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)


#@step(r'I create BigML association using dataset and log resources in "(.*)"')
def i_create_association_from_dataset(step, output_dir=None):
    ok_(output_dir is not None)
    command = ("bigmler association --dataset " +
               world.dataset['resource'] +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "x.tmp"))


#@step(r'I create BigML association using source and log resources in "(.*)"')
def i_create_association_from_source(step, output_dir=None):
    ok_(output_dir is not None)
    command = ("bigmler association --source " +
               world.source['resource'] +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "x.tmp"))
