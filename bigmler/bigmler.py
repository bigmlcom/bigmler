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
import datetime
import argparse
import csv
import fileinput
import ast

import bigml.api
from bigml.multimodel import MultiModel
from bigml.multimodel import combine_predictions
from bigml.fields import Fields


def read_description(path):
    """Reads a text description from a file.

    """

    lines = ''
    for line in fileinput.input([path]):
        lines += line
    return lines


def read_field_names(path):
    """Reads field names from a file to update source field names.

    A column number and a name separated by a comma per line.

    For example:

    0, 'first name'
    1, 'last name'

    """
    field_names = {}
    for line in fileinput.input([path]):
        try:
            pair = ast.literal_eval(line)
            field_names.update({
                pair[0]: pair[1]})
        except SyntaxError:
            pass
    return field_names


def read_types(path):
    """Types to update source fields types.

    A column number and type separated by a comma per line.

    For example:

    0, 'categorical'
    1, 'numeric'

    """
    types_dict = {}
    for line in fileinput.input([path]):
        try:
            pair = ast.literal_eval(line)
            types_dict.update({
                pair[0]: pair[1]})
        except SyntaxError:
            pass
    return types_dict


def read_models(path):
    """Reads model ids from a file.

    For example:

    model/50974922035d0706da00003d
    model/509748b7035d0706da000039
    model/5097488b155268377a000059

    """
    models = []
    for line in fileinput.input([path]):
        models.append(line.rstrip())
    return models


def list_model_ids(api, query_string):
    """Lists BigML models filtered by `query_string`.

    """
    models = api.list_models(query_string)
    return [obj['resource'] for obj in models['objects']]


def predict(test_set, test_set_header, models, fields, output,
            objective_field, remote=False):
    """Computes a prediction for each entry in the `test_set`


    """

    test_reader = csv.reader(open(test_set, "U"))
    if test_set_header:
        test_reader.next()
    output = open(output, 'w', 0)
    if remote:
        for row in test_reader:
            predictions = []
            input_data = fields.pair(row, objective_field)

            for model in models:
                prediction = api.create_prediction(model, input_data,
                                                   by_name=False, wait_time=0)
                predictions.append(prediction['object']['prediction']
                                   [prediction['object']
                                   ['objective_fields'][0]])
            output.write("%s\n" % combine_predictions(predictions))
            output.flush()
    else:
        local_model = MultiModel(models)
        for row in test_reader:
            input_data = fields.pair(row, objective_field)
            print input_data
            prediction = local_model.predict(input_data)
            output.write("%s\n" % prediction)
            output.flush()
    output.close()


def compute_output(api, args, training_set, test_set=None, output=None,
                   objective_field=None,
                   description=None,
                   field_names=None,
                   types=None,
                   dataset_fields=None,
                   model_fields=None,
                   name=None, training_set_header=True,
                   test_set_header=True, model_ids=None):
    """ Creates one or models using the `training_set` or uses the ids
    of previous created BigML models to make predictions for the `test_set`.

    """
    source = None
    dataset = None
    model = None
    models = None
    fields = None

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
        source = api.create_source(training_set, source_args)
        source = api.check_resource(source, api.get_source)
        fields = Fields(source['object']['fields'])

        update_fields = {}
        if field_names:
            for (column, value) in field_names.iteritems():
                update_fields.update({
                    fields.field_id(column): {'name': value}})
            source = api.update_source(source, {"fields": update_fields})

        update_fields = {}
        if types:
            for (column, value) in types.iteritems():
                update_fields.update({
                    fields.field_id(column): {'optype': value}})
            source = api.update_source(source, {"fields": update_fields})
    # If a source is provided, we retrieve it.
    elif args.source:
        source = api.get_source(source)

    # If we alreday have source, we check that is finished and extract the
    # fields.
    if source:
        source = api.check_resource(source, api.get_source)
        fields = Fields(source['object']['fields'])

    # If we have a source but not dataset or model has been provided, we
    # create a new dataset
    if (source and not args.dataset and not args.model and not model_ids):
        dataset_args = {
            "description": description,
            "tags": args.tag
        }
        update_fields = {}
        if dataset_fields:
            for name in dataset_fields:
                update_fields.update({
                    fields.field_id(name): {'name': name}})
            dataset_args.update(fields=update_fields)

        dataset = api.create_dataset(source, dataset_args)
    # If a dataset is provided, let's retrieve it.
    elif args.dataset:
        dataset = api.get_dataset(args.dataset)

    # If we already have a dataset, we check the status and get the fields if
    # we hadn't them yet.
    if dataset:
        dataset = api.check_resource(dataset, api.get_dataset)
        if not fields:
            fields = Fields(dataset['object']['fields'])

    # If we have a dataset but not a model we create the model.
    if (dataset and not args.model and not model_ids):
        model_args = {
            "description": description,
            "tags": args.tag
        }
        if not objective_field is None:
            model_args.update({"objective_field":
                               fields.field_id(objective_field)})

        update_fields = []
        if model_fields:
            for name in model_fields:
                update_fields.append(fields.field_id(name))
            model_args.update(input_fields=update_fields)

        model_args.update(sample_rate=args.sample_rate,
                          replacement=args.replacement)
        model_ids = []
        model_file = open(name + '_models', 'w', 0)
        last_model = None
        for i in range(1, args.number_of_models + 1):
            if i > args.max_parallel_models:
                api.check_resource(last_model, api.get_model)
            model = api.create_model(dataset, model_args)
            last_model = model
            model_ids.append(model['resource'])
            model_file.write("%s\n" % model['resource'])
            model_file.flush()
        model_file.close()

    # If a model is provided, we retrieve it.
    elif args.model:
        model = api.get_model(args.model)

    if model_ids:
        models = []
        for model in model_ids:
            model = api.check_resource(model, api.get_model)
            models.append(model)
        model = models[0]

    # We check that the model is finished and get the fields if haven't got
    # them yet.
    if model:
        model = api.check_resource(model, api.get_model)
        if not fields:
            fields = Fields(model['object']['model']['fields'])
    else:
        raise ValueError("You need a valid model")

    if model and not models:
        models = [model]

    if test_set:
        predict(test_set, test_set_header, models, fields, output,
                objective_field, args.remote)

if __name__ == '__main__':

    # Date and time in format SunNov0412_120510 to name and tag resources
    NOW = datetime.datetime.now().strftime("%a%b%d%g_%H%M%S")

    parser = argparse.ArgumentParser(
        description="A higher level API to BigML's API.",
        epilog="Happy predictive modeling!")

    # Shows log info for each https request.
    parser.add_argument('--debug',
                        action='store_true',
                        help="Activates debug level")

    # Uses BigML dev environment. Sizes must be under 1MB though.
    parser.add_argument('--dev',
                        action='store_true',
                        dest='dev_mode',
                        help="""Computes a test output using BigML FREE
                                development environment""")

    # Path to the training set
    parser.add_argument('--train',
                        action='store',
                        dest='training_set',
                        help="Training set path")

    # Path to the test set
    parser.add_argument('--test',
                        action='store',
                        dest='test_set',
                        help="Test set path")

    # Name of the output
    parser.add_argument('--output',
                        action='store',
                        dest='submission',
                        default='submission_%s.csv' % NOW,
                        help="Submission path")

    # The name of the field that represents the objective field (i.e., class or label)
    parser.add_argument('--objective',
                        action='store',
                        dest='objective_field',
                        help="The column number of the Objective Field")

    # Category code.
    parser.add_argument('--category',
                        action='store',
                        dest='category',
                        default=12,
                        type=int,
                        help="Category code")

    # A file including a makdown description
    parser.add_argument('--description',
                        action='store',
                        dest='description',
                        help="""Path to a file with a description in plain
                                text or markdown""")

    # The path to a file containing names if you want to alter BigML's
    # default field names or the ones provided by the train file header.
    parser.add_argument('--field_names',
                        action='store',
                        dest='field_names',
                        help="""Path to a file describing field names. One
                                definition per line (e.g., 0, 'Last Name')""")

    # The path to a file containing types if you want to alter BigML's
    # type auto-detect.
    parser.add_argument('--types',
                        action='store',
                        dest='types',
                        help="""Path to a file describing field types. One
                                definition per line (e.g., 0, 'numeric')""")

    # Fields to include in the dataset.
    parser.add_argument('--dataset_fields',
                        action='store',
                        dest='dataset_fields',
                        help="""Comma-separated list of field column numbers
                                to include in the dataset""")

    # Input fields to include in the model.
    parser.add_argument('-mf', '--model_fields',
                        action='store',
                        dest='model_fields',
                        help="""Comma-separated list of input fields
                                (predictors) to create the model""")

    # Set when the training set file doesn't include a header on the first
    # line.
    parser.add_argument('--no-train-header',
                        action='store_false',
                        dest='train_header',
                        help="The train set file hasn't a header")

    # Set when the test set file doesn't include a header on the first
    # line.
    parser.add_argument('--no-test-header',
                        action='store_false',
                        dest='test_header',
                        help="The test set file hasn't a header")

    # Name to be used with the source and then with datasets, models and
    # predicitions.
    parser.add_argument('--name',
                        action='store',
                        dest='name',
                        default='BigMLer_%s' % NOW,
                        help="Name for the resources in BigML")

    # If a BigML source is provided, the script won't create a new one
    parser.add_argument('--source',
                        action='store',
                        dest='source',
                        help="BigML source Id")

    # If a BigML dataset is provided, the script won't create a new one
    parser.add_argument('--dataset',
                        action='store',
                        dest='dataset',
                        help="BigML dataset Id")

    # If a BigML model is provided, the script will use it to generate
    # predictions.
    parser.add_argument('--model',
                        action='store',
                        dest='model',
                        help="BigML model Id")

    # Use it to compute predictions remotely.
    parser.add_argument('--remote',
                        action='store_true',
                        help="Computes predictions remotely")

    # The path to a file containing model ids.
    parser.add_argument('--models',
                        action='store',
                        dest='models',
                        help="""Path to a file containing model/ids. One model
                                per line (e.g., 0, 'model/4f824203ce80053')""")

    # Number of models to create when using ensembles.
    parser.add_argument('--number_of_models',
                        action='store',
                        dest='number_of_models',
                        default=1,
                        type=int,
                        help="Number of models to create when using ensembles")

    # Sampling to use when using bagging.
    parser.add_argument('--sample_rate',
                        action='store',
                        dest='sample_rate',
                        default=1,
                        type=float,
                        help="Sample rate to create models")

    # Replacement to use when using bagging.
    parser.add_argument('--replacement',
                        action='store_true',
                        help="Use replacement when sampling")

    # Max number of models to create in parallel.
    parser.add_argument('--max_parallel_models',
                        action='store',
                        dest='max_parallel_models',
                        default=1,
                        type=int,
                        help="Max number of models to create in parallel")

    # Use it to add a tag to the new resources created.
    parser.add_argument('--tag',
                        action='append',
                        default=['BigMLer', 'BigMLer_%s' % NOW],
                        help="""Tag to later retrieve new resources""")

    # Use it to retrieve models that were tagged with tag.
    parser.add_argument('--model_tag',
                        help="Retrieve models that were tagged with tag")

    # Parses command line arguments.
    ARGS = parser.parse_args()

    API = bigml.api.BigML(dev_mode=ARGS.dev_mode, debug=ARGS.debug)

    output_args = {
        "api": API,
        "training_set": ARGS.training_set,
        "test_set": ARGS.test_set,
        "output": ARGS.submission,
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
    if ARGS.field_names:
        FIELD_NAMES = read_field_names(ARGS.field_names)
        output_args.update(field_names=FIELD_NAMES)

    # Parses types if provided.
    if ARGS.types:
        TYPES = read_types(ARGS.types)
        output_args.update(types=TYPES)

    # Parses dataset fields if provided.
    if ARGS.dataset_fields:
        DATASET_FIELDS =  map(lambda x: x.strip(), ARGS.dataset_fields.split(','))
        output_args.update(dataset_fields=DATASET_FIELDS)

    # Parses model input fields if provided.
    if ARGS.model_fields:
        MODEL_FIELDS = map(lambda x: x.strip(), ARGS.model_fields.split(','))
        output_args.update(model_fields=MODEL_FIELDS)

    model_ids = []
    # Parses model/ids if provided
    if ARGS.models:
        model_ids = read_models(ARGS.models)
        output_args.update(model_ids=model_ids)

    # Retrieve model/ids if provided
    if ARGS.model_tag:
        model_ids = model_ids + list_model_ids(API,
                                               "tags__in=%s" % ARGS.model_tag)
        output_args.update(model_ids=model_ids)

    compute_output(**output_args)
