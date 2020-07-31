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
import csv
import json
import sys
from bigmler.tests.world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigmler.checkpoint import file_number_of_lines
from bigmler.utils import BIGML_SYS_ENCODING
from bigml.api import check_resource
from bigmler.tests.common_steps import check_debug
from nose.tools import ok_, eq_


#@step(r'I create a BigML dataset from "(.*)" and store logs in "(.*)"')
def i_create_dataset(step, data=None, output_dir=None):
    if data is None or output_dir is None:
        assert False
    world.directory = output_dir
    world.folders.append(world.directory)

    try:
        command = ("bigmler --train " + res_filename(data) +
                   " --no-model --store --output-dir " + output_dir)

        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output_dir
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create a BigML dataset from previous source and store logs in "(.*)"')
def i_create_dataset_from_source(step, output_dir=None):
    if output_dir is None:
        assert False
    world.directory = output_dir
    world.folders.append(world.directory)
    try:

        command = (("bigmler --source %s" % world.source['resource']) +
                   " --no-model --store --output-dir " + output_dir)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output_dir
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create a BigML filtered dataset with filter "(.*)" from previous dataset and store logs in "(.*)"')
def i_create_filtered_dataset_from_dataset(step, filter_exp=None, output_dir=None):
    if filter_exp is None or output_dir is None:
        assert False
    world.directory = output_dir
    world.folders.append(world.directory)
    try:
        if not sys.platform == 'win32':
            filter_exp = '"%s"' % filter_exp.replace('"', '\\"')
        command = ('echo ' +
                   filter_exp + ' > ' +
                   output_dir + "/filter.lisp")
        retcode = check_call(command, shell=True)
        command = (("bigmler --dataset %s" % world.dataset['resource']) +
                   " --no-model --store --output-dir " + output_dir +
                   " --lisp-filter " + output_dir + "/filter.lisp")
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output_dir
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create a new BigML dataset using the specs in JSON file "(.*)" and a model with "(.*)"')
def i_create_dataset_new_fields(step, json_file=None, model_fields=None):
    if json_file is None or model_fields is None:
        assert False
    json_file = res_filename(json_file)
    try:
        command = ("bigmler --dataset " + world.dataset['resource'] +
                   " --model-fields \"" + model_fields + "\" --store" +
                   " --output-dir " + world.output +
                   " --new-fields " + json_file)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I update the dataset using the specs in JSON file "(.*)"')
def i_update_dataset_new_properties(step, json_file=None):
    if json_file is None:
        assert False
    json_file = res_filename(json_file)
    try:
        command = ("bigmler --dataset " + world.dataset['resource'] +
                   " --no-model --store --output-dir " + world.output +
                   " --dataset-attributes " + json_file)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I check that the new dataset has field "(.*)"')
def i_check_dataset_has_field(step, field):
    fields = world.dataset['object']['fields']
    for field_id in fields:
        if fields[field_id]['name'] == field:
            assert True
            return
    assert False


#@step(r'I check that property "(.*)" for field id "(.*)" is "(.*)" of type "(.*)"')
def i_check_dataset_has_property(step, attribute=None, field_id=None, value=None, type=None):
    if attribute is None or field_id is None or value is None:
        assert False
    fields = world.dataset['object']['fields']
    if type == "boolean":
        value = bool(value)
    if type == "integer":
        value = int(value)
    if fields[field_id][attribute] == value:
        assert True
        return
    assert False


#@step(r'I create a multi-dataset from the datasets file and store logs in "(.*)"')
def i_create_multi_dataset(step, output_dir):
    if output_dir is None:
        assert False
    world.folders.append(output_dir)
    datasets_file = "%s%sdataset" % (world.directory, os.sep)
    try:
        command = ("bigmler --datasets " + datasets_file +
                   " --multi-dataset --no-model --store --output-dir " +
                   output_dir)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.directory = output_dir
            world.output = output_dir
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I check that the multi-dataset\'s origin are the datasets in "(.*)"')
def i_check_multi_dataset_origin(step, output_dir=None):
    if output_dir is None:
        assert False
    datasets_file = "%s%sdataset" % (output_dir, os.sep)
    try:
        origin_datasets = world.dataset['object']['origin_datasets']
        count = 0
        with open(datasets_file, 'r') as datasets_file_handler:
            for dataset_id in datasets_file_handler:
                dataset_id = dataset_id.strip()
                if not (dataset_id in origin_datasets):
                    assert False
                count += 1
        if count != len(origin_datasets):
            assert False
        else:
            assert True
    except KeyError:
        assert False

#@step(r'I filter out field "(.*)" from dataset and log to "(.*)"')
def i_filter_field_from_dataset(step, field=None, output_dir=None):
    if field is None or output_dir is None:
        assert False
    try:
        empty_json = res_filename('data/empty.json')
        command = ("bigmler --dataset " + world.dataset['resource'] +
                   " --no-model --store --output-dir " + output_dir +
                   " --dataset-fields=\"-" + field + "\""+
                   " --new-fields " + empty_json)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

#@step(r'I check that the multi-dataset has been created$')
def i_check_create_multi_dataset(step):
    dataset_file = "%s%sdataset_multi" % (world.directory, os.sep)
    try:
        with open(dataset_file, "r") as dataset_file_handler:
            dataset_id = dataset_file_handler.readline().strip()
        dataset = check_resource(dataset_id,
                                 world.api.get_dataset)
        world.datasets.append(dataset['resource'])
        world.dataset = dataset
        assert True
    except Exception as exc:
        assert False, str(exc)


#@step(r'file "(.*)" is like file "(.*)"$')
def i_files_equal(step, local_file, data):
    data = res_filename(data)
    contents_local_file = open(os.path.join(world.directory,
                                            local_file)).read()
    contents_data = open(data).read()
    assert contents_local_file == contents_data

#@step(r'I export the dataset to the CSV file "(.*)"$')
def i_export_the_dataset(step, filename):
    if filename is None:
        assert False
    try:
        command = ("bigmler --dataset " + world.dataset['resource'] +
                   " --to-csv " + filename +
                   " --output-dir " + world.directory + " --no-model")
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create a BigML dataset from "(.*)" and a summary file "(.*)" for its fields and store logs in "(.*)"')
def i_create_dataset_with_summary(step, data=None, summary_file=None, output_dir=None):
    ok_(data is not None and output_dir is not None and summary_file is not None)
    world.directory = output_dir
    world.folders.append(world.directory)

    try:
        command = ("bigmler --train " + res_filename(data) +
                   " --no-model --store --output-dir " + output_dir +
                   " --export-fields " + summary_file)

        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output_dir
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create a new dataset juxtaposing both datasets')
def i_create_juxtaposed(step, output_dir=None):
    if output_dir is None:
        assert False
    world.directory = output_dir
    world.folders.append(world.directory)

    try:
        command = ("bigmler dataset --datasets " +
                   os.path.join(output_dir, "dataset") +
                   " --juxtapose --store --output-dir " + output_dir)

        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output_dir
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create a new dataset joining both datasets')
def i_create_join(step, output_dir=None, sql=None):
    print(output_dir, sql)
    if output_dir is None or sql is None:
        assert False
    world.directory = output_dir
    world.folders.append(world.directory)

    try:
        command = ("bigmler dataset --datasets " +
                   os.path.join(output_dir, "dataset") +
                   " --sql-query \"" + sql + "\" --store --output-dir " +
                   output_dir)

        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output_dir
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create a BigML cluster with params "(.*)" from dataset in "(.*)"')
def i_create_cluster_with_params_from_dataset( \
    step, cluster_params=None, output_dir=None):
    ok_(output_dir is not None and cluster_params is not None)
    world.directory = output_dir
    world.folders.append(world.directory)
    try:
        command = ("bigmler cluster --dataset " + world.dataset['resource'] +
                   " --store --output-dir " + output_dir +
                   " " + cluster_params)

        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output_dir
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create a BigML anomaly with params "(.*)" from dataset in "(.*)"')
def i_create_anomaly_with_params_from_dataset( \
    step, params=None, output_dir=None):
    ok_(output_dir is not None and params is not None)
    world.directory = output_dir
    world.folders.append(world.directory)
    try:
        command = ("bigmler anomaly --dataset " + world.dataset['resource'] +
                   " --store --output-dir " + output_dir +
                   " " + params)

        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output_dir
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create a BigML logistic with params "(.*)" from dataset in "(.*)"')
def i_create_logistic_with_params_from_dataset( \
    step, params=None, output_dir=None):
    ok_(output_dir is not None and params is not None)
    world.directory = output_dir
    world.folders.append(world.directory)
    try:
        command = ("bigmler logistic-regression --dataset " +
                   world.dataset['resource'] +
                   " --store --output-dir " + output_dir +
                   " " + params)

        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output_dir
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create a BigML association with params "(.*)" from dataset in "(.*)"')
def i_create_association_with_params_from_dataset( \
    step, params=None, output_dir=None):
    ok_(output_dir is not None and params is not None)
    world.directory = output_dir
    world.folders.append(world.directory)
    try:
        command = ("bigmler association --dataset " +
                   world.dataset['resource'] +
                   " --store --output-dir " + output_dir +
                   " " + params)

        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output_dir
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I import fields attributes in file "(.*)" to dataset$')
def i_import_fields(step, summary=None):
    ok_(summary is not None)
    try:
        command = ("bigmler --dataset " + world.dataset['resource'] +
                   " --import-fields " + res_filename(summary) +
                   " --output-dir " + world.directory + " --no-model")
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'the field "(.*)" has "(.*)" equal to "(.*)"$')
def field_attribute_value(step, field=None, attribute=None,
                          attribute_value=None):
    dataset = check_resource(world.dataset['resource'],
                             world.api.get_dataset)
    fields = dataset['object']['fields']
    eq_(fields[field][attribute], attribute_value)


#@step(r'the cluster params are "(.*)"$')
def i_check_cluster_params(step, params_json=None):
    params_dict = json.loads(params_json)
    for key, value in list(params_dict.items()):
        eq_(value, world.cluster['object'].get(key))


#@step(r'the anomaly params are "(.*)"$')
def i_check_anomaly_params(step, params_json=None):
    params_dict = json.loads(params_json)
    for key, value in list(params_dict.items()):
        eq_(value, world.anomaly['object'].get(key))


#@step(r'the logistic params are "(.*)"$')
def i_check_logistic_params(step, params_json=None):
    params_dict = json.loads(params_json)
    for key, value in list(params_dict.items()):
        eq_(value, world.logistic_regression['object'].get(key))


#@step(r'the association params are "(.*)"$')
def i_check_association_params(step, params_json=None):
    params_dict = json.loads(params_json)
    for key, value in list(params_dict.items()):
        eq_(value, world.association['object'].get(key))

#@step(r'I check that datasets have been juxtaposed')
def i_check_juxtaposed(step, datasets=None):
    rows = world.dataset["object"]["rows"]
    eq_(rows, datasets[0]["object"]["rows"])
    number_of_fields = 0
    for dataset in datasets:
        number_of_fields += dataset["object"]["field_types"]["total"]
    eq_(number_of_fields, world.dataset["object"]["field_types"]["total"])

#@step(r'I check that datasets have been joined')
def i_check_joined(step, rows=None):
    eq_(rows, world.dataset["object"]["rows"])
