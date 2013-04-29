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

"""Utilities for BigMLer

"""
from __future__ import absolute_import

import csv
import fileinput
import ast
import glob
import os
import sys
import datetime
import numbers

try:
    import simplejson as json
except ImportError:
    import json

import bigml.api
from bigml.multimodel import read_votes
from bigml.util import console_log

PAGE_LENGTH = 200
ATTRIBUTE_NAMES = ['name', 'label', 'description']
NEW_DIRS_LOG = ".bigmler_dirs"
RESOURCE_URL = "https://bigml.com/dashboard/"


def read_description(path):
    """Reads a text description from a file.

    """
    return ''.join(fileinput.input([path]))


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
    try:
        attributes_reader = csv.reader(open(path, "U"), quotechar="'")
    except IOError:
        sys.exit("Error: cannot read field attributes %s" % path)

    for row in attributes_reader:
        attributes = {}
        if len(row) > 1:
            for index in range(0, min(len(ATTRIBUTE_NAMES), len(row) - 1)):
                attributes.update({ATTRIBUTE_NAMES[index]: row[index + 1]})
            field_attributes.update({
                int(row[0]): attributes})
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
                pair[0]: {'optype': pair[1]}})
        except SyntaxError:
            console_log("WARNING: The following line in file %s"
                        " does not match the expected"
                        " syntax: %s" % (path, line))
    return types_dict


def read_fields_map(path):
    """Fields map from test dataset to evaluated model.

    The test dataset field column and the evaluated model field column
    separated by a comma per line.

    For example:

    0, 0
    1, 2
    2, 1

    """
    map_dict = {}
    for line in fileinput.input([path]):
        try:
            pair = ast.literal_eval(line)
            map_dict.update({
                pair[0]: pair[1]})
        except SyntaxError:
            console_log("WARNING: The following line in file %s"
                        " does not match the expected"
                        " syntax: %s" % (path, line))
    return map_dict


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
    with open(path) as json_data:
        return json.load(json_data)


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


def read_votes_files(dirs_list, path):
    """Reads a list of directories to look for votes.

    If model's prediction files are found, they are retrieved to be combined.
    Models' predictions files are expected to be named after the model id,
    for instance: model_50974922035d0706da00003d__predictions.csv
    """
    file_name = "%s%scombined_predictions" % (path,
                                              os.sep)
    check_dir(file_name)
    group_predictions = open(file_name, "w", 0)
    current_directory = os.getcwd()
    predictions_files = []
    for directory in dirs_list:
        directory = os.path.abspath(directory)
        os.chdir(directory)
        for predictions_file in glob.glob("model_*_predictions.csv"):
            predictions_files.append("%s%s%s" % (os.getcwd(),
                                     os.sep, predictions_file))
            group_predictions.write("%s\n" % predictions_file)
        os.chdir(current_directory)
    group_predictions.close()
    return predictions_files


def list_ids(api_function, query_string):
    """Lists BigML resources filtered by `query_string`.

    """
    q_s = 'status.code=%s;limit=%s;%s' % (
          bigml.api.FINISHED, PAGE_LENGTH, query_string)
    resources = api_function(q_s)
    ids = [obj['resource'] for obj in (resources['objects'] or [])]
    while (resources['objects'] and
          (resources['meta']['total_count'] > (resources['meta']['offset'] +
           resources['meta']['limit']))):
        offset = resources['meta']['offset'] + PAGE_LENGTH
        q_s = 'status.code=%s;offset=%s;limit=%s;%s' % (
              bigml.api.FINISHED, offset, PAGE_LENGTH, query_string)
        resources = api_function(q_s)
        if resources['objects']:
            ids.extend([obj['resource'] for obj in resources['objects']])
    return ids


def combine_votes(votes_files, to_prediction, to_file, method=0):
    """Combines the votes found in the votes' files and stores predictions.

       votes_files: should contain the list of file names
       to_prediction: is the Model method that casts prediction to numeric
                      type if needed
       to_file: is the name of the final output file.
    """
    votes = read_votes(votes_files, to_prediction)

    check_dir(to_file)
    output = csv.writer(open(to_file, 'w', 0),
                        lineterminator="\n")
    for multivote in votes:
        write_prediction(multivote.combine(method, True), output)


def delete(api, delete_list):
    """ Deletes the resources given in the list.

    """
    delete_functions = {bigml.api.SOURCE_RE: api.delete_source,
                        bigml.api.DATASET_RE: api.delete_dataset,
                        bigml.api.MODEL_RE: api.delete_model,
                        bigml.api.PREDICTION_RE: api.delete_prediction,
                        bigml.api.EVALUATION_RE: api.delete_evaluation}
    for resource_id in delete_list:
        resource_type = None
        try:
            for resource_type in delete_functions:
                try:
                    bigml.api.get_resource(resource_type, resource_id)
                    break
                except ValueError:
                    pass
            delete_functions[resource_type](resource_id)
        except ValueError:
            console_log("Failed to delete resource %s" % resource_id)


def check_dir(path):
    """Creates a directory if it doesn't exist

    """
    directory = os.path.dirname(path)
    if len(directory) > 0 and not os.path.exists(directory):
        os.makedirs(directory)
        with open(NEW_DIRS_LOG, "a", 0) as directory_log:
            directory_log.write("%s\n" % os.path.abspath(directory))
    return directory


def write_prediction(prediction, output=sys.stdout):
    """Writes the final combined prediction to the required output

    """
    confidence = False
    if isinstance(prediction, tuple):
        prediction, confidence = prediction
    if isinstance(prediction, basestring):
        prediction = prediction.encode("utf-8")
    row = [prediction]
    if confidence:
        row.append(confidence)
    try:
        output.writerow(row)
    except AttributeError:
        try:
            output.write(row)
        except AttributeError:
            raise AttributeError("You should provide a writeable object")


def tail(file_handler, window=1):
    """Returns the last n lines of a file.

    """
    bufsiz = 1024
    file_handler.seek(0, 2)
    file_bytes = file_handler.tell()
    size = window + 1
    block = -1
    data = []
    while size > 0 and file_bytes > 0:
        if (file_bytes - bufsiz > 0):
            # Seek back one whole bufsiz
            file_handler.seek(block * bufsiz, 2)
            # read BUFFER
            new_data = [file_handler.read(bufsiz)]
            new_data.extend(data)
            data = new_data
        else:
            # file too small, start from begining
            file_handler.seek(0, 0)
            # only read what was not read
            data.append(file_handler.read(file_bytes))
        lines_found = data[0].count('\n')
        size -= lines_found
        file_bytes -= bufsiz
        block -= 1
    return ''.join(data).splitlines()[-window:]


def get_log_reversed(file_name, stack_level):
    """Reads the line of a log file that has the chosen stack_level

    """
    lines_list = tail(open(file_name, "r"), window=(stack_level + 1))
    return lines_list[0]


def is_source_created(path):
    """Reads the source id from the source file in the path directory

    """
    source_id = None
    try:
        with open("%s%ssource" % (path, os.sep)) as source_file:
            source_id = source_file.readline().strip()
            try:
                source_id = bigml.api.get_source_id(source_id)
                return True, source_id
            except ValueError:
                return False, None
    except IOError:
        return False, None


def is_dataset_created(path, suffix=""):
    """Reads the dataset id from the dataset file in the path directory

    """
    dataset_id = None
    try:
        with open("%s%sdataset%s" % (path, os.sep, suffix)) as dataset_file:
            dataset_id = dataset_file.readline().strip()
            try:
                dataset_id = bigml.api.get_dataset_id(dataset_id)
                return True, dataset_id
            except ValueError:
                return False, None
    except IOError:
        return False, None


def are_models_created(path, number_of_models):
    """Reads the model ids from the models file in the path directory

    """
    model_ids = []
    try:
        with open("%s%smodels" % (path, os.sep)) as models_file:
            for line in models_file:
                model = line.strip()
                try:
                    model_id = bigml.api.get_model_id(model)
                    model_ids.append(model_id)
                except ValueError:
                    return False, model_ids
        if len(model_ids) == number_of_models:
            return True, model_ids
        else:
            return False, model_ids
    except IOError:
        return False, model_ids


def are_predictions_created(predictions_file, number_of_tests):
    """Reads the predictions from the predictions file in the path directory

    """
    predictions = file_number_of_lines(predictions_file)
    if predictions != number_of_tests:
        os.remove(predictions_file)
        return False
    return True


def is_evaluation_created(path):
    """Reads the evaluation id from the evaluation file in the path directory

    """
    evaluation_id = None
    try:
        with open("%s%sevaluation" % (path, os.sep)) as evaluation_file:
            evaluation_id = evaluation_file.readline().strip()
            try:
                evaluation_id = bigml.api.get_evaluation_id(evaluation_id)
                return True, evaluation_id
            except ValueError:
                return False, None
    except IOError:
        return False, None


def are_evaluations_created(path, number_of_evaluations):
    """Reads the evaluation ids from the evaluations file in the path directory
       and checks the corresponding evaluations

    """
    evaluation_ids = []
    try:
        with open("%s%sevaluations" % (path, os.sep)) as evaluations_file:
            for line in evaluations_file:
                evaluation = line.strip()
                try:
                    evaluation_id = bigml.api.get_evaluation_id(evaluation)
                    evaluation_ids.append(evaluation_id)
                except ValueError:
                    return False, evaluation_ids
        if len(evaluation_ids) == number_of_evaluations:
            return True, evaluation_ids
        else:
            return False, evaluation_ids
    except IOError:
        return False, evaluation_ids


def checkpoint(function, *args, **kwargs):
    """Redirects to each checkpoint function

    """

    debug = kwargs.get('debug', False)
    result = function(*args)
    if debug:
        console_log("Checkpoint: checking %s with args:\n%s\n\nResult:\n%s\n" %
                    (function.__name__, "\n".join([repr(arg) for arg in args]),
                     repr(result)))
    return result


def file_number_of_lines(file_name):
    """Counts the number of lines in a file

    """
    try:
        item = (0, None)
        with open(file_name) as file_handler:
            for item in enumerate(file_handler):
                pass
        return item[0] + 1
    except IOError:
        return 0


def print_tree(directory, padding):
    """Returns a graphical directory tree structure as a string

    """
    if padding != ' ':
        output = padding[:-1] + '├─'
    else:
        output = padding
    output += os.path.basename(os.path.abspath(directory)) + '\n'
    padding = padding + ' '
    files = []
    files = os.listdir(directory)
    count = 0
    for i in range(0, len(files)):
        file_name = files[i]
        count += 1
        path = directory + os.sep + file_name
        if os.path.isdir(path):
            if count == len(files):
                output += print_tree(path, padding + ' ')
            else:
                output += print_tree(path, padding + '|')
        else:
            if i < (len(files) - 1):
                output += padding + '├─' + file_name + '\n'
            else:
                output += padding + '└─' + file_name + '\n'
    return output


def dated(message):
    """Prepends date in log format in string

    """
    return "[%s] %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        message)


def prediction_to_row(prediction):
    """Returns a csv row to store main prediction info in csv files.

    """
    prediction = prediction['object']
    prediction_class = prediction['objective_fields'][0]
    row = [prediction['prediction'][prediction_class],
           prediction['prediction_path']['confidence']]
    tree = prediction['prediction_path']
    if ('objective_summary' in tree):
        summary = tree['objective_summary']
        if 'bins' in summary:
            distribution = summary['bins']
        elif 'counts' in summary:
            distribution = summary['counts']
        elif 'categories' in summary:
            distribution = summary['categories']
    if distribution:
        row.extend([repr(distribution), sum([x[1] for x in distribution])])
    return row


def get_url(resource):
    """Returns the resource's url in bigml.com

    """
    resource_id = bigml.api.get_resource_id(resource)
    if not resource_id:
        return ""
    return RESOURCE_URL + resource_id


def log_message(message, log_file=None, console=False):
    """Logs a message in a file and/or to console

       If log_file is set, logs the message in the file.
       If console is True, sends the message to console.
    """
    if console:
        console_log(message)
    if log_file is not None:
        if isinstance(message, unicode):
            message = message.encode("utf-8")
        with open(log_file, 'a', 0) as log_file:
            log_file.write(message)


def plural(text, num):
    """Pluralizer: adds "s" at the end of a string if a given number is > 1

    """
    return "%s%s" % (text, "s"[num == 1:])


def check_resource_error(resource, message):
    """Checks if a given resource is faulty and exits

    """
    if bigml.api.get_status(resource)['code'] == bigml.api.FAULTY:
        sys.exit("%s: %s" % (message, resource['error']))


def average_evaluations(evaluation_files):
    """Reads the contents of the evaluations files and averages its measures

    """
    special_keys = ["class_names", "per_class_statistics",
                    "confusion_matrix", "present_in_test_data"]
    averaged_evaluation = {}
    number_of_evaluations = float(len(evaluation_files))
    for evaluation_file in evaluation_files:
        with open(evaluation_file, 'U') as evaluation_file:
            evaluation = json.loads(evaluation_file.read())
            avg_evaluation(averaged_evaluation, evaluation,
                           number_of_evaluations, special_keys)
    return averaged_evaluation


def avg_evaluation(total, component, number_of_evaluations, special_keys):
    """Adds a new set of evaluation measures to the cumulative average

    """

    for key in component:
        value = component[key]
        # Handle the non-averageable values in
        # classifications' evaluation data
        if key in special_keys:
            if key == "class_names":
                if not key in total:
                    total[key] = []
                total[key].extend(component[key])
                total[key] = list(set(total[key]))
            if key == "confusion_matrix":
                if not key in total:
                    total[key] = component[key]
                else:
                    total[key] = add_matrices(total[key], component[key])
            if key == "per_class_statistics":
                if not key in total:
                    total[key] = []
                total[key] = avg_class_statistics(total[key], component[key],
                                                  number_of_evaluations)
        else:
            # Average numerical values
            if isinstance(value, numbers.Number):
                new_key = (key if key.startswith("average_")
                           else ("average_%s" % key))
                if not new_key in total:
                    total[new_key] = 0
                total[new_key] += component[key] / number_of_evaluations
            # Handle grouping keys
            elif isinstance(value, list) or isinstance(value, dict):
                if not key in total:
                    total[key] = [] if isinstance(value, list) else {}
                avg_evaluation(total[key], component[key],
                               number_of_evaluations, special_keys)


def add_matrices(matrix_a, matrix_b):
    """Add two n x n matrices

    """
    return map(lambda i: map(lambda x, y: x + y, matrix_a[i], matrix_b[i]),
               xrange(len(matrix_a)))


def avg_class_statistics(total, component, number_of_evaluations):
    """Adds a new set of per class evaluation measures to the total average

    """
    special_keys = ['class_name', 'present_in_test_data', 'occurrences']
    for class_info in component:
        class_name = class_info['class_name']
        found = False
        for total_class_info in total:
            if class_name == total_class_info['class_name']:
                found = True
                flag = class_info['present_in_test_data']
                # If the class is not present in the evaluation test data set,
                # the measures for that class are not affected by it
                if not flag:
                    total_class_info['occurrences'] -= 1
                    occurrences = total_class_info['occurrences']
                    for key in total_class_info:
                        # renormalizing previous average count
                        if not key in special_keys:
                            total_class_info[key] *= ((occurrences + 1) /
                                                      occurrences)
                total_class_info['present_in_test_data'] = flag
                occurrences = total_class_info['occurrences']
                for key in class_info:
                    if not key in special_keys:
                        new_key = (key if key.startswith("average_")
                                   else ("average_%s" % key))
                        if new_key in total_class_info:
                            total_class_info[new_key] += (class_info[key] /
                                                          occurrences)
                        else:
                            total_class_info[new_key] = (class_info[key] /
                                                         occurrences)
                break
        if not found:
            flag = class_info['present_in_test_data']
            class_info['occurrences'] = number_of_evaluations
            if not flag:
                class_info['occurrences'] -= 1
            for key in class_info:
                if not key in special_keys:
                    if not key.startswith("average_"):
                        new_key = "average_%s" % key
                        class_info[new_key] = (class_info[key] /
                                               class_info['occurrences'])
                        del class_info[key]
                    else:
                        class_info[key] = (class_info[key] /
                                           class_info['occurrences'])
            total.append(class_info)
    return total
