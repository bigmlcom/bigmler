# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2021-2024 BigML
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
import zipfile
import glob


from bigml.api import check_resource
from bigml.util import filter_by_extension
from bigml.fields import Fields
from bigml.constants import IMAGE_EXTENSIONS

from bigmler.tests.common_steps import shell_execute
from bigmler.utils import read_sources
from bigmler.processing.annotations import fields_from_annotations, \
    labels_from_annotations
from bigmler.tests.world import world, res_filename, ok_, eq_


TRANSLATED_FEATURES = {"histogram_of_gradients": "HOG"}


def i_create_composite_from_sources(step, sources=None, output_dir=None):
    """Step: I create BigML composite from a list of sources and
    log results in <output_dir>
    """
    ok_(sources is not None and output_dir is not None)
    command = ("bigmler source --sources " + sources +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "txt.tmp"))


def i_create_empty_composite_and_add_source(step, add_sources=None,
                                            output_dir=None):
    """Step: I create empty BigML composite and then add list of sources
    and log results in <output_dir>
    """
    ok_(add_sources is not None and output_dir is not None)
    command = ("bigmler source --sources \"\" --add-sources " + add_sources +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "txt.tmp"))


def remove_sources(step, output_dir=None):
    """Step: I remove the sources from a BigML composite and
    log results in <output_dir>
    """
    ok_(output_dir is not None)
    command = ("bigmler source --source " + world.source["resource"] +
               " --remove-sources " + ",".join(step.sources) +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "txt.tmp"))


def delete_sources(step, output_dir=None):
    """Step: I delete the sources from a BigML composite and
    log results in <output_dir>
    """
    ok_(output_dir is not None)
    command = ("bigmler source --source " + world.source["resource"] +
               " --delete-sources " + ",".join(step.sources) +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "txt.tmp"))


def i_create_annotated_source(
    step, annotations_file=None, images_file=None, output_dir=None):
    """Step: I create  BigML composite for an <annotations_file> and an
    <images_file> and log results in <output_dir>
    """
    ok_(annotations_file is not None and images_file is not None and
        output_dir is not None)
    annotations_file = res_filename(annotations_file)
    images_file = res_filename(images_file)
    command = ("bigmler source --annotations-file " + annotations_file +
               " --data " + images_file +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "txt.tmp"))


def i_create_lang_annotated_source(
    step, annotations_dir=None, images_dir=None,
    annotations_language=None, output_dir=None):
    """Step: I create  BigML composite for a "<annotations_language>"
    <annotations_dir> and an <images_dir> and log results in <output_dir>
    """
    ok_(annotations_dir is not None and images_dir is not None and
        annotations_language is not None and output_dir is not None)
    command = ("bigmler source --annotations-dir " + annotations_dir +
               " --data " + images_dir + " --annotations-language " +
               annotations_language +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "txt.tmp"))


def check_sources_in_composite(step):
    """Step: I check that the sources are in the composite"""
    eq_(step.sources, ["source/%s" % source for source in
                       world.source["object"].get("sources", [])])


def i_check_create_composite(step):
    """Step: I check that the composite has been created"""
    source_file = os.path.join(world.directory, "source")
    message = None
    try:
        last_source = read_sources(source_file)
        source = check_resource(
            last_source.strip(), world.api.get_source)
        if source['resource'] not in world.composites:
            world.composites.append(source['resource'])
        world.source = source
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def check_images_number_in_composite(step, zip_file):
    """Step: I check the number of sources in the composite is
    <images_number>
    """
    sources = []
    zip_file = res_filename(zip_file)
    if os.path.isdir(zip_file):
        sources = filter_by_extension(glob.glob(os.path.join(zip_file, "**"),
                                                recursive=True),
                                      IMAGE_EXTENSIONS)
    else:
        with zipfile.ZipFile(zip_file) as zip_handler:
            sources = filter_by_extension(zip_handler.namelist(),
                IMAGE_EXTENSIONS)
    eq_(len(sources), len(step.sources), msg="Found %s sources in composite."
        " %s expected" % (len(step.sources), len(sources)))


def check_annotation_fields(step, annotations_file):
    """Checks the created label fields"""
    annotations_file = res_filename(annotations_file)
    fields = fields_from_annotations(annotations_file)
    field_labels = labels_from_annotations(annotations_file)
    source_fields = Fields(world.source)
    field_names = list(source_fields.fields_by_name.keys())
    for field in fields:
        ok_(field["name"] in field_names)
        field_labels[field["name"]].sort()
        source_fields.fields[
            source_fields.fields_by_name[
            field["name"]]]["values"].sort()
        eq_(field_labels[field["name"]],
            source_fields.fields[
                source_fields.fields_by_name[
                field["name"]]]["values"])


def i_extract_features(step, extracted_features, output_dir):
    """Updating extracted features from source"""
    extracted_features_str = " --".join(extracted_features)
    if extracted_features_str:
        extracted_features_str = " --" + extracted_features_str
    command = ("bigmler source --source " + world.source["resource"] + " " +
               extracted_features_str +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "txt.tmp"))


def i_check_extracted_features(step, extracted_features):
    """Checking extracted features"""
    message = None
    try:
        extracted = world.source["object"]["image_analysis"][
            "extracted_features"]
        extracted = [TRANSLATED_FEATURES.get(feature, feature) for
            feature in extracted]
        ok_(all(feature in extracted for feature in extracted_features))
    except KeyError as exc:
        message = "Feature not found: %s" % str(exc)
    ok_(message is None, msg=message)


def i_extract_t2_features(step, attr, attr_value, output_dir):
    """Extracting features that involve wavelet subbands or cnns"""
    command = ("bigmler source --source " + world.source["resource"] +
               " --" +  attr + " " + str(attr_value) +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "txt.tmp"))


def i_check_extracted_t2_features(step, attr, attr_value):
    """Checking wavelet extracted features"""
    attr = attr.replace("ws-level", "wavelet_subbands").replace("-", "_")
    message = None
    try:
        value = None
        extracted = world.source["object"]["image_analysis"][
            "extracted_features"]
        for feature in extracted:
            if isinstance(feature, list) and feature[0] == attr:
                value = feature[1]
        eq_(value, attr_value)
    except KeyError as exc:
        message = "Feature not found: %s" % str(exc)
    ok_(message is None, msg=message)
