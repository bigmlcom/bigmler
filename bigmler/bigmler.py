# -*- coding: utf-8 -*-
#
# Copyright 2012-2014 BigML
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

import bigml.api
import bigmler.utils as u
import bigmler.resources as r
import bigmler.labels as l
import bigmler.processing.args as a
import bigmler.processing.sources as ps
import bigmler.processing.datasets as pd
import bigmler.processing.models as pm

from bigml.multivote import PLURALITY
from bigml.model import Model
from bigml.ensemble import Ensemble

from bigmler.evaluation import evaluate, cross_validate
from bigmler.options import create_parser
from bigmler.defaults import get_user_defaults
from bigmler.defaults import DEFAULTS_FILE
from bigmler.prediction import predict, combine_votes, remote_predict
from bigmler.prediction import (MAX_MODELS, OTHER, COMBINATION,
                                THRESHOLD_CODE)

COMMAND_LOG = ".bigmler"
DIRS_LOG = ".bigmler_dir_stack"
SESSIONS_LOG = "bigmler_sessions"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]


def has_test(args):
    """Returns if some kind of test data is given in args.

    """
    return args.test_set or args.test_source or args.test_dataset


def belongs_to_ensemble(model):
    """Checks if a model is part of an ensemble

    """
    return ('object' in model and 'ensemble' in model['object'] and
            model['object']['ensemble'])


def get_ensemble_id(model):
    """Returns the ensemble/id for a model that belongs to an ensemble

    """
    if 'object' in model and 'ensemble_id' in model['object']:
        return "ensemble/%s" % model['object']['ensemble_id']


def get_metadata(resource, key, default_value):
    """Retrieves from the user_metadata key in the resource the
       given key using default_value as a default

    """
    if ('object' in resource and 'user_metadata' in resource['object'] and
            key in resource['object']['user_metadata']):
        return resource['object']['user_metadata'][key]
    return default_value


def get_date(reference, api):
    """Extract the date from a given reference in days from now, date format
       or existing resource

    """
    days = None
    date = None
    try:
        days = int(reference)
        date = datetime.datetime.now() - datetime.timedelta(days=days)
    except ValueError:
        try:
            date = datetime.datetime.strptime(reference, '%Y-%m-%d')
            date = date.strftime('%Y-%m-%dT%H:%M:%S.%f')
        except ValueError:
            try:
                resource_type = bigml.api.get_resource_type(reference)
                resource = bigml.api.check_resource(reference,
                                                    api.getters[resource_type])
                date = resource['object']['created']
            except:
                return None
    return date


def delete_resources(command_args, api):
    """Deletes the resources selected by the user given options

    """
    if command_args.predictions is None:
        path = a.NOW
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

    resource_selectors = [
        (command_args.source_tag, api.list_sources),
        (command_args.dataset_tag, api.list_datasets),
        (command_args.model_tag, api.list_models),
        (command_args.prediction_tag, api.list_predictions),
        (command_args.evaluation_tag, api.list_evaluations),
        (command_args.ensemble_tag, api.list_ensembles),
        (command_args.batch_prediction_tag, api.list_batch_predictions)]

    query_string=None
    if command_args.older_than:
        date_str = get_date(command_args.older_than, api)
        if date_str:
            query_string = "created__lt=%s" % date_str
        else:
            sys.exit("The --older-than and --newer-than flags only accept "
                     "integers (number of days), dates in YYYY-MM-DD format "
                     " and resource ids. Please, double-check your input.")

    if command_args.newer_than:
        date_str = get_date(command_args.newer_than, api)
        if date_str:
            if query_string is None:
                query_string = ""
            else:
                query_string += ";"
            query_string += "created__gt=%s" % date_str
        else:
            sys.exit("The --older-than and --newer-than flags only accept "
                     "integers (number of days), dates in YYYY-MM-DD format "
                     " and resource ids. Please, double-check your input.")

    if (any([selector[0] is not None for selector in resource_selectors]) or
        command_args.all_tag):
        if query_string is None:
            query_string = ""
        else:
            query_string += ";"
        for selector, api_call in resource_selectors:
            combined_query = query_string
            if command_args.all_tag:
                combined_query += "tags__in=%s" % command_args.all_tag
                delete_list.extend(u.list_ids(api_call, combined_query))
            elif selector:
                combined_query += "tags__in=%s" % selector
                delete_list.extend(u.list_ids(api_call, combined_query))
    else:
        if query_string:
            for selector, api_call in resource_selectors:
                delete_list.extend(u.list_ids(api_call, query_string))

    message = u.dated("Deleting objects.\n")
    u.log_message(message, log_file=session_file,
                  console=command_args.verbosity)
    message = "\n".join(delete_list)
    u.log_message(message, log_file=session_file)
    #u.delete(api, delete_list)
    if sys.platform == "win32" and sys.stdout.isatty():
        message = (u"\nGenerated files:\n\n" +
                   unicode(u.print_tree(path, " "), "utf-8") + u"\n")
    else:
        message = "\nGenerated files:\n\n" + u.print_tree(path, " ") + "\n"
    u.log_message(message, log_file=session_file,
                  console=command_args.verbosity)


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
    multi_label_data = None
    multi_label_fields = []
    local_ensemble = None

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
        (training_set, multi_label_data) = ps.multi_label_expansion(
            training_set, training_set_header, objective_field, args, path,
            labels=labels, session_file=session_file)
        training_set_header = True
        objective_field = multi_label_data["objective_name"]
        all_labels = l.get_all_labels(multi_label_data)
        if not labels:
            labels = all_labels
    else:
        all_labels = labels

    source, resume, csv_properties, fields = ps.source_processing(
        training_set, test_set, training_set_header, test_set_header,
        api, args, resume, name=name, description=description,
        csv_properties=csv_properties, field_attributes=field_attributes,
        types=types, multi_label_data=multi_label_data,
        session_file=session_file, path=path, log=log)
    if args.multi_label and source:
        multi_label_data = l.get_multi_label_data(source)
        (objective_field, labels,
            all_labels, multi_label_fields) = l.multi_label_sync(
                objective_field, labels, multi_label_data, fields,
                multi_label_fields)

    datasets, resume, csv_properties, fields = pd.dataset_processing(
        source, training_set, test_set, fields, objective_field,
        api, args, resume, name=name, description=description,
        dataset_fields=dataset_fields, multi_label_data=multi_label_data,
        csv_properties=csv_properties,
        session_file=session_file, path=path, log=log)
    if datasets:
        dataset = datasets[0]

    # If test_split is used, split the dataset in a training and a test dataset
    # according to the given split
    if args.test_split > 0:
        dataset, test_dataset, resume = pd.split_processing(
            dataset, api, args, resume, name=name, description=description,
            multi_label_data=multi_label_data,
            session_file=session_file, path=path, log=log)
        datasets[0] = dataset

    # Check if the dataset has a categorical objective field and it
    # has a max_categories limit for categories
    if args.max_categories > 0 and len(datasets) == 1:
        objective_id = fields.field_id(fields.objective_field)
        if pd.check_max_categories(fields.fields[objective_id]):
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
            sys.exit("The provided objective field is not categorical nor "
                     "a full terms only text field. "
                     "Only these fields can be used with"
                     "  --max-categories")

    # Check if the dataset a generators file associated with it, and
    # generate a new dataset with the specified field structure
    if args.new_fields:
        dataset, resume = pd.create_new_dataset(
            dataset, api, args, resume, name=name,
            description=description, session_file=session_file, path=path,
            log=log)
        datasets[0] = dataset
    if args.multi_label and dataset and multi_label_data is None:
        multi_label_data = l.get_multi_label_data(dataset)
        (objective_field, labels,
            all_labels, multi_label_fields) = l.multi_label_sync(
                objective_field, labels, multi_label_data,
                fields, multi_label_fields)
    if dataset:
        # retrieves max_categories data, if any
        args.max_categories = get_metadata(dataset, 'max_categories',
                                           args.max_categories)
        other_label = get_metadata(dataset, 'other_label',
                                   other_label)

    models, model_ids, ensemble_ids, resume = pm.models_processing(
        datasets, models, model_ids,
        objective_field, fields, api, args, resume,
        name=name, description=description, model_fields=model_fields,
        session_file=session_file, path=path, log=log, labels=labels,
        multi_label_data=multi_label_data, other_label=other_label)
    if models:
        model = models[0]
        single_model = len(models) == 1

    # If multi-label flag is set and no training_set was provided, label
    # info is extracted from the user_metadata. If models belong to an
    # ensemble, the ensemble must be retrieved to get the user_metadata.
    if model and args.multi_label and multi_label_data is None:
        if len(ensemble_ids) > 0 and isinstance(ensemble_ids[0], dict):
            resource = ensemble_ids[0]
        elif belongs_to_ensemble(model):
            ensemble_id = get_ensemble_id(model)
            resource = r.get_ensemble(ensemble_id, api=api,
                                      verbosity=args.verbosity,
                                      session_file=session_file)
        else:
            resource = model
        multi_label_data = l.get_multi_label_data(resource)

    # We get the fields of the model if we haven't got
    # them yet and update its public state if needed
    if model and not args.evaluate and (test_set or args.black_box
                                        or args.white_box):
        if args.black_box or args.white_box:
            model = r.publish_model(model, args, api, session_file)
            models[0] = model
        # If more than one model, use the full field structure
        if (not single_model and not args.multi_label and
                belongs_to_ensemble(model)):
            if len(ensemble_ids) > 0:
                ensemble_id = ensemble_ids[0]
            else:
                ensemble_id = get_ensemble_id(model)
            local_ensemble = Ensemble(ensemble_id, api=api)
        fields, objective_field = pm.get_model_fields(
            model, csv_properties, args, single_model=single_model,
            multi_label_data=multi_label_data, local_ensemble=local_ensemble)

    # Fills in all_labels from user_metadata
    if args.multi_label and not all_labels:
        (objective_field, labels,
            all_labels, multi_label_fields) = l.multi_label_sync(
                objective_field, labels, multi_label_data,
                fields, multi_label_fields)
    if model:
        # retrieves max_categories data, if any
        args.max_categories = get_metadata(model, 'max_categories',
                                           args.max_categories)
        other_label = get_metadata(model, 'other_label',
                                   other_label)
    # If predicting
    if models and has_test(args) and not args.evaluate:
        models_per_label = 1
        test_dataset = None

        if args.multi_label:
            # When prediction starts from existing models, the
            # multi_label_fields can be retrieved from the user_metadata
            # in the models
            if args.multi_label_fields is None and multi_label_fields:
                multi_label_field_names = [field[1] for field
                                           in multi_label_fields]
                args.multi_label_fields = ",".join(multi_label_field_names)
            test_set = ps.multi_label_expansion(
                test_set, test_set_header, objective_field, args, path,
                labels=labels, session_file=session_file, input_flag=True)[0]
            test_set_header = True

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
                        api, args, resume, name=test_name,
                        description=description,
                        field_attributes=test_field_attributes,
                        types=test_types,
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

            csv_properties.update(objective_field=None,
                                  objective_field_present=False)
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
                    resume=resume, session_file=session_file, labels=labels,
                    models_per_label=models_per_label, other_label=other_label,
                    multi_label_data=multi_label_data)

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

        if args.multi_label and args.test_set is not None:
            # When evaluation starts from existing models, the
            # multi_label_fields can be retrieved from the user_metadata
            # in the models
            if args.multi_label_fields is None and multi_label_fields:
                args.multi_label_fields = multi_label_fields
            test_set = ps.multi_label_expansion(
                test_set, test_set_header, objective_field, args, path,
                labels=labels, session_file=session_file)[0]
            test_set_header = True

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
    (flags, train_stdin, test_stdin) = a.get_flags(args)

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        for log_file in LOG_FILES:
            try:
                open(log_file, 'w', 0).close()
            except IOError:
                pass
    message = a.get_command_message(args)

    # Resume calls are not logged
    if not "--resume" in args:
        with open(COMMAND_LOG, "a", 0) as command_log:
            command_log.write(message)
        resume = False
    user_defaults = get_user_defaults()
    parser = create_parser(defaults=get_user_defaults(),
                           constants={'NOW': a.NOW,
                                      'MAX_MODELS': MAX_MODELS,
                                      'PLURALITY': PLURALITY})
    # Parses command line arguments.
    command_args = a.parse_and_check(parser, args, train_stdin, test_stdin)

    default_output = ('evaluation' if command_args.evaluate
                      else 'predictions.csv')
    if command_args.resume:
        # Restore the args of the call to resume from the command log file
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
                               constants={'NOW': a.NOW,
                                          'MAX_MODELS': MAX_MODELS,
                                          'PLURALITY': PLURALITY})
        # Parses resumed arguments.
        command_args = a.parse_and_check(parser, args, train_stdin, test_stdin)
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
            command_args.output_dir = a.NOW
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

    # Creates the corresponding api instance
    if resume and debug:
        command_args.debug = True
    api = a.get_api_instance(command_args, u.check_dir(session_file))

    # Selects the action to perform: delete or create resources
    if command_args.delete:
        delete_resources(command_args, api)
    elif (command_args.training_set or has_test(command_args)
          or command_args.source or command_args.dataset
          or command_args.datasets or command_args.votes_dirs):
        output_args = a.get_output_args(api, train_stdin, test_stdin,
                                        command_args, resume)
        a.transform_args(command_args, flags, api, user_defaults)
        compute_output(**output_args)
    u.log_message("_" * 80 + "\n", log_file=session_file)

if __name__ == '__main__':
    main(sys.argv[1:])
