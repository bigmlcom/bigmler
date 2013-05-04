# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012 BigML
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
import bigmler.checkpoint as c

from bigml.fields import Fields
from bigml.multivote import COMBINATION_WEIGHTS, COMBINER_MAP, PLURALITY
from bigml.model import Model

from bigmler.evaluation import evaluate, cross_validate
from bigmler.options import create_parser
from bigmler.defaults import get_user_defaults
from bigmler.defaults import DEFAULTS_FILE
from bigmler.prediction import predict
from bigmler.prediction import MAX_MODELS


# Date and time in format SunNov0412_120510 to name and tag resources
NOW = datetime.datetime.now().strftime("%a%b%d%y_%H%M%S")
COMMAND_LOG = ".bigmler"
DIRS_LOG = ".bigmler_dir_stack"
SESSIONS_LOG = "bigmler_sessions"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
MISSING_TOKENS = ['', 'N/A', 'n/a', 'NULL', 'null', '-', '#DIV/0', '#REF!',
                  '#NAME?', 'NIL', 'nil', 'NA', 'na', '#VALUE!', '#NULL!',
                  'NaN', '#N/A', '#NUM!', '?']
MONTECARLO_FACTOR = 200


def source_processing(training_set, test_set, training_set_header,
                      test_set_header, name, description, api, args, resume,
                      csv_properties=None, field_attributes=None, types=None,
                      session_file=None, path=None, log=None):
    """Creating or retrieving a data source from input arguments

    """
    source = None
    fields = None
    if (training_set or (args.evaluate and test_set)):
        # If resuming, try to extract args.source form log files
        if resume:
            resume, args.source = c.checkpoint(c.is_source_created, path,
                                               debug=args.debug)
            if not resume:
                message = u.dated("Source not found. Resuming.\n")
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)

    # If neither a previous source, dataset or model are provided.
    # we create a new one. Also if --evaluate and test data are provided
    # we create a new dataset to test with.
    data_set, data_set_header = r.data_to_source(training_set, test_set,
                                                 training_set_header,
                                                 test_set_header, args)
    if data_set is not None:
        source_args = r.set_source_args(data_set_header, name, description,
                                        args)
        source = r.create_source(data_set, source_args, args, api,
                                 path, session_file, log)

    # If a source is provided either through the command line or in resume
    # steps, we use it.
    elif args.source:
        source = bigml.api.get_source_id(args.source)

    # If we already have source, we check that is finished, extract the
    # fields, and update them if needed.
    if source:
        source = r.get_source(source, api, args.verbosity, session_file)
        if 'source_parser' in source['object']:
            source_parser = source['object']['source_parser']
            if 'missing_tokens' in source_parser:
                csv_properties['missing_tokens'] = (
                    source_parser['missing_tokens'])
            if 'data_locale' in source_parser:
                csv_properties['data_locale'] = source_parser['locale']

        fields = Fields(source['object']['fields'], **csv_properties)
        if field_attributes:
            source = r.update_source_fields(source, field_attributes, fields,
                                            api, args.verbosity,
                                            session_file)
        if types:
            source = r.update_source_fields(source, types, fields, api,
                                            args.verbosity, session_file)
    return source, resume, csv_properties, fields


def dataset_processing(source, training_set, test_set, model_ids, name,
                       description, fields, dataset_fields, api, args,
                       resume, csv_properties=None,
                       session_file=None, path=None, log=None):
    """Creating or retrieving dataset from input arguments

    """
    dataset = None
    if (training_set or args.source or (args.evaluate and test_set)):
        # if resuming, try to extract args.dataset form log files
        if resume:
            resume, args.dataset = c.checkpoint(c.is_dataset_created, path,
                                                debug=args.debug)
            if not resume:
                message = u.dated("Dataset not found. Resuming.\n")
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)
    # If we have a source but no dataset or model has been provided, we
    # create a new dataset if the no_dataset option isn't set up. Also
    # if evaluate is set and test_set has been provided.
    if ((source and not args.dataset and not args.model and not model_ids and
            not args.no_dataset) or
            (args.evaluate and args.test_set and not args.dataset)):
        dataset_args = r.set_dataset_args(name, description, args, fields,
                                          dataset_fields)
        dataset = r.create_dataset(source, dataset_args, args, api,
                                   path, session_file, log)

    # If a dataset is provided, let's retrieve it.
    elif args.dataset:
        dataset = bigml.api.get_dataset_id(args.dataset)

    # If we already have a dataset, we check the status and get the fields if
    # we hadn't them yet.
    if dataset:
        dataset = r.get_dataset(dataset, api, args.verbosity, session_file)
        if not csv_properties and 'locale' in dataset['object']:
            csv_properties = {
                'data_locale': dataset['object']['locale']}
        fields = Fields(dataset['object']['fields'], **csv_properties)
        if args.public_dataset:
            r.publish_dataset(dataset, api, args, session_file)
    return dataset, resume, csv_properties, fields


def split_processing(dataset, name, description, api, args, resume,
                     session_file=None, path=None, log=None):
    """Splits a dataset into train and test datasets
    """
    train_dataset = None
    test_dataset = None
    sample_rate = 1 - args.test_split
    # if resuming, try to extract train dataset form log files
    if resume:
        resume, train_dataset = c.checkpoint(c.is_dataset_created, path,
                                             "_train",
                                             debug=args.debug)
        if not resume:
            message = u.dated("Dataset not found. Resuming.\n")
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)

    if train_dataset is None:
        dataset_split_args = r.set_dataset_split_args(
            "%s - train (%s %%)" % (name,
            int(sample_rate * 100)), description, args,
            sample_rate, out_of_bag=False)
        train_dataset = r.create_dataset(
            dataset, dataset_split_args, args, api, path, session_file,
            log, "train")
        if train_dataset:
            train_dataset = r.get_dataset(train_dataset, api,
                                          args.verbosity, session_file)

    # if resuming, try to extract test dataset form log files
    if resume:
        resume, test_dataset = c.checkpoint(c.is_dataset_created, path,
                                            "_test",
                                            debug=args.debug)
        if not resume:
            message = u.dated("Dataset not found. Resuming.\n")
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
    if test_dataset is None:
        dataset_split_args = r.set_dataset_split_args(
            "%s - test (%s %%)" % (name,
            int(args.test_split * 100)), description, args,
            sample_rate, out_of_bag=True)
        test_dataset = r.create_dataset(
            dataset, dataset_split_args, args, api, path, session_file,
            log, "test")
        if test_dataset:
            test_dataset = r.get_dataset(test_dataset, api, args.verbosity,
                                         session_file)
    return train_dataset, test_dataset, resume


def models_processing(dataset, models, model_ids, name, description, test_set,
                      objective_field, fields, model_fields, api, args, resume,
                      session_file=None, path=None, log=None):
    """Creates or retrieves models from the input data

    """
    # If we have a dataset but not a model, we create the model if the no_model
    # flag hasn't been set up.
    if (dataset and not args.model and not model_ids and not args.no_model
            and not args.ensemble):
        # Cross-validation case: we create 2 * n models to be validated
        # holding out an n% of data
        if args.cross_validation_rate > 0:
            args.number_of_models = int(MONTECARLO_FACTOR *
                                        args.cross_validation_rate)
        model_ids = []
        models = []
        if resume:
            resume, model_ids = c.checkpoint(c.are_models_created, path,
                                             args.number_of_models,
                                             debug=args.debug)
            if not resume:
                message = u.dated("Found %s models out of %s. Resuming.\n" %
                                  (len(model_ids),
                                   args.number_of_models))
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)
            models = model_ids
            args.number_of_models -= len(model_ids)

        model_args = r.set_model_args(name, description, args,
                                      objective_field, fields, model_fields)
        models, model_ids = r.create_models(dataset, models,
                                            model_args, args, api,
                                            path, session_file, log)
    # If a model is provided, we use it.
    elif args.model:
        model_ids = [args.model]
        models = model_ids[:]

    elif args.ensemble:
        ensemble = r.get_ensemble(args.ensemble, api, args.verbosity,
                                  session_file)
        model_ids = ensemble['object']['models']
        models = model_ids[:]

    elif args.models or args.model_tag:
        models = model_ids[:]

    # If we are going to predict we must retrieve the models
    if model_ids and test_set and not args.evaluate:
        models, model_ids = r.get_models(models, args, api, session_file)

    return models, model_ids, resume


def get_model_fields(model, model_fields, csv_properties, args):
    """Retrieves fields info from model resource

    """
    if not csv_properties:
        csv_properties = {}
    csv_properties.update(verbose=True)
    if args.user_locale is None:
        args.user_locale = model['object'].get('locale', None)
    csv_properties.update(data_locale=args.user_locale)
    if 'model_fields' in model['object']['model']:
        model_fields = model['object']['model']['model_fields'].keys()
        csv_properties.update(include=model_fields)
    if 'missing_tokens' in model['object']['model']:
        missing_tokens = model['object']['model']['missing_tokens']
    else:
        missing_tokens = MISSING_TOKENS
    csv_properties.update(missing_tokens=missing_tokens)
    objective_field = model['object']['objective_fields']
    if isinstance(objective_field, list):
        objective_field = objective_field[0]
    csv_properties.update(objective_field=objective_field)
    fields = Fields(model['object']['model']['fields'], **csv_properties)

    return fields, objective_field


def compute_output(api, args, training_set, test_set=None, output=None,
                   objective_field=None,
                   description=None,
                   field_attributes=None,
                   types=None,
                   dataset_fields=None,
                   model_fields=None,
                   name=None, training_set_header=True,
                   test_set_header=True, model_ids=None,
                   votes_files=None, resume=False, fields_map=None):
    """ Creates one or more models using the `training_set` or uses the ids
    of previously created BigML models to make predictions for the `test_set`.

    """
    source = None
    dataset = None
    model = None
    models = None
    fields = None

    # It is compulsory to have a description to publish either datasets or
    # models
    if (not description and
            (args.black_box or args.white_box or args.public_dataset)):
        raise Exception("You should provide a description to publish.")

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

    source, resume, csv_properties, fields = source_processing(
        training_set, test_set, training_set_header, test_set_header,
        name, description, api, args, resume, csv_properties=csv_properties,
        field_attributes=field_attributes,
        types=types, session_file=session_file, path=path, log=log)

    dataset, resume, csv_properties, fields = dataset_processing(
        source, training_set, test_set, model_ids, name, description, fields,
        dataset_fields, api, args, resume, csv_properties=csv_properties,
        session_file=session_file, path=path, log=log)

    # If test_split is used, split the dataset in a training and a test dataset
    # according to the given split
    if args.test_split > 0:
        dataset, test_dataset, resume = split_processing(
            dataset, name, description, api, args, resume,
            session_file=session_file, path=path, log=log)

    models, models_ids, resume = models_processing(
        dataset, models, model_ids, name, description, test_set,
        objective_field, fields, model_fields, api, args, resume,
        session_file=session_file, path=path, log=log)
    if models:
        model = models[0]

    # We get the fields of the model if we haven't got
    # them yet and update its public state if needed
    if model and not args.evaluate and (test_set or args.black_box
                                        or args.white_box):
        if args.black_box or args.white_box:
            model = r.publish_model(model, args, api, session_file)
            models[0] = model
        fields, objective_field = get_model_fields(model, model_fields,
                                                   csv_properties, args)

    # If predicting
    if models and test_set and not args.evaluate:
        predict(test_set, test_set_header, models, fields, output,
                objective_field, args.remote, api, log,
                args.max_batch_models, args.method, resume, args.tag,
                args.verbosity, session_file, args.debug)

    # When combine_votes flag is used, retrieve the predictions files saved
    # in the comma separated list of directories and combine them
    if votes_files:
        model_id = re.sub(r'.*(model_[a-f0-9]{24})__predictions\.csv$',
                          r'\1', votes_files[0]).replace("_", "/")
        try:
            model = bigml.api.check_resource(model_id, api.get_model)
        except ValueError, exception:
            sys.exit("Failed to get model %s: %s" % (model_id, str(exception)))

        local_model = Model(model)
        message = u.dated("Combining votes.\n")
        u.log_message(message, log_file=session_file,
                      console=args.verbosity)
        u.combine_votes(votes_files, local_model.to_prediction,
                        output, args.method)

    # If evaluate flag is on, create remote evaluation and save results in
    # json and human-readable format.
    if args.evaluate:
        if args.test_split > 0:
            dataset = test_dataset
        resume = evaluate(model, dataset, name, description, fields,
                          fields_map, output, api, args, resume,
                          session_file=session_file, path=path, log=log)

    # If cross_validation_rate is > 0, create remote evaluations and save
    # results in json and human-readable format. Then average the results to
    # issue a cross_validation measure set.
    if args.cross_validation_rate > 0:
        args.sample_rate = 1 - args.cross_validation_rate
        number_of_evaluations = int(MONTECARLO_FACTOR *
                                    args.cross_validation_rate)
        cross_validate(models, dataset, number_of_evaluations, name,
                       description, fields, fields_map, api, args, resume,
                       session_file=session_file, path=path, log=log)

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
    for i in range(0, len(args)):
        if args[i].startswith("--"):
            args[i] = args[i].replace("_", "-")
            if (args[i] == '--train' and
                    (i == len(args) - 1 or args[i + 1].startswith("--"))):
                train_stdin = True

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        for log_file in LOG_FILES:
            try:
                open(log_file, 'w', 0).close()
            except IOError:
                pass
    literal_args = args[:]
    for i in range(0, len(args)):
        if ' ' in args[i]:
            literal_args[i] = '"%s"' % args[i]
    message = "bigmler %s\n" % " ".join(literal_args)

    # Resume calls are not logged
    if not "--resume" in args:
        with open(COMMAND_LOG, "a", 0) as command_log:
            command_log.write(message)
        resume = False

    parser = create_parser(defaults=get_user_defaults(),
                           constants={'NOW': NOW,
                           'MAX_MODELS': MAX_MODELS, 'PLURALITY': PLURALITY})

    # Parses command line arguments.
    command_args = parser.parse_args(args)

    if command_args.cross_validation_rate > 0 and (
            command_args.test_set or command_args.evaluate or
            command_args.model or command_args.models or
            command_args.model_tag):
        parser.error("Non compatible flags: --cross-validation-rate"
                     " cannot be used with --evaluate, --model,"
                     " --models or --model-tag. Usage:\n\n"
                     "bigmler --train data/iris.csv "
                     "--cross-validation-rate 0.1")

    default_output = ('evaluation' if command_args.evaluate
                      else 'predictions.csv')
    if command_args.resume:
        debug = command_args.debug
        command = u.get_log_reversed(COMMAND_LOG,
                                     command_args.stack_level)
        args = shlex.split(command)[1:]
        try:
            position = args.index("--train")
            if (position == (len(args) - 1) or
                    args[position + 1].startswith("--")):
                train_stdin = True
        except ValueError:
            pass
        output_dir = u.get_log_reversed(DIRS_LOG,
                                        command_args.stack_level)
        defaults_file = "%s%s%s" % (output_dir, os.sep, DEFAULTS_FILE)
        parser = create_parser(defaults=get_user_defaults(defaults_file),
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
        if command_args.predictions is None:
            command_args.predictions = ("%s%s%s" %
                                        (NOW, os.sep,
                                         default_output))
        if len(os.path.dirname(command_args.predictions).strip()) == 0:
            command_args.predictions = ("%s%s%s" %
                                        (NOW, os.sep,
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
        command_args.training_set = StringIO.StringIO(sys.stdin.read())

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
        and not (command_args.test_set and (command_args.model or
                 command_args.models or command_args.model_tag or
                 command_args.ensemble))):
        parser.error("Evaluation wrong syntax.\n"
                     "\nTry for instance:\n\nbigmler --train data/iris.csv"
                     " --evaluate\nbigmler --model "
                     "model/5081d067035d076151000011 --dataset "
                     "dataset/5081d067035d076151003423 --evaluate\n"
                     "bigmler --ensemble ensemble/5081d067035d076151003443"
                     " --evaluate")

    if command_args.objective_field:
        objective = command_args.objective_field
        try:
            command_args.objective_field = int(objective)
        except ValueError:
            pass

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

    # Parses types if provided.
    if command_args.types:
        types_arg = u.read_types(command_args.types)
        output_args.update(types=types_arg)

    # Parses dataset fields if provided.
    if command_args.dataset_fields:
        dataset_fields_arg = map(lambda x: x.strip(),
                                 command_args.dataset_fields.split(','))
        output_args.update(dataset_fields=dataset_fields_arg)

    # Parses model input fields if provided.
    if command_args.model_fields:
        model_fields_arg = map(lambda x: x.strip(),
                               command_args.model_fields.split(','))
        output_args.update(model_fields=model_fields_arg)

    model_ids = []
    # Parses model/ids if provided.
    if command_args.models:
        model_ids = u.read_models(command_args.models)
        output_args.update(model_ids=model_ids)

    dataset_id = None
    # Parses dataset/id if provided.
    if command_args.datasets:
        dataset_id = u.read_dataset(command_args.datasets)
        command_args.dataset = dataset_id

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
    if (command_args.method and
            not command_args.method in COMBINATION_WEIGHTS.keys()):
        command_args.method = 0
    else:
        combiner_methods = dict([[value, key]
                                for key, value in COMBINER_MAP.items()])
        command_args.method = combiner_methods.get(command_args.method, 0)

    # Reads votes files in the provided directories.
    if command_args.votes_dirs:
        dirs = map(lambda x: x.strip(), command_args.votes_dirs.split(','))
        votes_path = os.path.dirname(command_args.predictions)
        votes_files = u.read_votes_files(dirs, votes_path)
        output_args.update(votes_files=votes_files)

    # Parses fields map if provided.
    if command_args.fields_map:
        fields_map_arg = u.read_fields_map(command_args.fields_map)
        output_args.update(fields_map=fields_map_arg)

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
            delete_list = map(lambda x: x.strip(),
                              command_args.delete_list.split(','))
        if command_args.delete_file:
            if not os.path.exists(command_args.delete_file):
                raise Exception("File %s not found" % command_args.delete_file)
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
    elif (command_args.training_set or command_args.test_set
          or command_args.source or command_args.dataset
          or command_args.datasets or command_args.votes_dirs):
        compute_output(**output_args)
    u.log_message("_" * 80 + "\n", log_file=session_file)

if __name__ == '__main__':
    main(sys.argv[1:])
