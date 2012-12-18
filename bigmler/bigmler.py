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
import datetime
import csv
import re

import bigml.api
from bigml.model import Model
from bigml.multimodel import MultiModel
from bigml.multimodel import COMBINATION_METHODS
from bigml.fields import Fields

from bigml.util import reset_progress_bar, localize, \
    get_csv_delimiter, clear_progress_bar
from bigmler.options import create_parser
from bigmler.utils import read_description, read_field_attributes, \
    read_types, read_models, read_dataset, read_json_filter, \
    read_lisp_filter, read_votes, list_source_ids, list_dataset_ids, \
    list_model_ids, list_prediction_ids, combine_votes, delete, check_dir, \
    write_prediction

MAX_MODELS = 10


def predict(test_set, test_set_header, models, fields, output,
            objective_field, remote=False, api=None, log=None,
            max_models=MAX_MODELS, method='plurality'):
    """Computes a prediction for each entry in the `test_set`


    """
    out = sys.stdout

    def draw_progress_bar(current, total):
        """Draws a text based progress report.

        """
        pct = 100 - ((total - current) * 100) / (total)
        clear_progress_bar(out=out)
        reset_progress_bar(out=out)
        out.write("Predicted on %s out of %s models [%s%%]" % (
            localize(current), localize(total), pct))
        reset_progress_bar(out=out)

    try:
        test_reader = csv.reader(open(test_set, "U"),
                                 delimiter=get_csv_delimiter(),
                                 lineterminator="\n")
    except IOError:
        sys.exit("Error: cannot read test %s" % test_set)

    headers = None
    exclude = []
    if test_set_header:
        headers = test_reader.next()
        # validate headers against model fields excluding objective_field,
        # that may be present or not
        fields_names = [fields.fields[fields.field_id(i)]
                        ['name'] for i in
                        sorted(fields.fields_by_column_number.keys())
                        if i != fields.field_column_number(objective_field)]
        headers = [unicode(header, "utf-8") for header in headers]
        exclude = [i for i in range(len(headers)) if not headers[i]
                   in fields_names]
        exclude.reverse()
        if len(exclude):
            if (len(headers) - len(exclude)):
                print (u"WARNING: predictions will be processed but some data"
                       u" might not be used. The used fields will be:\n\n%s"
                       u"\n\nwhile the headers found in the test file are:"
                       u"\n\n%s" %
                       (",".join(fields_names),
                        ",".join(headers))).encode("utf-8")
                for index in exclude:
                    del headers[index]
            else:
                raise Exception((u"No test field matches the model fields.\n"
                                 u"The expected fields are:\n\n%s\n\nwhile "
                                 u"the headers found in the test file are:\n\n"
                                 u"%s\n\nUse --no-test-header flag if first li"
                                 u"ne should not be interpreted as headers." %
                                 (",".join(fields_names),
                                  ",".join(headers))).encode("utf-8"))

    output_path = check_dir(output)
    output = open(output, 'w', 0)
    if remote:
        for row in test_reader:
            predictions = {}
            for index in exclude:
                del row[index]
            input_data = fields.pair(row, headers, objective_field)

            for model in models:
                prediction = api.create_prediction(model, input_data,
                                                   by_name=test_set_header,
                                                   wait_time=0)
                if log:
                    log.write("%s\n" % prediction['resource'])
                    log.flush()
                prediction_key = (prediction['object']['prediction']
                                  [prediction['object']
                                  ['objective_fields'][0]])
                if not prediction_key in predictions:
                    predictions[prediction_key] = []
                predictions[prediction_key].append(prediction['object']
                                                   ['prediction_path']
                                                   ['confidence'])
            write_prediction(predictions, method, output)
    else:
        models_total = len(models)
        if models_total < max_models:
            local_model = MultiModel(models)
            for row in test_reader:
                for index in exclude:
                    del row[index]
                input_data = fields.pair(row, headers, objective_field)
                prediction = local_model.predict(input_data,
                                                 by_name=test_set_header)
                if isinstance(prediction, basestring):
                    prediction = prediction.encode("utf-8")
                output.write("%s\n" % prediction)
                output.flush()
        else:
            models_splits = [models[index:(index + max_models)] for index
                             in range(0, models_total, max_models)]
            input_data_list = []
            for row in test_reader:
                for index in exclude:
                    del row[index]
                input_data_list.append(fields.pair(row, headers,
                                                   objective_field))
            total_votes = []
            models_count = 0
            for models_split in models_splits:
                complete_models = []
                for index in range(len(models_split)):
                    complete_models.append(api.check_resource(
                        models_split[index], api.get_model))

                local_model = MultiModel(complete_models)
                local_model.batch_predict(input_data_list,
                                          output_path, reuse=True)
                votes = local_model.batch_votes(output_path)
                models_count += max_models
                if models_count > models_total:
                    models_count = models_total
                draw_progress_bar(models_count, models_total)
                if total_votes:
                    for index in range(len(votes)):
                        for prediction in votes[index].keys():
                            if not prediction in total_votes[index]:
                                total_votes[index][prediction] = []
                            total_votes[index][prediction].extend(votes[index]
                                                                  [prediction])
                else:
                    total_votes = votes


            clear_progress_bar(out=out)
            reset_progress_bar(out=out)
            out.write("Combining predictions.")
            reset_progress_bar(out=out)
            for predictions in total_votes:
                write_prediction(predictions, method, output)

            clear_progress_bar(out=out)
            reset_progress_bar(out=out)
            out.write("Done.")
            reset_progress_bar(out=out)
            clear_progress_bar(out=out)
            reset_progress_bar(out=out)
    output.close()


def compute_output(api, args, training_set, test_set=None, output=None,
                   objective_field=None,
                   description=None,
                   field_attributes=None,
                   types=None,
                   dataset_fields=None,
                   model_fields=None,
                   name=None, training_set_header=True,
                   test_set_header=True, model_ids=None,
                   votes_files=None):
    """ Creates one or models using the `training_set` or uses the ids
    of previous created BigML models to make predictions for the `test_set`.

    """
    source = None
    dataset = None
    model = None
    models = None
    fields = None

    path = check_dir(output)
    csv_properties = {}
    # If logging is required, open the file for logging
    log = None
    if args.log_file:
        check_dir(args.log_file)
        log = open(args.log_file, 'a', 0)

    # If neither a previous source, dataset or model are provided.
    # we create a new one
    if (training_set and not args.source and not args.dataset and
            not args.model and not args.models):
        source_args = {
            "name": name,
            "description": description,
            "category": args.category,
            "tags": args.tag,
            "source_parser": {"header": training_set_header}}
        source = api.create_source(training_set, source_args,
                                   progress_bar=args.progress_bar)
        source = api.check_resource(source, api.get_source)
        if log:
            log.write("%s\n" % source['resource'])
            log.flush()

        fields = Fields(source['object']['fields'],
                        source['object']['source_parser']['missing_tokens'],
                        source['object']['source_parser']['locale'])

    # If a source is provided, we retrieve it.
    elif args.source:
        source = api.get_source(args.source)

    # If we already have source, we check that is finished and extract the
    # fields, and update them if needed.
    if source:
        source = api.check_resource(source, api.get_source)
        csv_properties = {'missing_tokens':
                          source['object']['source_parser']['missing_tokens'],
                          'data_locale':
                          source['object']['source_parser']['locale']}

        fields = Fields(source['object']['fields'], **csv_properties)
        update_fields = {}
        if field_attributes:
            for (column, value) in field_attributes.iteritems():
                update_fields.update({
                    fields.field_id(column): value})
            source = api.update_source(source, {"fields": update_fields})

        update_fields = {}
        if types:
            for (column, value) in types.iteritems():
                update_fields.update({
                    fields.field_id(column): {'optype': value}})
            source = api.update_source(source, {"fields": update_fields})
        source_file = open(path + '/source', 'w', 0)
        source_file.write("%s\n" % source['resource'])
        source_file.write("%s\n" % source['object']['name'])
        source_file.flush()
        source_file.close()

    # If we have a source but not dataset or model has been provided, we
    # create a new dataset if the no_dataset option isn't set up.
    if (source and not args.dataset and not args.model and not model_ids and
            not args.no_dataset):
        dataset_args = {
            "name": name,
            "description": description,
            "category": args.category,
            "tags": args.tag
        }

        if args.json_filter:
            dataset_args.update(json_filter=args.json_filter)
        elif args.lisp_filter:
            dataset_args.update(lisp_filter=args.lisp_filter)

        input_fields = []
        if dataset_fields:
            for name in dataset_fields:
                input_fields.append(fields.field_id(name))
            dataset_args.update(input_fields=input_fields)

        dataset = api.create_dataset(source, dataset_args)
        if log:
            log.write("%s\n" % dataset['resource'])
            log.flush()
        dataset_file = open(path + '/dataset', 'w', 0)
        dataset_file.write("%s\n" % dataset['resource'])
        dataset_file.flush()
        dataset_file.close()

    # If a dataset is provided, let's retrieve it.
    elif args.dataset:
        dataset = api.get_dataset(args.dataset)

    # If we already have a dataset, we check the status and get the fields if
    # we hadn't them yet.
    if dataset:
        dataset = api.check_resource(dataset, api.get_dataset)
        if not csv_properties:
            csv_properties = {'data_locale':
                              dataset['object']['locale']}
        if args.public_dataset:
            public_dataset = {"private": False}
            if args.dataset_price:
                public_dataset.update(price=args.dataset_price)
            dataset = api.update_dataset(dataset, public_dataset)
        fields = Fields(dataset['object']['fields'], **csv_properties)

    # If we have a dataset but not a model, we create the model if the no_model
    # flag hasn't been set up.
    if (dataset and not args.model and not model_ids and not args.no_model):
        model_args = {
            "name": name,
            "description": description,
            "category": args.category,
            "tags": args.tag
        }
        if not objective_field is None:
            model_args.update({"objective_field":
                               fields.field_id(objective_field)})

        input_fields = []
        if model_fields:
            for name in model_fields:
                input_fields.append(fields.field_id(name))
            model_args.update(input_fields=input_fields)

        if args.stat_pruning:
            model_args.update(stat_pruning=True)

        if args.no_stat_pruning:
            model_args.update(stat_pruning=False)

        model_args.update(sample_rate=args.sample_rate,
                          replacement=args.replacement,
                          randomize=args.randomize)
        model_ids = []
        models = []
        model_file = open(path + '/models', 'w', 0)
        last_model = None
        for i in range(1, args.number_of_models + 1):
            if i > args.max_parallel_models:
                api.check_resource(last_model, api.get_model)
            model = api.create_model(dataset, model_args)
            if log:
                log.write("%s\n" % model['resource'])
                log.flush()
            last_model = model
            model_ids.append(model['resource'])
            models.append(model)
            model_file.write("%s\n" % model['resource'])
            model_file.flush()
        model_file.close()

    # If a model is provided, we retrieve it.
    elif args.model:
        model = api.get_model(args.model)

    elif args.models or args.model_tag:
        models = model_ids[:]

    if model_ids and test_set:
        if len(model_ids) < MAX_MODELS:
            models = []
            for model in model_ids:
                model = api.check_resource(model, api.get_model)
                models.append(model)
            model = models[0]
        else:
            model = api.check_resource(model_ids[0], api.get_model)
            models[0] = model

    # We check that the model is finished and get the fields if haven't got
    # them yet.
    if model and (test_set or args.black_box or args.white_box):
        model = api.check_resource(model, api.get_model)
        if args.black_box:
            model = api.update_model(model, {"private": False})
        if args.white_box:
            public_model = {"private": False, "white_box": True}
            if args.model_price:
                public_model.update(price=args.model_price)
            if args.cpp:
                public_model.update(credits_per_prediction=args.cpp)
            model = api.update_model(model, public_model)
        if not csv_properties:
            csv_properties = {'data_locale':
                              model['object']['locale']}
        csv_properties.update(verbose=True)
        if args.user_locale:
            csv_properties.update(data_locale=args.user_locale)

        fields = Fields(model['object']['model']['fields'], **csv_properties)

    if model and not models:
        models = [model]

    if models and test_set:
        objective_field = models[0]['object']['objective_fields']
        if isinstance(objective_field, list):
            objective_field = objective_field[0]
        predict(test_set, test_set_header, models, fields, output,
                objective_field, args.remote, api, log,
                args.max_batch_models, args.method)

    if votes_files:
        model_id = re.sub(r'.*(model_[a-f0-9]{24})__predictions\.csv$',
                          r'\1', votes_files[0]).replace("_", "/")
        model = api.check_resource(model_id, api.get_model)
        local_model = Model(model)
        combine_votes(votes_files, local_model.to_prediction,
                      output, args.method)

    if args.log_file and log:
        log.close()


def main(args=sys.argv[1:]):
    """Main process

    """
    command_log = open(".bigmler", "a", 0)
    command_log.write("bigmler %s\n" % " ".join(args))
    command_log.close()
    # Date and time in format SunNov0412_120510 to name and tag resources
    NOW = datetime.datetime.now().strftime("%a%b%d%y_%H%M%S")

    parser = create_parser(defaults={'NOW': NOW, 'MAX_MODELS': MAX_MODELS})

    # Parses command line arguments.
    ARGS = parser.parse_args(args)

    if len(os.path.dirname(ARGS.predictions).strip()) == 0:
        ARGS.predictions = "%s%s%s" % (NOW, os.sep, ARGS.predictions)

    API_ARGS = {
        'username': ARGS.username,
        'api_key': ARGS.api_key,
        'dev_mode': ARGS.dev_mode,
        'debug': ARGS.debug}

    API = bigml.api.BigML(**API_ARGS)

    output_args = {
        "api": API,
        "training_set": ARGS.training_set,
        "test_set": ARGS.test_set,
        "output": ARGS.predictions,
        "objective_field": ARGS.objective_field,
        "name": ARGS.name,
        "training_set_header": ARGS.train_header,
        "test_set_header": ARGS.test_header,
        "args": ARGS,
    }

    # Reads description if provided.
    if ARGS.description:
        DESCRIPTION = read_description(ARGS.description)
        output_args.update(description=DESCRIPTION)
    else:
        output_args.update(description="Created using BigMLer")

    # Parses fields if provided.
    if ARGS.field_attributes:
        FIELD_ATTRIBUTES = read_field_attributes(ARGS.field_attributes)
        output_args.update(field_attributes=FIELD_ATTRIBUTES)

    # Parses types if provided.
    if ARGS.types:
        TYPES = read_types(ARGS.types)
        output_args.update(types=TYPES)

    # Parses dataset fields if provided.
    if ARGS.dataset_fields:
        DATASET_FIELDS = map(lambda x: x.strip(),
                             ARGS.dataset_fields.split(','))
        output_args.update(dataset_fields=DATASET_FIELDS)

    # Parses model input fields if provided.
    if ARGS.model_fields:
        MODEL_FIELDS = map(lambda x: x.strip(), ARGS.model_fields.split(','))
        output_args.update(model_fields=MODEL_FIELDS)

    model_ids = []
    # Parses model/ids if provided.
    if ARGS.models:
        model_ids = read_models(ARGS.models)
        output_args.update(model_ids=model_ids)

    dataset_id = None
    # Parses dataset/id if provided.
    if ARGS.datasets:
        dataset_id = read_dataset(ARGS.datasets)
        ARGS.dataset = dataset_id

    # Retrieve model/ids if provided.
    if ARGS.model_tag:
        model_ids = model_ids + list_model_ids(API,
                                               "tags__in=%s" % ARGS.model_tag)
        output_args.update(model_ids=model_ids)

    # Reads a json filter if provided.
    if ARGS.json_filter:
        json_filter = read_json_filter(ARGS.json_filter)
        ARGS.json_filter = json_filter

    # Reads a lisp filter if provided.
    if ARGS.lisp_filter:
        lisp_filter = read_lisp_filter(ARGS.lisp_filter)
        ARGS.lisp_filter = lisp_filter

    # Adds default tags unless that it is requested not to do so.
    if ARGS.no_tag:
        ARGS.tag.append('BigMLer')
        ARGS.tag.append('BigMLer_%s' % NOW)

    # Checks combined votes method
    if ARGS.method and not ARGS.method in COMBINATION_METHODS.keys():
        ARGS.method = 'plurality'

    # Reads votes files in the provided directories.
    if ARGS.votes_dirs:
        dirs = map(lambda x: x.strip(), ARGS.votes_dirs.split(','))
        votes_files = read_votes(dirs, os.path.dirname(ARGS.predictions))
        output_args.update(votes_files=votes_files)

    # Parses resources ids if provided.
    if ARGS.delete:
        delete_list = []
        if ARGS.delete_list:
            delete_list = map(lambda x: x.strip(), ARGS.delete_list.split(','))
        if ARGS.delete_file:
            if not os.path.exists(ARGS.delete_file):
                raise Exception("File %s not found" % ARGS.delete_file)
            delete_list.extend([line for line in open(ARGS.delete_file, "r")])
        if ARGS.all_tag:
            query_string = "tags__in=%s" % ARGS.all_tag
            delete_list.extend(list_source_ids(API, query_string))
            delete_list.extend(list_dataset_ids(API, query_string))
            delete_list.extend(list_model_ids(API, query_string))
            delete_list.extend(list_prediction_ids(API, query_string))
        # Retrieve sources/ids if provided
        if ARGS.source_tag:
            query_string = "tags__in=%s" % ARGS.source_tag
            delete_list.extend(list_source_ids(API, query_string))
        # Retrieve datasets/ids if provided
        if ARGS.dataset_tag:
            query_string = "tags__in=%s" % ARGS.dataset_tag
            delete_list.extend(list_dataset_ids(API, query_string))
        # Retrieve model/ids if provided
        if ARGS.model_tag:
            query_string = "tags__in=%s" % ARGS.model_tag
            delete_list.extend(list_model_ids(API, query_string))
        # Retrieve prediction/ids if provided
        if ARGS.prediction_tag:
            query_string = "tags__in=%s" % ARGS.prediction_tag
            delete_list.extend(list_prediction_ids(API, query_string))

        delete(API, delete_list)
    else:
        compute_output(**output_args)


if __name__ == '__main__':
    main(sys.argv[1:])
