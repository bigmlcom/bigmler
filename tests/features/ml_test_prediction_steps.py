import os
import time
import csv
import json
from lettuce import step, world
from subprocess import check_call, CalledProcessError
from bigmler.checkpoint import file_number_of_lines

@step(r'I create BigML multi-label resources tagged as "(.*)" with "(.*)" label separator and (\d*) labels uploading train "(.*)" file with "(.*)" field separator to test "(.*)" and log predictions in "(.*)"')
def i_create_all_ml_resources(step, tag=None, label_separator=None, number_of_labels=None, data=None, training_separator=None, test=None, output=None):
    if tag is None or label_separator is None or training_separator is None or number_of_labels is None or data is None or test is None or output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    world.number_of_models = int(number_of_labels)
    try:
        command = "bigmler --multi-label --train " + data + " --label-separator \"" + label_separator + "\" --training-separator \"" + training_separator + "\" --test " + test + " --store --output " + output + " --tag " + tag + " --max-batch-models 1"
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)



@step(r'I create BigML multi-label resources using models tagged as "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_predict_ml_from_model_tag(step, tag=None, test=None, output=None):
    if tag is None or test is None or output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        command = "bigmler --multi-label --model-tag " + tag + " --test " + test + " --store --output " + output + " --max-batch-models 1"
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

@step(r'I create BigML multi-label resources with labels "(.*)" using models tagged as "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_predict_ml_from_model_tag_with_labels(step, labels=None, tag=None, test=None, output=None):
    if tag is None or labels is None or test is None or output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        command = "bigmler --multi-label --model-tag " + tag + " --labels " + labels + " --test " + test + " --store --output " + output + " --max-batch-models 1"
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

@step(r'I create BigML multi-label resources tagged as "(.*)" with "(.*)" label separator and (\d*) labels uploading train "(.*)" file with "(.*)" field separator and (\d+) models ensembles to test "(.*)" and log predictions in "(.*)"')
def i_create_all_ml_resources_and_ensembles(step, tag=None, label_separator=None, number_of_labels=None, data=None, training_separator=None, number_of_models=None, test=None, output=None):
    if tag is None or label_separator is None or training_separator is None or number_of_labels is None or data is None or test is None or output is None or number_of_models is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    world.number_of_models = int(number_of_labels) * int(number_of_models)
    try:
        command = "bigmler --multi-label --train " + data + " --label-separator \"" + label_separator + "\" --training-separator \"" + training_separator + "\" --test " + test + " --number-of-models " + str(number_of_models) + " --store --output " + output + " --tag " + tag + " --max-batch-models 1"
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


@step(r'I create BigML (multi-label\s)?resources using source and (\d+) models ensembles to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_and_ensembles_from_source(step, multi_label=None, number_of_models=None, test=None, output=None):
    if test is None or output is None or number_of_models is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    multi_label = "" if multi_label is None else " --multi-label " 
    try:
        retcode = check_call("bigmler "+ multi_label +"--source " + world.source['resource'] + " --number-of-models " + str(number_of_models) + " --test " + test + " --store --output " + output, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

@step(r'I create BigML (multi-label\s)?resources using dataset and (\d+) models ensembles to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_and_ensembles_from_dataset(step, multi_label=None, number_of_models=None, test=None, output=None):
    if test is None or output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    multi_label = "" if multi_label is None else " --multi-label " 
    try:
        retcode = check_call("bigmler "+ multi_label +"--dataset " + world.dataset['resource'] + " --number-of-models " + str(number_of_models) + " --test " + test + " --store --output " + output, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)
