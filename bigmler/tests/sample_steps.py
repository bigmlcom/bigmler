# -*- coding: utf-8 -*-
#
# Copyright 2014-2020 BigML
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
import time
import json
from bigmler.tests.world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigmler.checkpoint import file_number_of_lines
from bigmler.utils import BIGML_SYS_ENCODING, open_mode
from bigml.api import check_resource
from bigmler.tests.common_steps import check_debug


#@step(r'I create a new sample from the dataset and get the sample using options "(.*)" storing logs in "(.*)"')
def i_create_sample(step, options=None, output_dir=None):
    if options is None or output_dir is None:
        assert False
    world.directory = output_dir
    world.folders.append(world.directory)
    try:
        command = ("bigmler sample --dataset " + world.dataset['resource'] +
                   " --store --output-dir " + output_dir +
                   " " + options)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output_dir
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I check that the sample has been created')
def i_check_create_sample(step):
    sample_file = "%s%ssamples" % (world.directory, os.sep)
    try:
        sample_file = open(sample_file, "r")
        sample = check_resource(sample_file.readline().strip(),
                                world.api.get_sample)
        world.samples.append(sample['resource'])
        world.sample = sample
        sample_file.close()
        assert True
    except Exception as exc:
        assert False, str(exc)


#@step(r'the sample contains stat-info like in "(.*)"')
def i_check_sample_stat(step, check_sample_json=None):
    if check_sample_json is None:
        assert False
    check_sample_json = res_filename(check_sample_json)
    try:
        sample_json = os.path.join(world.directory, "stat_info.json")
        with open(check_sample_json, "r") as check_sample_file:
            check_sample_contents = check_sample_file.read()
        with open(sample_json, "r") as sample_file:
            sample_file_contents = sample_file.read()
        if check_sample_contents == sample_file_contents:
            assert True
        else:
            assert False, ("File contents:\n%s\nExpected contents:\n%s" %
                           (sample_file_contents, check_sample_contents))
    except Exception as exc:
        assert False, str(exc)


#@step(r'the sample file is like "(.*)"')
def i_check_sample_file(step, check_sample_file=None):
    if check_sample_file is None:
        assert False
    check_sample_file = res_filename(check_sample_file)
    try:
        sample_file = os.path.join(world.directory, "sample.csv")
        with open(check_sample_file, open_mode("r")) as check_sample_file:
            check_sample_contents = check_sample_file.read()
        with open(sample_file, open_mode("r")) as sample_file:
            sample_file_contents = sample_file.read()
        if check_sample_contents == sample_file_contents:
            assert True
        else:
            assert False, ("File contents:\n%s\nExpected contents:\n%s" %
                           (sample_file_contents, check_sample_contents))
    except Exception as exc:
        assert False, str(exc)


#@step(r'the sample JSON is like the one in "(.*)"')
def i_check_sample_json(step, check_sample_file=None):
    if check_sample_file is None:
        assert False
    check_sample_file = res_filename(check_sample_file)
    try:
        sample_file = os.path.join(world.directory, "stat_info.json")
        with open(check_sample_file, open_mode("r")) as check_sample_file:
            contents = check_sample_file.read()
            check_sample_json = json.loads(contents)
        with open(sample_file, open_mode("r")) as sample_file:
            contents = sample_file.read()
            sample_file_json = json.loads(contents)
        if check_sample_json == sample_file_json:
            assert True
        else:
            assert False, ("File contents:\n%s\nExpected contents:\n%s" %
                           (sample_file_json, check_sample_json))
    except Exception as exc:
        assert False, str(exc)
