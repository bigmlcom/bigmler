# -*- coding: utf-8 -*-
#
# Copyright 2014-2016 BigML
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
import json
from bigmler.tests.world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigml.api import check_resource
from bigml.io import UnicodeReader
from bigmler.processing.models import MONTECARLO_FACTOR
from bigmler.checkpoint import file_number_of_lines
from bigmler.utils import storage_file_name, open_mode, decode2
from bigmler.utils import PYTHON3
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
from bigmler.tests.common_steps import check_debug
from bigmler.reports import REPORTS_DIR
from nose.tools import ok_, assert_equal, assert_not_equal, assert_almost_equal


def shell_execute(command, output, test=None, options=None,
                  test_rows=None, project=True):
    """Excute bigmler command in shell

    """
    command = check_debug(command, project=project)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
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
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

#@step(r'I create BigML resources from "(.*)" using ensemble of (.*) models to test "(.*)" using median and log predictions in "(.*)"')
def i_create_resources_from_ensemble_using_median( \
    step, data=None, number_of_models=None, test=None, output=None):
    ok_(data is not None and test is not None and output is not None and \
        number_of_models is not None)
    data = res_filename(data)
    test = res_filename(test)
    command = ("bigmler --train " + data + " --test " + test +
               " --store --output " + output +
               " --number-of-models " + number_of_models +
               " --median --max-batch-models 1 --no-fast")
    world.number_of_models = int(number_of_models)
    shell_execute(command, output, test=test)

#@step(r'I create BigML resources uploading train "(.*?)" file using the median to test "(.*?)" and log predictions in "([^"]*)"$')
def i_create_all_resources_with_median(step, data=None,
                                       test=None, output=None):
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --store --output " + output +
               " --median --max-batch-models 1 --no-fast")
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources uploading train "(.*?)" file to test "(.*?)" remotely to a dataset with no CSV output and log resources in "([^"]*)"$')
def i_create_all_resources_batch_to_dataset(step, data=None,
                                            test=None, output_dir=None):
    ok_(data is not None and test is not None and output_dir is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --store --no-csv --to-dataset --output-dir " +
               output_dir + " --remote")
    shell_execute(command, "%s/x.csv" % output_dir, test=test)


#@step(r'I create a BigML source from file "([^"]*)" with locale "([^"]*)", field attributes "([^"]*)" and types file "([^"]*)" storing results in "(.*)"$')
def i_create_source_with_locale(step, data=None, locale=None,
                                field_attributes=None, types=None,
                                output=None):
    ok_(data is not None and locale is not None and output is not None and \
        types is not None and field_attributes is not None)
    field_attributes = res_filename(field_attributes)
    types = res_filename(types)
    command = ("bigmler --train " + res_filename(data) + " --locale " +
               locale + " --field-attributes " + field_attributes +
               " --types " + types + " --output " + output +
               " --no-dataset --no-model --store")
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


#@step(r'I create BigML resources uploading train "(.*?)" file to create model and log in "([^"]*)"$')
def i_create_all_resources_to_model(step, data=None, output=None):
    ok_(data is not None and output is not None)
    command = ("bigmler --train " + res_filename(data) +
               " --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=None)


#@step(r'I create BigML feature selection (\d*)-fold cross-validations for "(.*)" improving "(.*)"$')
def i_create_kfold_cross_validation_objective(step, k_folds=None,
                                              objective=None, metric=None):
    ok_(k_folds is not None and metric is not None and objective is not None)
    command = ("bigmler analyze --dataset " +
                             world.dataset['resource'] +
                             " --features --k-folds " + k_folds +
                             " --output " + world.directory +
                             " --optimize " + metric +
                             " --objective " + objective)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = os.path.join(world.directory, "test", "kfold1",
                                        "evaluation")
            assert True
    except OSError as e:
        assert False


#@step(r'I create BigML feature selection (\d*)-fold cross-validation with options "(.*)"$')
def i_create_kfold_cross_validation_options(step, k_folds=None,
                                            options=None):
    ok_(k_folds is not None and options is not None)
    command = ("bigmler analyze --dataset " +
                             world.dataset['resource'] +
                             " --features --k-folds " + k_folds +
                             " --output " + world.directory +
                             options)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = os.path.join(world.directory, "test", "kfold1",
                                        "evaluation")
            assert True
    except OSError as e:
        assert False


#@step(r'I create BigML resources uploading train "(.*?)" file to test "(.*?)" with proportional missing strategy and log predictions in "([^"]*)"$')
def i_create_all_resources_proportional(step, data=None,
                                        test=None, output=None):
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --missing-strategy proportional" +
               " --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources uploading train "(.*?)" file to test "(.*?)" with a missing-splits model and log predictions in "([^"]*)"$')
def i_create_all_resources_missing_splits(step, data=None,
                                          test=None, output=None):
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --missing-splits" +
               " --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources uploading train "(.*?)" file to test "(.*?)" remotely with proportional missing strategy and log predictions in "([^"]*)"$')
def i_create_all_resources_remote_proportional(step, data=None,
                                               test=None, output=None):
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --missing-strategy proportional --remote" +
               " --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources uploading train "(.*?)" file to test "(.*?)" remotely with a missing-splits model and log predictions in "([^"]*)"$')
def i_create_all_resources_remote_missing_splits(step, data=None,
                                                 test=None, output=None):
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --missing-splits --remote" +
               " --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources uploading train "(.*?)" file to test "(.*?)" and log predictions in "(.*?)" with "(.*?)" as test field separator$')
def i_create_all_resources_with_separator(step, data=None,
                                          test=None, output=None,
                                          separator=None):
    ok_(data is not None and test is not None and separator is not None and \
        output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --test-separator " + separator + " --store --output " +
               output + " --max-batch-models 1")
    shell_execute(command, output, test=test)

#@step(r'I create BigML resources uploading train "(.*?)" file to test "(.*?)" remotely with mapping file "(.*?)" and log predictions in "([^"]*)"$')
def i_create_all_resources_batch_map(step, data=None, test=None, fields_map=None, output=None):
    ok_(data is not None and test is not None and output is not None and fields_map is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test + " --fields-map "
               + res_filename(fields_map) + " --store --output " + output + " --remote")
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources uploading train "(.*?)" file to test "(.*?)" remotely and log predictions in "([^"]*)"$')
def i_create_all_resources_batch(step, data=None, test=None, output=None):
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --store --output " + output + " --remote")
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources uploading train "(.*?)" file with no headers to test "(.*?)" with no headers and log predictions in "([^"]*)"$')
def i_create_all_resources_with_no_headers(step, data=None, test=None, output=None):
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --store --output " + output + " --max-batch-models 1 --no-fast --no-train-header --no-test-header")
    shell_execute(command, output, test=test, options='--prediction-header')


#@step(r'I create BigML resources uploading train "(.*?)" file to test "(.*?)" and log predictions in "([^"]*)"$')
def i_create_all_resources(step, data=None, test=None, output=None):
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --store --output " + output + " --max-batch-models 1 --no-fast")
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources uploading train "(.*?)" file to test "(.*?)" and log predictions in "(.*?)" with prediction options "(.*?)"')
def i_create_all_resources_with_options(step, data=None, test=None, output=None, options=''):
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --store --output " + output + " --max-batch-models 1 " +
               options.replace("'", "\""))
    shell_execute(command, output, test=test, options=options)


#@step(r'I create BigML (multi-label\s)?resources using source with objective "(.*)" and model fields "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_source_with_objective(step, multi_label=None, objective=None, model_fields=None, test=None, output=None):
    ok_(test is not None and output is not None)
    test = res_filename(test)
    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler "+ multi_label +"--source " + world.source['resource']
               + " --objective " + objective + " --model-fields \" "
               + model_fields + "\" --test " + test
               + " --store --output " + output)
    shell_execute(command, output, test=test)

#@step(r'I create BigML (multi-label\s)?resources using source to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_source(step, multi_label=None, test=None, output=None):
    ok_(test is not None and output is not None)
    test = res_filename(test)
    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler "+ multi_label +"--source " + world.source['resource']
               + " --test " + test + " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources using source to test the previous test source remotely and log predictions in "(.*)"')
def i_create_resources_from_source_batch(step, output=None):
    ok_(output is not None)
    command = ("bigmler --source " + world.source['resource']
               + " --test-source " + world.test_source['resource']
               + " --store --remote --output " + output)
    shell_execute(command, output)

#@step(r'I create BigML (multi-label\s)?resources using dataset with objective "(.*)" and model fields "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_dataset_with_objective(step, multi_label=None, objective=None, model_fields=None, test=None, output=None):
    ok_(test is not None and output is not None)
    test = res_filename(test)
    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler "+ multi_label +"--dataset " + world.dataset['resource']
               + " --objective " + objective + " --model-fields \" "
               + model_fields + "\" --test " + test
               + " --store --output " + output)
    shell_execute(command, output, test=test)

#@step(r'I create BigML (multi-label\s)?resources using dataset to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_dataset(step, multi_label=None, test=None, output=None):
    ok_(test is not None and output is not None)
    multi_label = "" if multi_label is None else " --multi-label "
    test = res_filename(test)
    command = ("bigmler "+ multi_label +"--dataset " +
               world.dataset['resource'] + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)

#@step(r'I create BigML resources using a model to test the previous test dataset remotely with prediction headers and fields "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_model_batch(step, fields=None, output=None):
    ok_(output is not None and fields is not None)
    command = ("bigmler --model " + world.model['resource'] + " --test-dataset " +
               world.test_dataset['resource'] + " --store --remote " +
               "--prediction-header --prediction-info full " +
               "--prediction-fields \"" + fields + "\" --output " + output)
    shell_execute(command, output, options="--prediction-header", test_rows=world.test_dataset['object']['rows'])

#@step(r'I create BigML resources using dataset to test the previous test dataset remotely and log predictions in "(.*)"')
def i_create_resources_from_dataset_batch(step, output=None):
    ok_(output is not None)
    command = ("bigmler --dataset " + world.dataset['resource'] + " --test-dataset " +
               world.test_dataset['resource'] + " --store --remote --output " + output)
    shell_execute(command, output, test_rows=world.test_dataset['object']['rows'])


#@step(r'I create BigML resources using dataset, objective field (.*) and model fields (.*) to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_dataset_objective_model(step, objective=None, fields=None, test=None, output=None):
    ok_(objective is not None and fields is not None and test is not None \
        and output is not None)
    test = res_filename(test)
    command = (u"bigmler --dataset " + world.dataset['resource'] +
               u" --objective " + objective + u" --model-fields " +
               fields + u" --test " + test + u" --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources using local model in "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_local_model(step, directory=None, test=None, output=None):
    ok_(test is not None and output is not None and directory is not None)
    test = res_filename(test)
    with open(os.path.join(directory, "models")) as model_file:
        model_id = model_file.read().strip()
    command = ("bigmler --model-file " +
               storage_file_name(directory, model_id) +
               " --test " +
               test + " --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources using model to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_model(step, test=None, output=None):
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --model " + world.model['resource'] + " --test " +
               test + " --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=test)

#@step(r'I create BigML resources using the previous ensemble with different thresholds to test "(.*)" and log predictions in "(.*)" and "(.*)"')
def i_create_resources_from_ensemble_with_threshold(step, test=None, output2=None, output3=None):
    ok_(test is not None and output2 is not None and output3 is not None)
    try:
        test = res_filename(test)
        command = ("bigmler --ensemble " + world.ensemble['resource'] +
                   " --test " + test + " --tag my_ensemble --store --output " +
                   output2 + " --method threshold --threshold " +
                   str(world.number_of_models))
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            assert True
        command = ("bigmler --ensemble " + world.ensemble['resource'] +
                   " --test " + test + " --tag my_ensemble --store --output " +
                   output3 + " --method threshold --threshold 1")
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML resources using local ensemble of (.*) models in "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_local_ensemble(step, number_of_models=None, directory=None, test=None, output=None):
    ok_(number_of_models is not None and test is not None and \
        output is not None and directory is not None)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
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
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            world.number_of_models = len(world.ensemble['object']['models'])
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

#@step(r'I create BigML resources using ensemble of (.*) models with replacement to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_ensemble_with_replacement(step, number_of_models=None, test=None, output=None):
    i_create_resources_from_ensemble_generic(step, number_of_models, "", test, output)

#@step(r'I create BigML resources using ensemble of (.*) models to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_ensemble(step, number_of_models=None, test=None, output=None):
    i_create_resources_from_ensemble_generic(step, number_of_models, \
        " --no-fast --ensemble-sample-no-replacement",
        test, output)

def i_create_resources_from_ensemble_generic(step, number_of_models=None, \
    no_replacement="", test=None, output=None):
    ok_(number_of_models is not None and test is not None and \
        output is not None)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        test = res_filename(test)
        command = ("bigmler --dataset " + world.dataset['resource'] +
                   " --test " + test + " --number-of-models " +
                   str(number_of_models) + " --tag my_ensemble --store" +
                   " --output " + output + no_replacement)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            world.number_of_models = int(number_of_models)
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML (multi-label\s)?resources using models in file "(.*)" with objective "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_models_file_with_objective(step, multi_label=None, models_file=None, objective=None, test=None, output=None):
    ok_(models_file is not None and test is not None and output is not None
        and objective is not None)
    test = res_filename(test)
    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler "+ multi_label +"--models " + models_file + " --test "
               + test + " --store --output " + output
               + " --objective " + objective)
    shell_execute(command, output, test=test)

#@step(r'I create BigML (multi-label\s)?resources using models in file "([^"]*)" to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_models_file(step, multi_label=None, models_file=None, test=None, output=None):
    ok_(models_file is not None and test is not None and output is not None)
    test = res_filename(test)
    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler "+ multi_label +"--models " + models_file + " --test "
               + test + " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources using dataset in file "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_dataset_file(step, dataset_file=None, test=None, output=None):
    ok_(dataset_file is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --datasets " + dataset_file + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create a BigML cross-validation with rate (0\.\d+) using the dataset in file "(.*)" and log results in "(.*)"')
def i_create_cross_validation_from_dataset(step, rate=None, dataset_file=None, output=None):
    ok_(rate is not None and output is not None and dataset_file is not None)
    with open(dataset_file, "r") as handler:
        dataset_id = handler.readline().strip()
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    world.number_of_models = int(MONTECARLO_FACTOR * float(rate))
    world.number_of_evaluations = world.number_of_models
    try:
        command = ("bigmler --dataset " + dataset_id +
                   " --cross-validation-rate " + rate + " --store --output "
                   + output)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I combine BigML predictions files in "(.*)" and "(.*)" into "(.*)"')
def i_find_predictions_files(step, directory1=None, directory2=None, output=None):
    ok_(directory1 is not None and directory2 is not None and \
        output is not None)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        command = ("bigmler --combine-votes " + directory1 + "," + directory2 +
                   " --store --output " + output)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines("%s%spredictions.csv" % (directory1, os.sep))
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I combine BigML predictions files in "(.*)" and "(.*)" into "(.*)" with method "(.*)"')
def i_find_predictions_files_with_method(step, directory1=None, directory2=None, output=None, method=None):
    ok_(directory1 is not None and directory2 is not None and \
        output is not None and method is not None)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        command = ("bigmler --combine-votes " + directory1 + "," + directory2 +
                   " --store --output " + output + " --method " + method)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines("%s%spredictions.csv" % (directory1, os.sep))
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create a BigML balanced model from "(.*)" and store logs in "(.*)"')
def i_create_balanced_model(step, data=None, output_dir=None):
    ok_(data is not None and output_dir is not None)
    world.directory = output_dir
    world.folders.append(world.directory)
    try:
        command = ("bigmler --train " + res_filename(data) + " --balance " +
                   " --store --output-dir " + output_dir)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

#@step(r'I create a BigML field weighted model from "(.*)" using field "(.*)" as weight and store logs in "(.*)"')
def i_create_weighted_field_model(step, data=None, field=None, output_dir=None):
    ok_(data is not None and field is not None and output_dir is not None)
    world.directory = output_dir
    world.folders.append(world.directory)
    try:
        command = ("bigmler --train " + res_filename(data) + " --weight-field " + field +
                   " --store --output-dir " + output_dir)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create a BigML objective weighted model from "(.*)" using the objective weights in file "(.*)" and store logs in "(.*)"')
def i_create_objective_weighted_model(step, data=None, path=None, output_dir=None):
    ok_(data is not None and path is not None and output_dir is not None)
    world.directory = output_dir
    world.folders.append(world.directory)
    try:
        command = ("bigmler --train " + res_filename(data) +
                   " --objective-weights " + res_filename(path) +
                   " --store --output-dir " + output_dir)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I check that the source has been created$')
def i_check_create_source(step):
    source_file = "%s%ssource" % (world.directory, os.sep)
    try:
        source_file = open(source_file, "r")
        source = check_resource(
            source_file.readline().strip(), world.api.get_source)
        world.sources.append(source['resource'])
        world.source = source
        source_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)


#@step(r'I check that the (test\s|train\s)?dataset has been created$')
def i_check_create_dataset(step, suffix=None):
    import traceback
    suffix = "" if suffix is None else "_%s" % suffix[:-1]
    dataset_file = "%s%sdataset%s" % (world.directory, os.sep, suffix)
    try:
        dataset_file = open(dataset_file, "r")
        for dataset_id in dataset_file:
            dataset_id = dataset_id.strip()
        dataset = check_resource(dataset_id,
                                 world.api.get_dataset)
        assert (not 'user_metadata' in dataset['object'] or
                not 'max_categories'
                in dataset['object']['user_metadata'])
        world.datasets.append(dataset['resource'])
        world.dataset = dataset
        dataset_file.close()
        assert True
    except Exception, exc:
        assert False, traceback.format_exc()


#@step(r'I check that the new dataset has been created$')
def i_check_create_new_dataset(step):
    dataset_file = "%s%sdataset_gen" % (world.directory, os.sep)
    try:
        dataset_file = open(dataset_file, "r")
        dataset_id = dataset_file.readline().strip()
        dataset = check_resource(dataset_id,
                                 world.api.get_dataset)
        world.datasets.append(dataset['resource'])
        world.dataset = dataset
        dataset_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)


#@step(r'I check that the dataset has been created and shared$')
def i_check_create_dataset_shared(step):
    i_check_create_dataset(step)
    assert world.dataset['object']['shared']


#@step(r'I check that the model has been created')
def i_check_create_model(step):
    model_file = "%s%smodels" % (world.directory, os.sep)
    try:
        model_file = open(model_file, "r")
        model = check_resource(model_file.readline().strip(),
                               world.api.get_model)
        world.models.append(model['resource'])
        world.model = model
        model_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)


#@step(r'I check that the (\d*)-models have been created')
def i_check_create_kfold_models(step, kfolds):
    directory = os.path.dirname(os.path.dirname(world.output))

    directories = [os.path.join(directory, folder)
                   for folder in os.listdir(directory) if
                   os.path.isdir(os.path.join(directory, folder))]
    for directory in directories:
        if not directory.endswith("_pred"):
            model_file = os.path.join(directory, "models")
            try:
                with open(model_file, "r") as models_file:
                    models_list = map(str.strip, models_file.readlines())

                world.models.extend(models_list)
                world.model = models_list[-1]
                assert_equal(int(kfolds), len(models_list))
            except Exception, exc:
                assert False, str(exc)


#@step(r'I check that the (\d*)-ensembles have been created')
def i_check_create_kfold_ensembles(step, kfolds):
    directory = os.path.dirname(os.path.dirname(world.output))

    directories = [os.path.join(directory, folder)
                   for folder in os.listdir(directory) if
                   os.path.isdir(os.path.join(directory, folder))]
    for directory in directories:
        if not directory.endswith("_pred"):
            model_file = os.path.join(directory, "ensembles")
            try:
                with open(model_file, "r") as models_file:
                    models_list = map(str.strip, models_file.readlines())
                world.ensembles.extend(models_list)
                world.ensemble = models_list[-1]
                assert_equal(int(kfolds), len(models_list))
            except Exception, exc:
                assert False, str(exc)

#@step(r'I check that the model has been created and shared$')
def i_check_create_model_shared(step):
    i_check_create_model(step)
    assert world.model['object']['shared']


#@step(r'I check that the model is balanced')
def i_check_model_is_balanced(step):
    assert ('balance_objective' in world.model['object'] and
            world.model['object']['balance_objective'])


#@step(r'I check that the model uses as weight "(.*)"')
def i_check_weighted_model(step, field=None):
    if field is None:
        assert False
    assert ('weight_field' in world.model['object'] and
            world.model['object']['weight_field'] == field)


#@step(r'I check that the model uses as objective weights "(.*)"')
def i_check_objective_weighted_model(step, weights=None):
    if weights is None:
        assert False
    assert ('objective_weights' in world.model['object'] and
            world.model['object']['objective_weights'] == json.loads(weights))


#@step(r'I check that the ensemble has been created')
def i_check_create_ensemble(step):
    ensemble_file = "%s%sensembles" % (world.directory, os.sep)
    try:
        ensemble_file = open(ensemble_file, "r")
        ensemble = check_resource(ensemble_file.readline().strip(),
                               world.api.get_ensemble)
        world.ensembles.append(ensemble['resource'])
        world.ensemble = ensemble
        ensemble_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)

#@step(r'I check that the models have been created')
def i_check_create_models(step):
    i_check_create_models_in_ensembles(step, False)


#@step(r'I check that the models in the ensembles have been created')
def i_check_create_models_in_ensembles(step, in_ensemble=True):
    model_file = "%s%smodels" % (world.directory, os.sep)
    number_of_lines = 0
    count = 0
    while world.number_of_models != number_of_lines and count < 10:
        number_of_lines = 0
        model_ids = []
        for line in open(model_file, "r"):
            number_of_lines += 1
            model_id = line.strip()
            model_ids.append(model_id)
        if world.number_of_models != number_of_lines:
            time.sleep(10)
            count += 1
    if world.number_of_models != number_of_lines:
        assert False, "number of models %s and number of lines in models file %s: %s" % (world.number_of_models, model_file, number_of_lines)
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

            assert True
        except Exception, exc:
            assert False, str(exc)


#@step(r'I check that the evaluation has been created')
def i_check_create_evaluation(step):
    evaluation_file = "%s%sevaluations" % (world.directory, os.sep)
    try:
        evaluation_file = open(evaluation_file, "r")
        evaluation = check_resource(evaluation_file.readline().strip(),
                                    world.api.get_evaluation)
        world.evaluations.append(evaluation['resource'])
        world.evaluation = evaluation
        evaluation_file.close()
        assert True
    except:
        assert False


def check_create_kfold_cross_validation(step, kfolds, directory):
    evaluations_file = os.path.join(directory, "evaluations")
    try:
        with open(evaluations_file, "r") as evaluations_file:
            evaluations_list = map(str.strip, evaluations_file.readlines())
        world.evaluations.extend(evaluations_list)
        world.evaluation = evaluations_list[-1]
        if int(kfolds) == len(evaluations_list):
            assert True
        else:
            assert False
    except:
        assert False


#@step(r'I check that all the (\d*)-fold cross-validations have been created')
def i_check_create_all_kfold_cross_validations(step, kfolds):
    directory = os.path.dirname(os.path.dirname(world.output))
    directories = [os.path.join(directory, folder)
                   for folder in os.listdir(directory) if
                   os.path.isdir(os.path.join(directory, folder))]
    for directory in directories:
        if not directory.endswith("_pred"):
            check_create_kfold_cross_validation(step, kfolds, directory)


#@step(r'I check that the (\d*)-fold cross-validation has been created')
def i_check_create_kfold_cross_validation(step, kfolds):
    check_create_kfold_cross_validation(step, kfolds,
                                        os.path.dirname(world.output))


#@step(r'I check that the (\d*)-datasets have been created')
def i_check_create_kfold_datasets(step, kfolds):
    datasets_file = os.path.join(
        os.path.dirname(os.path.dirname(world.output)),
        "dataset_gen")
    try:
        with open(datasets_file, "r") as datasets_file:
            datasets_list = map(str.strip, datasets_file.readlines())
        world.datasets.extend(datasets_list)
        world.dataset = datasets_list[-1]
        if int(kfolds) == len(datasets_list):
            assert True
        else:
            assert False
    except:
        assert False


#@step(r'the best feature selection is "(.*)", with "(.*)" of (.*)')
def i_check_feature_selection(step, selection, metric, metric_value):
    ok_(selection is not None and metric is not None and \
        metric_value is not None)
    sessions_file = os.path.join(world.directory, "bigmler_sessions")
    try:
        with open(sessions_file, open_mode("r")) as sessions_file:
            content = sessions_file.read()
            if not PYTHON3:
                content = decode2(content)
        text = "The best feature subset is: %s \n%s = %s" % (
            selection, metric.capitalize(), metric_value)
        if content.find(text) > -1:
            assert True
        else:
            assert False
    except Exception, exc:
        assert False, str(exc)


#@step(r'the best node threshold is "(.*)", with "(.*)" of (.*)')
def i_check_node_threshold(step, node_threshold, metric, metric_value):
    ok_(node_threshold is not None and metric is not None and \
        metric_value is not None)
    sessions_file = os.path.join(world.directory, "bigmler_sessions")
    try:
        with open(sessions_file, open_mode("r")) as sessions_file:
            content = sessions_file.read()
            if not PYTHON3:
                content = decode2(content)
        text = "The best node threshold is: %s \n%s = %s" % (
            node_threshold, metric.capitalize(), metric_value)
        if content.find(text) > -1:
            assert True
        else:
            assert False
    except:
        assert False


#@step(r'I check that the evaluation has been created and shared$')
def i_check_create_evaluation_shared(step):
    i_check_create_evaluation(step)
    assert world.evaluation['object']['shared']


#@step(r'I check that the Gazibit (shared )?report has been created$')
def i_check_gazibit_reports(step, shared=''):
    shared = "_%s" % shared[0: -1] if shared is not None else ''
    gazibit_file = "%s%sreports%sgazibit%s.json" % (
        world.directory, os.sep, os.sep, shared)
    try:
        gazibit_file = open(gazibit_file, "r")
        content = gazibit_file.read()
        if (content.find('%START_BIGML_') < 0 and
                content.find('%END_BIGML_') < 0 and
                content.find('%BIGML_') < 0):
            assert True
        else:
            assert False
    except Exception, exc:
        assert False, str(exc)


#@step(r'I check that the (\d+ )?evaluations have been created')
def i_check_create_evaluations(step, number_of_evaluations=None):
    if number_of_evaluations is not None:
        world.number_of_evaluations = int(number_of_evaluations)
    evaluations_file = "%s%sevaluations" % (world.directory, os.sep)
    evaluation_ids = []
    number_of_lines = 0
    count = 0
    while world.number_of_evaluations != number_of_lines and count < 10:
        number_of_lines = 0
        for line in open(evaluations_file, "r"):
            number_of_lines += 1
            evaluation_id = line.strip()
            evaluation_ids.append(evaluation_id)
        if world.number_of_evaluations != number_of_lines:
            time.sleep(10)
            count += 1
    if world.number_of_evaluations != number_of_lines:
        assert False, "number of evaluations %s and number of lines in evaluations file %s: %s" % (world.number_of_evaluations, evaluation_file, number_of_lines)
    world.evaluation_ids = evaluation_ids
    for evaluation_id in evaluation_ids:
        try:
            evaluation = check_resource(evaluation_id, world.api.get_evaluation)
            world.evaluations.append(evaluation_id)
            assert True
        except Exception, exc:
            assert False, str(exc)


#@step(r'I check that the predictions are ready')
def i_check_create_predictions(step):
    previous_lines = -1
    predictions_lines = 0
    try:
        predictions_file = world.output
        predictions_file = open(predictions_file, "r")
        predictions_lines = 0
        for line in predictions_file:
            predictions_lines += 1
        if predictions_lines == world.test_lines:
            assert True
        else:
            assert False, "predictions lines: %s, test lines: %s" % (predictions_lines, world.test_lines)
        predictions_file.close()
    except Exception, exc:
        assert False, str(exc)


#@step(r'the predictions file "(.*)" is like "(.*)"')
def i_check_predictions_file(step, predictions_file, check_file):
    world.output = predictions_file
    i_check_predictions(step, check_file)


#@step(r'the local prediction file is like "(.*)"')
def i_check_predictions(step, check_file):
    check_file = res_filename(check_file)
    predictions_file = world.output
    import traceback
    try:
        with UnicodeReader(predictions_file) as predictions_file:
            with UnicodeReader(check_file) as check_file:
                for row in predictions_file:
                    check_row = check_file.next()
                    assert len(check_row) == len(row)
                    for index in range(len(row)):
                        dot = row[index].find(".")
                        decimal_places = 1
                        if dot > 0 or (check_row[index].find(".") > 0
                                       and check_row[index].endswith(".0")):
                            try:
                                decimal_places = min(len(row[index]), len(check_row[index])) - dot - 1
                                row[index] = round(float(row[index]), decimal_places)
                                check_row[index] = round(float(check_row[index]), decimal_places)
                            except ValueError:
                                decimal_places = 1
                            assert_almost_equal(check_row[index], row[index],
                                                places=(decimal_places - 1))
                        else:
                            assert_equal(check_row[index], row[index])
    except Exception, exc:
        assert False, traceback.format_exc()


#@step(r'local predictions for different thresholds in "(.*)" and "(.*)" are different')
def i_check_predictions_with_different_thresholds(step, output2, output3):
    try:
        predictions_file = open(output2, "U").read()
        predictions_file_k = open(output3, "U").read()
    except Exception, exc:
        assert False, str(exc)
    assert_not_equal(predictions_file, predictions_file_k)


#@step(r'the cross-validation json model info is like the one in "(.*)"')
def i_check_cross_validation(step, check_file):
    check_file = res_filename(check_file)
    cv_file = "%s/cross_validation.json" % world.directory
    try:
        with open(cv_file, "U") as cv_handler:
            cv_content = json.loads(cv_handler.read())
        with open(check_file, "U") as check_handler:
            check_content = json.loads(check_handler.read())
    except Exception, exc:
        assert False, str(exc)
    assert_equal(cv_content['model'], check_content['model'])


#@step(r'I check that the stored source file exists')
def i_check_stored_source(step):
    try:
        with open("%s%ssource" % (world.directory, os.sep), "r") as source_file:
            source_id = source_file.readline().strip()
            world.sources.append(source_id)
        storage_source_file = "%s%s%s" % (world.directory, os.sep, source_id.replace("/", "_"))
        if os.path.exists(storage_source_file):
            with open(storage_source_file, "r") as storage_source_file:
                world.source = json.loads(storage_source_file.read().strip())
            assert True
        else:
            assert False
    except Exception, exc:
        assert False, str(exc)


#@step(r'And the locale of the source is "(.*)"')
def i_check_source_locale(step, bigml_locale):
    try:
        locale = world.source['object']["source_parser"]["locale"]
        if bigml_locale == locale:
            assert True
        else:
            assert False, "Found locale: %s, expected %s" % (locale, bigml_locale)
    except KeyError, exc:
        assert False, str(exc)


#@step(r'the type of field "(.*)" is "(.*)"')
def i_check_source_type(step, field_id, field_type):
    try:
        type = world.source['object']["fields"][field_id]['optype']
        if type == field_type:
            assert True
        else:
            assert False, "Found field type: %s, expected %s" % (type, field_type)
    except KeyError, exc:
        assert False, str(exc)


#@step(r'the label of field "(.*)" is "(.*)"')
def i_check_source_label(step, field_id, field_label):
    try:
        label = world.source['object']["fields"][field_id]['label']
        if label == field_label:
            assert True
        else:
            assert False, "Found field label: %s, expected %s" % (label, field_label)
    except KeyError, exc:
        assert False, str(exc)


#@step(r'I create BigML resources uploading train "(.*)" file to evaluate and log evaluation in "(.*)"')
def i_create_all_resources_to_evaluate(step, data=None, output=None):
    ok_(data is not None and output is not None)
    command = "bigmler --evaluate --train " + res_filename(data) + " --store --output " + output
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


#@step(r'I create BigML resources and share them uploading train "(.*)" file to evaluate and log evaluation and reports in "(.*)"')
def i_create_all_resources_to_evaluate_and_report(
    step, data=None, output=None):
    ok_(data is not None and output is not None)
    command = ("bigmler --evaluate --shared --report gazibit" +
               " --train " + res_filename(data) +
               " --store --no-upload --output " + output)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


#@step(r'I create BigML resources and share them uploading train "(.*)" file to evaluate and log evaluation in "(.*)"')
def i_create_all_resources_to_evaluate_and_share(step, data=None, output=None):
    ok_(data is not None and output is not None)
    command = ("bigmler --evaluate --shared --train " + res_filename(data) +
               " --store --output " + output)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


#@step(r'I create BigML dataset uploading train "(.*)" file with attributes "(.*)" in "(.*)"')
def i_create_dataset_with_attributes(step, data=None, attributes=None, output=None):
    ok_(data is not None and output is not None and attributes is not None)
    command = ("bigmler --train " + res_filename(data) +
               " --source-attributes " + res_filename(attributes) +
               " --no-model --store --output " + output)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


#@step(r'I create BigML dataset uploading train "(.*)" file in "(.*)"')
def i_create_dataset(step, data=None, output=None):
    ok_(data is not None and output is not None)
    command = ("bigmler --train " + res_filename(data) +
               " --no-model --store --output " + output)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


#@step(r'I create BigML (\d*)-fold cross-validation')
def i_create_kfold_cross_validation(step, k_folds=None):
    ok_(k_folds is not None)
    command = ("bigmler analyze --dataset " +
               world.dataset['resource'] +
               " --cross-validation --k-folds " + k_folds +
               " --output " + world.directory)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = os.path.join(world.directory, "test", "k_fold0",
                                        "evaluation")
            assert True
    except OSError as e:
        assert False


#@step(r'I create BigML nodes analysis from (\d*) to (\d*) by (\d*) with (\d*)-cross-validation improving "(.*)"')
def i_create_nodes_analysis(step, min_nodes=None, max_nodes=None,
                            nodes_step=None, k_fold=None, metric=None):
    ok_(max_nodes is not None and \
        nodes_step is not None and k_fold is not None and \
        metric is not None)
    command = ("bigmler analyze --dataset " + world.dataset['resource'] +
               " --nodes --min-nodes " + min_nodes +
               " --max-nodes " + max_nodes +
               " --nodes-step " + nodes_step +
               " --k-folds " + k_fold +
               " --output " + world.directory +
               " --optimize " + metric)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        ok_(retcode == 0)
        world.output = os.path.join(world.directory, "test", "kfold1",
                                    "evaluation")
    except OSError as e:
        assert False



#@step(r'I create BigML nodes analysis from datasets file from (\d*) to (\d*) by (\d*) with (\d*)-cross-validation improving "(.*)"')
def i_create_nodes_analysis_from_dataset_file(
    step, min_nodes=None, max_nodes=None,
    nodes_step=None, k_fold=None, metric=None):
    ok_(max_nodes is not None and \
        nodes_step is not None and k_fold is not None and \
        metric is not None)
    command = ("bigmler analyze --datasets %s/dataset" % world.directory +
               " --nodes --min-nodes " + min_nodes +
               " --max-nodes " + max_nodes +
               " --nodes-step " + nodes_step +
               " --k-folds " + k_fold +
               " --output " + world.directory +
               " --optimize " + metric)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        ok_(retcode == 0)
        world.output = os.path.join(world.directory, "test", "kfold1",
                                    "evaluation")
    except OSError as e:
        assert False


#@step(r'I create BigML feature selection (\d*)-fold cross-validations excluding "(.*)" with separator "(.*)" improving "(.*)"')
def i_create_kfold_cross_validation_separator_metric_no_fields(
    step, k_folds=None, features=None, args_separator=None, metric=None):
    ok_(k_folds is not None and metric is not None and features is not None \
        and args_separator is not None)
    command = ("bigmler analyze --dataset " +
               world.dataset['resource'] +
               " --features --k-folds " + k_folds +
               " --output " + world.directory +
               " --exclude-features \"" + features + "\"" +
               " --args-separator " + args_separator +
               " --optimize " + metric)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = os.path.join(world.directory, "test", "kfold1",
                                        "evaluation")
            assert True
    except OSError as e:
        assert False


#@step(r'I create BigML feature selection (\d*)-fold cross-validations improving "(.*)" in dev mode$')
def i_create_kfold_cross_validation_in_dev(step, k_folds=None, metric=None):
    ok_(k_folds is not None and metric is not None)
    command = ("bigmler analyze --dataset " +
               world.dataset['resource'] +
               " --features --dev --k-folds " + k_folds +
               " --output " + world.directory +
               " --optimize " + metric)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = os.path.join(world.directory, "test", "kfold1",
                                        "evaluation")
            assert True
    except OSError as e:
        assert False

#@step(r'I create BigML feature selection (\d*)-fold cross-validations improving "(.*)" for category "(.*)"$')
def i_create_kfold_cross_validation_metric_category(step, k_folds=None, metric=None, category=None):
    ok_(k_folds is not None and metric is not None and category is not None)
    command = ("bigmler analyze --dataset " +
               world.dataset['resource'] +
               " --features --k-folds " + k_folds +
               " --output " + world.directory +
               " --optimize " + metric +
               " --optimize-category " + category)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = os.path.join(world.directory, "test", "kfold1",
                                        "evaluation")
            assert True
    except OSError as e:
        assert False


#@step(r'I create BigML feature selection (\d*)-fold cross-validations improving "(.*)"$')
def i_create_kfold_cross_validation_metric(step, k_folds=None, metric=None):
    ok_(k_folds is not None and metric is not None)
    command = ("bigmler analyze --dataset " +
               world.dataset['resource'] +
               " --features --k-folds " + k_folds +
               " --output " + world.directory +
               " --optimize " + metric)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = os.path.join(world.directory, "test", "kfold1",
                                        "evaluation")
            assert True
    except OSError as e:
        assert False


#@step(r'I generate a report from the output directory$')
def i_generate_report(step):
    command = ("bigmler report --no-server --from-dir " +
               world.directory)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = os.path.join(world.directory, "test", "kfold1",
                                        "evaluation")
            assert True
    except OSError as e:
        assert False


#@step(r'a symlink file is generated in the reports directory$')
def is_symlink(step):
    resource_file = os.path.join(world.directory, REPORTS_DIR, "symlink")
    try:
        with open(resource_file, open_mode("r")) as resource_handler:
            assert True
    except IOError:
        assert False


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
        with open(os.path.join(scenario_path, "source"), open_mode("r")) as source_id_file:
            source_id = source_id_file.readline().strip()
            world.source = retrieve_resource(scenario_path, source_id)
    except:
        pass
    try:
        with open(os.path.join(scenario_path, "dataset"), open_mode("r")) as dataset_id_file:
            dataset_id = dataset_id_file.readline().strip()
            world.dataset = retrieve_resource(scenario_path, dataset_id)
    except:
        pass
    try:
        with open(os.path.join(scenario_path, "source_test"), open_mode("r")) as source_id_file:
            source_id = source_id_file.readline().strip()
            world.test_source = retrieve_resource(scenario_path, source_id)
    except:
        pass
    try:
        with open(os.path.join(scenario_path, "dataset_test"), open_mode("r")) as dataset_id_file:
            dataset_id = dataset_id_file.readline().strip()
            world.test_dataset = retrieve_resource(scenario_path, dataset_id)
    except:
        pass
    try:
        with open(os.path.join(scenario_path, "models"), open_mode("r")) as model_id_file:
            model_id = model_id_file.readline().strip()
            world.model = retrieve_resource(scenario_path, model_id)
    except:
        pass



#@step(r'I have previously executed "(.*)" or reproduce it with arguments (.*)$')
def i_have_previous_scenario_or_reproduce_it(step, scenario, kwargs):
    scenarios = {'scenario1': [(i_create_all_resources, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_model, False)],
                 'scenario1_r': [(i_create_all_resources, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_model, False)],
                 'scenario5': [(i_create_resources_from_ensemble, True), (i_check_create_ensemble, False)],
                 'scenario_e1': [(i_create_all_resources_to_evaluate, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_model, False), (i_check_create_evaluation, False)],
                 'scenario_ml_1': [(i_create_all_ml_resources, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_models, False)],
                 'scenario_ml_6': [(i_create_all_ml_resources, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_models, False)],
                 'scenario_mle_1': [(i_create_all_ml_resources_and_ensembles, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_models_in_ensembles, False)],
                 'scenario_ml_e1': [(i_create_all_ml_resources_for_evaluation, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_models, False)],
                 'scenario_mc_1': [(i_create_all_mc_resources, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_max_categories_datasets, False), (i_check_create_models, False)],
                 'scenario_r1': [(i_create_all_resources_batch, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_model, False), (i_check_create_test_source, False), (i_check_create_test_dataset, False), (i_check_create_batch_prediction, False)],
                 'scenario_mlm_1': [(i_create_all_mlm_resources, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_models, False)],
                'scenario_c_1': [(i_create_all_cluster_resources, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_cluster, False)],
                'scenario_an_1': [(i_create_all_anomaly_resources, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_anomaly, False)],
                'scenario_ass_1': [(i_create_association, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_association, False)],
                'scenario1_lr': [(i_create_all_lr_resources, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_lr_model, False)]}
    scenario_path = "%s/" % scenario
    if os.path.exists(scenario_path):
        retrieve_resources(scenario_path, step)
        assert True
    else:
        try:
            kwargs = json.loads(kwargs)
        except Exception, exc:
            print str(exc)
        for function, with_args in scenarios[scenario]:
            if with_args:
                function(step, **kwargs)
            else:
                function(step)


#@step(r'I create BigML dataset in dev mode uploading train "(.*)" file in "(.*)"')
def i_create_dev_dataset(step, data=None, output=None):
    ok_(data is not None and output is not None)
    try:
        retcode = check_call("bigmler --train " + res_filename(data) + " --no-model --store --dev --output " + output, shell=True)
        if retcode < 0:
            assert False
        else:
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


#@step(r'I create BigML random fields analysis with (\d*)-cross-validation improving "(.*)"')
def i_create_random_analysis(step, k_fold=None, metric=None):
    ok_(k_fold is not None and metric is not None)
    try:
        retcode = check_call("bigmler analyze --dataset " +
                             world.dataset['resource'] +
                             " --random-fields --number_of_models 2" +
                             " --k-folds " + k_fold +
                             " --output " + world.directory +
                             " --optimize " + metric,
                             shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = os.path.join(world.directory, "test", "random1",
                                        "evaluation")
            assert True
    except OSError as e:
        assert False

#@step(r'I check that the (\d*)-random forests have been created')
def i_check_create_kfold_random_forest(step, kfolds):
    directory = os.path.dirname(os.path.dirname(world.output))

    directories = [os.path.join(directory, folder)
                   for folder in os.listdir(directory) if
                   os.path.isdir(os.path.join(directory, folder))]
    for directory in directories:
        ensembles_file = os.path.join(directory, "ensembles")
        try:
            with open(ensembles_file, "r") as ensembles_file:
                ensembles_list = map(str.strip, ensembles_file.readlines())

            world.ensembles.extend(ensembles_list)
            world.ensemble = ensembles_list[-1]
            if int(kfolds) == len(ensembles_list):
                assert True
            else:
                assert False
        except Exception, exc:
            assert False, str(exc)


#@step(r'the best random candidates number is "(.*)", with "(.*)" of (.*)')
def i_check_random_candidates(step, random_candidates, metric, metric_value):
    ok_(random_candidates is not None and metric is not None and \
        metric_value is not None)
    sessions_file = os.path.join(world.directory, "bigmler_sessions")
    try:
        with open(sessions_file, open_mode("r")) as sessions_file:
            content = sessions_file.read()
            if not PYTHON3:
                content = decode2(content)
        text = "The best random candidates number is: %s \n%s = %s" % (
            random_candidates, metric.capitalize(), metric_value)
        if content.find(text) > -1:
            assert True
        else:
            assert False
    except:
        assert False
