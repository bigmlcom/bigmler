import os
import time
import csv
import json
from lettuce import step, world
from subprocess import check_call, CalledProcessError
from bigmler.checkpoint import file_number_of_lines
from bigml.api import check_resource
from common_steps import check_debug

@step(r'I create a BigML dataset from "(.*)" and store logs in "(.*)"')
def i_create_dataset(step, data=None, output_dir=None):
    if data is None:
        assert False
    world.directory = output_dir
    world.folders.append(world.directory)
    try:
        command = ("bigmler --train " + data +
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


@step(r'I create a new BigML dataset using the specs in JSON file "(.*)"')
def i_create_dataset_new_fields(step, json_file=None):
    if json_file is None:
        assert False
    try:
        command = ("bigmler --dataset " + world.dataset['resource'] +
                   " --no-model --store --output-dir " + world.output +
                   " --new-fields " + json_file)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

@step(r'I update the dataset using the specs in JSON file "(.*)"')
def i_update_dataset_new_properties(step, json_file=None):
    if json_file is None:
        assert False
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


@step(r'I check that the new dataset has field "(.*)"')
def i_check_dataset_has_field(step, field):
    fields = world.dataset['object']['fields']
    for field_id in fields:
        if fields[field_id]['name'] == field:
            assert True
            return
    assert False


@step(r'I check that property "(.*)" for field id "(.*)" is "(.*)" of type "(.*)"')
def i_check_dataset_has_field(step, attribute=None, field_id=None, value=None, type=None):
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


@step(r'I create a multi-dataset from the datasets file and store logs in "(.*)"')
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


@step(r'I check that the multi-dataset\'s origin are the datasets in "(.*)"')
def i_check_multi_dataset_origin(step, output_dir=None):
    if output_dir is None:
        assert False
    datasets_file = "%s%sdataset" % (output_dir, os.sep) 
    try:
        origin_datasets = world.dataset['object']['ranges'].keys()
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

@step(r'I filter out field "(.*)" from dataset and log to "(.*)"')
def i_filter_field_from_dataset(step, field=None, output_dir=None):
    if field is None or output_dir is None:
        assert False
    try:
        command = ("bigmler --dataset " + world.dataset['resource'] +
                   " --no-model --store --output-dir " + output_dir +
                   " --dataset-fields=\"-" + field + "\""+
                   " --new-fields ../data/empty.json")
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

@step(r'I check that the multi-dataset has been created$')
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
    except Exception, exc:
        assert False, str(exc)

@step(r'file "(.*)" is like file "(.*)"$')
def i_files_equal(step, local_file, data):
    contents_local_file = open(os.path.join(world.directory,
                                            local_file)).read()
    contents_data = open(data).read()
    assert contents_local_file == contents_data

@step(r'I export the dataset to the CSV file "(.*)"$')
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
