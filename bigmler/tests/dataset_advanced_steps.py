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
import json
import sys

from bigml.api import check_resource

from bigmler.tests.common_steps import base_shell_execute
from bigmler.tests.world import world, res_filename, ok_, eq_


def i_create_dataset(step, data=None, output_dir=None):
    """Step: I create a BigML dataset from <data> and store logs in
    <output_dir>
    """
    ok_(data is not None and output_dir is not None)
    command = ("bigmler --train " + res_filename(data) +
               " --no-model --store --output-dir " + output_dir)
    message = base_shell_execute(command, output_dir)
    ok_(message is None, msg=message)


def i_create_dataset_from_source(step, output_dir=None):
    """Step: I create a BigML dataset from previous source and store logs in
    <output_dir>
    """
    ok_(output_dir is not None)
    command = (("bigmler --source %s" % world.source['resource']) +
               " --no-model --store --output-dir " + output_dir)
    message = base_shell_execute(command, output_dir)
    ok_(message is None, msg=message)


def i_create_filtered_dataset_from_dataset(
    step, filter_exp=None, output_dir=None):
    """Step: I create a BigML filtered dataset with filter <filter_exp>
    from previous dataset and store logs in <output_dir>
    """
    ok_(filter_exp is not None and output_dir is not None)
    if sys.platform != 'win32':
        filter_exp = '"%s"' % filter_exp.replace('"', '\\"')
    command = ('echo ' +
               filter_exp + ' > ' +
               output_dir + "/filter.lisp")
    message = base_shell_execute(command, output_dir)
    ok_(message is None, msg=message)
    command = (("bigmler --dataset %s" % world.dataset['resource']) +
               " --no-model --store --output-dir " + output_dir +
               " --lisp-filter " + output_dir + "/filter.lisp")
    message = base_shell_execute(command, output_dir)
    ok_(message is None, msg=message)


def i_create_dataset_new_fields(step, json_file=None, model_fields=None):
    """Step: I create a new BigML dataset using the specs in JSON file
    <json_file> and a model with <model_fields>
    """
    ok_(json_file is not None and model_fields is not None)
    json_file = res_filename(json_file)
    command = ("bigmler --dataset " + world.dataset['resource'] +
               " --model-fields \"" + model_fields + "\" --store" +
               " --output-dir " + world.directory +
               " --new-fields " + json_file)
    message = base_shell_execute(command, world.directory)
    ok_(message is None, msg=message)


def i_update_dataset_new_properties(step, json_file=None):
    """Step: I update the dataset using the specs in JSON file <json_file>"""
    ok_(json_file is not None)
    json_file = res_filename(json_file)
    command = ("bigmler --dataset " + world.dataset['resource'] +
               " --no-model --store --output-dir " + world.directory +
               " --dataset-attributes " + json_file)
    message = base_shell_execute(command, world.directory)
    ok_(message is None, msg=message)


def i_check_dataset_has_field(step, field):
    """Step: I check that the new dataset has field <field>"""
    fields = world.dataset['object']['fields']
    for field_id in fields:
        if fields[field_id]['name'] == field:
            ok_(True)
            return
    ok_(False)


def i_check_dataset_has_property(
    step, attribute=None, field_id=None, value=None, attr_type=None):
    """Step: I check that property <attribute> for field id <field_id> is
    <value> of type <type>
    """
    if attribute is None or field_id is None or value is None:
        assert False
    fields = world.dataset['object']['fields']
    if attr_type == "boolean":
        value = bool(value)
    if attr_type == "integer":
        value = int(value)
    if fields[field_id][attribute] == value:
        ok_(True)
        return
    ok_(False)


def i_create_multi_dataset(step, output_dir):
    """Step: I create a multi-dataset from the datasets file and store logs
    in <output_dir>
    """
    ok_(output_dir is not None)
    datasets_file = os.path.join(world.directory, "dataset")
    command = ("bigmler --datasets " + datasets_file +
               " --multi-dataset --no-model --store --output-dir " +
               output_dir)
    message = base_shell_execute(command, output_dir)
    ok_(message is None, msg=message)


def i_check_multi_dataset_origin(step, output_dir=None):
    """Step: I check that the multi-dataset\'s origin are the datasets in
    <output_dir>
    """
    ok_(output_dir is not None)
    datasets_file = os.path.join(output_dir, "dataset")
    message = None
    try:
        origin_datasets = world.dataset['object']['origin_datasets']
        count = 0
        with open(datasets_file) as datasets_file_handler:
            for dataset_id in datasets_file_handler:
                dataset_id = dataset_id.strip()
                ok_(dataset_id in origin_datasets,
                    msg=f"{dataset_id} not in {origin_datasets}")
                count += 1
        eq_(count, len(origin_datasets))
    except KeyError as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_filter_field_from_dataset(step, field=None, output_dir=None):
    """Step: I filter out field <field> from dataset and log to <output_dir>"""
    ok_(field is not None and output_dir is not None)
    empty_json = res_filename('data/empty.json')
    command = ("bigmler --dataset " + world.dataset['resource'] +
               " --no-model --store --output-dir " + output_dir +
               " --dataset-fields=\"-" + field + "\""+
               " --new-fields " + empty_json)
    message = base_shell_execute(command, world.directory)
    ok_(message is None, msg=message)


def i_check_create_multi_dataset(step):
    """Step: I check that the multi-dataset has been created"""
    dataset_file = os.path.join(world.directory, "dataset_multi")
    message = None
    try:
        with open(dataset_file) as dataset_file_handler:
            dataset_id = dataset_file_handler.readline().strip()
        dataset = check_resource(dataset_id,
                                 world.api.get_dataset)
        world.datasets.append(dataset['resource'])
        world.dataset = dataset
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_files_equal(step, local_file, data):
    """Step: file <local_file> is like file <data>"""
    data = res_filename(data)
    with open(os.path.join(world.directory, local_file)) as handler:
        contents_local = handler.read()
    with open(data) as handler:
        contents = handler.read()
    eq_(contents_local, contents)


def i_export_the_dataset(step, filename):
    """Step: I export the dataset to the CSV file <filename>"""
    ok_(filename is not None)
    command = ("bigmler --dataset " + world.dataset['resource'] +
               " --to-csv " + filename +
               " --output-dir " + world.directory + " --no-model")
    message = base_shell_execute(command, world.directory)
    ok_(message is None, msg=message)


def i_create_dataset_with_summary(
    step, data=None, summary_file=None, output_dir=None):
    """Step: I create a BigML dataset from <data> and a summary file
    <summary_file> for its fields and store logs in <output_dir>
    """
    ok_(data is not None and output_dir is not None and
        summary_file is not None)
    command = ("bigmler --train " + res_filename(data) +
               " --no-model --store --output-dir " + output_dir +
               " --export-fields " + summary_file)
    message = base_shell_execute(command, output_dir)
    ok_(message is None, msg=message)


def i_create_juxtaposed(step, output_dir=None):
    """Step: I create a new dataset juxtaposing both datasets"""
    ok_(output_dir is not None)
    command = ("bigmler dataset --datasets " +
               os.path.join(output_dir, "dataset") +
               " --juxtapose --store --output-dir " + output_dir)
    message = base_shell_execute(command, output_dir)
    ok_(message is None, msg=message)


def i_create_join(step, output_dir=None, sql=None):
    """Step: I create a new dataset joining both datasets"""
    ok_(output_dir is not None and sql is not None)
    command = ("bigmler dataset --datasets " +
               os.path.join(output_dir, "dataset") +
               " --sql-query \"" + sql + "\" --store --output-dir " +
               output_dir)
    message = base_shell_execute(command, output_dir)
    ok_(message is None, msg=message)


def i_create_cluster_with_params_from_dataset(
    step, cluster_params=None, output_dir=None):
    """Step: I create a BigML cluster with params <cluster_params> from dataset
    in <output_dir>
    """
    ok_(output_dir is not None and cluster_params is not None)
    command = ("bigmler cluster --dataset " + world.dataset['resource'] +
               " --store --output-dir " + output_dir +
               " " + cluster_params)
    message = base_shell_execute(command, output_dir)
    ok_(message is None, msg=message)


def i_create_anomaly_with_params_from_dataset(
    step, params=None, output_dir=None):
    """Step: I create a BigML anomaly with params <params> from dataset in
    <output_dir>
    """
    ok_(output_dir is not None and params is not None)
    command = ("bigmler anomaly --dataset " + world.dataset['resource'] +
               " --store --output-dir " + output_dir +
               " " + params)
    message = base_shell_execute(command, output_dir)
    ok_(message is None, msg=message)


def i_create_logistic_with_params_from_dataset(
    step, params=None, output_dir=None):
    """Step: I create a BigML logistic with params <params> from dataset in
    <output_dir>
    """
    ok_(output_dir is not None and params is not None)
    command = ("bigmler logistic-regression --dataset " +
               world.dataset['resource'] +
               " --store --output-dir " + output_dir +
               " " + params)
    message = base_shell_execute(command, output_dir)
    ok_(message is None, msg=message)


def i_create_association_with_params_from_dataset(
    step, params=None, output_dir=None):
    """Step: I create a BigML association with params <params> from dataset in
    <output_dir>
    """
    ok_(output_dir is not None and params is not None)
    command = ("bigmler association --dataset " +
               world.dataset['resource'] +
               " --store --output-dir " + output_dir +
               " " + params)
    message = base_shell_execute(command, output_dir)
    ok_(message is None, msg=message)


def i_import_fields(step, summary=None):
    """Step: I import fields attributes in file <summary> to dataset"""
    ok_(summary is not None)
    command = ("bigmler --dataset " + world.dataset['resource'] +
               " --import-fields " + res_filename(summary) +
               " --output-dir " + world.directory + " --no-model")
    message = base_shell_execute(command, world.directory)
    ok_(message is None, msg=message)


def field_attribute_value(step, field=None, attribute=None,
                          attribute_value=None):
    """Step: the field <field> has <attribute> equal to <attribute_value>"""
    dataset = check_resource(world.dataset['resource'],
                             world.api.get_dataset)
    fields = dataset['object']['fields']
    eq_(fields[field][attribute], attribute_value)


def i_check_cluster_params(step, params_json=None):
    """Step: the cluster params are <params_json>"""
    params_dict = json.loads(params_json)
    for key, value in list(params_dict.items()):
        eq_(value, world.cluster['object'].get(key))


def i_check_anomaly_params(step, params_json=None):
    """Step: the anomaly params are <params_json>"""
    params_dict = json.loads(params_json)
    for key, value in list(params_dict.items()):
        eq_(value, world.anomaly['object'].get(key))


def i_check_logistic_params(step, params_json=None):
    """Step: the logistic params are <params_json>"""
    params_dict = json.loads(params_json)
    for key, value in list(params_dict.items()):
        eq_(value, world.logistic_regression['object'].get(key))


def i_check_association_params(step, params_json=None):
    """Step: the association params are <params_json>"""
    params_dict = json.loads(params_json)
    for key, value in list(params_dict.items()):
        eq_(value, world.association['object'].get(key))


def i_check_juxtaposed(step, datasets=None):
    """Step: I check that datasets have been juxtaposed"""
    rows = world.dataset["object"]["rows"]
    eq_(rows, datasets[0]["object"]["rows"])
    number_of_fields = 0
    for dataset in datasets:
        number_of_fields += dataset["object"]["field_types"]["total"]
    eq_(number_of_fields, world.dataset["object"]["field_types"]["total"])


def i_check_joined(step, rows=None):
    """Step: I check that datasets have been joined"""
    eq_(rows, world.dataset["object"]["rows"])
