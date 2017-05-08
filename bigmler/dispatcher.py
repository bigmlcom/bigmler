# -*- coding: utf-8 -*-
#
# Copyright 2012-2017 BigML
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

"""BigMLer - main processing dispatching

"""
from __future__ import absolute_import

import sys
import os
import re
import gc
import shutil

import bigml.api

from bigml.model import Model
from bigml.basemodel import retrieve_resource
from bigml.fields import Fields

import bigmler.utils as u
import bigmler.resources as r
import bigmler.labels as l
import bigmler.processing.args as a
import bigmler.processing.sources as ps
import bigmler.processing.datasets as pd
import bigmler.processing.models as pm

from bigmler.evaluation import evaluate, cross_validate
from bigmler.defaults import DEFAULTS_FILE
from bigmler.prediction import predict, combine_votes, remote_predict
from bigmler.prediction import OTHER, COMBINATION
from bigmler.reports import clear_reports, upload_reports
from bigmler.command import Command, get_stored_command
from bigmler.command import COMMAND_LOG, DIRS_LOG, SESSIONS_LOG


LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
MINIMUM_MODEL = "full=false"


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


def has_source(args):
    """Checks whether the command options include a source or a previous
       training file
    """
    return (args.training_set or args.source or args.source_file or
            args.train_stdin)



def command_handling(args, log=COMMAND_LOG):
    """Rebuilds command string, logs it for --resume future requests and
       parses it.

    """
    # Create the Command object
    command = Command(args, None)

    # Resume calls are not logged
    if not command.resume:
        u.sys_log_message(command.command.replace('\\', '\\\\'), log_file=log)

    return command


def clear_log_files(log_files):
    """Clear all contents in log files

    """
    for log_file in log_files:
        try:
            open(log_file, 'w', 0).close()
        except IOError:
            pass


def get_test_dataset(args):
    """Returns the dataset id from one of the possible user options:
       --test-dataset --test-datasets

    """
    args.test_dataset_ids = []
    try:
        # Parses dataset/id if provided.
        if args.test_datasets:
            args.test_dataset_ids = u.read_datasets(args.test_datasets)
    except AttributeError:
        pass
    return (args.test_dataset if args.test_dataset is not None
            else None if not args.test_dataset_ids
            else args.test_dataset_ids[0])


def get_objective_id(args, fields):
    """Returns the objective id set by the user or the default

    """
    if args.objective_field is not None:
        try:
            objective_id = u.get_objective_id(fields, args.objective_field)
            fields.update_objective_field(
                fields.field_column_number(objective_id), True)
        except (KeyError, ValueError), exc:
            sys.exit(exc)
    else:
        return fields.field_id(fields.objective_field)
    return objective_id


def check_args_coherence(args):
    """Checks the given options for coherence and completitude

    """
    # It is compulsory to have a description to publish either datasets or
    # models
    if (not args.description_ and
            (args.black_box or args.white_box or args.public_dataset)):
        sys.exit("You should provide a description to publish.")

    # When using --max-categories, it is compulsory to specify also the
    # objective_field
    if args.max_categories > 0 and args.objective_field is None:
        sys.exit("When --max-categories is used, you must also provide the"
                 " --objective field name or column number")

    # When using --new-fields, it is compulsory to specify also a dataset
    # id
    if args.new_fields and not args.dataset:
        sys.exit("To use --new-fields you must also provide a dataset id"
                 " to generate the new dataset from it.")
    # The --median option is only available for local predictions, not for
    # remote ones.
    if args.median and args.remote:
        args.median = False
        print ("WARNING: the --median option is only available for local"
               " predictions. Using the mean value in the predicted node"
               " instead.")


def main_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    command = command_handling(args, COMMAND_LOG)

    # Parses command line arguments.
    command_args = a.parse_and_check(command)
    default_output = ('evaluation' if command_args.evaluate
                      else 'predictions.csv')
    resume = command_args.resume
    if command_args.resume:
        command_args, session_file, output_dir = get_stored_command(
            args, command_args.debug, command_log=COMMAND_LOG,
            dirs_log=DIRS_LOG, sessions_log=SESSIONS_LOG)
        default_output = ('evaluation' if command_args.evaluate
                          else 'predictions.csv')
        if command_args.predictions is None:
            command_args.predictions = os.path.join(output_dir,
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
            shutil.copy(DEFAULTS_FILE, os.path.join(directory, DEFAULTS_FILE))
        except IOError:
            pass
        u.sys_log_message(u"%s\n" % os.path.abspath(directory),
                          log_file=DIRS_LOG)

    # Creates the corresponding api instance
    api = a.get_api_instance(command_args, u.check_dir(session_file))

    if (a.has_train(command_args) or a.has_test(command_args)
            or command_args.votes_dirs):
        output_args = a.get_output_args(api, command_args, resume)
        a.transform_args(command_args, command.flags, api)
        compute_output(**output_args)
    u.log_message("_" * 80 + "\n", log_file=session_file)


def compute_output(api, args):
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
    #local_ensemble = None
    test_dataset = None
    datasets = None

    # variables from command-line options
    resume = args.resume_
    model_ids = args.model_ids_
    output = args.predictions
    dataset_fields = args.dataset_fields_

    check_args_coherence(args)
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
    labels = (None if args.labels is None else
              [label.strip() for label in
               args.labels.split(args.args_separator)])
    if labels is not None:
        labels = sorted([label for label in labels])

    # multi_label file must be preprocessed to obtain a new extended file
    if args.multi_label and args.training_set is not None:
        (args.training_set, multi_label_data) = ps.multi_label_expansion(
            args.training_set, args.train_header, args, path,
            labels=labels, session_file=session_file)
        args.train_header = True
        args.objective_field = multi_label_data["objective_name"]
        all_labels = l.get_all_labels(multi_label_data)
        if not labels:
            labels = all_labels
    else:
        all_labels = labels
    if args.objective_field:
        csv_properties.update({'objective_field': args.objective_field})
    if args.source_file:
        # source is retrieved from the contents of the given local JSON file
        source, csv_properties, fields = u.read_local_resource(
            args.source_file,
            csv_properties=csv_properties)
    else:
        # source is retrieved from the remote object
        source, resume, csv_properties, fields = ps.source_processing(
            api, args, resume,
            csv_properties=csv_properties, multi_label_data=multi_label_data,
            session_file=session_file, path=path, log=log)
    if args.multi_label and source:
        multi_label_data = l.get_multi_label_data(source)
        (args.objective_field,
         labels,
         all_labels,
         multi_label_fields) = l.multi_label_sync(args.objective_field,
                                                  labels,
                                                  multi_label_data,
                                                  fields,
                                                  multi_label_fields)
    if fields and args.export_fields:
        fields.summary_csv(os.path.join(path, args.export_fields))
    if args.dataset_file:
        # dataset is retrieved from the contents of the given local JSON file
        model_dataset, csv_properties, fields = u.read_local_resource(
            args.dataset_file,
            csv_properties=csv_properties)
        if not args.datasets:
            datasets = [model_dataset]
            dataset = model_dataset
        else:
            datasets = u.read_datasets(args.datasets)
    if not datasets:
        # dataset is retrieved from the remote object
        datasets, resume, csv_properties, fields = pd.dataset_processing(
            source, api, args, resume,
            fields=fields,
            csv_properties=csv_properties,
            multi_label_data=multi_label_data,
            session_file=session_file, path=path, log=log)
    if datasets:
        dataset = datasets[0]
        if args.to_csv is not None:
            resume = pd.export_dataset(dataset, api, args, resume,
                                       session_file=session_file, path=path)

        # Now we have a dataset, let's check if there's an objective_field
        # given by the user and update it in the fields structure
        args.objective_id_ = get_objective_id(args, fields)

    # If test_split is used, split the dataset in a training and a test dataset
    # according to the given split
    if args.test_split > 0:
        dataset, test_dataset, resume = pd.split_processing(
            dataset, api, args, resume,
            multi_label_data=multi_label_data,
            session_file=session_file, path=path, log=log)
        datasets[0] = dataset

    # Check if the dataset has a categorical objective field and it
    # has a max_categories limit for categories
    if args.max_categories > 0 and len(datasets) == 1:
        if pd.check_max_categories(fields.fields[args.objective_id_]):
            distribution = pd.get_categories_distribution(dataset,
                                                          args.objective_id_)
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
            datasets, api, args, resume, fields=fields,
            session_file=session_file, path=path, log=log)
        datasets = [dataset]

    # Check if the dataset has a generators file associated with it, and
    # generate a new dataset with the specified field structure. Also
    # if the --to-dataset flag is used to clone or sample the original dataset
    if args.new_fields or (args.sample_rate != 1 and args.no_model) or \
            (args.lisp_filter or args.json_filter) and not has_source(args):
        if fields is None:
            if isinstance(dataset, basestring):
                dataset = u.check_resource(dataset, api=api)
            fields = Fields(dataset, csv_properties)
        args.objective_id_ = get_objective_id(args, fields)
        args.objective_name_ = fields.field_name(args.objective_id_)
        dataset, resume = pd.create_new_dataset(
            dataset, api, args, resume, fields=fields,
            session_file=session_file, path=path, log=log)
        datasets[0] = dataset
        # rebuild fields structure for new ids and fields
        csv_properties.update({'objective_field': args.objective_name_,
                               'objective_field_present': True})
        fields = pd.get_fields_structure(dataset, csv_properties)
        args.objective_id_ = get_objective_id(args, fields)
    if args.multi_label and dataset and multi_label_data is None:
        multi_label_data = l.get_multi_label_data(dataset)
        (args.objective_field,
         labels,
         all_labels,
         multi_label_fields) = l.multi_label_sync(args.objective_field,
                                                  labels,
                                                  multi_label_data,
                                                  fields, multi_label_fields)

    if dataset:
        # retrieves max_categories data, if any
        args.max_categories = get_metadata(dataset, 'max_categories',
                                           args.max_categories)
        other_label = get_metadata(dataset, 'other_label',
                                   other_label)
    if fields and args.export_fields:
        fields.summary_csv(os.path.join(path, args.export_fields))
    if args.model_file:
        # model is retrieved from the contents of the given local JSON file
        model, csv_properties, fields = u.read_local_resource(
            args.model_file,
            csv_properties=csv_properties)
        models = [model]
        model_ids = [model['resource']]
        ensemble_ids = []
    elif args.ensemble_file:
        # model is retrieved from the contents of the given local JSON file
        ensemble, csv_properties, fields = u.read_local_resource(
            args.ensemble_file,
            csv_properties=csv_properties)
        model_ids = ensemble['object']['models'][:]
        ensemble_ids = [ensemble['resource']]
        models = model_ids[:]

        model = retrieve_resource(args.retrieve_api_,
                                  models[0],
                                  query_string=r.ALL_FIELDS_QS)
        models[0] = model
    else:
        # model is retrieved from the remote object
        models, model_ids, ensemble_ids, resume = pm.models_processing(
            datasets, models, model_ids,
            api, args, resume, fields=fields,
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
        if (isinstance(model, basestring) or
                bigml.api.get_status(model)['code'] != bigml.api.FINISHED):
            if not args.evaluate and not a.has_train(args) and \
                    not a.has_test(args):
                query_string = MINIMUM_MODEL
            elif not args.test_header:
                query_string = r.ALL_FIELDS_QS
            else:
                query_string = "%s;%s" % (r.ALL_FIELDS_QS, r.FIELDS_QS)
            model = u.check_resource(model, api.get_model,
                                     query_string=query_string)
            models[0] = model
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
    if model and not args.evaluate and (a.has_test(args) or
                                        args.export_fields):
        # if we are using boosted ensembles to predict, activate boosting
        if model['object'].get('boosted_ensemble'):
            args.boosting = True
        # If more than one model, use the full field structure
        if (not single_model and not args.multi_label and
                belongs_to_ensemble(model)):
            if len(ensemble_ids) > 0:
                ensemble_id = ensemble_ids[0]
                args.ensemble_ids_ = ensemble_ids
            else:
                ensemble_id = get_ensemble_id(model)
        fields = pm.get_model_fields(
            model, csv_properties, args, single_model=single_model,
            multi_label_data=multi_label_data)
        # Free memory after getting fields
        # local_ensemble = None
        gc.collect()

    # Fills in all_labels from user_metadata
    if args.multi_label and not all_labels:
        (args.objective_field,
         labels,
         all_labels,
         multi_label_fields) = l.multi_label_sync(args.objective_field, labels,
                                                  multi_label_data, fields,
                                                  multi_label_fields)
    if model:
        # retrieves max_categories data, if any
        args.max_categories = get_metadata(model, 'max_categories',
                                           args.max_categories)
        other_label = get_metadata(model, 'other_label',
                                   other_label)
    if fields and args.export_fields:
        fields.summary_csv(os.path.join(path, args.export_fields))
    # If predicting
    if (models and (a.has_test(args) or (test_dataset and args.remote))
            and not args.evaluate):
        models_per_label = 1
        if test_dataset is None:
            test_dataset = get_test_dataset(args)

        if args.multi_label:
            # When prediction starts from existing models, the
            # multi_label_fields can be retrieved from the user_metadata
            # in the models
            if args.multi_label_fields is None and multi_label_fields:
                multi_label_field_names = [field[1] for field
                                           in multi_label_fields]
                args.multi_label_fields = ",".join(multi_label_field_names)
            test_set = ps.multi_label_expansion(
                args.test_set, args.test_header, args, path,
                labels=labels, session_file=session_file, input_flag=True)[0]
            test_set_header = True

        # Remote predictions: predictions are computed as batch predictions
        # in bigml.com except when --no-batch flag is set on or multi-label
        # or max-categories are used
        if (args.remote and not args.no_batch and not args.multi_label
                and not args.method == COMBINATION):
            # create test source from file
            test_name = "%s - test" % args.name
            if args.test_source is None:
                test_properties = ps.test_source_processing(
                    api, args, resume, session_file=session_file,
                    path=path, log=log)

                (test_source, resume, csv_properties,
                 test_fields) = test_properties
            else:
                test_source_id = bigml.api.get_source_id(args.test_source)
                test_source = api.check_resource(test_source_id)
            if test_dataset is None:
            # create test dataset from test source
                dataset_args = r.set_basic_dataset_args(args, name=test_name)
                test_dataset, resume = pd.alternative_dataset_processing(
                    test_source, "test", dataset_args, api, args,
                    resume, session_file=session_file, path=path, log=log)
            else:
                test_dataset_id = bigml.api.get_dataset_id(test_dataset)
                test_dataset = api.check_resource(test_dataset_id)

            csv_properties.update(objective_field=None,
                                  objective_field_present=False)
            test_fields = pd.get_fields_structure(test_dataset,
                                                  csv_properties)

            if args.to_dataset and args.dataset_off:
                model = api.check_resource(model['resource'],
                                           query_string=r.ALL_FIELDS_QS)
                model_fields = Fields(model)
                objective_field_name = model_fields.field_name( \
                    model_fields.objective_field)
                if objective_field_name in test_fields.fields_by_name.keys():
                    args.prediction_name = "%s (predicted)" % \
                        objective_field_name
            batch_prediction_args = r.set_batch_prediction_args(
                args, fields=fields,
                dataset_fields=test_fields)

            remote_predict(model, test_dataset, batch_prediction_args, args,
                           api, resume, prediction_file=output,
                           session_file=session_file, path=path, log=log)
        else:
            models_per_label = args.number_of_models
            if (args.multi_label and len(ensemble_ids) > 0
                    and args.number_of_models == 1):
                # use case where ensembles are read from a file
                models_per_label = len(models) / len(ensemble_ids)
            predict(models, fields, args, api=api, log=log,
                    resume=resume, session_file=session_file, labels=labels,
                    models_per_label=models_per_label, other_label=other_label,
                    multi_label_data=multi_label_data)

    # When combine_votes flag is used, retrieve the predictions files saved
    # in the comma separated list of directories and combine them
    if args.votes_files_:
        model_id = re.sub(r'.*(model_[a-f0-9]{24})__predictions\.csv$',
                          r'\1', args.votes_files_[0]).replace("_", "/")
        try:
            model = u.check_resource(model_id, api.get_model)
        except ValueError, exception:
            sys.exit("Failed to get model %s: %s" % (model_id, str(exception)))

        local_model = Model(model)
        message = u.dated("Combining votes.\n")
        u.log_message(message, log_file=session_file,
                      console=args.verbosity)

        combine_votes(args.votes_files_, local_model.to_prediction,
                      output, method=args.method)

    # If evaluate flag is on, create remote evaluation and save results in
    # json and human-readable format.
    if args.evaluate:
        # When we resume evaluation and models were already completed, we
        # should use the datasets array as test datasets
        if args.has_test_datasets_:
            test_dataset = get_test_dataset(args)
        if args.dataset_off and not args.has_test_datasets_:
            args.test_dataset_ids = datasets
        if args.test_dataset_ids and args.dataset_off:
            eval_ensembles = len(ensemble_ids) == len(args.test_dataset_ids)
            models_or_ensembles = (ensemble_ids if eval_ensembles else
                                   models)
            # Evaluate the models with the corresponding test datasets.
            resume = evaluate(models_or_ensembles, args.test_dataset_ids, api,
                              args, resume,
                              fields=fields, dataset_fields=dataset_fields,
                              session_file=session_file, path=path,
                              log=log, labels=labels, all_labels=all_labels,
                              objective_field=args.objective_field)
        else:
            if args.multi_label and args.test_set is not None:
                # When evaluation starts from existing models, the
                # multi_label_fields can be retrieved from the user_metadata
                # in the models
                if args.multi_label_fields is None and multi_label_fields:
                    args.multi_label_fields = multi_label_fields
                test_set = ps.multi_label_expansion(
                    test_set, test_set_header, args, path,
                    labels=labels, session_file=session_file)[0]
                test_set_header = True

            if args.test_split > 0 or args.has_test_datasets_:
                dataset = test_dataset
            dataset = u.check_resource(dataset, api=api,
                                       query_string=r.ALL_FIELDS_QS)
            dataset_fields = pd.get_fields_structure(dataset, None)
            models_or_ensembles = (ensemble_ids if ensemble_ids != []
                                   else models)
            resume = evaluate(models_or_ensembles, [dataset], api,
                              args, resume,
                              fields=fields, dataset_fields=dataset_fields,
                              session_file=session_file, path=path,
                              log=log, labels=labels, all_labels=all_labels,
                              objective_field=args.objective_field)

    # If cross_validation_rate is > 0, create remote evaluations and save
    # results in json and human-readable format. Then average the results to
    # issue a cross_validation measure set.
    if args.cross_validation_rate > 0:
        args.sample_rate = 1 - args.cross_validation_rate
        cross_validate(models, dataset, fields, api, args, resume,
                       session_file=session_file,
                       path=path, log=log)

    u.print_generated_files(path, log_file=session_file,
                            verbosity=args.verbosity)
    if args.reports:
        clear_reports(path)
        if args.upload:
            upload_reports(args.reports, path)
