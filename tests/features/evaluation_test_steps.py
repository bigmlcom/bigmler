import os
import time
try:
    import simplejson as json
except ImportError:
    import json
from lettuce import step, world
from subprocess import check_call
from bigml.api import check_resource


@step(r'I create BigML resources using source to evaluate and log evaluation in "(.*)"')
def given_i_create_bigml_resources_using_source_to_evaluate(step, output=None):
    if output is None:
        assert False
    try:
        retcode = check_call("bigmler --evaluate --source " + world.source['resource'] + " --output " + output, shell=True)
        if retcode < 0:
            assert False
        else:
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


@step(r'I create BigML resources using dataset to evaluate and log evaluation in "(.*)"')
def given_i_create_bigml_resources_using_dataset_to_evaluate(step, output=None):
    if output is None:
        assert False
    try:
        retcode = check_call("bigmler --evaluate --dataset " + world.dataset['resource'] + " --output " + output, shell=True)
        if retcode < 0:
            assert False
        else:
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


@step(r'I create BigML resources using test file "([^"]*)" and a fields map "([^"]*)" to evaluate a model and log evaluation in "(.*)"')
def i_create_all_resources_to_evaluate_with_model(step, data=None, fields_map=None, output=None):
    if data is None or fields_map is None or output is None:
        assert False
    try:
        retcode = check_call("bigmler --evaluate --test " + data + " --model " +
                       world.model['resource'] + " --output " + output +
                       " --fields-map " + fields_map,
                       shell=True)
        if retcode < 0:
            assert False
        else:
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


@step(r'I create BigML resources using test file "([^"]*)" to evaluate a model and log evaluation in "(.*)"')
def i_create_all_resources_to_evaluate_with_model(step, data=None, output=None):
    if data is None or output is None:
        assert False
    try:
        retcode = check_call("bigmler --evaluate --test " + data + " --model " +
                       world.model['resource'] + " --output " + output,
                       shell=True)
        if retcode < 0:
            assert False
        else:
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


@step(r'I create BigML resources using a dataset to evaluate a model and log evaluation in "(.*)"')
def given_i_create_bigml_resources_using_dataset_to_evaluate_with_model(step, output=None):
    if output is None:
        assert False
    try:
        retcode = check_call("bigmler --evaluate --dataset " +
                       world.dataset['resource']  + " --model " +
                       world.model['resource'] + " --output " + output,
                       shell=True)
        if retcode < 0:
            assert False
        else:
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


@step(r'I create BigML resources uploading train "(.*)" file to evaluate with test-split (.*) and log evaluation in "(.*)"')
def i_create_with_split_to_evaluate(step, data=None, split=None, output=None):
    if data is None or split is None or output is None:
        assert False
    try:
        retcode = check_call("bigmler --evaluate --train " + data + " --test-split " + split +  " --output " + output, shell=True)
        if retcode < 0:
            assert False
        else:
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


@step(r'the evaluation file is like "(.*)"$')
def then_the_evaluation_file_is_like(step, check_file_json):
    evaluation_file_json = world.output + ".json"
    try:
        evaluation_file_json = open(evaluation_file_json, "U")
        check_file_json = open(check_file_json, "U")
        check = check_file_json.readline()
        evaluation = evaluation_file_json.readline()
        check = json.loads(check)
        evaluation = json.loads(evaluation)
        assert check['model'] == evaluation['model']
        assert check['mode'] == evaluation['mode']
        evaluation_file_json.close()
        check_file_json.close()
    except:
        assert False

@step(r'I check that the (.*) dataset has been created$')
def i_check_create_dataset(step, dataset_type=None):
    dataset_file = "%s%sdataset_%s" % (world.directory, os.sep, dataset_type)
    try:
        dataset_file = open(dataset_file, "r")
        dataset = check_resource(dataset_file.readline().strip(),
                                 world.api.get_dataset)
        world.datasets.append(dataset['resource'])
        world.dataset = dataset
        dataset_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)


@step(r'the evaluation key "(.*)" value for the model is greater than (.*)$')
def i_check_evaluation_key(step, key=None, value=None):
    evaluation_file_json = world.output + ".json"
    try:
        evaluation_file_json = open(evaluation_file_json, "U")
        evaluation = evaluation_file_json.readline()
        evaluation = json.loads(evaluation)
        model_evaluation = evaluation['model']
        assert model_evaluation[key] > float(value), "model evaluation %s: %s" % (key, value)
        evaluation_file_json.close()
    except:
        assert False
