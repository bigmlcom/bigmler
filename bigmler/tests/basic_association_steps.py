# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2015-2024 BigML
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


from bigml.api import check_resource

from bigmler.tests.common_steps import shell_execute
from bigmler.tests.world import world, res_filename, ok_

def i_create_association(step, data=None, output_dir=None):
    """Step: I create BigML association uploading train <data> file and log
    resources in <output_dir>"""
    ok_(data is not None and output_dir is not None)
    command = ("bigmler association --train " + res_filename(data) +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "x.tmp"))


def i_check_create_association(step):
    """Step: I check that the association has been created"""
    association_file = os.path.join(world.directory, "associations")
    message = None
    try:
        with open(association_file) as handler:
            association = check_resource(handler.readline().strip(),
                                         world.api.get_association)
            world.associations.append(association['resource'])
            world.association = association
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_create_association_from_dataset(step, output_dir=None):
    """Step: I create BigML association using dataset and log resources
    in <output_dir>
    """
    ok_(output_dir is not None)
    command = ("bigmler association --dataset " +
               world.dataset['resource'] +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "x.tmp"))


def i_create_association_from_source(step, output_dir=None):
    """Step: I create BigML association using source and log resources in
    <output_dir>
    """
    ok_(output_dir is not None)
    command = ("bigmler association --source " +
               world.source['resource'] +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "x.tmp"))
