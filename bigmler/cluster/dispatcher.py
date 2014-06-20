# -*- coding: utf-8 -*-
#
# Copyright 2014 BigML
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

"""BigMLer - cluster subcommand processing dispatching

"""
from __future__ import absolute_import

import sys
import os
import re
import datetime

import bigml.api
import bigmler.utils as u
import bigmler.resources as r
import bigmler.labels as l
import bigmler.processing.args as a
import bigmler.processing.sources as ps
import bigmler.processing.datasets as pd
import bigmler.processing.models as pm
import bigmler.processing.clusters as pc

from bigml.model import Model
from bigml.ensemble import Ensemble

from bigmler.evaluation import evaluate, cross_validate
from bigmler.defaults import DEFAULTS_FILE
from bigmler.prediction import predict, combine_votes, remote_predict
from bigmler.prediction import (OTHER, COMBINATION,
                                THRESHOLD_CODE)
from bigmler.reports import clear_reports, upload_reports
from bigmler.command import Command, StoredCommand

from bigmler.dispatcher import (COMMAND_LOG, command_handling, clear_log_files,
                                has_test, has_train)

COMMAND_LOG = ".bigmler_cluster"
DIRS_LOG = ".bigmler_cluster_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
MINIMUM_MODEL = "full=false"


def cluster_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    command = command_handling(args, COMMAND_LOG)

    # Parses command line arguments.
    command_args = a.parse_and_check(command)
    default_output = 'centroids.csv'
    resume = command_args.resume
    if command_args.resume:
        # Keep the debug option if set
        debug = command_args.debug
        # Restore the args of the call to resume from the command log file
        stored_command = StoredCommand(args, COMMAND_LOG, DIRS_LOG)
        command = Command(None, stored_command=stored_command)
        # Logs the issued command and the resumed command
        session_file = os.path.join(stored_command.output_dir, SESSIONS_LOG)
        stored_command.log_command(session_file=session_file)
        # Parses resumed arguments.
        command_args = a.parse_and_check(command)
        default_output = 'centroids.csv'
        if command_args.predictions is None:
            command_args.predictions = os.path.join(stored_command.output_dir,
                                                    default_output)
    else:
        if command_args.output_dir is None:
            command_args.output_dir = a.NOW
        if command_args.predictions is None:
            command_args.predictions = os.path.join(command_args.output_dir,
                                                    default_output)
        if len(os.path.dirname(command_args.predictions).strip()) == 0:
            command_args.predictions = os.path.join(command_args.output_dir,
                                                    command_args.predictions)
        directory = u.check_dir(command_args.predictions)
        session_file = os.path.join(directory, SESSIONS_LOG)
        u.log_message(command.command + "\n", log_file=session_file)
        try:
            defaults_file = open(DEFAULTS_FILE, 'r')
            contents = defaults_file.read()
            defaults_file.close()
            defaults_copy = open(os.path.join(directory, DEFAULTS_FILE),
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

    # Selects the action to perform
    if (has_train(command_args) or has_test(command_args)
            or command_args.votes_dirs):
        output_args = a.get_output_args(api, command.train_stdin,
                                        command.test_stdin,
                                        command_args, resume)
        a.transform_args(command_args, command.flags, api,
                         command.user_defaults)
        compute_output(**output_args)
    u.log_message("_" * 80 + "\n", log_file=session_file)


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
    cluster = None
    clusters = None
    fields = None
    other_label = OTHER
    multi_label_data = None
    multi_label_fields = []

    # It is compulsory to have a description to publish either datasets or
    # models
    if (not description and (args.public_cluster or args.public_dataset)):
        sys.exit("You should provide a description to publish.")

    # When using --new-fields, it is compulsory to specify also a dataset
    # id
    if args.new_fields and not args.dataset:
        sys.exit("To use --new-fields you must also provide a dataset id"
                 " to generate the new dataset from it.")

    path = u.check_dir(output)
    session_file = "%s%s%s" % (path, os.sep, SESSIONS_LOG)
    csv_properties = {}
    # If logging is required set the file for logging
    log = None
    if args.log_file:
        u.check_dir(args.log_file)
        log = args.log_file
        # If --clear_logs the log files are cleared
        clear_log_files([log])

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

    # If multi-dataset flag is on, generate a new dataset from the given
    # list of datasets
    if args.multi_dataset:
        dataset, resume = pd.create_new_dataset(
            datasets, api, args, resume, name=name,
            description=description, fields=fields,
            dataset_fields=dataset_fields, objective_field=objective_field,
            session_file=session_file, path=path, log=log)
        datasets = [dataset]

    # Check if the dataset has a generators file associated with it, and
    # generate a new dataset with the specified field structure
    if args.new_fields:
        dataset, resume = pd.create_new_dataset(
            dataset, api, args, resume, name=name,
            description=description, fields=fields,
            dataset_fields=dataset_fields, objective_field=objective_field,
            session_file=session_file, path=path, log=log)
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

    # We update the model's public state if needed
    if model:
        if isinstance(model, basestring):
            if not args.evaluate:
                query_string = MINIMUM_MODEL
            else:
                query_string = r.FIELDS_QS
            model = u.check_resource(model, api.get_model,
                                     query_string=query_string)
        if (args.black_box or args.white_box or
                (args.shared_flag and r.shared_changed(args.shared, model))):
            model_args = {}
            if args.shared_flag and r.shared_changed(args.shared, model):
                model_args.update(shared=args.shared)
            if args.black_box or args.white_box:
                model_args.update(r.set_publish_model_args(args))
            if model_args:
                model = r.update_model(model, model_args, args,
                                       api=api, path=path,
                                       session_file=session_file)
                models[0] = model

    # We get the fields of the model if we haven't got
    # them yet and need them
    if model and not args.evaluate and test_set:
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
        # When we resume evaluation and models were already completed, we
        # should use the datasets array as test datasets
        if args.dataset_off and not args.test_dataset_ids:
            args.test_dataset_ids = datasets
        if args.test_dataset_ids:
            # Evaluate the models with the corresponding test datasets.
            resume = evaluate(models, args.test_dataset_ids, output, api,
                              args, resume, name=name, description=description,
                              fields=fields, dataset_fields=dataset_fields,
                              fields_map=fields_map,
                              session_file=session_file, path=path,
                              log=log, labels=labels, all_labels=all_labels,
                              objective_field=objective_field)
        else:
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
            models_or_ensembles = (ensemble_ids if ensemble_ids != []
                                   else models)
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
                   unicode(u.print_tree(path, u" "), "utf-8") + u"\n")
    else:
        message = (u"\nGenerated files:\n\n" + 
                   u.print_tree(path, u" ") + u"\n")
    u.log_message(message, log_file=session_file, console=args.verbosity)
    if args.reports:
        clear_reports(path)
        if args.upload:
            upload_reports(args.reports, path)
