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
