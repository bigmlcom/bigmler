# -*- coding: utf-8 -*-
#
# Copyright 2021 BigML
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
import zipfile
import glob

from bigmler.tests.world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigml.api import check_resource
from bigml.util import filter_by_extension
from bigml.fields import Fields
from bigml.constants import IMAGE_EXTENSIONS
from nose.tools import ok_, assert_equal, assert_not_equal, assert_almost_equal
from bigmler.tests.common_steps import check_debug
from bigmler.utils import read_sources
from bigmler.processing.annotations import fields_from_annotations, \
    labels_from_annotations


def shell_execute(command, output, test=None, options=None,
                  test_rows=None, project=True):
    """Excute bigmler command in shell

    """
    command = check_debug(command, project=project)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        if test is not None:
            world.test_lines = file_number_of_lines(test)
            if options is None or \
                    options.find('--prediction-header') == -1:
                # test file has headers in it, so first line must be ignored
                world.test_lines -= 1
        elif test_rows is not None:
            world.test_lines = test_rows
            if options is not None and \
                    options.find('--prediction-header') > -1:
                world.test_lines += 1
        elif options is not None and \
                options.find('--prediction-header') > -1:
            world.test_lines += 1
        world.output = output
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

#@step(r'I create BigML composite from a list of sources and
#        log results in "(.*)"')
def i_create_composite_from_sources(step, sources=None, output_dir=None):
    ok_(sources is not None and output_dir is not None)
    command = ("bigmler source --sources " + sources +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "txt.tmp"))

#@step(r'I create empty BigML composite and then add list of sources and
#        log results in "(.*)"')
def i_create_empty_composite_and_add_source(step, add_sources=None,
                                            output_dir=None):
    ok_(add_sources is not None and output_dir is not None)
    command = ("bigmler source --sources \"\" --add-sources " + add_sources +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "txt.tmp"))

#@step(r'I remove the sources from a BigML composite and
#        log results in "(.*)"')
def remove_sources(step, output_dir=None):
    ok_(output_dir is not None)
    command = ("bigmler source --source " + world.source["resource"] +
               " --remove-sources " + ",".join(step.sources) +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "txt.tmp"))


#@step(r'I delete the sources from a BigML composite and
#        log results in "(.*)"')
def delete_sources(step, output_dir=None):
    ok_(output_dir is not None)
    command = ("bigmler source --source " + world.source["resource"] +
               " --delete-sources " + ",".join(step.sources) +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "txt.tmp"))


#@step(r'I create empty BigML composite and then add list of sources and
#        log results in "(.*)"')
def i_create_empty_composite_and_add_source(step, add_sources=None,
                                            output_dir=None):
    ok_(add_sources is not None and output_dir is not None)
    command = ("bigmler source --sources \"\" --add-sources " + add_sources +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "txt.tmp"))

#@step(r'I create  BigML composite for an "<annotations_file>" and an
# "<images_file>" and log results in "(.*)"')
def i_create_annotated_source(step, annotations_file=None,
                                    images_file=None,
                                    output_dir=None):
    ok_(annotations_file is not None and images_file is not None and
        output_dir is not None)
    command = ("bigmler source --annotations-file " + annotations_file +
               " --data " + images_file +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "txt.tmp"))


#@step(r'I create  BigML composite for a "<annotations_language>"
# "<annotations_dir>" and an
# "<images_dir>" and log results in "(.*)"')
def i_create_lang_annotated_source(step, annotations_dir=None,
                                        images_dir=None,
                                        annotations_language=None,
                                        output_dir=None):
    ok_(annotations_dir is not None and images_dir is not None and
        annotations_language is not None and output_dir is not None)
    command = ("bigmler source --annotations-dir " + annotations_dir +
               " --data " + images_dir + " --annotations-language " +
               annotations_language +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "txt.tmp"))


#@step(r'I check that the sources are in the composite')
def check_sources_in_composite(step):
    assert_equal(step.sources, ["source/%s" % source for source in
                                  world.source["object"].get("sources", [])])

#@step(r'I check that the composite has been created$')
def i_check_create_composite(step):
    source_file = os.path.join(world.directory, "source")
    try:
        last_source = read_sources(source_file)
        source = check_resource(
            last_source.strip(), world.api.get_source)
        if source['resource'] not in world.composites:
            world.composites.append(source['resource'])
        world.source = source
    except Exception as exc:
        assert False, str(exc)

#@step(r'I check the number of sources in the composite is <images_number>')
def check_images_number_in_composite(step, zip_file):
    sources = []
    if os.path.isdir(zip_file):
        sources = filter_by_extension(glob.glob(os.path.join(zip_file, "**"),
                                                recursive=True),
                                      IMAGE_EXTENSIONS)
    else:
        zip = zipfile.ZipFile(zip_file)
        sources = filter_by_extension(zip.namelist(), IMAGE_EXTENSIONS)
    assert_equal(len(sources), len(step.sources))

def check_annotation_fields(step, annotations_file):
    fields = fields_from_annotations(annotations_file)
    field_labels = labels_from_annotations(annotations_file)
    source_fields = Fields(world.source)
    field_names = list(source_fields.fields_by_name.keys())
    for field in fields:
        assert field["name"] in field_names
        assert field_labels[field["name"]] == source_fields.fields[source_fields.fields_by_name[field["name"]]]["values"]
