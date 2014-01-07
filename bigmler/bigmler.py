# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012, 2013 BigML
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

"""BigMLer - A Higher Level API to BigML's API

# Basic usage
python bigmler.py \
    --train data/iris.csv \
    --test data/test_iris.csv
    --no-test-header

# Create an 10-model ensemble using bagging
python bigmler.py
    --train train.csv \
    --output submission.csv \
    --objective 0 \
    --types types.txt \
    --name 'Iris Ensemble' \
    --number_of_models 10 \
    --sample_rate 0.75 \
    --replacement \
    --tag my_ensemble

# Make predictions using models tagged with my_ensemble
python bigmler.py \
    --model_tag my_ensemble \
    --test test.csv
    --no-test-header

"""
from __future__ import absolute_import

import sys
import os
import re
import shlex
import datetime
import StringIO

import bigml.api
import bigmler.utils as u
import bigmler.resources as r
import bigmler.labels as l
import bigmler.processing.sources as ps
import bigmler.processing.datasets as pd
import bigmler.processing.models as pm
import bigmler.processing.ensembles as pe

from bigml.multivote import COMBINATION_WEIGHTS, COMBINER_MAP, PLURALITY
from bigml.model import Model

from bigmler.evaluation import evaluate, cross_validate
from bigmler.options import create_parser
from bigmler.defaults import get_user_defaults
from bigmler.defaults import DEFAULTS_FILE
from bigmler.prediction import predict, combine_votes, remote_predict
from bigmler.prediction import (MAX_MODELS, FULL_FORMAT, OTHER, COMBINATION,
                                COMBINATION_LABEL, THRESHOLD_CODE)


# Date and time in format SunNov0412_120510 to name and tag resources
NOW = datetime.datetime.now().strftime("%a%b%d%y_%H%M%S")
COMMAND_LOG = ".bigmler"
DIRS_LOG = ".bigmler_dir_stack"
SESSIONS_LOG = "bigmler_sessions"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]


def non_compatible(args, option):
    """Return non_compatible options

    """
    if option == '--cross-validation-rate':
        return (args.test_set or args.evaluate or args.model or args.models or
                args.model_tag or args.multi_label)
    if option == '--max-categories':
        return (args.evaluate or args.test_split or args.remote)
    return False


def has_test(args):
    """Returns if some kind of test data is given in args.

    """
    return args.test_set or args.test_source or args.test_dataset


def compute_output(api, args, training_set, test_set=None, output=None,
                   objective_field=None,
                   description=None,
                   field_attributes=None,
                   types=None,
                   dataset_fields=None,
                   model_fields=None,
                   name=None, training_set_header=True,
                   test_set_header=True, model_ids=None,
                   votes_files=None, resume=False, fields_map=None,
                   test_field_attributes=None,
                   test_types=None):
    """ Creates one or more models using the `training_set` or uses the ids
    of previously created BigML models to make predictions for the `test_set`.

    """
    source = None
    dataset = None
    model = None
    models = None
    fields = None
    other_label = OTHER
    ensemble_ids = []

    # It is compulsory to have a description to publish either datasets or
    # models
    if (not description and
            (args.black_box or args.white_box or args.public_dataset)):
        sys.exit("You should provide a description to publish.")

    # When using --max-categories, it is compulsory to specify also the
    # objective_field
    if args.max_categories > 0 and objective_field is None:
        sys.exit("When --max-categories is used, you must also provide the"
                 " --objective field name or column number")

    # When using --new-fields, it is compulsory to specify also a dataset
    # id
    if args.new_fields and not args.dataset:
        sys.exit("To use --new-fields you must also provide a dataset id"
                 " to generate the new dataset from it.")

    path = u.check_dir(output)
    session_file = "%s%s%s" % (path, os.sep, SESSIONS_LOG)
    csv_properties = {}
    # If logging is required, open the file for logging
    log = None
    if args.log_file:
        u.check_dir(args.log_file)
        log = args.log_file
        # If --clear_logs the log files are cleared
        if args.clear_logs:
            try:
                open(log, 'w', 0).close()
            except IOError:
                pass

    # labels to be used in multi-label expansion
    labels = (map(str.strip, args.labels.split(','))
              if args.labels is not None else None)
    if labels is not None:
        labels = sorted([label.decode("utf-8") for label in labels])

    # multi_label file must be preprocessed to obtain a new extended file
    if args.multi_label and training_set is not None:
        (training_set, labels,
         field_attributes, objective_field) = ps.multi_label_expansion(
             training_set, training_set_header, objective_field, args, path,
             field_attributes=field_attributes, labels=labels,
             session_file=session_file)
        training_set_header = True
    all_labels = labels

    if args.multi_label and args.evaluate and args.test_set is not None:
        (test_set, test_labels,
         field_attributes, objective_field) = ps.multi_label_expansion(
             test_set, test_set_header, objective_field, args, path,
             field_attributes=field_attributes, labels=labels,
             session_file=session_file)
        test_set_header = True

    source, resume, csv_properties, fields = ps.source_processing(
        training_set, test_set, training_set_header, test_set_header,
        api, args, resume, name=name, description=description,
        csv_properties=csv_properties,
        field_attributes=field_attributes,
        types=types, session_file=session_file, path=path, log=log)

    datasets, resume, csv_properties, fields = pd.dataset_processing(
        source, training_set, test_set, fields, objective_field,
        api, args, resume, name=name, description=description,
        dataset_fields=dataset_fields, csv_properties=csv_properties,
        session_file=session_file, path=path, log=log)
    if datasets:
        dataset = datasets[0]

    # If test_split is used, split the dataset in a training and a test dataset
    # according to the given split
    if args.test_split > 0:
        dataset, test_dataset, resume = pd.split_processing(
            dataset, api, args, resume, name=name, description=description,
            session_file=session_file, path=path, log=log)
        datasets[0] = dataset

    # Check if the dataset has a categorical objective field and it
    # has a max_categories limit for categories
    if args.max_categories > 0 and len(datasets) == 1:
        objective_id = fields.field_id(fields.objective_field)
        if pd.check_categorical(fields.fields[objective_id]):
            distribution = pd.get_categories_distribution(dataset,
                                                          objective_id)
            if distribution and len(distribution) > args.max_categories:
                categories = [element[0] for element in distribution]
                other_label = pd.create_other_label(categories, other_label)
                datasets, resume = pd.create_categories_datasets(
                    dataset, distribution, fields, args,
                    api, resume, session_file=session_file, path=path, log=log,
                    other_label=other_label)
        else:
            sys.exit("The provided objective field is not categorical. A"
                     " categorical field is expected when using"
                     "  --max-categories")

    # Check if the dataset a generators file associated with it, and
    # generate a new dataset with the specified field structure
    if args.new_fields:
        dataset, resume = pd.create_new_dataset(
            dataset, api, args, resume, name=name,
            description=description, session_file=session_file, path=path,
            log=log)

    models, model_ids, ensemble_ids, resume = pm.models_processing(
        datasets, models, model_ids,
        objective_field, fields, api, args, resume,
        name=name, description=description, model_fields=model_fields,
        session_file=session_file, path=path, log=log, labels=labels,
        all_labels=all_labels)
    if models:
        model = models[0]
        single_model = len(models) == 1

    # We get the fields of the model if we haven't got
    # them yet and update its public state if needed
    if model and not args.evaluate and (test_set or args.black_box
                                        or args.white_box):
        if args.black_box or args.white_box:
            model = r.publish_model(model, args, api, session_file)
            models[0] = model
        # If more than one model, use the full field structure
        fields, objective_field = pm.get_model_fields(
            model, csv_properties, args, single_model=single_model)

    # If multi-label flag is set and no training_set was provided, label
    # info is extracted from the fields structure
    if args.multi_label and training_set is None:
        fields_list = []
        for model in models:
            if (isinstance(model, basestring) or
                    bigml.api.get_status(model)['code'] != bigml.api.FINISHED):
                # if there's more than one model the first one must contain
                # the entire field structure to be used as reference.
                query_string = (r.FIELDS_QS if single_model
                                else r.ALL_FIELDS_QS)
                model = bigml.api.check_resource(model, api.get_model,
                                                 query_string=query_string)
            fields_list.append(model['object']['model']['fields'])
        fields_list.reverse()
        all_labels, labels = l.retrieve_labels(fields_list, labels)

    # If predicting
    if models and has_test(args) and not args.evaluate:
        models_per_label = 1
        test_dataset = None
        if args.multi_label:
            models_per_label = len(models) / len(all_labels)

        # Remote predictions: predictions are computed as batch predictions
        # in bigml.com except when --no-batch flag is set on or multi-label
        # or max-categories are used
        if (args.remote and not args.no_batch and not args.multi_label
                and not args.method in [THRESHOLD_CODE, COMBINATION]):
            # create test source from file
            test_name = "%s - test" % name
            if args.test_source is None:
                (test_source, resume,
                 csv_properties, test_fields) = ps.test_source_processing(
                    test_set, test_set_header,
                    api, args, resume, name=test_name, description=description,
                    field_attributes=test_field_attributes, types=test_types,
                    session_file=session_file, path=path, log=log)
            else:
                test_source_id = bigml.api.get_source_id(args.test_source)
                test_source = api.check_resource(test_source_id,
                                                 api.get_source)
            if args.test_dataset is None:
            # create test dataset from test source
                dataset_args = r.set_basic_dataset_args(test_name,
                                                        description, args)
                test_dataset, resume = pd.alternative_dataset_processing(
                    test_source, "test", dataset_args, api, args,
                    resume, session_file=session_file, path=path, log=log)
            else:
                test_dataset_id = bigml.api.get_dataset_id(args.test_dataset)
                test_dataset = api.check_resource(test_dataset_id,
                                                  api.get_dataset)

            test_fields = pd.get_fields_structure(test_dataset,
                                                  csv_properties)

            batch_prediction_args = r.set_batch_prediction_args(
                name, description, args, fields=fields,
                dataset_fields=test_fields, fields_map=fields_map)

            remote_predict(model, test_dataset, batch_prediction_args, args,
                           api, resume, prediction_file=output,
                           session_file=session_file, path=path, log=log)
        else:
            models_per_label = args.number_of_models
            if (args.multi_label and len(ensemble_ids) > 0
                and args.number_of_models == 1):
                # use case where ensembles are read from a file
                models_per_label = len(models) / len(ensemble_ids)
            predict(test_set, test_set_header, models, fields, output,
                    objective_field, args, api=api, log=log,
                    max_models=args.max_batch_models, resume=resume,
                    session_file=session_file, labels=labels,
                    models_per_label=models_per_label, other_label=other_label)

    # When combine_votes flag is used, retrieve the predictions files saved
    # in the comma separated list of directories and combine them
    if votes_files:
        model_id = re.sub(r'.*(model_[a-f0-9]{24})__predictions\.csv$',
                          r'\1', votes_files[0]).replace("_", "/")
        try:
            model = u.check_resource(model_id, api.get_model)
        except ValueError, exception:
            sys.exit("Failed to get model %s: %s" % (model_id, str(exception)))

        local_model = Model(model)
        message = u.dated("Combining votes.\n")
        u.log_message(message, log_file=session_file,
                      console=args.verbosity)
        combine_votes(votes_files, local_model.to_prediction,
                      output, args.method)

    # If evaluate flag is on, create remote evaluation and save results in
    # json and human-readable format.
    if args.evaluate:
        if args.test_split > 0:
            dataset = test_dataset
        dataset_fields = pd.get_fields_structure(dataset, None)
        models_or_ensembles = ensemble_ids if ensemble_ids != [] else models
        resume = evaluate(models_or_ensembles, [dataset], output, api,
                          args, resume, name=name, description=description,
                          fields=fields, dataset_fields=dataset_fields,
                          fields_map=fields_map,
                          session_file=session_file, path=path,
                          log=log, labels=labels, all_labels=all_labels,
                          objective_field=objective_field)

    # If cross_validation_rate is > 0, create remote evaluations and save
    # results in json and human-readable format. Then average the results to
    # issue a cross_validation measure set.
    if args.cross_validation_rate > 0:
        args.sample_rate = 1 - args.cross_validation_rate
        cross_validate(models, dataset, fields, api, args, resume,
                       name=name, description=description,
                       fields_map=fields_map, session_file=session_file,
                       path=path, log=log)

    # Workaround to restore windows console cp850 encoding to print the tree
    if sys.platform == "win32" and sys.stdout.isatty():
        import locale
        data_locale = locale.getlocale()
        if not data_locale[0] is None:
            locale.setlocale(locale.LC_ALL, (data_locale[0], "850"))
        message = (u"\nGenerated files:\n\n" +
                   unicode(u.print_tree(path, " "), "utf-8") + u"\n")
    else:
        message = "\nGenerated files:\n\n" + u.print_tree(path, " ") + "\n"
    u.log_message(message, log_file=session_file, console=args.verbosity)


def main(args=sys.argv[1:]):
    """Main process

    """
    train_stdin = False
    test_stdin = False
    flags = []
    for i in range(0, len(args)):
        if args[i].startswith("--"):
            flag = args[i]
            # syntax --flag=value
            if "=" in flag:
                flag = args[i][0: flag.index("=")]
            flag = flag.replace("_", "-")
            flags.append(flag)
            if (flag == '--train' and
                    (i == len(args) - 1 or args[i + 1].startswith("--"))):
                train_stdin = True
            elif (flag == '--test' and
                    (i == len(args) - 1 or args[i + 1].startswith("--"))):
                test_stdin = True

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        for log_file in LOG_FILES:
            try:
                open(log_file, 'w', 0).close()
            except IOError:
                pass
    literal_args = args[:]
    for i in range(0, len(args)):
        # quoting literals with blanks: 'petal length'
        if ' ' in args[i]:
            prefix = ""
            literal = args[i]
            # literals with blanks after "+" or "-": +'petal length'
            if args[i][0] in r.ADD_REMOVE_PREFIX:
                prefix = args[i][0]
                literal = args[i][1:]
            literal_args[i] = '%s"%s"' % (prefix, literal)
    message = "bigmler %s\n" % " ".join(literal_args)

    # Resume calls are not logged
    if not "--resume" in args:
        with open(COMMAND_LOG, "a", 0) as command_log:
            command_log.write(message)
        resume = False
    user_defaults = get_user_defaults()
    parser = create_parser(defaults=get_user_defaults(),
                           constants={'NOW': NOW,
                                      'MAX_MODELS': MAX_MODELS,
                                      'PLURALITY': PLURALITY})

    # Parses command line arguments.
    command_args = parser.parse_args(args)

    if command_args.cross_validation_rate > 0 and (
            non_compatible(command_args, '--cross-validation-rate')):
        parser.error("Non compatible flags: --cross-validation-rate"
                     " cannot be used with --evaluate, --model,"
                     " --models, --model-tag or --multi-label. Usage:\n\n"
                     "bigmler --train data/iris.csv "
                     "--cross-validation-rate 0.1")

    if command_args.max_categories and (
            non_compatible(command_args, '--max-categories')):
        parser.error("Non compatible flags: --max-categories cannot "
                     "be used with --test-split, --remote or --evaluate.")

    if train_stdin and command_args.multi_label:
        parser.error("Reading multi-label training sets from stream "
                     "is not yet available.")

    if test_stdin and command_args.resume:
        parser.error("Can't resume when using stream reading test sets.")

    default_output = ('evaluation' if command_args.evaluate
                      else 'predictions.csv')
    if command_args.resume:
        debug = command_args.debug
        command = u.get_log_reversed(COMMAND_LOG,
                                     command_args.stack_level)
        args = shlex.split(command)[1:]
        try:
            position = args.index("--train")
            train_stdin = (position == (len(args) - 1) or
                           args[position + 1].startswith("--"))
        except ValueError:
            pass
        try:
            position = args.index("--test")
            test_stdin = (position == (len(args) - 1) or
                          args[position + 1].startswith("--"))
        except ValueError:
            pass
        output_dir = u.get_log_reversed(DIRS_LOG,
                                        command_args.stack_level)
        defaults_file = "%s%s%s" % (output_dir, os.sep, DEFAULTS_FILE)
        user_defaults = get_user_defaults(defaults_file)
        parser = create_parser(defaults=user_defaults,
                               constants={'NOW': NOW,
                                          'MAX_MODELS': MAX_MODELS,
                                          'PLURALITY': PLURALITY})
        command_args = parser.parse_args(args)
        if command_args.predictions is None:
            command_args.predictions = ("%s%s%s" %
                                        (output_dir, os.sep,
                                         default_output))

        # Logs the issued command and the resumed command
        session_file = "%s%s%s" % (output_dir, os.sep, SESSIONS_LOG)
        u.log_message(message, log_file=session_file)
        message = "\nResuming command:\n%s\n\n" % command
        u.log_message(message, log_file=session_file, console=True)
        try:
            defaults_handler = open(defaults_file, 'r')
            contents = defaults_handler.read()
            message = "\nUsing the following defaults:\n%s\n\n" % contents
            u.log_message(message, log_file=session_file, console=True)
            defaults_handler.close()
        except IOError:
            pass

        resume = True
    else:
        if command_args.output_dir is None:
            command_args.output_dir = NOW
        if command_args.predictions is None:
            command_args.predictions = ("%s%s%s" %
                                        (command_args.output_dir, os.sep,
                                         default_output))
        if len(os.path.dirname(command_args.predictions).strip()) == 0:
            command_args.predictions = ("%s%s%s" %
                                        (command_args.output_dir, os.sep,
                                         command_args.predictions))
        directory = u.check_dir(command_args.predictions)
        session_file = "%s%s%s" % (directory, os.sep, SESSIONS_LOG)
        u.log_message(message + "\n", log_file=session_file)
        try:
            defaults_file = open(DEFAULTS_FILE, 'r')
            contents = defaults_file.read()
            defaults_file.close()
            defaults_copy = open("%s%s%s" % (directory, os.sep, DEFAULTS_FILE),
                                 'w', 0)
            defaults_copy.write(contents)
            defaults_copy.close()
        except IOError:
            pass
        with open(DIRS_LOG, "a", 0) as directory_log:
            directory_log.write("%s\n" % os.path.abspath(directory))

    if resume and debug:
        command_args.debug = True

    if train_stdin:
        if test_stdin:
            sys.exit("The standard input can't be used both for training and"
                     " testing. Choose one of them")
        command_args.training_set = StringIO.StringIO(sys.stdin.read())
    elif test_stdin:
        command_args.test_set = StringIO.StringIO(sys.stdin.read())

    api_command_args = {
        'username': command_args.username,
        'api_key': command_args.api_key,
        'dev_mode': command_args.dev_mode,
        'debug': command_args.debug}

    if command_args.store:
        api_command_args.update({'storage': u.check_dir(session_file)})

    api = bigml.api.BigML(**api_command_args)

    if (command_args.evaluate
        and not (command_args.training_set or command_args.source
                 or command_args.dataset)
        and not ((command_args.test_set or command_args.test_split) and
                 (command_args.model or
                  command_args.models or command_args.model_tag or
                  command_args.ensemble or command_args.ensembles or
                  command_args.ensemble_tag))):
        parser.error("Evaluation wrong syntax.\n"
                     "\nTry for instance:\n\nbigmler --train data/iris.csv"
                     " --evaluate\nbigmler --model "
                     "model/5081d067035d076151000011 --dataset "
                     "dataset/5081d067035d076151003423 --evaluate\n"
                     "bigmler --ensemble ensemble/5081d067035d076151003443"
                     " --dataset "
                     "dataset/5081d067035d076151003423 --evaluate")

    if command_args.objective_field:
        objective = command_args.objective_field
        try:
            command_args.objective_field = int(objective)
        except ValueError:
            if not command_args.train_header:
                sys.exit("The %s has been set as objective field but"
                         " the file has not been marked as containing"
                         " headers.\nPlease set the --train-header flag if"
                         " the file has headers or use a column number"
                         " to set the objective field." % objective)

    output_args = {
        "api": api,
        "training_set": command_args.training_set,
        "test_set": command_args.test_set,
        "output": command_args.predictions,
        "objective_field": command_args.objective_field,
        "name": command_args.name,
        "training_set_header": command_args.train_header,
        "test_set_header": command_args.test_header,
        "args": command_args,
        "resume": resume,
    }

    # Reads description if provided.
    if command_args.description:
        description_arg = u.read_description(command_args.description)
        output_args.update(description=description_arg)
    else:
        output_args.update(description="Created using BigMLer")

    # Parses fields if provided.
    if command_args.field_attributes:
        field_attributes_arg = (
            u.read_field_attributes(command_args.field_attributes))
        output_args.update(field_attributes=field_attributes_arg)
    if command_args.test_field_attributes:
        field_attributes_arg = (
            u.read_field_attributes(command_args.test_field_attributes))
        output_args.update(test_field_attributes=field_attributes_arg)

    # Parses types if provided.
    if command_args.types:
        types_arg = u.read_types(command_args.types)
        output_args.update(types=types_arg)
    if command_args.test_types:
        types_arg = u.read_types(command_args.test_types)
        output_args.update(test_types=types_arg)

    # Parses dataset fields if provided.
    if command_args.dataset_fields:
        dataset_fields_arg = map(str.strip,
                                 command_args.dataset_fields.split(','))
        output_args.update(dataset_fields=dataset_fields_arg)

    # Parses dataset attributes in json format if provided
    if command_args.dataset_attributes:
        json_dataset_attributes = u.read_json(command_args.dataset_attributes)
        command_args.dataset_json_args = json_dataset_attributes
    else:
        command_args.dataset_json_args = {}

    # Parses dataset attributes in json format if provided
    if command_args.model_attributes:
        json_model_attributes = u.read_json(command_args.model_attributes)
        command_args.model_json_args = json_model_attributes
    else:
        command_args.model_json_args = {}

    # Parses dataset generators in json format if provided
    if command_args.new_fields:
        json_generators = u.read_json(command_args.new_fields)
        command_args.dataset_json_generators = json_generators
    else:
        command_args.dataset_json_generators = {}

    # Parses model input fields if provided.
    if command_args.model_fields:
        model_fields_arg = map(str.strip,
                               command_args.model_fields.split(','))
        output_args.update(model_fields=model_fields_arg)

    model_ids = []
    # Parses model/ids if provided.
    if command_args.models:
        model_ids = u.read_resources(command_args.models)
        output_args.update(model_ids=model_ids)

    dataset_ids = None
    command_args.dataset_ids = []
    # Parses dataset/id if provided.
    if command_args.datasets:
        dataset_ids = u.read_datasets(command_args.datasets)
        if len(dataset_ids) == 1:
            command_args.dataset = dataset_ids[0]
        command_args.dataset_ids = dataset_ids

    # Retrieve dataset/ids if provided.
    if command_args.dataset_tag:
        dataset_ids = dataset_ids.extend(
                     u.list_ids(api.list_datasets,
                                "tags__in=%s" % command_args.dataset_tag))
        if len(dataset_ids) == 1:
            command_args.dataset = dataset_ids[0]
        command_args.dataset_ids = dataset_ids

    # Retrieve model/ids if provided.
    if command_args.model_tag:
        model_ids = (model_ids +
                     u.list_ids(api.list_models,
                                "tags__in=%s" % command_args.model_tag))
        output_args.update(model_ids=model_ids)

    # Reads a json filter if provided.
    if command_args.json_filter:
        json_filter = u.read_json_filter(command_args.json_filter)
        command_args.json_filter = json_filter

    # Reads a lisp filter if provided.
    if command_args.lisp_filter:
        lisp_filter = u.read_lisp_filter(command_args.lisp_filter)
        command_args.lisp_filter = lisp_filter

    # Adds default tags unless that it is requested not to do so.
    if command_args.no_tag:
        command_args.tag.append('BigMLer')
        command_args.tag.append('BigMLer_%s' % NOW)

    # Checks combined votes method
    if (command_args.method and command_args.method != COMBINATION_LABEL and
            not (command_args.method in COMBINATION_WEIGHTS.keys())):
        command_args.method = 0
    else:
        combiner_methods = dict([[value, key]
                                for key, value in COMBINER_MAP.items()])
        combiner_methods[COMBINATION_LABEL] = COMBINATION
        command_args.method = combiner_methods.get(command_args.method, 0)

    # Adds replacement=True if creating ensemble and nothing is specified
    if (command_args.number_of_models > 1 and
            not command_args.replacement and
            not '--no-replacement' in flags and
            not 'replacement' in user_defaults and
            not '--no-randomize' in flags and
            not 'randomize' in user_defaults and
            not '--sample-rate' in flags and
            not 'sample_rate' in user_defaults):
        command_args.replacement = True

    # Reads votes files in the provided directories.
    if command_args.votes_dirs:
        dirs = map(str.strip, command_args.votes_dirs.split(','))
        votes_path = os.path.dirname(command_args.predictions)
        votes_files = u.read_votes_files(dirs, votes_path)
        output_args.update(votes_files=votes_files)

    # Parses fields map if provided.
    if command_args.fields_map:
        fields_map_arg = u.read_fields_map(command_args.fields_map)
        output_args.update(fields_map=fields_map_arg)

    # Old value for --prediction-info='full data' maps to 'full'
    if command_args.prediction_info == 'full data':
        print "WARNING: 'full data' is a deprecated value. Use 'full' instead"
        command_args.prediction_info = FULL_FORMAT

    # Parses resources ids if provided.
    if command_args.delete:
        if command_args.predictions is None:
            path = NOW
        else:
            path = u.check_dir(command_args.predictions)
        session_file = "%s%s%s" % (path, os.sep, SESSIONS_LOG)
        message = u.dated("Retrieving objects to delete.\n")
        u.log_message(message, log_file=session_file,
                      console=command_args.verbosity)
        delete_list = []
        if command_args.delete_list:
            delete_list = map(str.strip,
                              command_args.delete_list.split(','))
        if command_args.delete_file:
            if not os.path.exists(command_args.delete_file):
                sys.exit("File %s not found" % command_args.delete_file)
            delete_list.extend([line for line
                                in open(command_args.delete_file, "r")])
        if command_args.all_tag:
            query_string = "tags__in=%s" % command_args.all_tag
            delete_list.extend(u.list_ids(api.list_sources, query_string))
            delete_list.extend(u.list_ids(api.list_datasets, query_string))
            delete_list.extend(u.list_ids(api.list_models, query_string))
            delete_list.extend(u.list_ids(api.list_predictions, query_string))
            delete_list.extend(u.list_ids(api.list_evaluations, query_string))
        # Retrieve sources/ids if provided
        if command_args.source_tag:
            query_string = "tags__in=%s" % command_args.source_tag
            delete_list.extend(u.list_ids(api.list_sources, query_string))
        # Retrieve datasets/ids if provided
        if command_args.dataset_tag:
            query_string = "tags__in=%s" % command_args.dataset_tag
            delete_list.extend(u.list_ids(api.list_datasets, query_string))
        # Retrieve model/ids if provided
        if command_args.model_tag:
            query_string = "tags__in=%s" % command_args.model_tag
            delete_list.extend(u.list_ids(api.list_models, query_string))
        # Retrieve prediction/ids if provided
        if command_args.prediction_tag:
            query_string = "tags__in=%s" % command_args.prediction_tag
            delete_list.extend(u.list_ids(api.list_predictions, query_string))
        # Retrieve evaluation/ids if provided
        if command_args.evaluation_tag:
            query_string = "tags__in=%s" % command_args.evaluation_tag
            delete_list.extend(u.list_ids(api.list_evaluations, query_string))
        # Retrieve ensembles/ids if provided
        if command_args.ensemble_tag:
            query_string = "tags__in=%s" % command_args.ensemble_tag
            delete_list.extend(u.list_ids(api.list_ensembles, query_string))
        message = u.dated("Deleting objects.\n")
        u.log_message(message, log_file=session_file,
                      console=command_args.verbosity)
        message = "\n".join(delete_list)
        u.log_message(message, log_file=session_file)
        u.delete(api, delete_list)
        if sys.platform == "win32" and sys.stdout.isatty():
            message = (u"\nGenerated files:\n\n" +
                       unicode(u.print_tree(path, " "), "utf-8") + u"\n")
        else:
            message = "\nGenerated files:\n\n" + u.print_tree(path, " ") + "\n"
        u.log_message(message, log_file=session_file,
                      console=command_args.verbosity)
    elif (command_args.training_set or has_test(command_args)
          or command_args.source or command_args.dataset
          or command_args.datasets or command_args.votes_dirs):
        compute_output(**output_args)
    u.log_message("_" * 80 + "\n", log_file=session_file)

if __name__ == '__main__':
    main(sys.argv[1:])
