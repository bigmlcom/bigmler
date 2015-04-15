# -*- coding: utf-8 -*-
#
# Copyright 2012-2104 BigML
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
"""Resources management functions

"""
from __future__ import absolute_import

import sys
import time

try:
    import simplejson as json
except ImportError:
    import json

import bigml.api

from bigmler.utils import (dated, get_url, log_message, plural, check_resource,
                           check_resource_error, log_created_resources,
                           is_shared)
from bigmler.labels import label_model_args, get_all_labels
from bigmler.reports import report
from bigml.util import bigml_locale


EVALUATE_SAMPLE_RATE = 0.8
SEED = "BigML, Machine Learning made easy"
LOCALE_DEFAULT = "en_US"
FIELDS_QS = 'only_model=true'
ALL_FIELDS_QS = "limit=-1"
ADD_PREFIX = '+'
REMOVE_PREFIX = '-'
ADD_REMOVE_PREFIX = [ADD_PREFIX, REMOVE_PREFIX]
BRIEF_FORMAT = 'brief'
NORMAL_FORMAT = 'normal'
FULL_FORMAT = 'full'


def get_basic_seed(order):
    """ Builds a standard seed from a text adding the order

    """
    return "%s - %s" % (SEED, order)


def shared_changed(shared, resource):
    """Returns True if the shared status of the resource differs from the user
       given value

    """
    return is_shared(resource) != shared


def configure_input_fields(fields, user_given_fields, by_name=False):
    """ Returns the input fields used in the new resource creation as given

        The user can choose to write all the fields that will be used in the
        new resource or modify the set of fields retrieved from the
        resource that will be used to create the new one.
    """
    def modify_input_fields(prefix, field, input_fields):
        """Adds or removes according to the prefix in the given field
           this field from the list of input fields.

        """
        if prefix == ADD_PREFIX:
            if not field in input_fields:
                input_fields.append(field)
        elif field in input_fields:
            input_fields.remove(field)

    # case of adding and removing fields to the dataset preferred field set
    if all([name[0] in ADD_REMOVE_PREFIX for name in user_given_fields]):
        preferred_fields = fields.preferred_fields()
        input_fields = preferred_fields.keys()
        if by_name:
            input_fields = [fields.field_name(field_id) for field_id in
                            input_fields]
        for name in user_given_fields:
            prefix = name[0]
            field_name = name[1:]
            if by_name:
                modify_input_fields(prefix, field_name, input_fields)
            else:
                try:
                    field_id = fields.field_id(field_name)
                except ValueError, exc:
                    sys.exit(exc)
                modify_input_fields(prefix, field_id, input_fields)
    # case of user given entire list of fields
    else:
        if by_name:
            return user_given_fields
        else:
            input_fields = []
            for name in user_given_fields:
                try:
                    input_fields.append(fields.field_id(name))
                except ValueError, exc:
                    sys.exit(exc)
    return input_fields


def update_attributes(updatable_attributes, new_attributes, by_column=False,
                      fields=None):
    """Correctly merging the "fields" attribute substructure in updates.

       updatable_attributes: previous attributes to be updated
       new_attributes: updates to be added
       by_column: set to True is keys are the column position of the field
       fields: Fields object info
    """
    if new_attributes:
        fields_substructure = updatable_attributes.get("fields", {})
        field_attributes = new_attributes.get("fields", {})
        if field_attributes and (not by_column or fields):
            for field_key, value in field_attributes.items():
                field_id = (field_key if not by_column
                            else fields.field_id(field_key))
                if not field_id in fields_substructure.keys():
                    fields_substructure.update({field_id: {}})
                fields_substructure[field_id].update(value)
            updatable_attributes.update({"fields": fields_substructure})
        else:
            updatable_attributes.update(new_attributes)


def relative_input_fields(fields, user_given_fields):
    """Returns the user given input fields using relative syntax

    """

    input_fields = []
    if all([(name[0] in ADD_REMOVE_PREFIX) for name in user_given_fields]):
        return user_given_fields

    preferred_fields = fields.preferred_fields()
    for field_id in preferred_fields.keys():
        name = fields.fields[field_id]['name']
        if not name in user_given_fields:
            input_fields.append("%s%s" % (REMOVE_PREFIX, name))
    for name in user_given_fields:
        try:
            field_id = fields.field_id(name)
        except ValueError, exc:
            sys.exit(exc)
        input_fields.append("%s%s" % (ADD_PREFIX, name))

    return input_fields


def wait_for_available_tasks(inprogress, max_parallel, api,
                             resource_type, wait_step=2):
    """According to the max_parallel number of parallel resources to be
       created, when the number of in progress resources reaches the limit,
       it checks the ones in inprogress to see if there's a
       FINISHED or FAULTY resource. If found, it is removed from the
       inprogress list and returns to allow another one to be created.

    """

    check_kwargs = {"retries": 0, "query_string": "full=false", "api": api}
    while len(inprogress) == max_parallel:
        for j in range(0, len(inprogress)):
            try:
                ready = check_resource(inprogress[j], **check_kwargs)
                status = bigml.api.get_status(ready)
                if status['code'] == bigml.api.FINISHED:
                    del inprogress[j]
                    return
                elif status['code'] == bigml.api.FAULTY:
                    raise ValueError(status['message'])
            except ValueError, exception:
                sys.exit("Failed to get a finished %s: %s" %
                         (resource_type, str(exception)))
        time.sleep(max_parallel * wait_step)


def set_source_args(args, name=None, multi_label_data=None,
                    data_set_header=None, fields=None):
    """Returns a source arguments dict

    """

    if name is None:
        name = args.name
    source_args = {
        "name": name,
        "description": args.description_,
        "category": args.category,
        "tags": args.tag}
    if args.project_id is not None:
        source_args.update({"project": args.project_id})
    # if header is set, use it
    if data_set_header is not None:
        source_args.update({"source_parser": {"header": data_set_header}})
    # If user has given an OS locale, try to add the locale used in bigml.com
    if args.user_locale is not None:
        source_locale = bigml_locale(args.user_locale)
        if source_locale is None:
            log_message("WARNING: %s locale equivalence not found."
                        " Using %s instead.\n" % (args.user_locale,
                                                  LOCALE_DEFAULT),
                        log_file=None, console=True)
            source_locale = LOCALE_DEFAULT
        source_args.update({'source_parser': {}})
        source_args["source_parser"].update({'locale': source_locale})
    # If user has set a training separator, use it.
    if args.training_separator is not None:
        training_separator = args.training_separator.decode("string_escape")
        source_args["source_parser"].update({'separator': training_separator})
    # If uploading a multi-label file, add the user_metadata info needed to
    # manage the multi-label fields
    if (hasattr(args, 'multi_label') and args.multi_label
            and multi_label_data is not None):
        source_args.update({
            "user_metadata": {
                "multi_label_data": multi_label_data}})

    # to update fields attributes or types you must have a previous fields
    # structure (at update time)
    if fields:
        if args.field_attributes_:
            update_attributes(source_args,
                              {"fields": args.field_attributes_},
                              by_column=True, fields=fields)
        if args.types_:
            update_attributes(source_args,
                              {"fields": args.types_},
                              by_column=True, fields=fields)

        update_attributes(source_args, args.json_args.get('source'))
    return source_args


def create_source(data_set, source_args, args, api=None, path=None,
                  session_file=None, log=None, source_type=None):
    """Creates remote source

    """
    if api is None:
        api = bigml.api.BigML()
    suffix = "" if source_type is None else "%s " % source_type
    message = dated("Creating %ssource.\n" % suffix)
    log_message(message, log_file=session_file, console=args.verbosity)

    source = api.create_source(data_set, source_args,
                               progress_bar=args.progress_bar)
    if path is not None:
        try:
            suffix = "_" + source_type if source_type else ""
            with open("%s/source%s" % (path, suffix), 'w', 0) as source_file:
                source_file.write("%s\n" % source['resource'])
                source_file.write("%s\n" % source['object']['name'])
        except IOError, exc:
            sys.exit("%s: Failed to write %s/source" % (str(exc), path))
    source_id = check_resource_error(source, "Failed to create source: ")
    try:
        source = check_resource(source, api.get_source,
                                query_string=ALL_FIELDS_QS)
    except ValueError, exception:
        sys.exit("Failed to get a finished source: %s" % str(exception))
    message = dated("Source created: %s\n" % get_url(source))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % source_id, log_file=log)
    if args.reports:
        report(args.reports, path, source)
    return source


def data_to_source(args):
    """Extracts the flags info to create a source object

    """
    data_set = None
    data_set_header = None
    if (args.training_set and not args.source and not args.dataset and
            not args.has_models_):
        data_set = args.training_set
        data_set_header = args.train_header
    elif (hasattr(args, 'evaluate') and args.evaluate and args.test_set
          and not args.source):
        data_set = args.test_set
        data_set_header = args.test_header

    return data_set, data_set_header


def get_source(source, api=None, verbosity=True,
               session_file=None):
    """Retrieves the source in its actual state and its field info

    """
    if api is None:
        api = bigml.api.BigML()
    if (isinstance(source, basestring) or
            bigml.api.get_status(source)['code'] != bigml.api.FINISHED):
        message = dated("Retrieving source. %s\n" %
                        get_url(source))
        log_message(message, log_file=session_file,
                    console=verbosity)
        try:
            source = check_resource(source, api.get_source,
                                    query_string=ALL_FIELDS_QS)
        except ValueError, exception:
            sys.exit("Failed to get a finished source: %s" % str(exception))
    return source


def update_source(source, source_args, args,
                  api=None, session_file=None):
    """Updates source properties

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Updating source. %s\n" %
                    get_url(source))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    source = api.update_source(source, source_args)
    check_resource_error(source, "Failed to update source: ")
    source = check_resource(source, api.get_source)
    return source


def set_basic_dataset_args(args, name=None):
    """Return dataset basic arguments dict

    """
    if name is None:
        name = args.name
    dataset_args = {
        "name": name,
        "description": args.description_,
        "category": args.category,
        "tags": args.tag
    }

    return dataset_args


def set_dataset_args(args, fields, multi_label_data=None):
    """Return dataset arguments dict

    """
    dataset_args = set_basic_dataset_args(args)
    objective_field = (None if not hasattr(args, 'objective_field')
                       else args.objective_field)
    if multi_label_data is not None and objective_field is None:
        objective_field = multi_label_data['objective_name']
    if objective_field is not None and fields is not None:
        try:
            objective_id = fields.field_id(objective_field)
        except ValueError, exc:
            sys.exit(exc)
        dataset_args.update(objective_field={'id': objective_id})

    if args.json_filter:
        dataset_args.update(json_filter=args.json_filter)
    elif args.lisp_filter:
        dataset_args.update(lisp_filter=args.lisp_filter)

    if args.dataset_fields_ and fields is not None:
        input_fields = configure_input_fields(fields, args.dataset_fields_)
        dataset_args.update(input_fields=input_fields)
    if (hasattr(args, 'multi_label') and args.multi_label
            and multi_label_data is not None):
        dataset_args.update(
            user_metadata={'multi_label_data': multi_label_data})
    update_attributes(dataset_args, args.json_args.get('dataset'))
    return dataset_args


def set_dataset_split_args(name, description, args, sample_rate,
                           out_of_bag=False, multi_label_data=None):
    """Return dataset arguments dict to split a dataset

    """
    dataset_args = {
        "name": name,
        "description": description,
        "category": args.category,
        "tags": args.tag,
        "seed": SEED if args.seed is None else args.seed,
        "sample_rate": sample_rate,
        "out_of_bag": out_of_bag
    }
    if (hasattr(args, "multi_label") and
            args.multi_label and multi_label_data is not None):
        dataset_args.update(
            user_metadata={'multi_label_data': multi_label_data})
    return dataset_args


def create_dataset(source_or_dataset, dataset_args, args, api=None,
                   path=None, session_file=None, log=None, dataset_type=None):
    """Creates remote dataset from source, dataset or datasets list

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Creating dataset.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    dataset = api.create_dataset(source_or_dataset, dataset_args, retries=None)
    suffix = "_" + dataset_type if dataset_type else ""
    log_created_resources("dataset%s" % suffix, path,
                          bigml.api.get_dataset_id(dataset), open_mode='a')
    dataset_id = check_resource_error(dataset, "Failed to create dataset: ")
    try:
        dataset = check_resource(dataset, api.get_dataset,
                                 query_string=ALL_FIELDS_QS)
    except ValueError, exception:
        sys.exit("Failed to get a finished dataset: %s" % str(exception))
    message = dated("Dataset created: %s\n" % get_url(dataset))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % dataset_id, log_file=log)
    if args.reports:
        report(args.reports, path, dataset)
    return dataset


def get_dataset(dataset, api=None, verbosity=True, session_file=None):
    """Retrieves the dataset in its actual state

    """
    if api is None:
        api = bigml.api.BigML()
    if (isinstance(dataset, basestring) or
            bigml.api.get_status(dataset)['code'] != bigml.api.FINISHED):
        message = dated("Retrieving dataset. %s\n" %
                        get_url(dataset))
        log_message(message, log_file=session_file,
                    console=verbosity)
        dataset = check_resource(dataset, api.get_dataset,
                                 query_string=ALL_FIELDS_QS)
        check_resource_error(dataset, "Failed to get dataset: ")
    return dataset


def publish_dataset(dataset, args, api=None, session_file=None):
    """Publishes dataset and sets its price (if any)

    """
    if api is None:
        api = bigml.api.BigML()
    public_dataset = {"private": False}
    if args.dataset_price:
        public_dataset.update(price=args.dataset_price)
    dataset = update_dataset(dataset, public_dataset, args.verbosity, api=api,
                             session_file=session_file)
    check_resource_error(dataset, "Failed to update dataset: ")
    dataset = check_resource(dataset, api.get_dataset)
    return dataset

def update_dataset(dataset, dataset_args, args,
                   api=None, path=None, session_file=None):
    """Updates dataset properties

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Updating dataset. %s\n" %
                    get_url(dataset))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    dataset = api.update_dataset(dataset, dataset_args)
    if is_shared(dataset):
        message = dated("Shared dataset link. %s\n" %
                        get_url(dataset, shared=True))
        log_message(message, log_file=session_file,
                    console=args.verbosity)
        if args.reports:
            report(args.reports, path, dataset)
    check_resource_error(dataset, "Failed to update dataset: ")
    dataset = check_resource(dataset, api.get_dataset)

    return dataset


def set_model_args(args, name=None, objective_id=None, fields=None,
                   model_fields=None, other_label=None):
    """Return model arguments dict

    """
    if name is None:
        name = args.name
    if objective_id is None and args.max_categories is None:
        objective_id = args.objective_id_
    if args.max_categories > 0:
        objective_id = args.objective_field
    if model_fields is None:
        model_fields = args.model_fields_

    model_args = {
        "name": name,
        "description": args.description_,
        "category": args.category,
        "tags": args.tag,
        "missing_splits": args.missing_splits
    }
    if objective_id is not None and fields is not None:
        model_args.update({"objective_field": objective_id})

    # If evaluate flag is on and no test_split flag is provided,
    # we choose a deterministic sampling with
    # args.sample_rate (80% by default) of the data to create the model
    # If cross_validation_rate = n/100, then we choose to run 2 * n evaluations
    # by holding out a n% of randomly sampled data.

    if ((args.evaluate and args.test_split == 0 and args.test_datasets is None)
            or args.cross_validation_rate > 0):
        model_args.update(seed=SEED)
        if args.cross_validation_rate > 0:
            args.sample_rate = 1 - args.cross_validation_rate
            args.replacement = False
        elif (args.sample_rate == 1 and args.test_datasets is None
              and not args.dataset_off):
            args.sample_rate = EVALUATE_SAMPLE_RATE
    if model_fields and fields is not None:
        input_fields = configure_input_fields(
            fields, model_fields, by_name=(args.max_categories > 0))
        model_args.update(input_fields=input_fields)

    if args.pruning and args.pruning != 'smart':
        model_args.update(stat_pruning=(args.pruning == 'statistical'))

    if args.node_threshold > 0:
        model_args.update(node_threshold=args.node_threshold)

    if args.balance:
        model_args.update(balance_objective=True)

    if args.weight_field:
        try:
            weight_field = fields.field_id(args.weight_field)
        except ValueError, exc:
            sys.exit(exc)
        model_args.update(weight_field=weight_field)

    if args.objective_weights:
        model_args.update(objective_weights=args.objective_weights_json)

    if args.max_categories > 0:
        model_args.update(
            user_metadata={'other_label': other_label,
                           'max_categories': args.max_categories})
    update_attributes(model_args, args.json_args.get('model'))

    model_args.update(sample_rate=args.sample_rate,
                      replacement=args.replacement,
                      randomize=args.randomize)
    return model_args


def set_label_model_args(args, fields, labels, multi_label_data):
    """Set of args needed to build a model per label

    """

    objective_field = args.objective_field
    if not args.model_fields_:
        model_fields = []
    else:
        model_fields = relative_input_fields(fields, args.model_fields_)
    if objective_field is None:
        objective_field = fields.objective_field
    try:
        objective_id = fields.field_id(objective_field)
        objective_field = fields.field_name(objective_id)
    except ValueError, exc:
        sys.exit(exc)
    all_labels = get_all_labels(multi_label_data)
    model_args_list = []

    for index in range(args.number_of_models - 1, -1, -1):
        label = labels[index]
        (new_name, label_field, single_label_fields) = label_model_args(
            args.name, label, all_labels, model_fields,
            objective_field)
        model_args = set_model_args(args, name=new_name,
                                    objective_id=label_field, fields=fields,
                                    model_fields=single_label_fields)
        if multi_label_data is not None:
            model_args.update(
                user_metadata={'multi_label_data': multi_label_data})
        model_args_list.append(model_args)
    return model_args_list


def create_models(datasets, model_ids, model_args,
                  args, api=None, path=None,
                  session_file=None, log=None):
    """Create remote models

    """
    if api is None:
        api = bigml.api.BigML()

    models = model_ids[:]
    existing_models = len(models)
    model_args_list = []
    if args.dataset_off and args.evaluate:
        args.test_dataset_ids = datasets[:]
    if not args.multi_label:
        datasets = datasets[existing_models:]
    # if resuming and all models were created, there will be no datasets left
    if datasets:
        dataset = datasets[0]
        if isinstance(model_args, list):
            model_args_list = model_args
        if args.number_of_models > 0:
            message = dated("Creating %s.\n" %
                            plural("model", args.number_of_models))
            log_message(message, log_file=session_file,
                        console=args.verbosity)

            single_model = args.number_of_models == 1 and existing_models == 0
            # if there's more than one model the first one must contain
            # the entire field structure to be used as reference.
            query_string = (FIELDS_QS if single_model and args.test_header
                            else ALL_FIELDS_QS)
            inprogress = []
            for i in range(0, args.number_of_models):
                wait_for_available_tasks(inprogress, args.max_parallel_models,
                                         api, "model")
                if model_args_list:
                    model_args = model_args_list[i]
                if args.cross_validation_rate > 0:
                    new_seed = get_basic_seed(i + existing_models)
                    model_args.update(seed=new_seed)
                # one model per dataset (--max-categories or single model)
                if (args.max_categories or
                        (args.test_datasets and args.evaluate)) > 0:
                    dataset = datasets[i]
                    model = api.create_model(dataset, model_args, retries=None)
                elif args.dataset_off and args.evaluate:
                    multi_dataset = args.test_dataset_ids[:]
                    del multi_dataset[i + existing_models]
                    model = api.create_model(multi_dataset, model_args,
                                             retries=None)
                else:
                    model = api.create_model(datasets, model_args,
                                             retries=None)
                model_id = check_resource_error(model,
                                                "Failed to create model: ")
                log_message("%s\n" % model_id, log_file=log)
                model_ids.append(model_id)
                inprogress.append(model_id)
                models.append(model)
                log_created_resources("models", path, model_id, open_mode='a')

            if args.number_of_models < 2 and args.verbosity:
                if bigml.api.get_status(model)['code'] != bigml.api.FINISHED:
                    try:
                        model = check_resource(model, api.get_model,
                                               query_string=query_string)
                    except ValueError, exception:
                        sys.exit("Failed to get a finished model: %s" %
                                 str(exception))
                    models[0] = model
                message = dated("Model created: %s.\n" %
                                get_url(model))
                log_message(message, log_file=session_file,
                            console=args.verbosity)
                if args.reports:
                    report(args.reports, path, model)

    return models, model_ids


def update_model(model, model_args, args,
                 api=None, path=None, session_file=None):
    """Updates model properties

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Updating model. %s\n" %
                    get_url(model))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    model = api.update_model(model, model_args)
    check_resource_error(model, "Failed to update model: %s"
                         % model['resource'])
    model = check_resource(model, api.get_model, query_string=ALL_FIELDS_QS)
    if is_shared(model):
        message = dated("Shared model link. %s\n" %
                        get_url(model, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, model)

    return model


def get_models(model_ids, args, api=None, session_file=None):
    """Retrieves remote models in its actual status

    """
    if api is None:
        api = bigml.api.BigML()
    model_id = ""
    models = model_ids
    single_model = len(model_ids) == 1
    if single_model:
        model_id = model_ids[0]
    message = dated("Retrieving %s. %s\n" %
                    (plural("model", len(model_ids)),
                     get_url(model_id)))
    log_message(message, log_file=session_file, console=args.verbosity)
    if len(model_ids) < args.max_batch_models:
        models = []
        for model in model_ids:
            try:
                # if there's more than one model the first one must contain
                # the entire field structure to be used as reference.
                query_string = (
                    ALL_FIELDS_QS if (
                        (not single_model and (
                            len(models) == 0 or args.multi_label)) or
                        not args.test_header)
                    else FIELDS_QS)
                model = check_resource(model, api.get_model,
                                       query_string=query_string)
            except ValueError, exception:
                sys.exit("Failed to get a finished model: %s" %
                         str(exception))
            models.append(model)
        model = models[0]
    else:
        try:
            query_string = (ALL_FIELDS_QS if not single_model or
                            not args.test_header
                            else FIELDS_QS)
            model = check_resource(model_ids[0], api.get_model,
                                   query_string=query_string)
        except ValueError, exception:
            sys.exit("Failed to get a finished model: %s" % str(exception))
        models[0] = model

    return models, model_ids


def set_label_ensemble_args(args, labels, multi_label_data,
                            number_of_ensembles, fields):
    """Set of args needed to build an ensemble per label

    """

    if not args.model_fields_:
        args.model_fields_ = relative_input_fields(fields, args.model_fields_)
    if args.objective_field is None:
        args.objective_field = fields.objective_field
    try:
        objective_id = fields.field_id(args.objective_field)
    except ValueError, exc:
        sys.exit(exc)
    objective_field = fields.fields[objective_id]['name']
    ensemble_args_list = []

    for index in range(number_of_ensembles - 1, -1, -1):
        label = labels[index]
        all_labels = get_all_labels(multi_label_data)
        (new_name, label_field, single_label_fields) = label_model_args(
            args.name, label, all_labels, args.model_fields_,
            objective_field)
        ensemble_args = set_ensemble_args(args, name=new_name,
                                          objective_id=label_field,
                                          model_fields=single_label_fields,
                                          fields=fields)
        if multi_label_data is not None:
            ensemble_args.update(
                user_metadata={'multi_label_data': multi_label_data})
        ensemble_args_list.append(ensemble_args)
    return ensemble_args_list


def set_ensemble_args(args, name=None,
                      objective_id=None, model_fields=None, fields=None):
    """Return ensemble arguments dict

    """
    if name is None:
        name = args.name
    if objective_id is None:
        objective_id = args.objective_id_
    if model_fields is None:
        model_fields = args.model_fields_

    ensemble_args = {
        "name": name,
        "description": args.description_,
        "number_of_models": args.number_of_models,
        "category": args.category,
        "tags": args.tag,
        "missing_splits": args.missing_splits,
        "seed": SEED if args.seed is None else args.seed
    }
    if objective_id is not None and fields is not None:
        ensemble_args.update({"objective_field": objective_id})

    # If evaluate flag is on and no test_split flag is provided,
    # we choose a deterministic sampling with
    # args.sample_rate (80% by default) of the data to create the model

    if (args.evaluate and args.test_split == 0 and
            args.test_datasets is None and not args.dataset_off):
        ensemble_args.update(seed=SEED)
        if args.sample_rate == 1:
            args.sample_rate = EVALUATE_SAMPLE_RATE

    if model_fields and fields is not None:
        input_fields = configure_input_fields(fields, model_fields)
        ensemble_args.update(input_fields=input_fields)

    if args.pruning and args.pruning != 'smart':
        ensemble_args.update(stat_pruning=(args.pruning == 'statistical'))
    if args.node_threshold > 0:
        ensemble_args.update(node_threshold=args.node_threshold)
    if args.balance:
        ensemble_args.update(balance_objective=True)
    if args.weight_field:
        try:
            weight_field = fields.field_id(args.weight_field)
        except ValueError, exc:
            sys.exit(exc)
        ensemble_args.update(weight_field=weight_field)
    if args.objective_weights:
        ensemble_args.update(objective_weights=args.objective_weights_json)

    update_attributes(ensemble_args, args.json_args.get('model'))
    ensemble_args.update(sample_rate=args.sample_rate,
                         replacement=args.replacement,
                         randomize=args.randomize,
                         tlp=args.tlp)

    update_attributes(ensemble_args, args.json_args.get('ensemble'))
    return ensemble_args


def create_ensembles(datasets, ensemble_ids, ensemble_args, args,
                     number_of_ensembles=1,
                     api=None, path=None, session_file=None, log=None):
    """Create ensembles from input data

    """

    if api is None:
        api = bigml.api.BigML()
    ensembles = ensemble_ids[:]
    existing_ensembles = len(ensembles)
    model_ids = []
    ensemble_args_list = []
    if isinstance(ensemble_args, list):
        ensemble_args_list = ensemble_args
    if args.dataset_off and args.evaluate:
        args.test_dataset_ids = datasets[:]
    if not args.multi_label:
        datasets = datasets[existing_ensembles:]
    if number_of_ensembles > 0:
        message = dated("Creating %s.\n" %
                        plural("ensemble", number_of_ensembles))
        log_message(message, log_file=session_file,
                    console=args.verbosity)
        inprogress = []
        for i in range(0, number_of_ensembles):
            wait_for_available_tasks(inprogress, args.max_parallel_ensembles,
                                     api, "ensemble",
                                     wait_step=args.number_of_models)

            if ensemble_args_list:
                ensemble_args = ensemble_args_list[i]

            if args.dataset_off and args.evaluate:
                multi_dataset = args.test_dataset_ids[:]
                del multi_dataset[i + existing_ensembles]
                ensemble = api.create_ensemble(multi_dataset,
                                               ensemble_args,
                                               retries=None)
            else:
                ensemble = api.create_ensemble(datasets, ensemble_args,
                                               retries=None)
            ensemble_id = check_resource_error(ensemble,
                                               "Failed to create ensemble: ")
            log_message("%s\n" % ensemble_id, log_file=log)
            ensemble_ids.append(ensemble_id)
            inprogress.append(ensemble_id)
            ensembles.append(ensemble)
            log_created_resources("ensembles", path, ensemble_id,
                                  open_mode='a')
        models, model_ids = retrieve_ensembles_models(ensembles, api, path)
        if number_of_ensembles < 2 and args.verbosity:
            message = dated("Ensemble created: %s.\n" %
                            get_url(ensemble))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
            if args.reports:
                report(args.reports, path, ensemble)

    return ensembles, ensemble_ids, models, model_ids


def retrieve_ensembles_models(ensembles, api, path=None):
    """Retrieves the models associated to a list of ensembles

    """
    models = []
    model_ids = []
    for index in range(0, len(ensembles)):
        ensemble = ensembles[index]
        if (isinstance(ensemble, basestring) or
                bigml.api.get_status(ensemble)['code'] != bigml.api.FINISHED):
            try:
                ensemble = check_resource(ensemble, api.get_ensemble)
                ensembles[index] = ensemble
            except ValueError, exception:
                sys.exit("Failed to get a finished ensemble: %s" %
                         str(exception))
        model_ids.extend(ensemble['object']['models'])
    if path is not None:
        for model_id in model_ids:
            log_created_resources("models", path, model_id, open_mode='a')
    models = model_ids[:]
    models[0] = check_resource(models[0], api.get_model,
                               query_string=ALL_FIELDS_QS)
    return models, model_ids


def get_ensemble(ensemble, api=None, verbosity=True, session_file=None):
    """Retrieves remote ensemble in its actual status

    """
    if api is None:
        api = bigml.api.BigML()
    if (isinstance(ensemble, basestring) or
            bigml.api.get_status(ensemble)['code'] != bigml.api.FINISHED):
        message = dated("Retrieving ensemble. %s\n" %
                        get_url(ensemble))
        log_message(message, log_file=session_file,
                    console=verbosity)
        ensemble = check_resource(ensemble, api.get_ensemble)
        check_resource_error(ensemble, "Failed to get ensemble: ")
    return ensemble


def set_publish_model_args(args):
    """Set args to publish model

    """
    public_model = {}
    if args.black_box:
        public_model = {"private": False}
    if args.white_box:
        public_model = {"private": False, "white_box": True}
        if args.model_price:
            public_model.update(price=args.model_price)
        if args.cpp:
            public_model.update(credits_per_prediction=args.cpp)
    return public_model


def map_fields(fields_map, model_fields, dataset_fields):
    """Build a dict to map model to dataset fields

    """
    update_map = {}
    for (model_column, dataset_column) in fields_map.iteritems():
        try:
            update_map.update({
                model_fields.field_id(model_column):
                dataset_fields.field_id(dataset_column)})
        except ValueError, exc:
            sys.exit(exc)

    return update_map


def set_evaluation_args(args, fields=None,
                        dataset_fields=None, name=None):
    """Return evaluation args dict

    """
    if name is None:
        name = args.name
    evaluation_args = {
        "name": name,
        "description": args.description_,
        "tags": args.tag
    }

    if args.number_of_models > 1 or args.ensemble:
        evaluation_args.update(combiner=args.method)
    if args.fields_map_ and fields is not None:
        if dataset_fields is None:
            dataset_fields = fields
        evaluation_args.update({"fields_map": map_fields(args.fields_map_,
                                                         fields,
                                                         dataset_fields)})
    if args.missing_strategy:
        evaluation_args.update(missing_strategy=args.missing_strategy)

    update_attributes(evaluation_args, args.json_args.get('evaluation'))
    # Two cases to use out_of_bag and sample_rate: standard evaluations where
    # only the training set is provided, and cross_validation
    # [--dataset|--test] [--model|--models|--model-tag|--ensemble] --evaluate
    if ((args.dataset or args.test_set)
            and (args.model or args.models or args.model_tag or
                 (args.ensemble and args.number_of_models == 1))):
        return evaluation_args
    # [--train|--dataset] --test-split --evaluate
    if args.test_split > 0 and (args.training_set or args.dataset):
        return evaluation_args
    # --datasets --test-datasets
    if args.datasets and (args.test_datasets or args.dataset_off):
        return evaluation_args
    if args.sample_rate == 1:
        args.sample_rate = EVALUATE_SAMPLE_RATE
    evaluation_args.update(out_of_bag=True, seed=SEED,
                           sample_rate=args.sample_rate)
    return evaluation_args


def set_label_evaluation_args(args, labels, all_labels,
                              number_of_evaluations, fields, dataset_fields,
                              objective_field):
    """Set of args needed to build an evaluation per label

    """
    if objective_field is None:
        try:
            objective_id = fields.field_id(fields.objective_field)
        except ValueError, exc:
            sys.exit(exc)
        objective_field = fields.fields[objective_id]['name']
    evaluation_args_list = []

    for index in range(number_of_evaluations - 1, -1, -1):
        label = labels[index]
        new_name = label_model_args(
            args.name, label, all_labels, [], objective_field)[0]
        evaluation_args = set_evaluation_args(args,
                                              fields=fields,
                                              dataset_fields=dataset_fields,
                                              name=new_name)
        evaluation_args_list.append(evaluation_args)
    return evaluation_args_list


def create_evaluations(model_or_ensemble_ids, datasets, evaluation_args,
                       args, api=None,
                       path=None, session_file=None, log=None,
                       existing_evaluations=0):
    """Create evaluations for a list of models

       ``model_or_ensemble_ids``: list of model or ensemble ids to create
                                  an evaluation of
       ``datasets``: dataset objects or ids to evaluate with
       ``evaluation_args``: arguments for the ``create_evaluation`` call
       ``args``: input values for bigmler flags
       ``api``: api to remote objects in BigML
       ``path``: directory to store the BigMLer generated files in
       ``session_file``: file to store the messages of that session
       ``log``: user provided log file
       ``existing_evaluations``: evaluations found when attempting resume
    """

    evaluations = []
    dataset = datasets[0]
    evaluation_args_list = []
    if isinstance(evaluation_args, list):
        evaluation_args_list = evaluation_args
    if api is None:
        api = bigml.api.BigML()
    remaining_ids = model_or_ensemble_ids[existing_evaluations:]
    if args.test_dataset_ids or args.dataset_off:
        remaining_datasets = datasets[existing_evaluations:]
    number_of_evaluations = len(remaining_ids)
    message = dated("Creating evaluations.\n")
    log_message(message, log_file=session_file,
                console=args.verbosity)

    inprogress = []
    for i in range(0, number_of_evaluations):
        model = remaining_ids[i]
        if args.test_dataset_ids or args.dataset_off:
            dataset = remaining_datasets[i]
        wait_for_available_tasks(inprogress, args.max_parallel_evaluations,
                                 api, "evaluation")

        if evaluation_args_list != []:
            evaluation_args = evaluation_args_list[i]
        if args.cross_validation_rate > 0:
            new_seed = get_basic_seed(i + existing_evaluations)
            evaluation_args.update(seed=new_seed)
        evaluation = api.create_evaluation(model, dataset, evaluation_args,
                                           retries=None)
        evaluation_id = check_resource_error(evaluation,
                                             "Failed to create evaluation: ")
        inprogress.append(evaluation_id)
        log_created_resources("evaluations", path, evaluation_id,
                              open_mode='a')
        evaluations.append(evaluation)
        log_message("%s\n" % evaluation['resource'], log_file=log)

    if (args.number_of_evaluations < 2 and len(evaluations) == 1
            and args.verbosity):
        evaluation = evaluations[0]
        if bigml.api.get_status(evaluation)['code'] != bigml.api.FINISHED:
            try:
                evaluation = check_resource(evaluation, api.get_evaluation)
            except ValueError, exception:
                sys.exit("Failed to get a finished evaluation: %s" %
                         str(exception))
            evaluations[0] = evaluation
        message = dated("Evaluation created: %s.\n" %
                        get_url(evaluation))
        log_message(message, log_file=session_file,
                    console=args.verbosity)
        if args.reports:
            report(args.reports, path, evaluation)

    return evaluations


def get_evaluation(evaluation, api=None, verbosity=True, session_file=None):
    """Retrieves evaluation in its actual state

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Retrieving evaluation. %s\n" %
                    get_url(evaluation))
    log_message(message, log_file=session_file, console=verbosity)
    try:
        evaluation = check_resource(evaluation, api.get_evaluation)
    except ValueError, exception:
        sys.exit("Failed to get a finished evaluation: %s" % str(exception))
    return evaluation


def update_evaluation(evaluation, evaluation_args, args,
                      api=None, path=None, session_file=None):
    """Updates evaluation properties

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Updating evaluation. %s\n" %
                    get_url(evaluation))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    evaluation = api.update_evaluation(evaluation, evaluation_args)
    check_resource_error(evaluation, "Failed to update evaluation: %s"
                         % evaluation['resource'])
    evaluation = check_resource(evaluation, api.get_evaluation)
    if is_shared(evaluation):
        message = dated("Shared evaluation link. %s\n" %
                        get_url(evaluation, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, evaluation)

    return evaluation


def save_evaluation(evaluation, output, api=None):
    """Creates the evaluation .txt and .json files

    """
    if api is None:
        api = bigml.api.BigML()
    evaluation_json = open(output + '.json', 'w', 0)
    evaluation = evaluation.get('object', evaluation).get('result', evaluation)
    evaluation_json.write(json.dumps(evaluation))
    evaluation_json.flush()
    evaluation_json.close()
    evaluation_txt = open(output + '.txt', 'w', 0)
    api.pprint(evaluation, evaluation_txt)
    evaluation_txt.flush()
    evaluation_txt.close()


def set_batch_prediction_args(args, fields=None,
                              dataset_fields=None):
    """Return batch prediction args dict

    """
    batch_prediction_args = {
        "name": args.name,
        "description": args.description_,
        "tags": args.tag,
        "header": args.prediction_header,
        "combiner": args.method,
        "output_dataset": args.to_dataset
    }

    if args.fields_map_ and fields is not None:
        if dataset_fields is None:
            dataset_fields = fields
        batch_prediction_args.update({
            "fields_map": map_fields(args.fields_map_,
                                     fields, dataset_fields)})

    if args.prediction_info in [NORMAL_FORMAT, FULL_FORMAT]:
        batch_prediction_args.update(confidence=True)

    if args.prediction_info == FULL_FORMAT:
        batch_prediction_args.update(all_fields=True)
    if args.prediction_fields:
        batch_prediction_args.update(all_fields=False)
        prediction_fields = []
        for field in args.prediction_fields.split(args.args_separator):
            field = field.strip()
            if not field in dataset_fields.fields:
                try:
                    field = dataset_fields.field_id(field)
                except ValueError, exc:
                    sys.exit(exc)
            prediction_fields.append(field)
        batch_prediction_args.update(output_fields=prediction_fields)
    if args.missing_strategy:
        batch_prediction_args.update(missing_strategy=args.missing_strategy)

    update_attributes(batch_prediction_args,
                      args.json_args.get('batch_prediction'))

    return batch_prediction_args


def create_batch_prediction(model_or_ensemble, test_dataset,
                            batch_prediction_args, args,
                            api=None, session_file=None,
                            path=None, log=None):
    """Creates remote batch_prediction

    """
    if api is None:
        api = bigml.api.BigML()

    message = dated("Creating batch prediction.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    batch_prediction = api.create_batch_prediction(model_or_ensemble,
                                                   test_dataset,
                                                   batch_prediction_args,
                                                   retries=None)
    log_created_resources("batch_prediction", path,
                          bigml.api.get_batch_prediction_id(batch_prediction),
                          open_mode='a')
    batch_prediction_id = check_resource_error(
        batch_prediction, "Failed to create batch prediction: ")
    try:
        batch_prediction = check_resource(batch_prediction,
                                          api.get_batch_prediction)
    except ValueError, exception:
        sys.exit("Failed to get a finished batch prediction: %s"
                 % str(exception))
    message = dated("Batch prediction created: %s\n"
                    % get_url(batch_prediction))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % batch_prediction_id, log_file=log)
    if args.reports:
        report(args.reports, path, batch_prediction)
    return batch_prediction


def set_cluster_args(args, name=None, fields=None,
                     cluster_fields=None):
    """Return cluster arguments dict

    """
    if name is None:
        name = args.name
    if cluster_fields is None:
        cluster_fields = args.cluster_fields_

    cluster_args = {
        "name": name,
        "description": args.description_,
        "category": args.category,
        "tags": args.tag,
        "seed": SEED if args.seed is None else args.seed,
        "cluster_seed": (SEED if args.cluster_seed is None
                         else args.cluster_seed)
    }

    if args.cluster_k:
        cluster_args.update({"k": args.cluster_k})
    if cluster_fields and fields is not None:
        input_fields = configure_input_fields(fields, cluster_fields)
        cluster_args.update(input_fields=input_fields)

    update_attributes(cluster_args, args.json_args.get('cluster'))

    return cluster_args


def create_clusters(datasets, cluster_ids, cluster_args,
                    args, api=None, path=None,
                    session_file=None, log=None):
    """Create remote clusters

    """
    if api is None:
        api = bigml.api.BigML()

    clusters = cluster_ids[:]
    existing_clusters = len(clusters)
    cluster_args_list = []
    datasets = datasets[existing_clusters:]
    # if resuming and all clusters were created, there will be no datasets left
    if datasets:
        if isinstance(cluster_args, list):
            cluster_args_list = cluster_args

        # Only one cluster per command, at present
        number_of_clusters = 1
        message = dated("Creating %s.\n" %
                        plural("cluster", number_of_clusters))
        log_message(message, log_file=session_file,
                    console=args.verbosity)

        query_string = FIELDS_QS
        inprogress = []
        for i in range(0, number_of_clusters):
            wait_for_available_tasks(inprogress, args.max_parallel_clusters,
                                     api, "cluster")
            if cluster_args_list:
                cluster_args = cluster_args_list[i]

            cluster = api.create_cluster(datasets, cluster_args, retries=None)
            cluster_id = check_resource_error(cluster,
                                              "Failed to create cluster: ")
            log_message("%s\n" % cluster_id, log_file=log)
            cluster_ids.append(cluster_id)
            inprogress.append(cluster_id)
            clusters.append(cluster)
            log_created_resources("clusters", path, cluster_id, open_mode='a')

        if args.verbosity:
            if bigml.api.get_status(cluster)['code'] != bigml.api.FINISHED:
                try:
                    cluster = check_resource(cluster, api.get_cluster,
                                             query_string=query_string)
                except ValueError, exception:
                    sys.exit("Failed to get a finished cluster: %s" %
                             str(exception))
                clusters[0] = cluster
            message = dated("Cluster created: %s.\n" %
                            get_url(cluster))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
            if args.reports:
                report(args.reports, path, cluster)

    return clusters, cluster_ids


def get_clusters(cluster_ids, args, api=None, session_file=None):
    """Retrieves remote clusters in its actual status

    """
    if api is None:
        api = bigml.api.BigML()
    cluster_id = ""
    clusters = cluster_ids
    cluster_id = cluster_ids[0]
    message = dated("Retrieving %s. %s\n" %
                    (plural("cluster", len(cluster_ids)),
                     get_url(cluster_id)))
    log_message(message, log_file=session_file, console=args.verbosity)
    # only one cluster to predict at present
    try:
        query_string = FIELDS_QS
        cluster = check_resource(cluster_ids[0], api.get_cluster,
                                 query_string=query_string)
    except ValueError, exception:
        sys.exit("Failed to get a finished cluster: %s" % str(exception))
    clusters[0] = cluster

    return clusters, cluster_ids


def set_batch_centroid_args(args, fields=None,
                            dataset_fields=None):
    """Return batch centroid args dict

    """
    batch_centroid_args = {
        "name": args.name,
        "description": args.description_,
        "tags": args.tag,
        "header": args.prediction_header,
        "output_dataset": args.to_dataset
    }

    if args.fields_map_ and fields is not None:
        if dataset_fields is None:
            dataset_fields = fields
        batch_centroid_args.update({
            "fields_map": map_fields(args.fields_map_,
                                     fields, dataset_fields)})

    if args.prediction_info == FULL_FORMAT:
        batch_centroid_args.update(all_fields=True)

    update_attributes(batch_centroid_args,
                      args.json_args.get('batch_centroid'))

    return batch_centroid_args


def create_batch_centroid(cluster, test_dataset,
                          batch_centroid_args, args,
                          api=None, session_file=None,
                          path=None, log=None):
    """Creates remote batch_centroid

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Creating batch centroid.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    batch_centroid = api.create_batch_centroid(cluster,
                                               test_dataset,
                                               batch_centroid_args,
                                               retries=None)
    log_created_resources("batch_centroid", path,
                          bigml.api.get_batch_centroid_id(batch_centroid),
                          open_mode='a')
    batch_centroid_id = check_resource_error(
        batch_centroid, "Failed to create batch prediction: ")
    try:
        batch_centroid = check_resource(batch_centroid,
                                        api.get_batch_centroid)
    except ValueError, exception:
        sys.exit("Failed to get a finished batch centroid: %s"
                 % str(exception))
    message = dated("Batch centroid created: %s\n"
                    % get_url(batch_centroid))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % batch_centroid_id, log_file=log)
    if args.reports:
        report(args.reports, path, batch_centroid)
    return batch_centroid


def set_publish_cluster_args(args):
    """Set args to publish cluster

    """
    public_cluster = {}
    if args.public_cluster:
        public_cluster = {"private": False}
        if args.model_price:
            public_cluster.update(price=args.model_price)
        if args.cpp:
            public_cluster.update(credits_per_prediction=args.cpp)
    return public_cluster


def update_cluster(cluster, cluster_args, args,
                   api=None, path=None, session_file=None):
    """Updates cluster properties

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Updating cluster. %s\n" %
                    get_url(cluster))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    cluster = api.update_cluster(cluster, cluster_args)
    check_resource_error(cluster, "Failed to update cluster: %s"
                         % cluster['resource'])
    cluster = check_resource(cluster, api.get_cluster, query_string=FIELDS_QS)
    if is_shared(cluster):
        message = dated("Shared cluster link. %s\n" %
                        get_url(cluster, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, cluster)

    return cluster


def set_batch_anomaly_score_args(args, fields=None,
                                 dataset_fields=None):
    """Return batch anomaly score args dict

    """
    batch_anomaly_score_args = {
        "name": args.name,
        "description": args.description_,
        "tags": args.tag,
        "header": args.prediction_header,
        "output_dataset": args.to_dataset
    }

    if args.fields_map_ and fields is not None:
        if dataset_fields is None:
            dataset_fields = fields
        batch_anomaly_score_args.update({
            "fields_map": map_fields(args.fields_map_,
                                     fields, dataset_fields)})

    if args.prediction_info == FULL_FORMAT:
        batch_anomaly_score_args.update(all_fields=True)
    if args.prediction_fields:
        batch_anomaly_score_args.update(all_fields=False)
        prediction_fields = []
        for field in args.prediction_fields.split(args.args_separator):
            field = field.strip()
            if not field in dataset_fields.fields:
                try:
                    field = dataset_fields.field_id(field)
                except ValueError, exc:
                    sys.exit(exc)
            prediction_fields.append(field)
        batch_anomaly_score_args.update(output_fields=prediction_fields)

    update_attributes(batch_anomaly_score_args,
                      args.json_args.get('batch_anomaly_score'))

    return batch_anomaly_score_args


def set_anomaly_args(args, name=None, fields=None,
                     anomaly_fields=None):
    """Return anomaly arguments dict

    """
    if name is None:
        name = args.name
    if anomaly_fields is None:
        anomaly_fields = args.anomaly_fields_

    anomaly_args = {
        "name": name,
        "description": args.description_,
        "category": args.category,
        "tags": args.tag,
        "seed": SEED if args.seed is None else args.seed,
        "anomaly_seed": (SEED if args.anomaly_seed is None
                         else args.anomaly_seed)
    }

    if anomaly_fields and fields is not None:
        input_fields = configure_input_fields(fields, anomaly_fields)
        anomaly_args.update(input_fields=input_fields)

    update_attributes(anomaly_args, args.json_args.get('anomaly'))

    return anomaly_args


def set_publish_anomaly_args(args):
    """Set args to publish anomaly

    """
    public_anomaly = {}
    if args.public_anomaly:
        public_anomaly = {"private": False}
        if args.model_price:
            public_anomaly.update(price=args.model_price)
        if args.cpp:
            public_anomaly.update(credits_per_prediction=args.cpp)
    return public_anomaly


def create_anomalies(datasets, anomaly_ids, anomaly_args,
                     args, api=None, path=None,
                     session_file=None, log=None):
    """Create remote anomalies

    """
    if api is None:
        api = bigml.api.BigML()

    anomalies = anomaly_ids[:]
    existing_anomalies = len(anomalies)
    anomaly_args_list = []
    datasets = datasets[existing_anomalies:]
    # if resuming and all anomalies were created,
    # there will be no datasets left
    if datasets:
        if isinstance(anomaly_args, list):
            anomaly_args_list = anomaly_args

        # Only one anomaly per command, at present
        number_of_anomalies = 1
        message = dated("Creating %s.\n" %
                        plural("anomaly detector", number_of_anomalies))
        log_message(message, log_file=session_file,
                    console=args.verbosity)

        query_string = FIELDS_QS
        inprogress = []
        for i in range(0, number_of_anomalies):
            wait_for_available_tasks(inprogress, args.max_parallel_anomalies,
                                     api, "anomaly")
            if anomaly_args_list:
                anomaly_args = anomaly_args_list[i]

            anomaly = api.create_anomaly(datasets, anomaly_args, retries=None)
            anomaly_id = check_resource_error(anomaly,
                                              "Failed to create anomaly: ")
            log_message("%s\n" % anomaly_id, log_file=log)
            anomaly_ids.append(anomaly_id)
            inprogress.append(anomaly_id)
            anomalies.append(anomaly)
            log_created_resources("anomalies", path, anomaly_id, open_mode='a')

        if args.verbosity:
            if bigml.api.get_status(anomaly)['code'] != bigml.api.FINISHED:
                try:
                    anomaly = api.check_resource(anomaly,
                                                 query_string=query_string)
                except ValueError, exception:
                    sys.exit("Failed to get a finished anomaly: %s" %
                             str(exception))
                anomalies[0] = anomaly
            message = dated("Anomaly created: %s.\n" %
                            get_url(anomaly))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
            if args.reports:
                report(args.reports, path, anomaly)

    return anomalies, anomaly_ids


def get_anomalies(anomaly_ids, args, api=None, session_file=None):
    """Retrieves remote anomalies in its actual status

    """
    if api is None:
        api = bigml.api.BigML()
    anomaly_id = ""
    anomalies = anomaly_ids
    anomaly_id = anomaly_ids[0]
    message = dated("Retrieving %s. %s\n" %
                    (plural("anomaly detector", len(anomaly_ids)),
                     get_url(anomaly_id)))
    log_message(message, log_file=session_file, console=args.verbosity)
    # only one anomaly to predict at present
    try:
        query_string = FIELDS_QS
        anomaly = api.check_resource(anomaly_ids[0],
                                     query_string=query_string)
    except ValueError, exception:
        sys.exit("Failed to get a finished anomaly: %s" % str(exception))
    anomalies[0] = anomaly

    return anomalies, anomaly_ids


def create_batch_anomaly_score(anomaly, test_dataset,
                               batch_anomaly_score_args, args,
                               api=None, session_file=None,
                               path=None, log=None):
    """Creates remote batch anomaly score

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Creating batch anomaly score.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    batch_anomaly_score = api.create_batch_anomaly_score(
        anomaly, test_dataset, batch_anomaly_score_args, retries=None)
    log_created_resources(
        "batch_anomaly_score", path,
        bigml.api.get_batch_anomaly_score_id(batch_anomaly_score),
        open_mode='a')
    batch_anomaly_score_id = check_resource_error(
        batch_anomaly_score, "Failed to create batch prediction: ")
    try:
        batch_anomaly_score = api.check_resource(batch_anomaly_score)
    except ValueError, exception:
        sys.exit("Failed to get a finished batch anomaly score: %s"
                 % str(exception))
    message = dated("Batch anomaly score created: %s\n"
                    % get_url(batch_anomaly_score))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % batch_anomaly_score_id, log_file=log)
    if args.reports:
        report(args.reports, path, batch_anomaly_score)
    return batch_anomaly_score

def update_anomaly(anomaly, anomaly_args, args,
                   api=None, path=None, session_file=None):
    """Updates anomaly properties

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Updating anomaly detector. %s\n" %
                    get_url(anomaly))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    anomaly = api.update_anomaly(anomaly, anomaly_args)
    check_resource_error(anomaly, "Failed to update anomaly: %s"
                         % anomaly['resource'])
    anomaly = api.check_resource(anomaly, query_string=FIELDS_QS)
    if is_shared(anomaly):
        message = dated("Shared anomaly link. %s\n" %
                        get_url(anomaly, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, anomaly)

    return anomaly


def set_project_args(args, name=None):
    """Return project arguments dict

    """
    if name is None:
        name = args.name
    project_args = {
        "name": name,
        "description": args.description_,
        "category": args.category,
        "tags": args.tag
    }

    return project_args


def create_project(project_args, args, api=None,
                   session_file=None, path=None, log=None):
    """Creates remote project

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Creating project.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    project = api.create_project(project_args)
    log_created_resources("project", path,
                          bigml.api.get_project_id(project), open_mode='a')
    project_id = check_resource_error(project, "Failed to create project: ")
    try:
        project = check_resource(project, api=api)
    except ValueError, exception:
        sys.exit("Failed to get a finished project: %s" % str(exception))
    message = dated("Project \"%s\" has been created.\n" %
                    project['object']['name'])
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % project_id, log_file=log)
    if args.reports:
        report(args.reports, path, project)
    return project


def get_project_by_name(project, api=None, verbosity=True, session_file=None):
    """Retrieves the project info by project name

    """
    if api is None:
        api = bigml.api.BigML()
    project_id = None

    if (isinstance(project, basestring) or
            bigml.api.get_status(project)['code'] != bigml.api.FINISHED):
        message = dated("Retrieving project info.\n")
        log_message(message, log_file=session_file,
                    console=verbosity)
        projects = api.list_projects(query_string="name=%s" % project)
        projects = projects.get('objects', [])
        if projects:
            project_id = projects[0]['resource']

    return project_id


def set_sample_args(args, name=None):
    """Return sample arguments dict

    """
    if name is None:
        name = args.name

    sample_args = {
        "name": name,
        "description": args.description_,
        "category": args.category,
        "tags": args.tag
    }

    update_attributes(sample_args, args.json_args.get('sample'))
    return sample_args


def create_samples(datasets, sample_ids, sample_args,
                   args, api=None, path=None,
                   session_file=None, log=None):
    """Create remote samples

    """
    if api is None:
        api = bigml.api.BigML()

    samples = sample_ids[:]
    existing_samples = len(samples)
    sample_args_list = []
    datasets = datasets[existing_samples:]
    # if resuming and all samples were created, there will be no datasets left
    if datasets:
        if isinstance(sample_args, list):
            sample_args_list = sample_args

        # Only one sample per command, at present
        number_of_samples = 1
        max_parallel_samples = 1
        message = dated("Creating %s.\n" %
                        plural("sample", number_of_samples))
        log_message(message, log_file=session_file,
                    console=args.verbosity)

        inprogress = []
        for i in range(0, number_of_samples):
            wait_for_available_tasks(inprogress, max_parallel_samples,
                                     api, "sample")
            if sample_args_list:
                sample_args = sample_args_list[i]

            sample = api.create_sample(datasets[i], sample_args, retries=None)
            sample_id = check_resource_error(sample,
                                             "Failed to create sample: ")
            log_message("%s\n" % sample_id, log_file=log)
            sample_ids.append(sample_id)
            inprogress.append(sample_id)
            samples.append(sample)
            log_created_resources("samples", path, sample_id, open_mode='a')

        if args.verbosity:
            if bigml.api.get_status(sample)['code'] != bigml.api.FINISHED:
                try:
                    sample = check_resource(sample, api.get_sample)
                except ValueError, exception:
                    sys.exit("Failed to get a finished sample: %s" %
                             str(exception))
                samples[0] = sample
            message = dated("Sample created: %s.\n" %
                            get_url(sample))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
            if args.reports:
                report(args.reports, path, sample)

    return samples, sample_ids


def update_sample(sample, sample_args, args,
                  api=None, path=None, session_file=None):
    """Updates sample properties

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Updating sample. %s\n" %
                    get_url(sample))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    sample = api.update_sample(sample, sample_args)
    check_resource_error(sample, "Failed to update sample: %s"
                         % sample['resource'])
    sample = check_resource(sample, api.get_sample)
    if is_shared(sample):
        message = dated("Shared sample link. %s\n" %
                        get_url(sample, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, sample)

    return sample


def get_samples(sample_ids, args,
                api=None, session_file=None, query_string=''):
    """Retrieves remote samples in its actual status

    """
    if api is None:
        api = bigml.api.BigML()
    sample_id = ""
    samples = sample_ids
    sample_id = sample_ids[0]
    message = dated("Retrieving %s. %s\n" %
                    (plural("sample", len(sample_ids)),
                     get_url(sample_id)))
    log_message(message, log_file=session_file, console=args.verbosity)
    # only one sample to predict at present
    try:
        sample = api.get_sample(sample_ids[0],
                                query_string=query_string)
        check_resource_error(sample, "Failed to create sample: %s"
                             % sample['resource'])
        sample = check_resource(sample, api=api, query_string=query_string)
    except ValueError, exception:
        sys.exit("Failed to get a finished sample: %s" % str(exception))
    samples[0] = sample

    return samples, sample_ids


def set_publish_sample_args(args):
    """Set args to publish sample

    """
    public_sample = {}
    if args.public_sample:
        public_sample = {"private": False}
    return public_sample
