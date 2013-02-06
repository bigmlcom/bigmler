import os
import time
from lettuce import step, world
from subprocess import call


@step(r'I create BigML resources uploading train "(.*)" file to test "(.*)" and log predictions in "(.*)"')
def i_create_all_resources(step, data=None, test=None, output=None):
    if data is None or test is None or output is None:
        assert False
    try:
        retcode = call("bigmler --train " + data + " --test " + test + " --output " + output + " --max-batch-models 1", shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = 0
            for line in open(test, "r"):
                world.test_lines += 1
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


@step(r'I create BigML resources using source to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_source(step, test=None, output=None):
    if test is None or output is None:
        assert False
    try:
        retcode = call("bigmler --source " + world.source['resource'] + " --test " + test + " --output " + output, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = 0
            for line in open(test, "r"):
                world.test_lines += 1
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


@step(r'I create BigML resources using dataset to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_source(step, test=None, output=None):
    if test is None or output is None:
        assert False
    try:
        retcode = call("bigmler --dataset " + world.dataset['resource'] + " --test " + test + " --output " + output, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = 0
            for line in open(test, "r"):
                world.test_lines += 1
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False

@step(r'I create BigML resources using dataset, objective field (.*) and model fields (.*) to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_source(step, objective=None, fields=None, test=None, output=None):
    if objective is None or fields is None or test is None or output is None:
        assert False
    try:
        retcode = call("bigmler --dataset " + world.dataset['resource'] + " --objective " + objective + " --model-fields " + fields + " --test " + test + " --output " + output, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = 0
            for line in open(test, "r"):
                world.test_lines += 1
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False

@step(r'I create BigML resources using model to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_source(step, test=None, output=None):
    if test is None or output is None:
        assert False
    try:
        retcode = call("bigmler --model " + world.model['resource'] + " --test " + test + " --output " + output + " --max-batch-models 1", shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = 0
            for line in open(test, "r"):
                world.test_lines += 1
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


@step(r'I create BigML resources using ensemble of (.*) models to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_source(step, number_of_models=None, test=None, output=None):
    if number_of_models is None or test is None or output is None:
        assert False
    try:
        retcode = call("bigmler --dataset " + world.dataset['resource'] + " --test " + test + " --number-of-models " + number_of_models + " --tag my_ensemble --output " + output, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = 0
            for line in open(test, "r"):
                world.test_lines += 1
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            world.number_of_models = int(number_of_models)
            assert True
    except OSError as e:
        assert False


@step(r'I create BigML resources using models in file "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_source(step, models_file=None, test=None, output=None):
    if models_file is None or test is None or output is None:
        assert False
    try:
        retcode = call("bigmler --models " + models_file + " --test " + test + " --output " + output, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = 0
            for line in open(test, "r"):
                world.test_lines += 1
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


@step(r'I create BigML resources using dataset in file "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_source(step, dataset_file=None, test=None, output=None):
    if dataset_file is None or test is None or output is None:
        assert False
    try:
        retcode = call("bigmler --datasets " + dataset_file + " --test " + test + " --output " + output, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = 0
            for line in open(test, "r"):
                world.test_lines += 1
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


@step(r'I combine BigML predictions files in "(.*)" and "(.*)" into "(.*)"')
def i_find_predictions_files(step, directory1=None, directory2=None, output=None):
    if directory1 is None or directory2 is None or output is None:
        assert False
    try:
        retcode = call("bigmler --combine-votes " + directory1 + "," + directory2 + " --output " + output, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = 0
            for line in open("%s%spredictions.csv" % (directory1, os.sep), "r"):
                world.test_lines += 1
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


@step(r'I combine BigML predictions files in "(.*)" and "(.*)" into "(.*)" with method "(.*)"')
def i_find_predictions_files(step, directory1=None, directory2=None, output=None, method=None):
    if directory1 is None or directory2 is None or output is None or method is None:
        assert False
    try:
        retcode = call("bigmler --combine-votes " + directory1 + "," + directory2 + " --output " + output + " --method " + method, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = 0
            for line in open("%s%spredictions.csv" % (directory1, os.sep), "r"):
                world.test_lines += 1
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


@step(r'I check that the source has been created')
def i_check_create_source(step):
    source_file = "%s%ssource" % (world.directory, os.sep)
    try:
        source_file = open(source_file, "r")
        source = world.api.check_resource(source_file.readline().strip(),
                                             world.api.get_source)
        world.sources.append(source['resource'])
        world.source = source
        source_file.close()
        assert True
    except:
        assert False


@step(r'I check that the dataset has been created')
def i_check_create_dataset(step):
    dataset_file = "%s%sdataset" % (world.directory, os.sep)
    try:
        dataset_file = open(dataset_file, "r")
        dataset = world.api.check_resource(dataset_file.readline().strip(),
                                             world.api.get_dataset)
        world.datasets.append(dataset['resource'])
        world.dataset = dataset
        dataset_file.close()
        assert True
    except:
        assert False


@step(r'I check that the model has been created')
def i_check_create_model(step):
    model_file = "%s%smodels" % (world.directory, os.sep)
    try:
        model_file = open(model_file, "r")
        model = world.api.check_resource(model_file.readline().strip(),
                                             world.api.get_model)
        world.models.append(model['resource'])
        world.model = model
        model_file.close()
        assert True
    except:
        assert False

@step(r'I check that the models have been created')
def i_check_create_models(step):
    model_file = "%s%smodels" % (world.directory, os.sep)
    model_ids = []
    number_of_lines = 0
    count = 0
    while world.number_of_models != number_of_lines and count < 10:
        for line in open(model_file, "r"):
            number_of_lines += 1
            model_id = line.strip()
            model_ids.append(model_id)
        if world.number_of_models != number_of_lines:
            number_of_lines = 0
            time.sleep(10)
            count += 1
    if world.number_of_models != number_of_lines:
        assert False
    world.model_ids = model_ids
    for model_id in model_ids:
        try:
            model = world.api.check_resource(model_id, world.api.get_model)
            world.models.append(model_id)
            assert True
        except:
            assert False


@step(r'I check that the predictions are ready')
def i_check_create_predictions(step):

    previous_lines = -1
    predictions_lines = 0
    while previous_lines != predictions_lines:
        try:
            predictions_file = world.output
            predictions_file = open(predictions_file, "r")
            predictions_lines = 0
            for line in predictions_file:
                predictions_lines += 1
            if predictions_lines == world.test_lines:
                assert True
            else:
                previous_lines = predictions_lines
                time.sleep(10)
            predictions_file.close()
        except:
            assert False


@step(r'the local prediction file is like "(.*)"')
def i_check_predictions(step, check_file):
    predictions_file = world.output
    try:
        predictions_file = open(predictions_file, "U")
        check_file = open(check_file, "U")
        for line in predictions_file:
            check_line = check_file.readline()
            if check_line != line:
                print line, check_line
                assert False
        predictions_file.close()
        check_file.close()
        assert True
    except:
        assert False
