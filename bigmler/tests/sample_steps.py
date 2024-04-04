# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2014-2024 BigML
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
import json

from bigml.api import check_resource

from bigmler.tests.common_steps import base_shell_execute
from bigmler.utils import open_mode
from bigmler.tests.world import world, res_filename, ok_, eq_


def i_create_sample(step, options=None, output_dir=None):
    """Step: I create a new sample from the dataset and get the sample using
    options <options> storing logs in <output_dir>
    """
    ok_(options is not None and  output_dir is not None)
    command = ("bigmler sample --dataset " + world.dataset['resource'] +
               " --store --output-dir " + output_dir +
               " " + options)
    base_shell_execute(command, output_dir)


def i_check_create_sample(step):
    """Step: I check that the sample has been created"""
    sample_file = os.path.join(world.directory, "samples")
    message = None
    try:
        with open(sample_file) as handler:
            sample = check_resource(handler.readline().strip(),
                                    world.api.get_sample)
            world.samples.append(sample['resource'])
            world.sample = sample
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_sample_stat(step, check_sample_json=None):
    """Step: the sample contains stat-info like in <check_sample_json>"""
    ok_(check_sample_json is not None)
    check_sample_json = res_filename(check_sample_json)
    message = None
    try:
        sample_json = os.path.join(world.directory, "stat_info.json")
        with open(check_sample_json) as check_sample_file:
            check_sample_contents = check_sample_file.read()
        with open(sample_json) as sample_file:
            sample_file_contents = sample_file.read()
        eq_(check_sample_contents, sample_file_contents,
            msg=f"File contents:\n{sample_file_contents}\n"
                f"Expected contents:\n{check_sample_contents}")
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_sample_file(step, check_sample_file=None):
    """Step: the sample file is like <check_sample_file>"""
    ok_(check_sample_file is not None)
    check_sample_file = res_filename(check_sample_file)
    message = None
    try:
        sample_file = os.path.join(world.directory, "sample.csv")
        with open(check_sample_file, open_mode("r")) as check_handler:
            check_sample_contents = check_handler.read()
        with open(sample_file, open_mode("r")) as sample_handler:
            sample_file_contents = sample_handler.read()

        eq_(check_sample_contents, sample_file_contents,
            msg=f"File contents:\n{sample_file_contents}\n"
                f"Expected contents:\n{check_sample_contents}")
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_sample_json(step, check_sample_file=None):
    """Step: the sample JSON is like the one in <check_sample_file>"""
    ok_(check_sample_file is not None)
    check_sample_file = res_filename(check_sample_file)
    message = None
    try:
        sample_file = os.path.join(world.directory, "stat_info.json")
        with open(check_sample_file, open_mode("r")) as check_handler:
            contents = check_handler.read()
            check_sample_json = json.loads(contents)
        with open(sample_file, open_mode("r")) as sample_handler:
            contents = sample_handler.read()
            sample_file_json = json.loads(contents)
        eq_(check_sample_json, sample_file_json,
            msg=f"File contents:\n{sample_file_json}\n"
                f"Expected contents:\n{check_sample_json}")
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)
