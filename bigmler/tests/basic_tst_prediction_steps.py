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
import time
import json
import shutil
import traceback

from subprocess import check_call, CalledProcessError

from bigml.api import check_resource

from bigmler.processing.models import MONTECARLO_FACTOR
from bigmler.checkpoint import file_number_of_lines
from bigmler.utils import storage_file_name, open_mode
from bigmler.tests.world import world, res_filename, ok_, eq_
from bigmler.tests.ml_tst_prediction_steps import \
    i_create_all_ml_resources
from bigmler.tests.ml_tst_prediction_steps import \
    i_create_all_ml_resources_and_ensembles
from bigmler.tests.ml_tst_evaluation_steps import \
    i_create_all_ml_resources_for_evaluation
from bigmler.tests.max_categories_tst_prediction_steps import \
    i_check_create_max_categories_datasets, i_create_all_mc_resources
from bigmler.tests.basic_batch_tst_prediction_steps import \
    i_check_create_test_source, i_check_create_test_dataset, \
    i_check_create_batch_prediction
from bigmler.tests.basic_cluster_prediction_steps import \
    i_create_all_cluster_resources, i_check_create_cluster
from bigmler.tests.basic_anomaly_prediction_steps import \
    i_create_all_anomaly_resources, i_check_create_anomaly
from bigmler.tests.ml_tst_prediction_steps import \
    i_create_all_mlm_resources
from bigmler.tests.basic_association_steps import \
    i_create_association, i_check_create_association
from bigmler.tests.basic_logistic_r_steps import \
    i_create_all_lr_resources, i_check_create_lr_model
from bigmler.tests.basic_deepnet_steps import \
    i_create_all_dn_resources, i_check_create_dn_model
from bigmler.tests.basic_pca_steps import \
    i_create_all_pca_resources, i_check_create_pca_model
from bigmler.tests.composite_steps import i_check_create_composite
from bigmler.tests.common_steps import shell_execute, check_debug, \
    base_shell_execute, check_rows_equal
from bigmler.reports import REPORTS_DIR

DECIMAL_PLACES = 3


def i_create_resources_from_ensemble_using_median(
    step, data=None, number_of_models=None, test=None, output=None):
    """Step: I create BigML resources from <data> using ensemble of
    <number_of_models> models to test <test> using median and log predictions
    in <output>
    """
    ok_(data is not None and test is not None and output is not None and
        number_of_models is not None)
    data = res_filename(data)
    test = res_filename(test)
    command = ("bigmler --train " + data + " --test " + test +
               " --store --output " + output +
               " --number-of-models " + number_of_models +
               " --median --max-batch-models 1 --no-fast")
    world.number_of_models = int(number_of_models)
    shell_execute(command, output, test=test)


def i_create_resources_in_prod_from_ensemble(
    step, data=None, number_of_models=None, test=None, output=None):
    """Step: I create BigML resources from <data> using ensemble of
    <number_of_models> models to test <test> and log predictions in <output>
    """
    i_create_resources_in_mode_from_ensemble(
        step, data=data, number_of_models=number_of_models,
        test=test, output=output)


def i_create_resources_in_mode_from_ensemble(
    step, data=None, number_of_models=None, test=None, output=None):
    """Step: I create BigML resources from <data> using ensemble of
    <number_of_models> models to test <test> and log predictions in
    <output>
    """
    ok_(data is not None and test is not None and output is not None and \
        number_of_models is not None)
    data = res_filename(data)
    test = res_filename(test)
    command = ("bigmler --train " + data + " --test " + test +
               " --store --output " + output +
               " --number-of-models " + number_of_models +
               " --max-batch-models 1 --no-fast")
    world.number_of_models = int(number_of_models)
    shell_execute(command, output, test=test)

def i_create_all_resources_with_split_field(step, data=None,
                                            split_field=None,
                                            objective=None,
                                            output_dir=None):
    """Step: I create BigML resources uploading train <data> file with
    split field <split_field> and log in <output_dir>
    """
    ok_(data is not None and split_field is not None
        and objective is not None and output_dir is not None)
    command = ("bigmler --train " + res_filename(data) +
               " --split-field \"" + split_field +
               "\" --objective \"" + objective +
               "\" --store --output-dir " + output_dir +
               " --max-batch-models 1 --no-fast")
    shell_execute(command, "%s/xxx" % output_dir)


def i_create_all_resources_with_focus_field(step, data=None,
                                            focus_field=None,
                                            objective=None,
                                            output_dir=None):
    """Step: I create BigML resources uploading train <data> file with
    focus field <focus_field> and log in <output_dir>
    """
    ok_(data is not None and focus_field is not None
        and objective is not None and output_dir is not None)
    command = ("bigmler --train " + res_filename(data) +
               " --focus-field \"" + focus_field +
               "\" --objective \"" + objective +
               "\" --store --output-dir " + output_dir +
               " --max-batch-models 1 --no-fast")
    shell_execute(command, "%s/xxx" % output_dir)


def i_create_all_resources_with_median(step, data=None,
                                       test=None, output=None):
    """Step: I create BigML resources uploading train <data> file using the
    median to test <test> and log predictions in <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --store --output " + output +
               " --median --max-batch-models 1 --no-fast")
    shell_execute(command, output, test=test)


def i_create_all_resources_batch_to_dataset(step, data=None,
                                            test=None, output_dir=None):
    """Step: I create BigML resources uploading train <data> file to test
    <test> remotely to a dataset with no CSV output and log resources in
    <output_dir>
    """
    ok_(data is not None and test is not None and output_dir is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --store --no-csv --to-dataset --output-dir " +
               output_dir + " --remote")
    shell_execute(command, "%s/x.csv" % output_dir, test=test)


def i_create_source_with_locale(step, data=None, locale=None,
                                field_attributes=None, types=None,
                                output=None):
    """Step: I create a BigML source from file <data> with locale <locale>,
    field attributes <field_attributes> and types file <types> storing
    results in <output>
    """
    ok_(data is not None and locale is not None and output is not None and \
        types is not None and field_attributes is not None)
    field_attributes = res_filename(field_attributes)
    types = res_filename(types)
    command = ("bigmler --train " + res_filename(data) + " --locale " +
               locale + " --field-attributes " + field_attributes +
               " --types " + types + " --output " + output +
               " --no-dataset --no-model --store")
    shell_execute(command, output)


def i_create_composite_source(step, data=None, output=None):
    """Step: I create a BigML source from file <data> storing results in
    <output>
    """
    ok_(data is not None and output is not None)
    command = ("bigmler --train " + res_filename(data) + " --output " + output +
               " --no-dataset --no-model --store")
    shell_execute(command, output)


def i_create_source(step, data=None, output_dir=None):
    """Step: I create a BigML source from file <data> storing results in
    <output_dir>
    """
    ok_(data is not None and output_dir is not None)
    output = os.path.join(output_dir, "tmp.txt")
    command = ("bigmler source --data " + res_filename(data) +
               " --output-dir " + output_dir +
               " --store")
    shell_execute(command, output)


def i_create_all_resources_to_model(step, data=None, output=None):
    """Step: I create BigML resources uploading train <data> file to create
    model and log in <output>
    """
    ok_(data is not None and output is not None)
    command = ("bigmler --train " + res_filename(data) +
               " --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=None)


def i_create_kfold_cross_validation_objective(step, k_folds=None,
                                              objective=None, metric=None):
    """Step: I create BigML feature selection <k_folds>-fold cross-validations
    for <objective> improving <metric>
    """
    ok_(k_folds is not None and metric is not None and objective is not None)
    command = ("bigmler analyze --dataset " +
                             world.dataset['resource'] +
                             " --features --k-folds " + k_folds +
                             " --output " + world.directory +
                             " --optimize " + metric +
                             " --objective " + objective)
    shell_execute(command, os.path.join(world.directory, "tmp"))
    world.output = os.path.join(world.directory, "test", "kfold1",
                                "evaluation")


def i_create_kfold_cross_validation_options(step, k_folds=None, options=None):
    """Step: I create BigML feature selection <k_folds>-fold cross-validation
    with options <options>
    """
    ok_(k_folds is not None and options is not None)
    command = ("bigmler analyze --dataset " +
                             world.dataset['resource'] +
                             " --features --k-folds " + k_folds +
                             " --output " + world.directory +
                             options)
    shell_execute(command, os.path.join(world.directory, "tmp"))
    world.output = os.path.join(world.directory, "test", "kfold1",
                                "evaluation")

def i_create_all_resources_proportional(
    step, data=None, test=None, output=None):
    """Step: I create BigML resources uploading train <data> file to test
    <test> with proportional missing strategy and log predictions in
    <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --missing-strategy proportional" +
               " --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=test)


def i_create_all_resources_missing_splits(
    step, data=None, test=None, output=None):
    """Step: I create BigML resources uploading train <data> file to test
    <test> with a missing-splits model and log predictions in <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --missing-splits" +
               " --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=test)


def i_create_all_resources_remote_proportional(
    step, data=None, test=None, output=None):
    """Step: I create BigML resources uploading train <data> file to test
    <test> remotely with proportional missing strategy and log predictions
    in <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --missing-strategy proportional --remote" +
               " --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=test, options="--no-header")


def i_create_all_resources_remote_missing_splits(
    step, data=None, test=None, output=None):
    """Step: I create BigML resources uploading train <data> file to test
    <test> remotely with a missing-splits model and log predictions in
    <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --missing-splits --remote" +
               " --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=test, options="--no-header")


def i_create_all_resources_with_separator(
    step, data=None, test=None, output=None, separator=None):
    """Step: I create BigML resources uploading train <data> file to test
    <test> and log predictions in <output> with <separator>
    as test field separator
    """
    ok_(data is not None and test is not None and separator is not None and \
        output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --test-separator " + separator + " --store --output " +
               output + " --max-batch-models 1")
    shell_execute(command, output, test=test)


def i_create_all_resources_batch_map(
    step, data=None, test=None, fields_map=None, output=None):
    """Step: I create BigML resources uploading train <data> file to test
    <test> remotely with mapping file <fields_map> and log predictions in
    <output>
    """
    ok_(data is not None and test is not None and output is not None
        and fields_map is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --fields-map "
               + res_filename(fields_map) + " --store --output " + output +
               " --remote")
    shell_execute(command, output, test=test, options="--no-header")


def i_create_all_resources_batch(step, data=None, test=None, output=None):
    """Step: I create BigML resources uploading train <data> file to test
    <test> remotely and log predictions in <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --store --output " + output + " --remote")
    shell_execute(command, output, test=test, options="--no-header")


def i_create_all_resources_with_no_headers(
    step, data=None, test=None, output=None):
    """Step: I create BigML resources uploading train <data> file with no
    headers to test <test> with no headers and log predictions in
    <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --store --output " + output + " --max-batch-models 1 " +
               "--no-fast --no-train-header --no-test-header")
    shell_execute(command, output, test=test, options="--no-header")


def i_create_all_resources(step, data=None, test=None, output=None):
    """Step: I create BigML resources uploading train <data> file to test
    <test> and log predictions in <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --store --output " + output +
               " --max-batch-models 1 --no-fast")
    shell_execute(command, output, test=test)


def i_create_all_resources_with_options(
    step, data=None, test=None, output=None, options=''):
    """Step: I create BigML resources uploading train <data> file to test
    <test> and log predictions in <output> with prediction options
    <options>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --store --output " + output + " --max-batch-models 1 " +
               options.replace("'", "\""))
    shell_execute(command, output, test=test, options=options)


def i_create_resources_from_source_with_objective(
    step, multi_label=None, objective=None, model_fields=None,
    test=None, output=None):
    """Step: I create BigML <multi-label> resources using source with
    objective <objective> and model fields <model_fields> to test
    <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler "+ multi_label +"--source " + world.source['resource']
               + " --objective " + objective + " --model-fields \" "
               + model_fields + "\" --test " + test
               + " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_resources_from_source(
    step, multi_label=None, test=None, output=None):
    """Step: I create BigML <multi-label> resources using source to test
    <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler "+ multi_label +"--source " + world.source['resource']
               + " --test " + test + " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_resources_from_source_batch(step, output=None):
    """Step: I create BigML resources using source to test the previous test
    source remotely and log predictions in <output>
    """
    ok_(output is not None)
    command = ("bigmler --source " + world.source['resource']
               + " --test-source " + world.test_source['resource']
               + " --store --remote --output " + output)
    shell_execute(command, output)


def i_create_resources_from_dataset_with_objective(
    step, multi_label=None, objective=None, model_fields=None,
    test=None, output=None):
    """Step: I create BigML <multi-label> resources using dataset with
    objective <objective> and model fields <model_fields> to test <test>
    and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler "+ multi_label +"--dataset " +
               world.dataset['resource']
               + " --objective " + objective + " --model-fields \" "
               + model_fields + "\" --test " + test
               + " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_resources_from_dataset(
    step, multi_label=None, test=None, output=None):
    """Step: I create BigML <multi-label> resources using dataset to test
    <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    multi_label = "" if multi_label is None else " --multi-label "
    test = res_filename(test)
    command = ("bigmler "+ multi_label +"--dataset " +
               world.dataset['resource'] + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_resources_from_model_batch(step, fields=None, output=None):
    """Step: I create BigML resources using a model to test the previous test
    dataset remotely with prediction headers and fields <fields> and log
    predictions in <output>
    """
    ok_(output is not None and fields is not None)
    command = ("bigmler --model " + world.model['resource'] +
               " --test-dataset " +
               world.test_dataset['resource'] + " --store --remote " +
               "--prediction-header --prediction-info full " +
               "--prediction-fields \"" + fields + "\" --output " + output)
    shell_execute(command, output,
                  test_rows=world.test_dataset['object']['rows'] + 1)


def i_create_resources_from_dataset_batch(step, output=None):
    """Step: I create BigML resources using dataset to test the previous test
    dataset remotely and log predictions in <output>
    """
    ok_(output is not None)
    command = ("bigmler --dataset " + world.dataset['resource'] +
               " --test-dataset " +
               world.test_dataset['resource'] + " --store --remote --output "
               + output)
    shell_execute(command, output,
                  test_rows=world.test_dataset['object']['rows'])


def i_create_resources_from_dataset_objective_model(
    step, objective=None, fields=None, test=None, output=None):
    """Step: I create BigML resources using dataset, objective field
    <objective> and model fields <model_fields> to test <test> and log
    predictions in <output>
    """
    ok_(objective is not None and fields is not None and test is not None
        and output is not None)
    test = res_filename(test)
    command = ("bigmler --dataset " + world.dataset['resource'] +
               " --objective " + objective + " --model-fields " +
               fields + " --test " + test + " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_resources_from_local_model(
    step, directory=None, test=None, output=None):
    """Step: I create BigML resources using local model in <directory> to test
    <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None and directory is not None)
    test = res_filename(test)
    with open(os.path.join(directory, "models")) as model_file:
        model_id = model_file.read().strip()
    command = ("bigmler --model-file " +
               storage_file_name(directory, model_id) +
               " --test " +
               test + " --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=test)


def i_create_resources_from_model(step, test=None, output=None):
    """Step: I create BigML resources using model to test <test> and
    log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --model " + world.model['resource'] + " --test " +
               test + " --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=test)


def i_create_resources_from_model_with_op(step, operating_point=None,
                                          test=None, output=None):
    """Step: I create BigML resources using model with operating point
    <operating_point> to test <test> and log predictions in <output>
    """
    ok_(operating_point is not None and
        test is not None and output is not None)
    test = res_filename(test)
    operating_point = res_filename(operating_point)
    command = ("bigmler --model " + world.model['resource'] + " --test " +
               test + " --operating-point " + operating_point +
               " --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=test)

def i_create_resources_from_ensemble_with_threshold(
    step, test=None, output2=None, output3=None):
    """Step: I create BigML resources using the previous ensemble with
    different thresholds to test <test> and log predictions in <output2> and
    <output3>
    """
    ok_(test is not None and output2 is not None and output3 is not None)
    message = None
    try:
        test = res_filename(test)
        command = ("bigmler --ensemble " + world.ensemble['resource'] +
                   " --test " + test + " --tag my_ensemble --store --output " +
                   output2 + " --method threshold --threshold " +
                   str(world.number_of_models))
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        command = ("bigmler --ensemble " + world.ensemble['resource'] +
                   " --test " + test + " --tag my_ensemble --store --output " +
                   output3 + " --method threshold --threshold 1")
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
    except (OSError, CalledProcessError, IOError) as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_create_resources_from_ensemble_with_threshold_rem(
    step, test=None, output2=None, output3=None, threshold_class=None):
    """Step: I create BigML resources using the previous ensemble with
    different thresholds to test <test> remotely and log predictions in
    <output2> and <output3>
    """
    ok_(test is not None and output2 is not None and output3 is not None
        and threshold_class is not None)
    message = None
    try:
        test = res_filename(test)
        command = ("bigmler --ensemble " + world.ensemble['resource'] +
                   " --test " + test + " --tag my_ensemble --store --output " +
                   output2 + ' --class ' + threshold_class +
                   " --remote --method threshold" +
                   " --threshold " +
                   str(world.number_of_models))
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        command = ("bigmler --ensemble " + world.ensemble['resource'] +
                   " --test " + test + " --tag my_ensemble --store --output " +
                   output3 + ' --class ' + threshold_class +
                   " --remote --method threshold" +
                   " --threshold 1")
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
    except (OSError, CalledProcessError, IOError) as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_create_resources_from_local_ensemble(step, number_of_models=None,
                                           directory=None, test=None,
                                           output=None):
    """Step: I create BigML resources using local ensemble of <number_of_models>
    models in <directory> to test <test> and log predictions in <output>
    """
    ok_(number_of_models is not None and test is not None and
        output is not None and directory is not None)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    message = None
    with open(os.path.join(directory, "ensembles")) as ensemble_file:
        ensemble_id = ensemble_file.read().strip()
    try:
        test = res_filename(test)
        command = ("bigmler --ensemble-file " +
                   storage_file_name(directory, ensemble_id) +
                   " --test " + test + " --store" +
                   " --output " + output)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)

        world.test_lines = file_number_of_lines(test)
        # test file has headers in it, so first line must be ignored
        world.test_lines -= 1
        world.output = output
        world.number_of_models = len(world.ensemble['object']['models'])
    except (OSError, CalledProcessError, IOError) as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_create_resources_from_local_ensemble_with_op(
        step, number_of_models=None,
        directory=None, test=None,
        output=None, operating_point=None):
    """Step: I create BigML resources using local ensemble of
    <number_of_models> models with operating point <operating_point> in
    <idrectory> to test <test> and log predictions in <output>
    """
    ok_(number_of_models is not None and test is not None and
        output is not None and directory is not None and
        operating_point is not None)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    message = None
    with open(os.path.join(directory, "ensembles")) as ensemble_file:
        ensemble_id = ensemble_file.read().strip()
    try:
        test = res_filename(test)
        operating_point = res_filename(operating_point)
        command = ("bigmler --ensemble-file " +
                   storage_file_name(directory, ensemble_id) +
                   " --test " + test + " --store" +
                   " --output " + output + " --operating-point " +
                   operating_point)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)

        world.test_lines = file_number_of_lines(test)
        # test file has headers in it, so first line must be ignored
        world.test_lines -= 1
        world.output = output
        world.number_of_models = len(world.ensemble['object']['models'])
    except (OSError, CalledProcessError, IOError) as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_create_resources_from_ensemble_with_replacement(
    step, number_of_models=None, test=None, output=None):
    """Step: I create BigML resources using ensemble of <number_of_models>
    models with replacement to test <test> and log predictions in
    <output>
    """
    i_create_resources_from_ensemble_generic(step, number_of_models, "",
                                             test, output)


def i_create_resources_from_ensemble(
    step, number_of_models=None, test=None, output=None):
    """Step: I create BigML resources using ensemble of <number_of_models>
    models to test <test> and log predictions in <output>
    """
    i_create_resources_from_ensemble_generic(step, number_of_models,
        " --no-fast --ensemble-sample-no-replacement",
        test, output)


def i_create_resources_from_boosted_ensemble(
    step, iterations=None, test=None, output=None):
    """Step: I create BigML resources using boosted ensemble in
    <iterations> iterations to test <test> and log predictions in <output>
    """
    ok_(iterations is not None and test is not None and
        output is not None)
    test = res_filename(test)
    command = ("bigmler --dataset " + world.dataset['resource'] +
               " --test " + test + " --boosting-iterations " +
               str(iterations) + " --tag my_ensemble --store" +
               " --output " + output)
    shell_execute(command, output, test=test)


def i_create_resources_remotely_from_boosted_ensemble(
    step, iterations=None, test=None, output=None):
    """Step: I create BigML resources using boosted ensemble in <iterations>
    iterations to remotely test <test> and log predictions in <output>
    """
    ok_(iterations is not None and test is not None and \
        output is not None)
    test = res_filename(test)
    command = ("bigmler --dataset " + world.dataset['resource'] +
               " --test " + test + " --boosting-iterations " +
               str(iterations) + " --remote --tag my_ensemble --store" +
               " --output " + output + " --to-csv")
    shell_execute(command, output, test=test, options="--no-header")


def i_create_resources_from_ensemble_generic(step, number_of_models=None,
    no_replacement="", test=None, output=None):
    """Creating bagging ensemble with or withour replacement"""
    ok_(number_of_models is not None and test is not None and \
        output is not None)
    test = res_filename(test)
    command = ("bigmler --dataset " + world.dataset['resource'] +
               " --test " + test + " --number-of-models " +
               str(number_of_models) + " --tag my_ensemble --store" +
               " --output " + output + no_replacement)
    shell_execute(command, output, test=test)


def i_create_resources_from_models_file_with_objective(
    step, multi_label=None, models_file=None, objective=None,
    test=None, output=None):
    """Step: I create BigML <multi-label> resources using models in file
    <models_file> with objective <objective> to test <test> and log
    predictions in <output>
    """
    ok_(models_file is not None and test is not None and output is not None
        and objective is not None)
    test = res_filename(test)
    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler "+ multi_label +"--models " + models_file + " --test "
               + test + " --store --output " + output
               + " --objective " + objective)
    shell_execute(command, output, test=test)


def i_create_resources_from_models_file(
    step, multi_label=None, models_file=None, test=None, output=None):
    """Step: I create BigML <multi-label> resources using models in file
    <models_file> to test <test> and log predictions in <output>
    """
    ok_(models_file is not None and test is not None and output is not None)
    test = res_filename(test)
    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler "+ multi_label +"--models " + models_file + " --test "
               + test + " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_resources_from_dataset_file(
    step, dataset_file=None, test=None, output=None):
    """Step: I create BigML resources using dataset in file <dataset_file>
    to test <test> and log predictions in <output>
    """
    ok_(dataset_file is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --datasets " + dataset_file + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_cross_validation_from_dataset(
    step, rate=None, dataset_file=None, output=None):
    """Step: I create a BigML cross-validation with rate <rate> using the
    # dataset in file <dateset_file> and log results in <output>
    """
    ok_(rate is not None and output is not None and dataset_file is not None)
    with open(dataset_file, "r") as handler:
        dataset_id = handler.readline().strip()
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    world.number_of_models = int(MONTECARLO_FACTOR * float(rate))
    world.number_of_evaluations = world.number_of_models
    message = None
    try:
        command = ("bigmler --dataset " + dataset_id +
                   " --cross-validation-rate " + rate + " --store --output "
                   + output)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        world.output = output
    except (OSError, CalledProcessError, IOError) as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_find_predictions_files(
    step, directory1=None, directory2=None, output=None):
    """Step: I combine BigML predictions files in <directory1> and <directory2>
    into <output>
    """
    ok_(directory1 is not None and directory2 is not None and
        output is not None)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    message = None
    try:
        command = ("bigmler --combine-votes " + directory1 + "," + directory2 +
                   " --store --output " + output)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        world.test_lines = file_number_of_lines(
            os.path.join(directory1, "predictions.csv"))
        world.output = output
    except (OSError, CalledProcessError, IOError) as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_find_predictions_files_with_method(
    step, directory1=None, directory2=None, output=None, method=None):
    """Step: I combine BigML predictions files in <directory1> and
    <directory2> into <output> with method <method>
    """
    ok_(directory1 is not None and directory2 is not None and
        output is not None and method is not None)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    message = None
    try:
        command = ("bigmler --combine-votes " + directory1 + "," + directory2 +
                   " --store --output " + output + " --method " + method)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        world.test_lines = file_number_of_lines(
            os.path.join(directory1, "predictions.csv"))
        world.output = output
    except (OSError, CalledProcessError, IOError) as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_create_balanced_model(step, data=None, output_dir=None):
    """Step: I create a BigML balanced model from <data> and store logs in
    <output_dir>
    """
    ok_(data is not None and output_dir is not None)
    if not data.startswith("https"):
        data = res_filename(data)
    command = ("bigmler --train " + data + " --balance " +
               " --store --output-dir " + output_dir)
    base_shell_execute(command, output_dir)


def i_create_balanced_model_from_sample(step, data=None, output_dir=None):
    """Step: I create a BigML balanced model from <data> sampling 50% and store
    logs in <output_dir>
    """
    ok_(data is not None and output_dir is not None)
    if not data.startswith("https"):
        data = res_filename(data)
    command = ("bigmler --train " + data +
               " --store --no-model --output-dir " + output_dir)
    base_shell_execute(command, output_dir)
    command = ("bigmler --datasets " + output_dir + "/dataset" +
               " --store --to-dataset --sample-rate 0.5 --no-model "+
               " --output-dir " +
               output_dir)
    base_shell_execute(command, output_dir)

    command = ("bigmler --datasets " + output_dir + "/dataset_gen" +
               " --store --balance  --output-dir " +
               output_dir)
    base_shell_execute(command, output_dir)


def i_create_weighted_field_model(
    step, data=None, field=None, output_dir=None, objective=None):
    """Step: I create a BigML field weighted model from <data> using field
    <field> as weight and store logs in <objective>
    """
    ok_(data is not None and field is not None and output_dir is not None and
        objective is not None)
    command = ("bigmler --train " + res_filename(data) +
               " --weight-field " + field + " --objective " + objective +
               " --store --output-dir " + output_dir)
    base_shell_execute(command, output_dir)


def i_create_objective_weighted_model(
    step, data=None, path=None, output_dir=None):
    """Step: I create a BigML objective weighted model from <data> using the
    objective weights in file <path> and store logs in <output_dir>
    """
    ok_(data is not None and path is not None and output_dir is not None)
    command = ("bigmler --train " + res_filename(data) +
               " --objective-weights " + res_filename(path) +
               " --store --output-dir " + output_dir)
    base_shell_execute(command, output_dir)


def i_retrain_model(step, data=None, output_dir=None):
    """Step: I retrain the model from <data> and store logs in <output>"""
    ok_(data is not None and output_dir is not None)
    world.origin_model = world.model
    if not data.startswith("https"):
        data = res_filename(data)
    command = ("bigmler retrain --add " + data +
               " --id " + world.model['resource'] +
               " --store --output-dir " + output_dir)
    base_shell_execute(command, output_dir)


def i_create_source_from_connector(step, data=None, output_dir=None,
                                   query=None):
    """Step: I create source from external connector"""
    ok_(data is not None and output_dir is not None and query is not None)
    connector_id = world.external_connector["resource"].replace(
        "externalconnector/", "")
    with open(data, 'w+') as file_handler:
        json.dump({"source": "postgresql",
                   "externalconnector_id": connector_id,
                   "query": query}, file_handler)
    command = ("bigmler --train " + os.path.abspath(data) +
               " --store --no-dataset --output-dir " + output_dir)
    base_shell_execute(command, output_dir)


def i_check_create_source(step):
    """Step: I check that the source has been created"""
    source_file = os.path.join(world.directory, "source")
    message = None
    try:
        with open(source_file) as handler:
            source = check_resource(
                handler.readline().strip(), world.api.get_source)
            if source['resource'] not in world.sources:
                world.sources.append(source['resource'])
            world.source = source
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_model_double(step):
    """Step: I check that the model has doubled its rows"""
    ok_(world.model['object']['rows'] == \
        2 * world.origin_model['object']['rows'])


def i_check_create_dataset(step, suffix=None):
    """Step: I check that the <test|train> dataset has been created"""
    suffix = "" if suffix is None else "_%s" % suffix[:-1]
    dataset_file = os.path.join(world.directory, f"dataset{suffix}")
    message = None
    try:
        with open(dataset_file) as handler:
            for dataset_id in handler:
                dataset_id = dataset_id.strip()
                dataset = check_resource(dataset_id,
                                         world.api.get_dataset)
                assert (not 'user_metadata' in dataset['object'] or
                        not 'max_categories'
                        in dataset['object']['user_metadata'])
                if dataset['resource'] not in world.datasets:
                    world.datasets.append(dataset['resource'])
                world.dataset = dataset
    except Exception:
        message = traceback.format_exc()
    ok_(message is None, msg=message)


def i_check_create_new_dataset(step):
    """Step: I check that the new dataset has been created"""
    dataset_file = os.path.join(world.directory, "dataset_gen")
    message = None
    try:
        with open(dataset_file) as handler:
            dataset_id = handler.readline().strip()
            dataset = check_resource(dataset_id,
                                     world.api.get_dataset)
            world.datasets.append(dataset['resource'])
            world.dataset = dataset
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_dataset_shared(step):
    """Step: I check that the dataset has been created and shared"""
    i_check_create_dataset(step)
    assert world.dataset['object']['shared']


def i_check_create_model(step):
    """Step: I check that the model has been created"""
    model_file = os.path.join(world.directory, "models")
    message = None
    try:
        with open(model_file) as handler:
            model = check_resource(handler.readline().strip(),
                                   world.api.get_model)
            world.models.append(model['resource'])
            world.model = model
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_model_in_execution(step):
    """Step: I check that the model has been created in the execution"""
    output_resources = world.execution[
        "object"]["execution"]["output_resources"]
    for resource in output_resources:
        try:
            model = check_resource(resource["id"],
                                   world.api.get_model)
            if model is not None:
                world.models.append(model['resource'])
                world.model = model
                break
        except Exception:
            continue


def i_check_create_kfold_models(step, kfolds):
    """Step: I check that the <kfolds>-models have been created"""
    directory = os.path.dirname(os.path.dirname(world.output))
    directories = [os.path.join(directory, folder)
                   for folder in os.listdir(directory) if
                   os.path.isdir(os.path.join(directory, folder))]

    for directory in directories:
        if not directory.endswith("_pred"):
            model_file = os.path.join(directory, "models")
            try:
                with open(model_file) as models_file:
                    models_list = list(map(str.strip, models_file.readlines()))
                world.models.extend(models_list)
                world.model = models_list[-1]
                eq_(int(kfolds), len(models_list))
            except Exception as exc:
                ok_(False, msg=str(exc))


def i_check_create_kfold_ensembles(step, kfolds):
    """Step: I check that the <kfolds>-ensembles have been created"""
    directory = os.path.dirname(os.path.dirname(world.output))
    directories = [os.path.join(directory, folder)
                   for folder in os.listdir(directory) if
                   os.path.isdir(os.path.join(directory, folder))]
    for directory in directories:
        if not directory.endswith("_pred"):
            model_file = os.path.join(directory, "ensembles")
            try:
                with open(model_file) as models_file:
                    models_list = list(map(str.strip, models_file.readlines()))
                world.ensembles.extend(models_list)
                world.ensemble = models_list[-1]
                eq_(int(kfolds), len(models_list))
            except Exception as exc:
                ok_(False, msg=str(exc))


def i_check_create_model_shared(step):
    """Step: I check that the model has been created and shared"""
    i_check_create_model(step)
    ok_(world.model['object']['shared'])


def i_check_model_is_balanced(step):
    """Step: I check that the model is balanced"""
    assert ('balance_objective' in world.model['object'] and
            world.model['object']['balance_objective'])


def i_check_weighted_model(step, field=None):
    """Step: I check that the model uses as weight <field>"""
    ok_(field is not None, msg="No field provided")
    ok_('weight_field' in world.model['object'] and
        world.model['object']['weight_field'] == field)


def i_check_first_node_children(step, children=None, field=None):
    """Step: I check that the first node has <children> branches"""
    ok_(children is not None and field is not None)
    root_children = world.model['object'] and \
        len(world.model['object']['model']['root']['children'])
    root_field = world.model['object']['model']['root'][
        'children'][0]['predicate']['field']
    eq_(root_children, children)
    eq_(root_field, field)


def i_check_objective_weighted_model(step, weights=None):
    """Step: check that the model uses as objective weights <weights>"""
    ok_(weights is not None)
    ok_('objective_weights' in world.model['object'] and
        world.model['object']['objective_weights'] == json.loads(weights))


def i_check_create_ensemble(step):
    """Step: I check that the ensemble has been created"""
    ensemble_file = os.path.join(world.directory, "ensembles")
    message = None
    try:
        with open(ensemble_file) as handler:
            ensemble = check_resource(handler.readline().strip(),
                                      world.api.get_ensemble)
            world.ensembles.append(ensemble['resource'])
            world.ensemble = ensemble
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_models(step):
    """Step: I check that the models have been created"""
    i_check_create_models_in_ensembles(step, False)


def i_check_create_models_in_ensembles(step, in_ensemble=True):
    """Step: I check that the models in the ensembles have been created"""
    model_file = os.path.join(world.directory, "models")
    number_of_lines = 0
    count = 0
    message = None
    while world.number_of_models != number_of_lines and count < 10:
        number_of_lines = 0
        model_ids = []
        with open(model_file) as handler:
            for line in handler:
                number_of_lines += 1
                model_id = line.strip()
                model_ids.append(model_id)
            if world.number_of_models != number_of_lines:
                time.sleep(10)
                count += 1
    eq_(world.number_of_models, number_of_lines,
        msg="number of models %s and number of lines in models file %s: %s" % \
            (world.number_of_models, model_file, number_of_lines))
    world.model_ids = model_ids
    for model_id in model_ids:
        try:
            model = check_resource(model_id, world.api.get_model)
            if in_ensemble:
                ensemble_id = "ensemble/%s" % model['object']['ensemble_id']
                if not ensemble_id in world.ensembles:
                    world.ensembles.append(ensemble_id)
            else:
                world.models.append(model_id)
        except Exception as exc:
            message = str(exc)
            break
    ok_(message is None, msg=message)


def i_check_create_evaluation(step):
    """Step: I check that the evaluation has been created"""
    evaluation_file = os.path.join(world.directory, "evaluations")
    message = None
    try:
        with open(evaluation_file) as handler:
            evaluation = check_resource(handler.readline().strip(),
                                        world.api.get_evaluation)
            world.evaluations.append(evaluation['resource'])
            world.evaluation = evaluation
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def check_create_kfold_cross_validation(step, kfolds, directory):
    """Checking that all evaluations in a cross-validation are created"""
    evaluations_file = os.path.join(directory, "evaluations")
    message = None
    try:
        with open(evaluations_file, "r") as evaluations_file:
            evaluations_list = list(
                map(str.strip, evaluations_file.readlines()))
        world.evaluations.extend(evaluations_list)
        world.evaluation = evaluations_list[-1]
        eq_(int(kfolds), len(evaluations_list))
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_all_kfold_cross_validations(step, kfolds):
    """Step: I check that all the kfolds-fold cross-validations have been
    created
    """
    directory = os.path.dirname(os.path.dirname(world.output))
    directories = [os.path.join(directory, folder)
                   for folder in os.listdir(directory) if
                   os.path.isdir(os.path.join(directory, folder))]
    for directory in directories:
        if not directory.endswith("_pred"):
            check_create_kfold_cross_validation(step, kfolds, directory)


def i_check_create_kfold_cross_validation(step, kfolds):
    """Step: I check that the <kfolds>-fold cross-validation has been created
    """
    check_create_kfold_cross_validation(step, kfolds,
                                        os.path.dirname(world.output))


def i_check_create_kfold_datasets(step, kfolds):
    """Step: I check that the <kfolds>-datasets have been created"""
    datasets_file = os.path.join(os.path.dirname(
        os.path.dirname(world.output)), "dataset_gen")
    message = None
    try:
        with open(datasets_file) as handler:
            datasets_list = list(map(str.strip, handler.readlines()))
        world.datasets.extend(datasets_list)
        world.dataset = datasets_list[-1]
        eq_(int(kfolds), len(datasets_list))
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_feature_selection(step, selection, metric, metric_value):
    """Step: the best feature selection is <selection>, with <metric> of
    <metric_value>
    """
    ok_(selection is not None and metric is not None and \
        metric_value is not None)
    sessions_file = os.path.join(world.directory, "bigmler_sessions")
    message = None
    try:
        with open(sessions_file, open_mode("r")) as sessions_file:
            content = sessions_file.read()
        text = "The best feature subset is: %s \n%s = %s" % (
            selection, metric.capitalize(), metric_value)
        ok_(content.find(text) > -1)
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_node_threshold(step, node_threshold, metric, metric_value):
    """Step: the best node threshold is <node_threshold>, with <metric>
    of <metric_value>
    """
    ok_(node_threshold is not None and metric is not None and \
        metric_value is not None)
    sessions_file = os.path.join(world.directory, "bigmler_sessions")
    message = None
    try:
        with open(sessions_file, open_mode("r")) as handler:
            content = handler.read()
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)
    text = "The best node threshold is: %s \n%s = %s" % (
        node_threshold, metric.capitalize(), metric_value)
    ok_(content.find(text) > -1)


def i_check_create_evaluation_shared(step):
    """Step: I check that the evaluation has been created and shared"""
    i_check_create_evaluation(step)
    ok_(world.evaluation['object']['shared'])


def i_check_gazibit_reports(step, shared=''):
    """Step I check that the Gazibit (shared )?report has been created"""
    shared = "_%s" % shared[0: -1] if shared is not None else ''
    gazibit_file = os.path.join(world.directory,"reports", "gazibit%s.json" %
        shared)
    message = None
    try:
        with open(gazibit_file) as handler:
            content = handler.read()
        ok_(content.find('%START_BIGML_') < 0 and
            content.find('%END_BIGML_') < 0 and
            content.find('%BIGML_') < 0)
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_evaluations(step, number_of_evaluations=None):
    """Step: I check that the <number_of_evaluations> evaluations
    have been created
    """
    if number_of_evaluations is not None:
        world.number_of_evaluations = int(number_of_evaluations)
    evaluations_file = os.path.join(world.directory, "evaluations")
    evaluation_ids = []
    number_of_lines = 0
    count = 0
    message = None
    while world.number_of_evaluations != number_of_lines and count < 10:
        number_of_lines = 0
        with open(evaluations_file) as handler:
            for line in handler:
                number_of_lines += 1
                evaluation_id = line.strip()
                evaluation_ids.append(evaluation_id)
        if world.number_of_evaluations != number_of_lines:
            time.sleep(10)
            count += 1
    eq_(world.number_of_evaluations, number_of_lines,
        msg="number of evaluations %s and number of lines in"
            " evaluations file %s: %s" % (
            world.number_of_evaluations, evaluations_file, number_of_lines))
    world.evaluation_ids = evaluation_ids
    for evaluation_id in evaluation_ids:
        try:
            check_resource(evaluation_id, world.api.get_evaluation)
            world.evaluations.append(evaluation_id)
        except Exception as exc:
            message = str(exc)
            break
    ok_(message is None, msg=message)


def i_check_create_predictions(step):
    """Step: I check that the predictions are ready"""
    predictions_lines = file_number_of_lines(world.output)
    eq_(predictions_lines, world.test_lines)


def i_check_create_projections(step):
    """Step: I check that the projections are ready"""
    i_check_create_predictions(step)


def i_check_predictions_file(step, predictions_file, check_file):
    """Step: the predictions file <predictions_file> is like <check_file>"""
    world.output = predictions_file
    i_check_predictions(step, check_file)


def i_check_predictions(step, check_file, headers=False):
    """Step: the local prediction file is like <check_file>"""
    check_file_path = res_filename(check_file)
    predictions_file_path = world.output
    message = None
    try:
        message = check_rows_equal(predictions_file_path,
            check_file_path)
        if message is not None:
            shutil.copyfile(predictions_file_path, "%s.new" % check_file_path)
    except Exception:
        shutil.copyfile(predictions_file_path, "%s.new" % check_file_path)
        message = traceback.format_exc()
    ok_(message is None, msg=message)


def i_check_projections(step, check_file):
    """Checking that projections have been created"""
    i_check_predictions(step, check_file)


def i_check_predictions_with_different_thresholds(step, output2, output3):
    """Step: local predictions for different thresholds in <output2>
    and <output3> are different
    """
    try:
        with open(output2) as handler2:
            predictions_file = handler2.read()
        with open(output3) as handler3:
            predictions_file_k = handler3.read()
        ok_(predictions_file != predictions_file_k)
    except Exception as exc:
        ok_(False, msg=str(exc))


def i_check_cross_validation(step, check_file):
    """Step: the cross-validation json model info is like the one in
    <check_file>
    """
    check_file = res_filename(check_file)
    cv_file = os.path.join(world.directory, "cross_validation.json")
    try:
        with open(cv_file) as cv_handler:
            cv_content = json.loads(cv_handler.read())
        with open(check_file) as check_handler:
            check_content = json.loads(check_handler.read())
    except Exception as exc:
        ok_(False, msg=str(exc))
    eq_(cv_content['model'], check_content['model'])


def i_check_stored_source(step):
    """Step: I check that the stored source file exists"""
    source_file = os.path.join(world.directory, "source")
    message = None
    try:
        with open(source_file) as handler:
            source_id = handler.readline().strip()
            world.sources.append(source_id)
        storage_source_file = os.path.join(
            world.directory, source_id.replace("/", "_"))
        if os.path.exists(storage_source_file):
            with open(storage_source_file) as handler:
                world.source = json.loads(handler.read().strip())
        else:
            ok_(False)
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_source_locale(step, bigml_locale):
    """Step: And the locale of the source is <bigml_locale>"""
    try:
        locale = world.source['object']["source_parser"]["locale"]
        eq_(bigml_locale, locale)
    except KeyError as exc:
        ok_(False, msg=str(exc))


def i_check_source_type(step, field_id, field_type):
    """Step: the type of field <field_id> is <field_type>"""
    try:
        source_type = world.source['object']["fields"][field_id]['optype']
        eq_(source_type, field_type)
    except KeyError as exc:
        ok_(False, msg=str(exc))


def i_check_source_label(step, field_id, field_label):
    """Step: the label of field <field_id> is <field_label>"""
    try:
        label = world.source['object']["fields"][field_id]['label']
        eq_(label, field_label)
    except KeyError as exc:
        ok_(False, msg=str(exc))

def check_source_exists(step, exists=True):
    """Step: I check that the source exists"""
    source = world.api.get_source(step.source)
    eq_(world.api.ok(source), exists)


def i_create_all_resources_to_evaluate(step, data=None, output=None):
    """Step: I create BigML resources uploading train <data> file to evaluate
    and log evaluation in <output>
    """
    ok_(data is not None and output is not None)
    command = "bigmler --evaluate --train " + res_filename(data) + \
              " --store --output " + output
    shell_execute(command, output)


def i_create_all_resources_to_evaluate_and_report(
    step, data=None, output=None):
    """Step: I create BigML resources and share them uploading train <data>
    file to evaluate and log evaluation and reports in <output>
    """
    ok_(data is not None and output is not None)
    command = ("bigmler --evaluate --shared --report gazibit" +
               " --train " + res_filename(data) +
               " --store --no-upload --output " + output)
    shell_execute(command, output)

def i_create_all_resources_to_evaluate_and_share(step, data=None, output=None):
    """Step: I create BigML resources and share them uploading train <data>
    file to evaluate and log evaluation in <output>
    """
    ok_(data is not None and output is not None)
    command = ("bigmler --evaluate --shared --train " + res_filename(data) +
               " --store --output " + output)
    command = check_debug(command)
    shell_execute(command, output)

def i_create_dataset_with_attributes(
    step, data=None, attributes=None, output=None):
    """Step: I create BigML dataset uploading train <data> file with attributes
    <attributes> in <output>
    """
    ok_(data is not None and output is not None and attributes is not None)
    command = ("bigmler --train " + res_filename(data) +
               " --source-attributes " + res_filename(attributes) +
               " --no-model --store --output " + output)
    shell_execute(command, output)

def i_create_dataset(step, data=None, output=None):
    """Step: I create BigML dataset uploading train <data> file in <output>"""
    ok_(data is not None and output is not None)
    command = ("bigmler --train " + res_filename(data) +
               " --no-model --store --output " + output)
    shell_execute(command, output)


def i_create_kfold_cross_validation(step, k_folds=None):
    """Step: I create BigML <k_folds>-fold cross-validation"""
    ok_(k_folds is not None)
    output = os.path.abspath(
        os.path.join(world.directory, "test", "k_fold0", "evaluation"))
    command = ("bigmler analyze --dataset " +
               world.dataset['resource'] +
               " --cross-validation --k-folds " + k_folds +
               " --output " + world.directory)
    base_shell_execute(command, os.path.join(world.directory, "tmp"))
    world.output = output

def i_create_nodes_analysis(step, min_nodes=None, max_nodes=None,
                            nodes_step=None, k_fold=None, metric=None):
    """Step: I create BigML nodes analysis from <min_nodes> to
    <max_nodes> by <nodes_step> with <k_fold>-cross-validation
    improving <metric>
    """
    ok_(max_nodes is not None and \
        nodes_step is not None and k_fold is not None and \
        metric is not None)
    output = os.path.abspath(
        os.path.join(world.directory, "test", "k_fold0", "evaluation"))
    command = ("bigmler analyze --dataset " + world.dataset['resource'] +
               " --nodes --min-nodes " + min_nodes +
               " --max-nodes " + max_nodes +
               " --nodes-step " + nodes_step +
               " --k-folds " + k_fold +
               " --output " + world.directory +
               " --optimize " + metric)
    base_shell_execute(command, world.directory)
    world.output = output


def i_create_nodes_analysis_from_dataset_file(
    step, min_nodes=None, max_nodes=None,
    nodes_step=None, k_fold=None, metric=None):
    """Step: I create BigML nodes analysis from datasets file from <min_nodes>
    to <max_nodes> by <nodes_step> with <k_fold>-cross-validation improving
    <metric>
    """
    ok_(max_nodes is not None and \
        nodes_step is not None and k_fold is not None and \
        metric is not None)
    output = os.path.abspath(
        os.path.join(world.directory, "test", "k_fold1", "evaluation"))
    command = ("bigmler analyze --datasets %s/dataset" % world.directory +
               " --nodes --min-nodes " + min_nodes +
               " --max-nodes " + max_nodes +
               " --nodes-step " + nodes_step +
               " --k-folds " + k_fold +
               " --output " + world.directory +
               " --optimize " + metric)
    base_shell_execute(command, world.directory)
    world.output = output


def i_create_kfold_cross_validation_separator_metric_no_fields(
    step, k_folds=None, features=None, args_separator=None, metric=None):
    """Step: I create BigML feature selection <k_folds>-fold cross-validations
    excluding <features> with separator <args_separator> improving
    <metric>
    """
    ok_(k_folds is not None and metric is not None and features is not None
        and args_separator is not None)
    output = os.path.abspath(
        os.path.join(world.directory, "test", "k_fold1", "evaluation"))
    command = ("bigmler analyze --dataset " +
               world.dataset['resource'] +
               " --features --k-folds " + k_folds +
               " --output " + world.directory +
               " --exclude-features \"" + features + "\"" +
               " --args-separator " + args_separator +
               " --optimize " + metric)
    shell_execute(command, os.path.join(world.directory, "tmp"))
    world.output = output


def i_create_kfold_cross_validation_metric_category(
    step, k_folds=None, metric=None, category=None):
    """Step: I create BigML feature selection <k_folds>-fold cross-validations
    improving <metric> for category <category>
    """
    ok_(k_folds is not None and metric is not None and category is not None)
    output = os.path.abspath(
        os.path.join(world.directory, "test", "k_fold1", "evaluation"))
    command = ("bigmler analyze --dataset " +
               world.dataset['resource'] +
               " --features --k-folds " + k_folds +
               " --output " + world.directory +
               " --optimize " + metric +
               " --optimize-category " + category)
    shell_execute(command, os.path.join(world.directory, "tmp"))
    world.output = output


def i_create_kfold_cross_validation_metric(step, k_folds=None, metric=None):
    """Step: I create BigML feature selection <k_folds>-fold cross-validations
    improving <metric>
    """
    output = os.path.abspath(
        os.path.join(world.directory, "test", "k_fold1", "evaluation"))
    ok_(k_folds is not None and metric is not None)
    command = ("bigmler analyze --dataset " +
               world.dataset['resource'] +
               " --features --k-folds " + k_folds +
               " --output " + world.directory +
               " --optimize " + metric)
    shell_execute(command, os.path.join(world.directory, "tmp"))
    world.output = output


def i_generate_report(step):
    """Step: I generate a report from the output directory"""
    output = os.path.abspath(
        os.path.join(world.directory, "test", "k_fold1", "evaluation"))
    command = ("bigmler report --no-server --from-dir " +
               world.directory)
    shell_execute(command, os.path.join(world.directory, "tmp"))
    world.output = output


def is_symlink(step):
    """Step: a symlink file is generated in the reports directory"""
    resource_file = os.path.join(world.directory, REPORTS_DIR, "symlink")
    try:
        with open(resource_file, open_mode("r")) as resource_handler:
            ok_(resource_handler)
    except IOError as exc:
        ok_(False, msg=str(exc))


def retrieve_resource(scenario_path, resource_id):
    """Builds a resource from the contents of its local file

    """
    resource_file = os.path.join(scenario_path, resource_id.replace("/", "_"))
    with open(resource_file, open_mode("r")) as resource_handler:
        return json.loads(resource_handler.read())


def retrieve_resources(scenario_path, step):
    """Retrieves the resource ids and objects from the scenario path

    """
    try:
        with open(os.path.join(scenario_path, "source"), open_mode("r")) as \
                source_id_file:
            source_id = source_id_file.readline().strip()
            world.source = retrieve_resource(scenario_path, source_id)
    except Exception:
        pass
    try:
        with open(os.path.join(scenario_path, "dataset"), open_mode("r")) as \
                dataset_id_file:
            dataset_id = dataset_id_file.readline().strip()
            world.dataset = retrieve_resource(scenario_path, dataset_id)
    except Exception:
        pass
    try:
        with open(os.path.join(scenario_path, "source_test"), open_mode("r")) \
                as source_id_file:
            source_id = source_id_file.readline().strip()
            world.test_source = retrieve_resource(scenario_path, source_id)
    except Exception:
        pass
    try:
        with open(os.path.join(scenario_path, "dataset_test"),
                  open_mode("r")) as dataset_id_file:
            dataset_id = dataset_id_file.readline().strip()
            world.test_dataset = retrieve_resource(scenario_path, dataset_id)
    except Exception:
        pass
    try:
        with open(os.path.join(scenario_path, "models"), open_mode("r")) \
            as model_id_file:
            model_id = model_id_file.readline().strip()
            world.model = retrieve_resource(scenario_path, model_id)
    except Exception:
        pass
    try:
        with open(os.path.join(scenario_path, "deepnets"), open_mode("r")) \
            as model_id_file:
            model_id = model_id_file.readline().strip()
            world.deepnet = retrieve_resource(scenario_path, model_id)
    except Exception:
        pass
    try:
        with open(os.path.join(scenario_path, "logistic_regressions"),
                  open_mode("r")) as model_id_file:
            model_id = model_id_file.readline().strip()
            world.logistic_regression = retrieve_resource(scenario_path,
                                                          model_id)
    except Exception:
        pass
    try:
        with open(os.path.join(scenario_path, "linear_regressions"),
                  open_mode("r")) as model_id_file:
            model_id = model_id_file.readline().strip()
            world.linear_regression = retrieve_resource(scenario_path,
                                                        model_id)
    except Exception:
        pass


def i_have_previous_scenario_or_reproduce_it(step, scenario, kwargs):
    """Step: I have previously executed <scenario> or reproduce it with
    arguments <kwargs>
    """
    scenarios = {'scenario1': [(i_create_all_resources, True),
                               (i_check_create_source, False),
                               (i_check_create_dataset, False),
                               (i_check_create_model, False)],
                 'scenario1_img_dn': [(i_create_composite_source, True),
                                      (i_check_create_composite, False)],
                 'scenario1_r': [(i_create_all_resources, True),
                                 (i_check_create_source, False),
                                 (i_check_create_dataset, False),
                                 (i_check_create_model, False)],
                 'scenario5': [(i_create_resources_from_ensemble, True),
                               (i_check_create_ensemble, False)],
                 'scenario_e1': [(i_create_all_resources_to_evaluate, True),
                                 (i_check_create_source, False),
                                 (i_check_create_dataset, False),
                                 (i_check_create_model, False),
                                 (i_check_create_evaluation, False)],
                 'scenario_ml_1': [(i_create_all_ml_resources, True),
                                   (i_check_create_source, False),
                                   (i_check_create_dataset, False),
                                   (i_check_create_models, False)],
                 'scenario_ml_6': [(i_create_all_ml_resources, True),
                                   (i_check_create_source, False),
                                   (i_check_create_dataset, False),
                                   (i_check_create_models, False)],
                 'scenario_mle_1': [(i_create_all_ml_resources_and_ensembles,
                                     True),
                                    (i_check_create_source, False),
                                    (i_check_create_dataset, False),
                                    (i_check_create_models_in_ensembles,
                                     False)],
                 'scenario_ml_e1': [(i_create_all_ml_resources_for_evaluation,
                                     True),
                                    (i_check_create_source, False),
                                    (i_check_create_dataset, False),
                                    (i_check_create_models, False)],
                 'scenario_mc_1': [(i_create_all_mc_resources, True),
                                   (i_check_create_source, False),
                                   (i_check_create_dataset, False),
                                   (i_check_create_max_categories_datasets,
                                    False),
                                   (i_check_create_models, False)],
                 'scenario_r1': [(i_create_all_resources_batch, True),
                                 (i_check_create_source, False),
                                 (i_check_create_dataset, False),
                                 (i_check_create_model, False),
                                 (i_check_create_test_source, False),
                                 (i_check_create_test_dataset, False),
                                 (i_check_create_batch_prediction, False)],
                 'scenario_mlm_1': [(i_create_all_mlm_resources, True),
                                    (i_check_create_source, False),
                                    (i_check_create_dataset, False),
                                    (i_check_create_models, False)],
                'scenario_c_1': [(i_create_all_cluster_resources, True),
                                 (i_check_create_source, False),
                                 (i_check_create_dataset, False),
                                 (i_check_create_cluster, False)],
                'scenario_an_1': [(i_create_all_anomaly_resources, True),
                                  (i_check_create_source, False),
                                  (i_check_create_dataset, False),
                                  (i_check_create_anomaly, False)],
                'scenario_ass_1': [(i_create_association, True),
                                   (i_check_create_source, False),
                                   (i_check_create_dataset, False),
                                   (i_check_create_association, False)],
                'scenario1_lr': [(i_create_all_lr_resources, True),
                                 (i_check_create_source, False),
                                 (i_check_create_dataset, False),
                                 (i_check_create_lr_model, False)],
                'scenario1_dn': [(i_create_all_dn_resources,True),
                                 (i_check_create_source, False),
                                 (i_check_create_dataset, False),
                                 (i_check_create_dn_model, False)],
                'scenario1_pca': [(i_create_all_pca_resources, True),
                                  (i_check_create_source, False),
                                  (i_check_create_dataset, False),
                                  (i_check_create_pca_model, False)]}
    scenario_path = "%s/" % scenario
    if os.path.exists(scenario_path):
        retrieve_resources(scenario_path, step)
        assert True
    else:
        try:
            kwargs = json.loads(kwargs)
        except Exception as exc:
            print(str(exc))
        for function, with_args in scenarios[scenario]:
            if with_args:
                function(step, **kwargs)
            else:
                function(step)


def i_create_random_analysis(step, k_fold=None, metric=None):
    """Step: I create BigML random fields analysis with
    <k_fold>-cross-validation improving <metric>
    """
    output = os.path.abspath(
        os.path.join(world.directory, "test", "random1", "evaluation"))
    ok_(k_fold is not None and metric is not None)
    command = ("bigmler analyze --dataset " +
               world.dataset['resource'] +
               " --random-fields --number_of_models 2" +
               " --k-folds " + k_fold +
               " --output " + world.directory +
               " --optimize " + metric)
    shell_execute(command, os.path.join(world.directory, "tmp"))
    world.output = output


def i_check_create_kfold_random_forest(step, kfolds):
    """Step: I check that the <kfolds>-random forests have been created"""
    directory = os.path.dirname(os.path.dirname(world.output))
    directories = [os.path.join(directory, folder)
                   for folder in os.listdir(directory) if
                   os.path.isdir(os.path.join(directory, folder))]
    message = None
    for directory in directories:
        ensembles_file = os.path.join(directory, "ensembles")
        try:
            with open(ensembles_file) as handler:
                ensembles_list = list(
                    map(str.strip, handler.readlines()))
            world.ensembles.extend(ensembles_list)
            world.ensemble = ensembles_list[-1]
            eq_(int(kfolds), len(ensembles_list))
        except Exception as exc:
            message = str(exc)
            break
    ok_(message is None, msg=message)


def i_check_random_candidates(step, random_candidates, metric, metric_value):
    """Step: the best random candidates number is <random_candidates>,
    with <metric> of <metric_value>
    """
    ok_(random_candidates is not None and metric is not None and \
        metric_value is not None)
    sessions_file = os.path.join(world.directory, "bigmler_sessions")
    try:
        with open(sessions_file, open_mode("r")) as sessions_file:
            content = sessions_file.read()
        text = "The best random candidates number is: %s \n%s = %s" % (
            random_candidates, metric.capitalize(), metric_value)
        ok_(content.find(text) > -1)
    except Exception:
        ok_(False)
