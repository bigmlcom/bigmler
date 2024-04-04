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

from bigmler.tests.common_steps import shell_execute, base_shell_execute
from bigmler.tests.world import world, res_filename, ok_, eq_


def i_create_all_mlm_resources(
    step, tag=None, label_separator=None, number_of_labels=None, data=None,
    training_separator=None, ml_fields=None, model_fields=None, objective=None,
    test=None, output=None):
    """Step: I create BigML multi-label resources tagged as <tag> with
    <label_separator> label separator and <number_of_labels> labels uploading
    train <data> file with <training_separator> field separator and
    <ml_fields> as multi-label fields using model_fields <model_fields>
    and objective <objective> to test <test> and log predictions in <output>
    """
    ok_(tag is not None and label_separator is not None and
        training_separator is not None and number_of_labels is not None
        and data is not None and test is not None and output is not None
        and model_fields is not None and objective is not None and
        ml_fields is not None)
    world.number_of_models = int(number_of_labels)
    test = res_filename(test)
    command = ("bigmler --multi-label --train " + res_filename(data) +
               " --multi-label-fields " + ml_fields +
               " --label-separator \"" + label_separator +
               "\" --training-separator \"" + training_separator +
               "\" --model-fields \" " + model_fields +
               "\" --test " + test + " --store --output " + output +
               " --objective " + objective +
               " --tag " + tag + " --max-batch-models 1")
    shell_execute(command, output, test=test)


def i_create_all_ml_resources(
    step, tag=None, label_separator=None, number_of_labels=None, data=None,
    training_separator=None, test=None, output=None):
    """Step: I create BigML multi-label resources tagged as <tag> with
    <label_separator> label separator and <number_of_labels> labels uploading
    train <data> file with <training_separator> field separator to test <test>
    and log predictions in <output>
    """
    ok_(tag is not None and label_separator is not None and
        training_separator is not None and number_of_labels is not None and
        data is not None and test is not None and output is not None)
    world.number_of_models = int(number_of_labels)
    test = res_filename(test)
    command = ("bigmler --multi-label --train " + res_filename(data) +
               " --label-separator \"" + label_separator +
               "\" --training-separator \"" + training_separator +
               "\" --test " + test + " --store --output " + output +
               " --tag " + tag + " --max-batch-models 1")
    shell_execute(command, output, test=test)


def i_predict_ml_from_model_tag(step, tag=None, test=None, output=None):
    """Step: I create BigML multi-label resources using models tagged as <tag>
    to test <test> and log predictions in <output>
    """
    ok_(tag is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --multi-label --model-tag " + tag + " --test " +
               test + " --store --output " + output +
               " --max-batch-models 1")
    shell_execute(command, output, test=test)


def i_predict_ml_from_model_tag_with_labels_with_objective(
    step, labels=None, objective=None, tag=None, test=None, output=None):
    """Step: I create BigML multi-label resources with labels <labels>
    and objective <objective> using models tagged as <tag> to test <test>
    and log predictions in <output>
    """
    ok_(tag is not None and labels is not None and test is not None and
        output is not None and objective is not None)
    test = res_filename(test)
    command = ("bigmler --multi-label --model-tag " + tag + " --labels " +
               labels + " --test " + test + " --store --output " + output +
               " --objective " + objective + " --max-batch-models 1")
    shell_execute(command, output, test=test)


def i_predict_ml_from_model_tag_with_labels(
    step, labels=None, tag=None, test=None, output=None):
    """Step: I create BigML multi-label resources with labels <labels>
    using models tagged as <tag> to test <test> and log predictions in
    <output>
    """
    ok_(tag is not None and labels is not None and test is not None and
        output is not None)
    test = res_filename(test)
    command = ("bigmler --multi-label --model-tag " + tag + " --labels " +
               labels + " --test " + test + " --store --output " + output +
               " --max-batch-models 1")
    shell_execute(command, output, test=test)


def i_check_local_file(step, path=None):
    """Step: Then I check the extended file <path> has been created"""
    ok_(path is not None)
    message = None
    try:
        with open(path) as handler:
            world.headers = handler.readline().strip()
            world.first_row = handler.readline().strip()
    except IOError as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_headers_file(step, headers=None):
    """Step: the headers of the local extended file are <headers>"""
    ok_(headers is not None)
    eq_(headers, world.headers, msg="The expected headers are:\n%s\nand the"
        " ones found are:\n%s" % (headers, world.headers))


def i_check_first_row_file(step, first_row=None):
    """Step: the first row of the local extended file is <first_row>"""
    ok_(first_row is not None)
    eq_(first_row, world.first_row, msg=("The expected first row is:\n"
        f"{first_row}\nand the one found is:\n{world.first_row}"))


def i_create_ml_source(
    step, label_separator=None, number_of_labels=None, data=None,
    training_separator=None, multi_label_fields=None, objective=None,
    output_dir=None):
    """Step: I create BigML a multi-label source with <label_separator> label
    separator and <number_of_labels> labels from train <data> file with
    <training_separator> field separator and <multi_label_fields> as
    multi-label fields and objective <objective> and output in <output_dir>
    """
    ok_(label_separator is not None and training_separator is not None and
        number_of_labels is not None and data is not None and
        multi_label_fields is not None and output_dir is not None and
        objective is not None)
    command = ("bigmler --multi-label --train " + res_filename(data) +
               " --label-separator \"" + label_separator +
               "\" --training-separator \"" + training_separator +
               "\" --multi-label-fields " + multi_label_fields +
               " --objective " + objective + " --store --output-dir " +
               output_dir +
               "  --no-dataset --no-model --max-batch-models 1")
    base_shell_execute(command, output_dir)


def i_create_all_ml_resources_and_ensembles(
    step, tag=None, label_separator=None, number_of_labels=None, data=None,
    training_separator=None, number_of_models=None, test=None, output=None):
    """Step: I create BigML multi-label resources tagged as <tag> with
    <label_separator> label separator and <number_of_labels> labels uploading
    train <data> file with <training_separator> field separator and
    <number_of_models> models ensembles to test <test> and log predictions
    in <output>
    """
    ok_(tag is not None and label_separator is not None and
        training_separator is not None and number_of_labels is not None and
        data is not None and test is not None and output is not None and
        number_of_models is not None)
    world.number_of_models = int(number_of_labels) * int(number_of_models)
    test = res_filename(test)
    command = ("bigmler --multi-label --train " + res_filename(data) +
               " --label-separator \"" + label_separator +
               "\" --training-separator \"" + training_separator +
               "\" --test " + test + " --number-of-models " +
               str(number_of_models) + " --store --output " + output +
               " --tag " + tag + " --max-batch-models 1")
    shell_execute(command, output, test=test)


def i_create_resources_and_ensembles_from_source(
    step, multi_label=None, number_of_models=None, test=None, output=None):
    """Step: I create BigML <multi-label> resources using source and
    <number_of_models> models ensembles to test <test> and log predictions
    in <output>
    """
    ok_(test is not None and output is not None and
        number_of_models is not None)
    multi_label = "" if multi_label is None else " --multi-label "
    test = res_filename(test)
    command = ("bigmler "+ multi_label +"--source " +
               world.source['resource'] + " --number-of-models " +
               str(number_of_models) + " --test " + test +
                " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_resources_and_ensembles_from_dataset(
    step, multi_label=None, number_of_models=None, test=None, output=None):
    """Step: I create BigML <multi-label> resources using dataset and
    <number_of_models> models ensembles to test <test> and log predictions
    in <output>
    """
    ok_(test is not None and output is not None)
    multi_label = "" if multi_label is None else " --multi-label "
    test = res_filename(test)
    command = ("bigmler "+ multi_label +"--dataset " +
               world.dataset['resource'] + " --number-of-models " +
               str(number_of_models) + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)
