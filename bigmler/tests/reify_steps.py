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
import re


from bigmler.utils import open_mode
from bigmler.tests.common_steps import shell_execute
from bigmler.tests.world import world, res_filename, ok_, eq_


INDENT = ' ' * 4

def python3_contents(filename, prior_contents, alternative=""):
    """Check for a file that has alternative contents for Python3 and return
       its contents

    """
    directory = os.path.dirname(filename)
    basename = os.path.basename(filename)
    basename_name, basename_ext = basename.split(".")
    filename = os.path.join(directory, "%s_py3%s.%s" % ( \
        basename_name, alternative, basename_ext))
    try:
        with open(filename, open_mode("r")) as file_handler:
            return file_handler.read().strip("\n")
    except IOError:
        return prior_contents


def i_create_output(
    step, output=None, language=None, resource_type='source',
    add_fields=False):
    """Step: I create a reify output for the resource in <language> for
    <resource_type> <add_fields> and log results in <output>
    """
    ok_(output is not None and language is not None)
    resource_id = getattr(world, resource_type)['resource']
    command = ("bigmler reify --id " + resource_id + " --language " +
               language + " --store --output " + output)
    if add_fields:
        command += ' --add-fields'
    shell_execute(command, output)


def i_check_output_file(step, output=None, check_file=None):
    """Step: the <output> file is like <check_file>"""
    ok_(check_file is not None and output is not None)
    check_file = res_filename(check_file)
    output_file = os.path.join(world.directory, os.path.basename(output))
    with open(check_file, open_mode("r")) as check_file_handler:
        check_contents = check_file_handler.read().strip("\n")

    with open(output_file, open_mode("r")) as output_file:
        output_file_contents = output_file.read()

    #strip comments at the beginning of the file
    output_file_contents = re.sub(r'#!.*def\smain\(\):\n', '',
                                  output_file_contents,
                                  flags=re.S).strip("\n")
    output_file_contents = output_file_contents.replace( \
        '\nif __name__ == "__main__":\n    main()', '')

    #strip internally added project id information
    p_str = r'\'project\':\s\'project/[a-f0-9]{24}\',?\s?'
    output_file_contents = re.sub(p_str,
                                  '', output_file_contents,
                                  flags=re.S).strip("\n")
    p_str = r'/[a-f0-9]{24}'
    output_file_contents = re.sub(p_str,
                                  '', output_file_contents,
                                  flags=re.S)
    check_contents = re.sub(p_str,
                            '', check_contents,
                            flags=re.S)
    p_str = r';;.*\n'
    output_file_contents = re.sub(p_str,
                                  '', output_file_contents,
                                  flags=re.S)
    check_contents = re.sub(p_str,
                            '', check_contents,
                            flags=re.S)
    p_str = r'created by.*\n'
    output_file_contents = re.sub(p_str,
                                  '', output_file_contents,
                                  flags=re.S)
    check_contents = re.sub(p_str,
                            '', check_contents,
                            flags=re.S)
    p_str = r'    api = .*?\n'
    output_file_contents = re.sub(p_str,
                                  '    api = BigML()\n', output_file_contents,
                                  flags=re.S).strip("\n")
    output_file_contents = re.sub(r'\n\s*', '\n', output_file_contents)
    check_contents = re.sub(r'\n\s*', '\n', check_contents)
    output_file_contents = output_file_contents.strip("\n").strip()
    check_contents = check_contents.strip("\n").strip()
    #strip ids added in jupyter notebook transformation
    # e.g.: ,\n"id": "3185730b"
    p_str = r',\n"id":\s"[a-f0-9]{8}"'
    output_file_contents = re.sub(p_str,
                                  '', output_file_contents,
                                  flags=re.S)
    check_contents = re.sub(p_str,
                            '', check_contents,
                            flags=re.S)
    if check_contents != output_file_contents:
        with open("%s" % check_file, "w") as bck_file:
            bck_file.write(output_file_contents)
        eq_(check_contents, output_file_contents)


def create_source(filename, output=None, args=None):
    """Step: I create a BigML source with data <filename> and params <args>"""
    args.update({"project": world.project_id})
    source = world.api.create_source(res_filename(filename), args)
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])


def create_dataset(filename, output=None, args=None):
    """Step: I create a BigML dataset from a source with data <filename>
    and params <args>
    """
    source = world.api.create_source( \
        res_filename(filename), {"project": world.project_id})
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source, args)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])


def create_dataset_from_dataset(filename, output=None, args=None):
    """Step: I create a BigML dataset from dataset with data <filename>
    and params <args>
    """
    source = world.api.create_source( \
        res_filename(filename), {"project": world.project_id})
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    world.dataset = world.api.create_dataset(world.dataset, args)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])


def create_dataset_from_datasets(filename, output=None, args=None):
    """Step: I create a BigML dataset from a list of datasets with data
    <filename> and params <args>
    """
    source = world.api.create_source( \
        res_filename(filename), {"project": world.project_id})
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    datasets = [world.dataset['resource']]
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    datasets.append(world.dataset)
    world.dataset = world.api.create_dataset(datasets, args)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])


def create_model(filename, output=None, args=None):
    """Step: I create a BigML model from a dataset with data <filename>
    and params <args>
    """
    source = world.api.create_source( \
        res_filename(filename), {"project": world.project_id})
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    world.model = world.api.create_model(world.dataset, args)
    world.api.ok(world.model)
    world.models.append(world.model['resource'])


def create_prediction(filename, input_data= None, output=None, args=None):
    """Step: I create a BigML prediction for <filename> from a model with data
    <input_data> and params <args>
    """
    source = world.api.create_source( \
        res_filename(filename), {"project": world.project_id})
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    world.model = world.api.create_model(world.dataset)
    world.api.ok(world.model)
    world.models.append(world.model['resource'])
    world.prediction = world.api.create_prediction( \
        world.model, input_data, args)
    world.api.ok(world.prediction)
    world.predictions.append(world.prediction['resource'])


def create_cluster(filename, output=None, args=None):
    """Step: I create a BigML cluster from a dataset with data <filename>
    and params <args>
    """
    source = world.api.create_source( \
        res_filename(filename), {"project": world.project_id})
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    args.update({"cluster_seed": "bigml"})
    world.cluster = world.api.create_cluster(world.dataset, args)
    world.api.ok(world.cluster)
    world.clusters.append(world.cluster['resource'])


def create_anomaly(filename, output=None, args=None):
    """Step: I create a BigML anomaly from a dataset with data <filename> and
    params <args>
    """
    source = world.api.create_source( \
        res_filename(filename), {"project": world.project_id})
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    args.update({"seed": "bigml", "anomaly_seed": "bigml"})
    world.anomaly = world.api.create_anomaly(world.dataset, args)
    world.api.ok(world.anomaly)
    world.anomalies.append(world.anomaly['resource'])


def create_centroid(filename, input_data=None, output=None, args=None):
    """Step: I create a BigML centroid for <filename> from a cluster with
    data <input_data> and params <args>
    """
    source = world.api.create_source( \
        res_filename(filename), {"project": world.project_id})
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    world.cluster = world.api.create_cluster( \
        world.dataset, {"cluster_seed": "bigml"})
    world.api.ok(world.cluster)
    world.clusters.append(world.cluster['resource'])
    world.centroid = world.api.create_centroid( \
        world.cluster, input_data, args)
    world.api.ok(world.centroid)
    world.centroids.append(world.centroid['resource'])


def create_anomaly_score(filename, input_data=None, output=None, args=None):
    """Step: I create a BigML anomaly score for <filename> from an anomaly
    detector with data <input_data> and params <args>
    """
    source = world.api.create_source( \
        res_filename(filename), {"project": world.project_id})
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    world.anomaly = world.api.create_anomaly( \
        world.dataset, {"seed": "bigml", "anomaly_seed": "bigml"})
    world.api.ok(world.anomaly)
    world.anomalies.append(world.anomaly['resource'])
    world.anomaly_score = world.api.create_anomaly_score( \
        world.anomaly, input_data, args)
    world.api.ok(world.anomaly_score)
    world.anomaly_scores.append(world.anomaly_score['resource'])


def create_batch_prediction(filename, output=None, args=None):
    """Step: I create a BigML batch prediction from a model with data
    <filename> and params <args>
    """
    source = world.api.create_source(res_filename(filename))
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    world.model = world.api.create_model(world.dataset)
    world.api.ok(world.model)
    world.models.append(world.model['resource'])
    world.batch_prediction = world.api.create_batch_prediction( \
        world.model, world.dataset, args)
    world.api.ok(world.batch_prediction)
    world.batch_predictions.append(world.batch_prediction['resource'])


def create_batch_centroid(filename, output=None, args=None):
    """Step: I create a BigML batch centroid from a cluster with data
    <filename> and params <args>
    """
    source = world.api.create_source( \
        res_filename(filename), {"project": world.project_id})
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    world.cluster = world.api.create_cluster( \
        world.dataset, {"cluster_seed": "bigml"})
    world.api.ok(world.cluster)
    world.clusters.append(world.cluster['resource'])
    world.batch_centroid = world.api.create_batch_centroid( \
        world.cluster, world.dataset, args)
    world.api.ok(world.batch_centroid)
    world.batch_centroids.append(world.batch_centroid['resource'])


def create_batch_anomaly_score(filename, output=None, args=None):
    """Step: I create a BigML batch anomaly score from an anomaly detector
    with data <filename> and params <args>
    """
    source = world.api.create_source( \
        res_filename(filename), {"project": world.project_id})
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    world.anomaly = world.api.create_anomaly( \
        world.dataset, {"seed": "bigml", "anomaly_seed": "bigml"})
    world.api.ok(world.anomaly)
    world.anomalies.append(world.anomaly['resource'])
    world.batch_anomaly_score = world.api.create_batch_anomaly_score( \
        world.anomaly, world.dataset, args)
    world.api.ok(world.batch_anomaly_score)
    world.batch_anomaly_scores.append(world.batch_anomaly_score['resource'])


def create_evaluation(filename, output=None, args=None):
    """Step: I create a BigML evaluation with data <filename> and params
    <args>
    """
    source = world.api.create_source( \
        res_filename(filename), {"project": world.project_id})
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    world.model = world.api.create_model(world.dataset)
    world.api.ok(world.model)
    world.models.append(world.model['resource'])
    world.evaluation = world.api.create_evaluation( \
        world.model, world.dataset, args)
    world.api.ok(world.evaluation)
    world.evaluations.append(world.evaluation['resource'])


def create_ensemble(filename, output=None, args=None):
    """Step: I create a BigML ensemble from a dataset with data <filename>
    and params <args>
    """
    source = world.api.create_source( \
        res_filename(filename), {"project": world.project_id})
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    args.update({"seed": "BigML", "ensemble_sample": {"seed": "bigml"}})
    world.ensemble = world.api.create_ensemble(world.dataset, args)
    world.api.ok(world.ensemble)
    world.ensembles.append(world.ensemble['resource'])


def create_evaluation_split(filename, output=None, args=None):
    """Step: I create a BigML evaluation with data <filename> split
    training/test and params <args>
    """
    source = world.api.create_source( \
        res_filename(filename), {"project": world.project_id})
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    world.dataset_train = world.api.create_dataset(world.dataset, { \
        'sample_rate': 0.7, 'seed': 'BigML'})
    world.api.ok(world.dataset_train)
    world.datasets.append(world.dataset_train['resource'])
    world.dataset_test = world.api.create_dataset(world.dataset, { \
        'sample_rate': 0.7, 'seed': 'BigML', 'out_of_bag': True})
    world.api.ok(world.dataset_test)
    world.datasets.append(world.dataset_test['resource'])
    world.model = world.api.create_model(world.dataset_train)
    world.api.ok(world.model)
    world.models.append(world.model['resource'])
    world.evaluation = world.api.create_evaluation( \
        world.model, world.dataset_test, args)
    world.api.ok(world.evaluation)
    world.evaluations.append(world.evaluation['resource'])


def create_dataset_from_batch_prediction(filename, output=None, args=None):
    """Step: I create a BigML dataset from a batch prediction from a model
    with data <filename> and params <args>
    """
    source = world.api.create_source(res_filename(filename))
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    world.model = world.api.create_model(world.dataset)
    world.api.ok(world.model)
    world.models.append(world.model['resource'])
    world.batch_prediction = world.api.create_batch_prediction( \
        world.model, world.dataset, {"output_dataset": True})
    world.api.ok(world.batch_prediction)
    world.batch_predictions.append(world.batch_prediction['resource'])
    world.batch_prediction_dataset = world.api.get_dataset(
        world.batch_prediction['object']['output_dataset_resource'])
    world.api.ok(world.batch_prediction_dataset)
    world.batch_prediction_dataset = world.api.update_dataset( \
        world.batch_prediction_dataset, args)
    world.api.ok(world.batch_prediction_dataset)
    world.datasets.append(world.batch_prediction_dataset['resource'])


def create_dataset_from_batch_centroid(filename, output=None, args=None):
    """Step: I create a BigML dataset from a batch centroid from a cluster
    with data <filename> and params <args>
    """
    source = world.api.create_source(res_filename(filename))
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    world.cluster = world.api.create_cluster \
        (world.dataset, {"cluster_seed": "bigml"})
    world.api.ok(world.cluster)
    world.clusters.append(world.cluster['resource'])
    world.batch_centroid = world.api.create_batch_centroid( \
        world.cluster, world.dataset, {"output_dataset": True})
    world.api.ok(world.batch_centroid)
    world.batch_centroids.append(world.batch_centroid['resource'])
    world.batch_centroid_dataset = world.api.get_dataset(
        world.batch_centroid['object']['output_dataset_resource'])
    world.api.ok(world.batch_centroid_dataset)
    world.batch_centroid_dataset = world.api.update_dataset( \
        world.batch_centroid_dataset, args)
    world.api.ok(world.batch_centroid_dataset)
    world.datasets.append(world.batch_centroid_dataset['resource'])


def create_dataset_from_batch_anomaly(filename, output=None, args=None):
    """Step: I create a BigML dataset from a batch anomaly score from an
    anomaly detector with data <filename> and params <args>
    """
    source = world.api.create_source(res_filename(filename))
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    world.anomaly = world.api.create_anomaly(world.dataset,
                                             {"seed": "bigml",
                                              "anomaly_seed": "bigml"})
    world.api.ok(world.anomaly)
    world.anomalies.append(world.anomaly['resource'])
    world.batch_anomaly_score = world.api.create_batch_anomaly_score( \
        world.anomaly, world.dataset, {"output_dataset": True})
    world.api.ok(world.batch_anomaly_score)
    world.batch_anomaly_scores.append(world.batch_anomaly_score['resource'])
    world.batch_anomaly_score_dataset = world.api.get_dataset(
        world.batch_anomaly_score['object']['output_dataset_resource'])
    world.api.ok(world.batch_anomaly_score_dataset)
    world.batch_anomaly_score_dataset = world.api.update_dataset( \
        world.batch_anomaly_score_dataset, args)
    world.api.ok(world.batch_anomaly_score_dataset)
    world.datasets.append(world.batch_anomaly_score_dataset['resource'])


def create_dataset_from_dataset_from_batch_centroid(
    filename, output=None, args=None):
    """Step: I create a BigML dataset from a dataset from a batch centroid
    from a cluster with data <filename> and params <args>
    """
    source = world.api.create_source(res_filename(filename))
    world.source = source
    world.directory = os.path.dirname(output)
    world.output = output
    world.api.ok(world.source)
    world.sources.append(source['resource'])
    world.dataset = world.api.create_dataset(source)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
    world.cluster = world.api.create_cluster( \
        world.dataset, {"cluster_seed": "bigml"})
    world.api.ok(world.cluster)
    world.clusters.append(world.cluster['resource'])
    world.batch_centroid = world.api.create_batch_centroid( \
        world.cluster, world.dataset, {"output_dataset": True})
    world.api.ok(world.batch_centroid)
    world.batch_centroids.append(world.batch_centroid['resource'])
    world.batch_centroid_dataset = world.api.get_dataset(
        world.batch_centroid['object']['output_dataset_resource'])
    world.api.ok(world.batch_centroid_dataset)
    world.datasets.append(world.batch_centroid_dataset['resource'])
    world.dataset = world.api.create_dataset( \
        world.batch_centroid_dataset['resource'], args)
    world.api.ok(world.dataset)
    world.datasets.append(world.dataset['resource'])
