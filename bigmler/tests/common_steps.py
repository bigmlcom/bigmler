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
import csv

from subprocess import check_call, CalledProcessError

from bigml.api import HTTP_OK

from bigmler.checkpoint import file_number_of_lines
from bigmler.tests.world import world, approx_error, ok_, ok_error


def check_debug(command, project=True):
    """Adds verbosity level and command print.

    """
    non_project_commands = ["--project", "bigmler reify", "bigmler analyze",
                            "bigmler delete", "bigmler report",
                            "bigmler delete", "bigmler project",
                            "bigmler execute", "bigmler whizzml",
                            "bigmler export", "bigmler retrain",
                            "--org-project"]
    debug = os.environ.get('BIGMLER_DEBUG', False)

    if command.find("bigmler") < 0:
        if debug:
            print(command)
        return command

    # adding project id as source creation parameter
    if (project and
        all(command.find(string) < 0 for string in non_project_commands)):
        command = "%s --project-id %s" % (command, world.project_id)
    verbosity = 0
    extend_cmd = ''
    if debug == '1':
        verbosity = 1
    elif debug == '2':
        extend_cmd = ' --debug'
    if command.find("bigmler report") < 0:
        command = "%s --verbosity %s%s" % (command, verbosity, extend_cmd)
    if debug:
        print(command)
    return command


def check_http_code(resources):
    """Checks the http code in the resource list

    """
    if resources['code'] == HTTP_OK:
        assert True
    else:
        assert False, "Response code: %s" % resources['code']


def store_init_resources():
    """Store the initial existing resources grouped by resource_type

    """
    world.count_resources('init')


def store_final_resources():
    """Store the final existing resources grouped by resource_type

    """
    world.count_resources('final')


def check_init_equals_final():
    """Checks that the number of resources grouped by type has not changed

    """
    world.check_init_equals_final()


def shell_execute(command, output, test=None, options=None,
                  data=None, test_split=None, test_rows=None, project=True):
    """Excute bigmler command in shell and checking test rows"""
    world.output = output
    message = base_shell_execute(
        command, os.path.dirname(output), project=project)
    try:
        world.test_lines = 0
        if test is not None:
            world.test_header = 1
            world.test_lines += file_number_of_lines(test)
            # if test file containss headers and the prediction command don't,
            # we need to remove 1 to compensate for the header
            if '_nh' not in test and '--prediction-header' not in command \
                    and '--remote' not in command:
                world.test_lines -= 1
                world.test_header = 0
            if '_nh' not in test and options is not None and \
                    '--no-header' in options:
                world.test_lines -= 1
                world.test_header = 0
        elif test_rows is not None:
            world.test_header = 0
            world.test_lines += test_rows
        elif test_split is not None:
            world.test_header = 0
            data_lines = file_number_of_lines(data) - 1
            world.test_lines = int(data_lines * float(test_split))
    except IOError as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def base_shell_execute(command, output_dir, project=True):
    """Executing bigmler command in shell"""
    message = None
    command = check_debug(command, project=project)
    world.directory = output_dir
    world.folders.append(output_dir)
    try:
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
    except (OSError, CalledProcessError, IOError) as exc:
        message = str(exc)
    return message


def check_rows_equal(reader_file, check_file):
    """Checking values in rows are equal"""
    message = None
    with open(reader_file) as p_handler:
        reader = csv.reader(p_handler, lineterminator="\n")
        with open(check_file) as c_handler:
            check_reader = csv.reader(c_handler, lineterminator="\n")
            for index0, row in enumerate(reader):
                ref_row = next(check_reader)
                if len(ref_row) != len(row):
                    return "Row %s with different lengths: %s, %s, %s, %s" % (
                        str(index0), str(len(ref_row)), str(len(row)), ref_row,
                        row)
                for index, row_value in enumerate(row):
                    dot = row_value.find(".")
                    if dot > 0 or (ref_row[index].find(".") > 0
                                   and ref_row[index].endswith(".0")):
                        try:
                            decimal_places = min((
                                min(len(row_value), len(ref_row[index]))
                                - dot - 1), 5)
                            message = approx_error(
                                float(row_value),
                                float(ref_row[index]),
                                precision=decimal_places,
                                msg=("Row %s don't match. Found %s,"
                                     " %s expected" % (
                                     index0, row_value, ref_row[index])))
                        except ValueError:
                            message = ok_error(row_value == ref_row[index],
                                msg=("Row %s don't match. Found %s,"
                                     " %s expected" % (
                                     index0, row_value, ref_row[index])))
                    else:
                        message = ok_error(row_value == ref_row[index],
                            msg=("Row %s don't match. Found %s,"
                                 " %s expected" % (
                                 index0, row_value, ref_row[index])))
                    if message is not None:
                        break
                if message is not None:
                    break
    return message
