import os
import time
import csv
import json
from lettuce import step, world
from subprocess import check_call, CalledProcessError
from bigml.api import check_resource
from bigmler.processing.models import MONTECARLO_FACTOR
from bigmler.checkpoint import file_number_of_lines
from ml_test_prediction_steps import i_create_all_ml_resources
from ml_test_prediction_steps import i_create_all_ml_resources_and_ensembles
from ml_test_evaluation_steps import i_create_all_ml_resources_for_evaluation
from max_categories_test_prediction_steps import i_check_create_max_categories_datasets, i_create_all_mc_resources
from basic_batch_test_prediction_steps import i_check_create_test_source, i_check_create_test_dataset
from ml_test_prediction_steps import i_create_all_mlm_resources
from common_steps import check_debug


def shell_execute(command, output, test=None, options=None):
    """Excute bigmler command in shell

    """
    command = check_debug(command)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            if test is not None:
                world.test_lines = file_number_of_lines(test)
                if options is None or options.find('--prediction-header') == -1:
                    # test file has headers in it, so first line must be ignored
                    world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

@step(r'I create BigML resources uploading train "(.*?)" file to test "(.*?)" and log predictions in "(.*?)" with "(.*?)" as test field separator$')
def i_create_all_resources_with_separator(step, data=None, test=None, output=None, separator=None):
    if data is None or test is None or separator is None or output is None:
        assert False
    command = ("bigmler --train " + data + " --test " + test +
               " --test-separator " + separator + " --store --output " +
               output + " --max-batch-models 1")
    shell_execute(command, output, test=test)

@step(r'I create BigML resources uploading train "(.*?)" file to test "(.*?)" remotely with mapping file "(.*?)" and log predictions in "([^"]*)"$')
def i_create_all_resources_batch_map(step, data=None, test=None, fields_map=None, output=None):
    if data is None or test is None or output is None or fields_map is None:
        assert False
    command = ("bigmler --train " + data + " --test " + test + " --fields-map "
               + fields_map + " --store --output " + output + " --remote")
    shell_execute(command, output, test=test)


@step(r'I create BigML resources uploading train "(.*?)" file to test "(.*?)" remotely and log predictions in "([^"]*)"$')
def i_create_all_resources_batch(step, data=None, test=None, output=None):
    if data is None or test is None or output is None:
        assert False
    command = ("bigmler --train " + data + " --test " + test +
               " --store --output " + output + " --remote")
    shell_execute(command, output, test=test)


@step(r'I create BigML resources uploading train "(.*?)" file to test "(.*?)" and log predictions in "([^"]*)"$')
def i_create_all_resources(step, data=None, test=None, output=None):
    if data is None or test is None or output is None:
        assert False
    command = ("bigmler --train " + data + " --test " + test +
               " --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=test)


@step(r'I create BigML resources uploading train "(.*?)" file to test "(.*?)" and log predictions in "(.*?)" with prediction options "(.*?)"')
def i_create_all_resources_with_options(step, data=None, test=None, output=None, options=''):
    if data is None or test is None or output is None:
        assert False
    command = ("bigmler --train " + data + " --test " + test +
               " --store --output " + output + " --max-batch-models 1 " +
               options)
    shell_execute(command, output, test=test, options=options)


@step(r'I create BigML (multi-label\s)?resources using source with objective "(.*)" and model fields "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_source_with_objective(step, multi_label=None, objective=None, model_fields=None, test=None, output=None):
    if test is None or output is None:
        assert False

    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler "+ multi_label +"--source " + world.source['resource']
               + " --objective " + objective + " --model-fields ' "
               + model_fields + "' --test " + test
               + " --store --output " + output)
    shell_execute(command, output, test=test)

@step(r'I create BigML (multi-label\s)?resources using source to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_source(step, multi_label=None, test=None, output=None):
    if test is None or output is None:
        assert False

    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler "+ multi_label +"--source " + world.source['resource']
               + " --test " + test + " --store --output " + output)
    shell_execute(command, output, test=test)


@step(r'I create BigML resources using source to test the previous test source remotely and log predictions in "(.*)"')
def i_create_resources_from_source_batch(step, output=None):
    if output is None:
        assert False
    command = ("bigmler --source " + world.source['resource']
               + " --test-source " + world.test_source['resource']
               + " --store --remote --output " + output)
    shell_execute(command, output)

@step(r'I create BigML (multi-label\s)?resources using dataset with objective "(.*)" and model fields "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_dataset_with_objective(step, multi_label=None, objective=None, model_fields=None, test=None, output=None):
    if test is None or output is None:
        assert False

    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler "+ multi_label +"--dataset " + world.dataset['resource']
               + " --objective " + objective + " --model-fields ' "
               + model_fields + "' --test " + test
               + " --store --output " + output)
    shell_execute(command, output, test=test)

@step(r'I create BigML (multi-label\s)?resources using dataset to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_dataset(step, multi_label=None, test=None, output=None):
    if test is None or output is None:
        assert False
    multi_label = "" if multi_label is None else " --multi-label " 
    command = ("bigmler "+ multi_label +"--dataset " +
               world.dataset['resource'] + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)

@step(r'I create BigML resources using dataset to test the previous test dataset remotely and log predictions in "(.*)"')
def i_create_resources_from_dataset_batch(step, output=None):
    if output is None:
        assert False
    command = ("bigmler --dataset " + world.dataset['resource'] + " --test-dataset " +
               world.test_dataset['resource'] + " --store --remote --output " + output)
    shell_execute(command, output)


@step(r'I create BigML resources using dataset, objective field (.*) and model fields (.*) to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_dataset_objective_model(step, objective=None, fields=None, test=None, output=None):
    if objective is None or fields is None or test is None or output is None:
        assert False
    command = ("bigmler --dataset " + world.dataset['resource'] +
               " --objective " + objective + " --model-fields " +
               fields + " --test " + test + " --store --output " + output)
    shell_execute(command, output, test=test)


@step(r'I create BigML resources using model to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_model(step, test=None, output=None):
    if test is None or output is None:
        assert False
    command = ("bigmler --model " + world.model['resource'] + " --test " +
               test + " --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=test)

@step(r'I create BigML resources using the previous ensemble with different thresholds to test "(.*)" and log predictions in "(.*)" and "(.*)"')
def i_create_resources_from_ensemble_with_threshold(step, test=None, output2=None, output3=None):
    if test is None or output2 is None or output3 is None:
        assert False
    try:
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

@step(r'I create BigML resources using ensemble of (.*) models with replacement to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_ensemble_with_replacement(step, number_of_models=None, test=None, output=None):
    i_create_resources_from_ensemble_generic(step, number_of_models, "", test, output)

@step(r'I create BigML resources using ensemble of (.*) models to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_ensemble(step, number_of_models=None, test=None, output=None):
    i_create_resources_from_ensemble_generic(step, number_of_models, " --no-replacement", test, output)

def i_create_resources_from_ensemble_generic(step, number_of_models=None, no_replacement="", test=None, output=None):
    if number_of_models is None or test is None or output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
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

@step(r'I create BigML (multi-label\s)?resources using models in file "(.*)" with objective "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_models_file_with_objective(step, multi_label=None, models_file=None, objective=None, test=None, output=None):
    if (models_file is None or test is None or output is None
            or objective is None):
        assert False
    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler "+ multi_label +"--models " + models_file + " --test "
               + test + " --store --output " + output
               + " --objective " + objective)
    shell_execute(command, output, test=test)

@step(r'I create BigML (multi-label\s)?resources using models in file "([^"]*)" to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_models_file(step, multi_label=None, models_file=None, test=None, output=None):
    if models_file is None or test is None or output is None:
        assert False
    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler "+ multi_label +"--models " + models_file + " --test "
               + test + " --store --output " + output)
    shell_execute(command, output, test=test)


@step(r'I create BigML resources using dataset in file "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_from_dataset_file(step, dataset_file=None, test=None, output=None):
    if dataset_file is None or test is None or output is None:
        assert False
    command = ("bigmler --datasets " + dataset_file + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


@step(r'I create a BigML cross-validation with rate (0\.\d+) using a dataset and log results in "(.*)"')
def i_create_cross_validation_from_dataset(step, rate=None, output=None):
    if rate is None or output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    world.number_of_models = int(MONTECARLO_FACTOR * float(rate))
    world.number_of_evaluations = world.number_of_models
    try:
        command = ("bigmler --dataset " + world.dataset['resource'] +
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


@step(r'I combine BigML predictions files in "(.*)" and "(.*)" into "(.*)"')
def i_find_predictions_files(step, directory1=None, directory2=None, output=None):
    if directory1 is None or directory2 is None or output is None:
        assert False
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


@step(r'I combine BigML predictions files in "(.*)" and "(.*)" into "(.*)" with method "(.*)"')
def i_find_predictions_files(step, directory1=None, directory2=None, output=None, method=None):
    if directory1 is None or directory2 is None or output is None or method is None:
        assert False
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

@step(r'I create a BigML balanced model from "(.*)" and store logs in "(.*)"')
def i_create_balanced_model(step, data=None, output_dir=None):
    if data is None or output_dir is None:
        assert False
    world.directory = output_dir
    world.folders.append(world.directory)
    try:
        command = ("bigmler --train " + data + " --balance " +
                   " --store --output-dir " + output_dir)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

@step(r'I create a BigML field weighted model from "(.*)" using field "(.*)" as weight and store logs in "(.*)"')
def i_create_weighted_field_model(step, data=None, field=None, output_dir=None):
    if data is None or field is None or output_dir is None:
        assert False
    world.directory = output_dir
    world.folders.append(world.directory)
    try:
        command = ("bigmler --train " + data + " --weight-field " + field +
                   " --store --output-dir " + output_dir)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


@step(r'I create a BigML objective weighted model from "(.*)" using the objective weights in file "(.*)" and store logs in "(.*)"')
def i_create_objective_weighted_model(step, data=None, path=None, output_dir=None):
    if data is None or path is None or output_dir is None:
        assert False
    world.directory = output_dir
    world.folders.append(world.directory)
    try:
        command = ("bigmler --train " + data + " --objective-weights " + path +
                   " --store --output-dir " + output_dir)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


@step(r'I check that the source has been created$')
def i_check_create_source(step):
    source_file = "%s%ssource" % (world.directory, os.sep)
    try:
        source_file = open(source_file, "r")
        source = check_resource(source_file.readline().strip(),
                                world.api.get_source)
        world.sources.append(source['resource'])
        world.source = source
        source_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)


@step(r'I check that the (test\s|train\s)?dataset has been created$')
def i_check_create_dataset(step, suffix=None):
    import traceback
    suffix = "" if suffix is None else "_%s" % suffix[:-1]
    dataset_file = "%s%sdataset%s" % (world.directory, os.sep, suffix)
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
        assert False, traceback.format_exc()


@step(r'I check that the new dataset has been created$')
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


@step(r'I check that the model has been created')
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


@step(r'I check that the model is balanced')
def i_check_model_is_balanced(step):
    assert ('balance_objective' in world.model['object'] and
            world.model['object']['balance_objective'])


@step(r'I check that the model uses as weight "(.*)"')
def i_check_weighted_model(step, field=None):
    if field is None:
        assert False
    assert ('weight_field' in world.model['object'] and
            world.model['object']['weight_field'] == field)


@step(r'I check that the model uses as objective weights "(.*)"')
def i_check_objective_weighted_model(step, weights=None):
    if weights is None:
        assert False
    assert ('objective_weights' in world.model['object'] and
            world.model['object']['objective_weights'] == json.loads(weights))


@step(r'I check that the ensemble has been created')
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

@step(r'I check that the models have been created')
def i_check_create_models(step):
    i_check_create_models_in_ensembles(step, False)


@step(r'I check that the models in the ensembles have been created')
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


@step(r'I check that the evaluation has been created')
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


@step(r'I check that the (\d+ )?evaluations have been created')
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


@step(r'I check that the predictions are ready')
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


@step(r'the local prediction file is like "(.*)"')
def i_check_predictions(step, check_file):
    predictions_file = world.output
    try:
        predictions_file = csv.reader(open(predictions_file, "U"), lineterminator="\n")
        check_file = csv.reader(open(check_file, "U"), lineterminator="\n")
        for row in predictions_file:
            check_row = check_file.next()
            if len(check_row) != len(row):
                assert False
            for index in range(len(row)):
                dot = row[index].find(".")
                if dot > 0 or (check_row[index].find(".") > 0 
                               and check_row[index].endswith(".0")):
                    try:
                        decimal_places = min(len(row[index]), len(check_row[index])) - dot - 1
                        row[index] = round(float(row[index]), decimal_places)
                        check_row[index] = round(float(check_row[index]), decimal_places)    
                    except ValueError:
                        pass
                if check_row[index] != row[index]:
                    print row, check_row
                    assert False
        assert True
    except Exception, exc:
        assert False, str(exc)


@step(r'local predictions for different thresholds in "(.*)" and "(.*)" are different')
def i_check_predictions_with_different_thresholds(step, output2, output3):
    try:
        predictions_file = open(output2, "U").read()
        predictions_file_k = open(output3, "U").read()
        if predictions_file != predictions_file_k:
            assert True
        else:
            assert False
    except Exception, exc:
        assert False, str(exc)


@step(r'the cross-validation json model info is like the one in "(.*)"')
def i_check_cross_validation(step, check_file):
    cv_file = "%s/cross_validation.json" % world.directory
    try:
        with open(cv_file, "U") as cv_handler:
            cv_content = json.loads(cv_handler.read())
        with open(check_file, "U") as check_handler:
            check_content = json.loads(check_handler.read())
        if cv_content['model'] == check_content['model']: 
            assert True
        else:
            assert False, "content: %s, check: %s" % (cv_content, check_content)
    except Exception, exc:
        assert False, str(exc)


@step(r'I check that the stored source file exists')
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


@step(r'And the locale of the source is "(.*)"')
def i_check_source_locale(step, bigml_locale):
    try:
        if bigml_locale == world.source['object']["source_parser"]["locale"]:
            assert True
        else:
            assert False
    except KeyError, exc:
        assert False, str(exc)


@step(r'I create BigML resources uploading train "(.*)" file to evaluate and log evaluation in "(.*)"')
def i_create_all_resources_to_evaluate(step, data=None, output=None):
    if data is None or output is None:
        assert False
    try:
        retcode = check_call("bigmler --evaluate --train " + data + " --store --output " + output, shell=True)
        if retcode < 0:
            assert False
        else:
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


@step(r'I create a BigML source from file "(.*)" with locale "(.*)" storing results in "(.*)"')
def i_create_all_resources_to_evaluate_with_locale(step, data=None, locale=None, output=None):
    if data is None or locale is None or output is None:
        assert False
    try:
        retcode = check_call("bigmler --train " + data + " --locale " + locale + " --store --output " + output + " --no-dataset --no-model --store", shell=True)
        if retcode < 0:
            assert False
        else:
            world.directory = os.path.dirname(output)
            world.folders.append(world.directory)
            world.output = output
            assert True
    except OSError as e:
        assert False


@step(r'I have previously executed "(.*)" or reproduce it with arguments (.*)$')
def i_have_previous_scenario_or_reproduce_it(step, scenario, kwargs):
    scenarios = {'scenario1': [(i_create_all_resources, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_model, False)],
                 'scenario1_r': [(i_create_all_resources, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_model, False)],
                 'scenario5': [(i_create_resources_from_ensemble, True), (i_check_create_models, False)], 
                 'scenario_e1': [(i_create_all_resources_to_evaluate, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_model, False), (i_check_create_evaluation, False)],
                 'scenario_ml_1': [(i_create_all_ml_resources, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_models, False)],
                 'scenario_ml_6': [(i_create_all_ml_resources, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_models, False)],
                 'scenario_mle_1': [(i_create_all_ml_resources_and_ensembles, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_models_in_ensembles, False)],
                 'scenario_ml_e1': [(i_create_all_ml_resources_for_evaluation, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_models, False)],
                 'scenario_mc_1': [(i_create_all_mc_resources, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_max_categories_datasets, False), (i_check_create_models, False)],
                 'scenario_r1': [(i_create_all_resources_batch, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_max_categories_datasets, False), (i_check_create_models, False), (i_check_create_test_source, False), (i_check_create_test_dataset, False)],
                 'scenario_mlm_1': [(i_create_all_mlm_resources, True), (i_check_create_source, False), (i_check_create_dataset, False), (i_check_create_models, False)]}
    if os.path.exists("./%s/" % scenario):
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
