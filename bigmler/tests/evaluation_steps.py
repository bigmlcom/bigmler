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
try:
    import simplejson as json
except ImportError:
    import json
from bigmler.tests.world import world, res_filename
from subprocess import check_call
from bigml.api import check_resource

from bigmler.tests.common_steps import check_debug

from nose.tools import ok_, assert_equal


#@step(r'I create BigML resources using source to evaluate and log
# evaluation in "(.*)"')
def given_i_create_bigml_resources_using_source_to_evaluate(step,
                                                            output=None):
    if output is None:
        assert False
    command = ("bigmler --evaluate --source " + world.source['resource'] +
               " --output " + output)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        world.directory = os.path.dirname(output)
        world.folders.append(world.directory)
        world.output = output
    except OSError as e:
        assert False


def read_id_from_file(path):
    """Reading the id in first line in a file

    """

    with open(path) as id_file:
        return id_file.readline().strip()


#@step(r'I create BigML resources using dataset to evaluate and log
# evaluation in "(.*)"')
def given_i_create_bigml_resources_using_dataset_to_evaluate(step,
                                                             output=None):
    if output is None:
        assert False
    command = ("bigmler --evaluate --dataset " + world.dataset['resource'] +
               " --output " + output)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        world.directory = os.path.dirname(output)
        world.folders.append(world.directory)
        world.output = output
    except OSError as e:
        assert False


#@step(r'I create BigML resources using test file "([^"]*)" and a fields
# map "([^"]*)" to evaluate a model and log evaluation in "(.*)"')
def i_create_all_resources_to_evaluate_with_model_and_map( \
    step, data=None, fields_map=None, output=None):
    if data is None or fields_map is None or output is None:
        assert False
    command = ("bigmler --evaluate --test " + res_filename(data) +
               " --model " +
               world.model['resource'] + " --output " + output +
               " --fields-map " + res_filename(fields_map))
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        world.directory = os.path.dirname(output)
        world.folders.append(world.directory)
        world.output = output
    except OSError as e:
        assert False


#@step(r'I create BigML resources using test file "([^"]*)" to evaluate
# a model and log evaluation in "(.*)"')
def i_create_all_resources_to_evaluate_with_model(step,
                                                  data=None,
                                                  output=None):
    if data is None or output is None:
        assert False
    command = ("bigmler --evaluate --test " + res_filename(data) +
               " --model " +
               world.model['resource'] + " --output " + output)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        world.directory = os.path.dirname(output)
        world.folders.append(world.directory)
        world.output = output
    except OSError as e:
        assert False


#@step(r'I create BigML resources using a dataset to evaluate a
# model and log evaluation in "(.*)"')
def given_i_create_bigml_resources_using_dataset_to_evaluate_with_model( \
    step, output=None):
    if output is None:
        assert False
    command = ("bigmler --evaluate --dataset " +
               world.dataset['resource']  + " --model " +
               world.model['resource'] + " --output " + output)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        world.directory = os.path.dirname(output)
        world.folders.append(world.directory)
        world.output = output
    except OSError as e:
        assert False


#@step(r'I create BigML resources uploading train "(.*)" file to evaluate with
# test-split (.*) and log evaluation in "(.*)"')
def i_create_with_split_to_evaluate(step, data=None, split=None, output=None):
    if data is None or split is None or output is None:
        assert False
    command = ("bigmler --evaluate --train " + res_filename(data) +
               " --test-split " + split +  " --output " + output)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        world.directory = os.path.dirname(output)
        world.folders.append(world.directory)
        world.output = output
    except OSError as e:
        assert False


#@step(r'I evaluate "(.*)" with proportional missing strategy')
def i_create_proportional_to_evaluate(step, test=None):
    if test is None:
        assert False
    test = res_filename(test)

    try:
        output_dir = world.directory + "_eval/"
        output = output_dir + os.path.basename(world.output)
        command = ("bigmler --evaluate --model " +
                   world.model['resource'] +
                   " --test " + test +
                   " --missing-strategy proportional --output " +
                   output)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        world.directory = output_dir
        world.folders.append(world.directory)
        world.output = output
    except OSError as e:
        assert False


#@step(r'the evaluation file is like "(.*)"$')
def then_the_evaluation_file_is_like(step, check_file_json):
    check_file_json = res_filename(check_file_json)
    evaluation_file_json = world.output + ".json"
    try:
        evaluation_file_json = open(evaluation_file_json, "U")
        check_file_json = open(check_file_json, "U")
        check = check_file_json.readline()
        evaluation = evaluation_file_json.readline()
        check = json.loads(check)
        evaluation = json.loads(evaluation)
        if 'model' in check:
            assert_equal(check['model'], evaluation['model'])
            assert_equal(check['mode'], evaluation['mode'])
        else:
            del check["datasets"]
            del evaluation["datasets"]
            assert_equal(check, evaluation)
        evaluation_file_json.close()
        check_file_json.close()
    except Exception as exc:
        assert False, str(exc)

#@step(r'I check that the (.*) dataset has been created$')
def i_check_create_dataset(step, dataset_type=None):
    dataset_file = "%s%sdataset_%s" % (world.directory, os.sep, dataset_type)
    try:
        dataset_file = open(dataset_file, "r")
        dataset = check_resource(dataset_file.readline().strip(),
                                 world.api.get_dataset)
        world.datasets.append(dataset['resource'])
        world.dataset = dataset
        dataset_file.close()
    except Exception as exc:
        assert False, str(exc)


#@step(r'the evaluation key "(.*)" value for the model is greater than (.*)$')
def i_check_evaluation_key(step, key=None, value=None):
    evaluation_file_json = world.output + ".json"
    try:
        evaluation_file_json = open(evaluation_file_json, "U")
        evaluation = evaluation_file_json.readline()
        evaluation = json.loads(evaluation)
        model_evaluation = evaluation['model']
        ok_(model_evaluation[key] > float(value),
            "model key: %s, expected >: %s" % ( \
            model_evaluation[key], float(value)))
        evaluation_file_json.close()
    except Exception as exc:
        assert False, str(exc)


#@step(r'I create BigML resources uploading train "(.*)" file to evaluate an
# ensemble of (\d+) models with test-split (.*) and log evaluation in "(.*)"')
def i_create_with_split_to_evaluate_ensemble( \
    step, data=None, number_of_models=None, split=None, output=None):
    if data is None or split is None or output is None:
        assert False
    command = ("bigmler --evaluate --train " + res_filename(data) +
               " --test-split " + split +
               " --number-of-models " + number_of_models +
               " --output " + output)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        world.directory = os.path.dirname(output)
        world.folders.append(world.directory)
        world.output = output
    except OSError as e:
        assert False


#@step(r'I evaluate the ensemble in directory "(.*)" with the dataset in
# directory "(.*)" and log evaluation in "(.*)"')
def i_evaluate_ensemble_with_dataset( \
    step, ensemble_dir=None, dataset_dir=None, output=None):
    if ensemble_dir is None or dataset_dir is None or output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    ensemble_id = read_id_from_file(os.path.join(ensemble_dir, "ensembles"))
    dataset_id = read_id_from_file(os.path.join(dataset_dir, "dataset_test"))
    command = ("bigmler --dataset " + dataset_id +
               " --ensemble " + ensemble_id + " --store" +
               " --output " + output + " --evaluate")
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        world.output = output
    except OSError as exc:
        assert False, str(exc)


#@step(r'I evaluate the ensemble in directory "(.*)" with the dataset in
# directory "(.*)" and log evaluation in "(.*)"')
def i_evaluate_ensemble_with_dataset_and_options( \
    step, ensemble_dir=None, dataset_dir=None, output=None, options=None):
    if ensemble_dir is None or dataset_dir is None or output is None \
            or options is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    ensemble_id = read_id_from_file(os.path.join(ensemble_dir, "ensembles"))
    dataset_id = read_id_from_file(os.path.join(dataset_dir, "dataset_test"))
    command = ("bigmler --dataset " + dataset_id +
               " --ensemble " + ensemble_id + " --store" +
               " --output " + output + " --evaluate " + options)
    command = check_debug(command)
    try:
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        world.output = output
    except OSError as exc:
        assert False, str(exc)
