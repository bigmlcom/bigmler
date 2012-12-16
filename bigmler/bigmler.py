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
import sys
import os
import datetime
import argparse
import csv
import fileinput
import ast
import glob
import re

try:
    import simplejson as json
except ImportError:
    import json

import bigml.api
from bigml.model import Model
from bigml.multimodel import MultiModel
from bigml.multimodel import combine_predictions
from bigml.multimodel import COMBINATION_METHODS
from bigml.fields import Fields
from bigml.util import slugify, reset_progress_bar, localize, \
    get_predictions_file_name


PAGE_LENGTH = 200
MAX_MODELS = 10


def read_description(path):
    """Reads a text description from a file.

    """
    lines = ''
    for line in fileinput.input([path]):
        lines += line
    return lines


def read_field_attributes(path):
    """Reads field attributes from a csv file to update source fields.

    A column number and a list of attributes separated by a comma per line.
    The expected structure is:
    column number, name, label, description

    For example:

    0,'first name','label for the first field','fist field full description'
    1,'last name','label for the last field','last field full description'

    """
    field_attributes = {}
    ATTRIBUTE_NAMES = ['name', 'label', 'description']
    try:
        attributes_reader = csv.reader(open(path, "U"), quotechar="'")
    except IOError:
        sys.exit("Error: cannot read field attributes %s" % path)

    for row in attributes_reader:
        try:
            attributes = {}
            if len(row) > 1:
                for index in range(0, len(row) - 1):
                    attributes.update({ATTRIBUTE_NAMES[index]: row[index + 1]})
                field_attributes.update({
                    int(row[0]): attributes})
        except ValueError:
            pass
    return field_attributes


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


def read_dataset(path):
    """Reads dataset id from a file.

    For example:

    dataset/50978822035d0706da000069

    """
    datasets = []
    for line in fileinput.input([path]):
        datasets.append(line.rstrip())
    return datasets[0]


def read_json_filter(path):
    """Reads a json filter from a file.

    For example:

    [">", 3.14, ["field", "000002"]]

    """
    json_data = open(path)
    json_filter = json.load(json_data)
    json_data.close()
    return json_filter


def read_lisp_filter(path):
    """Reads a lisp filter from a file.

    For example:

    (> (/ (+ (- (field "00000") 4.4)
            (field 23)
            (* 2 (field "Class") (field "00004")))
       3)
       5.5)

    """
    return read_description(path)


def read_votes(dirs_list, path):
    """Reads a list of directories to look for votes.

    If model's prediction files are found, they are retrieved to be combined.
    """
    file_name = "%s%scombined_predictions" % (path,
                                              os.sep)
    check_dir(file_name)
    group_predictions = open(file_name, "w", 0)
    current_directory = os.getcwd()
    for directory in dirs_list:
        directory = os.path.abspath(directory)
        os.chdir(directory)
        predictions_files = []
        for predictions_file in glob.glob("model_*_predictions.csv"):
            predictions_files.append("%s%s%s" % (os.getcwd(),
                                     os.sep, predictions_file))
            group_predictions.write("%s\n" % predictions_file)
        os.chdir(current_directory)
    group_predictions.close()
    return predictions_files


def list_source_ids(api, query_string):
    """Lists BigML sources filtered by `query_string`.

    """
    sources = api.list_sources('status.code=%s;limit=%s;%s' % (
                               bigml.api.FINISHED, PAGE_LENGTH, query_string))
    ids = ([] if sources['objects'] is None else
           [obj['resource'] for obj in sources['objects']])
    while (not sources['objects'] is None and
          (sources['meta']['total_count'] > (sources['meta']['offset'] +
           sources['meta']['limit']))):
        offset = sources['meta']['offset'] + PAGE_LENGTH
        sources = api.list_sources('offset=%s;limit=%s;%s' % (offset,
                                   PAGE_LENGTH, query_string))
        ids.extend(([] if sources['objects'] is None else
                   [obj['resource'] for obj in sources['objects']]))
    return ids


def list_dataset_ids(api, query_string):
    """Lists BigML datasets filtered by `query_string`.

    """
    datasets = api.list_datasets('status.code=%s;limit=%s;%s' % (
                                 bigml.api.FINISHED, PAGE_LENGTH,
                                 query_string))
    ids = ([] if datasets['objects'] is None else
           [obj['resource'] for obj in datasets['objects']])
    while (not datasets['objects'] is None and
          (datasets['meta']['total_count'] > (datasets['meta']['offset'] +
           datasets['meta']['limit']))):
        offset = datasets['meta']['offset'] + PAGE_LENGTH
        datasets = api.list_datasets('offset=%s;limit=%s;%s' % (offset,
                                     PAGE_LENGTH, query_string))
        ids.extend(([] if datasets['objects'] is None else
                   [obj['resource'] for obj in datasets['objects']]))
    return ids


def list_model_ids(api, query_string):
    """Lists BigML models filtered by `query_string`.

    """
    models = api.list_models('status.code=%s;limit=%s;%s' % (
                             bigml.api.FINISHED, PAGE_LENGTH, query_string))
    ids = ([] if models['objects'] is None else
           [obj['resource'] for obj in models['objects']])
    while (not models['objects'] is None and
          (models['meta']['total_count'] > (models['meta']['offset'] +
           models['meta']['limit']))):
        offset = models['meta']['offset'] + PAGE_LENGTH
        models = api.list_models('offset=%s;limit=%s;%s' % (offset,
                                 PAGE_LENGTH, query_string))
        ids.extend(([] if models['objects'] is None else
                   [obj['resource'] for obj in models['objects']]))
    return ids


def list_prediction_ids(api, query_string):
    """Lists BigML predictions filtered by `query_string`.

    """
    predictions = api.list_predictions('status.code=%s;limit=%s;%s' % (
                                       bigml.api.FINISHED, PAGE_LENGTH,
                                       query_string))
    ids = ([] if predictions['objects'] is None else
           [obj['resource'] for obj in predictions['objects']])
    while (not predictions['objects'] is None and
          (predictions['meta']['total_count'] > (predictions['meta']['offset']
           + predictions['meta']['limit']))):
        offset = predictions['meta']['offset'] + PAGE_LENGTH
        predictions = api.list_predictions('offset=%s;limit=%s;%s' % (offset,
                                           PAGE_LENGTH, query_string))
        ids.extend(([] if predictions['objects'] is None else
                   [obj['resource'] for obj in predictions['objects']]))
    return ids


def predict(test_set, test_set_header, models, fields, output,
            objective_field, remote=False, api=None, log=None,
            max_models=MAX_MODELS, method='pluralize'):
    """Computes a prediction for each entry in the `test_set`


    """
    out = sys.stdout

    def draw_progress_bar(current, total):
        """Draws a text based progress report.

        """
        pct = 100 - ((total - current) * 100) / (total)
        reset_progress_bar(out=out)
        out.write("Predicted on %s out of %s models [%s%%]" % (
            localize(current), localize(total), pct))

    try:
        test_reader = csv.reader(open(test_set, "U"))
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
            predictions = []
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
                predictions.append(prediction['object']['prediction']
                                   [prediction['object']
                                   ['objective_fields'][0]])
            prediction = combine_predictions(predictions, method)
            if isinstance(prediction, basestring):
                prediction = prediction.encode("utf-8")
            output.write("%s\n" % prediction)
            output.flush()
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

            reset_progress_bar(out=out)
            out.write("Combining predictions.")
            for predictions in total_votes:
                prediction = combine_predictions(predictions, method)
                if isinstance(prediction, basestring):
                    prediction = prediction.encode("utf-8")
                output.write("%s\n" % prediction)
                output.flush()
            reset_progress_bar(out=out)
            out.write("Done.")
            reset_progress_bar(out=out)
    output.close()


def combine_votes(votes_files, to_prediction, data_locale,
                  to_file, method='pluralize'):
    """Combines the votes found in the votes' files and stores predictions.

    """
    votes = []
    for votes_file in votes_files:
        index = 0
        
        for row in csv.reader(open(votes_file, "U")):
            prediction = to_prediction(row[0])
            if index > (len(votes) - 1):
                votes.append({prediction: []})
            if not prediction in votes[index]:
                votes[index][prediction] = []
            votes[index][prediction].append(row[1])
            index += 1

    check_dir(to_file)
    output = open(to_file, 'w', 0)
    for predictions in votes:
        prediction = combine_predictions(predictions, method)
        if isinstance(prediction, basestring):
            prediction = prediction.encode("utf-8")
        output.write("%s\n" % prediction)
        output.flush()
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
        data_locale = (model['object']['locale'] if not args.user_locale
                       else args.user_locale)
        local_model = Model(model)
        combine_votes(votes_files, local_model.to_prediction,
                      data_locale, output, args.method)

    if args.log_file and log:
        log.close()


def delete(api, delete_list):
    """ Deletes the resources given in the list.

    """

    DELETE = {bigml.api.SOURCE_RE: api.delete_source,
              bigml.api.DATASET_RE: api.delete_dataset,
              bigml.api.MODEL_RE: api.delete_model,
              bigml.api.PREDICTION_RE: api.delete_prediction}
    for resource_id in delete_list:
        for resource_type in DELETE:
            try:
                bigml.api.get_resource(resource_type, resource_id)
                DELETE[resource_type](resource_id)
                break
            except ValueError:
                pass


def check_dir(path):
    """Creates a directory if it doesn't exist
    """
    directory = os.path.dirname(path)
    if len(directory) > 0 and not os.path.exists(directory):
        os.makedirs(directory)
        directory_log = open(".bigmler_dirs", "a", 0)
        directory_log.write("%s\n" % directory)
        directory_log.close()
    return directory


def main(args=sys.argv[1:]):
    """Main process

    """
    command_log = open(".bigmler", "a", 0)
    command_log.write("bigmler %s\n" % " ".join(args))
    command_log.close()
    # Date and time in format SunNov0412_120510 to name and tag resources
    NOW = datetime.datetime.now().strftime("%a%b%d%y_%H%M%S")

    parser = argparse.ArgumentParser(
        description="A higher level API to BigML's API.",
        epilog="Happy predictive modeling!")

    # Shows log info for each https request.
    parser.add_argument('--debug',
                        action='store_true',
                        help="Activate debug level")

    # Uses BigML dev environment. Sizes must be under 1MB though.
    parser.add_argument('--dev',
                        action='store_true',
                        dest='dev_mode',
                        help=("Compute a test output using BigML FREE"
                             " development environment"))
    # BigML's username.
    parser.add_argument('--username',
                        action='store',
                        help="BigML's username")

    # BigML's API key.
    parser.add_argument('--api_key',
                        action='store',
                        help="BigML's API key")

    # Path to the training set.
    parser.add_argument('--train',
                        action='store',
                        dest='training_set',
                        help="Training set path")

    # Path to the test set.
    parser.add_argument('--test',
                        action='store',
                        dest='test_set',
                        help="Test set path")

    # Name of the file to output predictions.
    parser.add_argument('--output',
                        action='store',
                        dest='predictions',
                        default='%s%spredictions.csv' % (NOW, os.sep),
                        help="Path to the file to output predictions.")

    # The name of the field that represents the objective field (i.e., class or
    # label).
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
                        help=("Path to a file with a description in plain"
                              " text or markdown"))

    # The path to a file containing names if you want to alter BigML's
    # default field names or the ones provided by the train file header.
    # Kept for backwards compatibility
    parser.add_argument('--field_names',
                        action='store',
                        dest='field_attributes',
                        help=("Path to a csv file describing field names. One"
                              " definition per line (e.g., 0,'Last Name')"))

    # The path to a file containing attributes if you want to alter BigML's
    # default field attributes or the ones provided by the train file header.
    parser.add_argument('--field_attributes',
                        action='store',
                        dest='field_attributes',
                        help=("Path to a csv file describing field attributes."
                              " One definition per line"
                              " (e.g., 0,'Last Name')"))

    # The path to a file containing types if you want to alter BigML's
    # type auto-detect.
    parser.add_argument('--types',
                        action='store',
                        dest='types',
                        help=("Path to a file describing field types. One"
                              " definition per line (e.g., 0, 'numeric')"))

    # Fields to include in the dataset.
    parser.add_argument('--dataset_fields',
                        action='store',
                        dest='dataset_fields',
                        help=("Comma-separated list of field column numbers"
                              " to include in the dataset"))

    # Path to a file that includes a JSON filter.
    parser.add_argument('--json_filter',
                        action='store',
                        help="File including a JSON filter")

    # Path to a file that includes a lisp filter.
    parser.add_argument('--lisp_filter',
                        action='store',
                        help="File including a Lisp filter")

    # Input fields to include in the model.
    parser.add_argument('--model_fields',
                        action='store',
                        dest='model_fields',
                        help=("Comma-separated list of input fields"
                              " (predictors) to create the model"))

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
                        help="Compute predictions remotely")

    # The path to a file containing model ids.
    parser.add_argument('--models',
                        action='store',
                        dest='models',
                        help=("Path to a file containing model/ids. One model"
                              " per line (e.g., model/50a206a8035d0706dc000376"
                              ")"))

    # The path to a file containing a dataset id.
    parser.add_argument('--datasets',
                        action='store',
                        dest='datasets',
                        help=("Path to a file containing a dataset/id. Just"
                              " one dataset"
                              " (e.g., dataset/50a20697035d0706da0004a4)"))

    # Set to True to active statiscal pruning.
    parser.add_argument('--stat_pruning',
                        action='store_true',
                        help="Use statiscal pruning.")

    # Set to False to deactivate statiscal pruning.
    parser.add_argument('--no_stat_pruning',
                        action='store_true',
                        help="Do not use statistical pruning.")

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

    # Max number of models to predict from in parallel.
    parser.add_argument('--max_batch_models',
                        action='store',
                        dest='max_batch_models',
                        default=MAX_MODELS,
                        type=int,
                        help="Max number of models to predict from in parallel")

    # Randomize feature selection at each split.
    parser.add_argument('--randomize',
                        action='store_true',
                        help="Randomize feature selection at each split.")

    # Use it to add a tag to the new resources created.
    parser.add_argument('--tag',
                        action='append',
                        default=[],
                        help="Tag to later retrieve new resources")

    # Avoid default tagging of resources.
    parser.add_argument('--no_tag',
                        action='store_false',
                        help="No tag resources with default BigMLer tags")

    # Use it to retrieve models that were tagged with tag.
    parser.add_argument('--model_tag',
                        help="Retrieve models that were tagged with tag")

    # Make dataset public.
    parser.add_argument('--public_dataset',
                        action='store_true',
                        help="Make generated dataset public")

    # Make model a public black-box model.
    parser.add_argument('--black_box',
                        action='store_true',
                        help="Make generated model black-box")

    # Make model a public white-box model.
    parser.add_argument('--white_box',
                        action='store_true',
                        help="Make generated model white-box")

    # Set a price tag to your white-box model.
    parser.add_argument('--model_price',
                        action='store',
                        type=float,
                        default=0.0,
                        help=("The price other users must pay to clone your"
                              " model"))

    # Set a price tag to your dataset.
    parser.add_argument('--dataset_price',
                        action='store',
                        type=float,
                        default=0.0,
                        help="Price for the dataset")

    # Set credits per prediction to your white box or black box models.
    parser.add_argument('--cpp',
                        action='store',
                        type=float,
                        default=0.0,
                        help=("The number of credits that other users will"
                              " consume to make a prediction with your"
                              " model."))

    # Shows progress information when uploading a file.
    parser.add_argument('--progress_bar',
                        action='store_true',
                        help="Show progress details when creating a source.")

    # Does not create a dataset.
    parser.add_argument('--no_dataset',
                        action='store_true',
                        help="Do not create a dataset.")

    # Does not create a model just a dataset.
    parser.add_argument('--no_model',
                        action='store_true',
                        help="Do not create a model.")

    # Log file to store resources ids.
    parser.add_argument('--resources_log',
                        action='store',
                        dest='log_file',
                        help=("Path to a file to store new resources ids."
                              " One resource per line"
                              " (e.g., model/50a206a8035d0706dc000376)"))
    # Changes to delete mode.
    parser.add_argument('--delete',
                        action='store_true',
                        help="Delete command.")

    # Resources to be deleted.
    parser.add_argument('--ids',
                        action='store',
                        dest='delete_list',
                        help=("Select comma separated list of"
                              " resources to be deleted."))

    # Resources to be deleted are taken from file.
    parser.add_argument('--from_file',
                        action='store',
                        dest='delete_file',
                        help=("Path to a file containing resources ids."
                              " One resource per line"
                              " (e.g., model/50a206a8035d0706dc000376)"))

    # Sources selected by tag to be deleted.
    parser.add_argument('--source_tag',
                        help=("Select sources tagged with tag to"
                              " be deleted"))

    # Datasets selected by tag to be deleted.
    parser.add_argument('--dataset_tag',
                        help=("Select datasets tagged with tag to"
                              " be deleted"))

    # Predictions selected by tag to be deleted.
    parser.add_argument('--prediction_tag',
                        help=("Select prediction tagged with tag to"
                              " be deleted"))

    # Resources selected by tag to be deleted.
    parser.add_argument('--all_tag',
                        help=("Select resources tagged with tag to"
                              " be deleted"))

    # Locale settings.
    parser.add_argument('--locale',
                        action='store',
                        dest='user_locale',
                        default=None,
                        help="Chosen locale code string.")

    # Prediction directories to be combined.
    parser.add_argument('--combine_votes',
                        action='store',
                        dest='votes_dirs',
                        help=("Comma separated list of"
                              " directories that contain models' votes"
                              " for the same test set."))

    # Method to combine votes in multiple models predictions
    parser.add_argument('--method',
                        action='store',
                        dest='method',
                        default='pluralize',
                        help="Method to combine votes from ensemble"
                             " predictions. Allowed methods: pluralize"
                             " or \"confidence weighted\".")

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
        ARGS.method = 'pluralize'

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
