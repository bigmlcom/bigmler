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
"""Prediction auxiliary functions

"""
from __future__ import absolute_import

import csv
import sys

import bigmler.utils as u

from bigml.model import Model
from bigml.multimodel import MultiModel
from bigml.util import (localize, console_log, get_csv_delimiter,
                        get_predictions_file_name)

MAX_MODELS = 10


def remote_predict(models, headers, output_path, number_of_tests, resume,
                   verbosity, test_reader, exclude, fields, api,
                   prediction_file, method, tags, objective_field,
                   session_file, test_set_header, log, debug):
    """Retrieve predictions remotely, combine them and save predictions to file

    """

    predictions_files = []
    prediction_args = {
        "tags": tags
    }
    for model in models:
        if not isinstance(model, basestring) and 'resource' in model:
            model = model['resource']
        predictions_file = get_predictions_file_name(model,
                                                     output_path)
        predictions_files.append(predictions_file)
        if (not resume or
            not u.checkpoint(u.are_predictions_created, predictions_file,
                             number_of_tests, debug=debug)):
            message = u.dated("Creating remote predictions.\n")
            u.log_message(message, log_file=session_file,
                          console=verbosity)

            predictions_file = csv.writer(open(predictions_file, 'w', 0))
            for row in test_reader:
                for index in exclude:
                    del row[index]
                input_data = fields.pair(row, headers, objective_field)
                prediction = api.create_prediction(model, input_data,
                                                   by_name=test_set_header,
                                                   wait_time=0,
                                                   args=prediction_args)
                u.log_message("%s\n" % prediction['resource'], log_file=log)
                prediction_row = u.prediction_to_row(prediction)
                predictions_file.writerow(prediction_row)
    u.combine_votes(predictions_files,
                    Model(models[0]).to_prediction,
                    prediction_file, method)


def local_predict(models, headers, test_reader, exclude, fields, method,
                  objective_field, output, test_set_header):
    """Get local predictions, combine them and save predictions to file

    """
    local_model = MultiModel(models)
    for row in test_reader:
        for index in exclude:
            del row[index]
        input_data = fields.pair(row, headers, objective_field)
        prediction = local_model.predict(input_data,
                                         by_name=test_set_header,
                                         method=method)
        u.write_prediction(prediction, output)


def local_batch_predict(models, headers, test_reader, exclude, fields, resume,
                        output_path, max_models, number_of_tests, api, output,
                        verbosity, method, objective_field, session_file,
                        debug):
    """Get local predictions form partial Multimodel, combine and save to file

    """
    def draw_progress_bar(current, total):
        """Draws a text based progress report.

        """
        pct = 100 - ((total - current) * 100) / (total)
        console_log("Predicted on %s out of %s models [%s%%]" % (
            localize(current), localize(total), pct))

    models_total = len(models)
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
        if resume:
            for model in models_split:
                pred_file = get_predictions_file_name(model,
                                                      output_path)
                u.checkpoint(u.are_predictions_created,
                             pred_file,
                             number_of_tests, debug=debug)
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
        if verbosity:
            draw_progress_bar(models_count, models_total)
        if total_votes:
            for index in range(0, len(votes)):
                predictions = total_votes[index].predictions
                predictions.extend(votes[index].predictions)
        else:
            total_votes = votes
    message = u.dated("Combining predictions.\n")
    u.log_message(message, log_file=session_file, console=verbosity)
    for multivote in total_votes:
        u.write_prediction(multivote.combine(method), output)


def predict(test_set, test_set_header, models, fields, output,
            objective_field, remote=False, api=None, log=None,
            max_models=MAX_MODELS, method=0, resume=False,
            tags=None, verbosity=1, session_file=None, debug=False):
    """Computes a prediction for each entry in the `test_set`.

       Predictions can be computed remotely, locally using MultiModels built
       on all the models or locally using MultiModels on subgroups of models.
       Chosing a max_batch_models value not bigger than the number_of_models
       flag will lead to the last case, where memory usage is bounded and each
       model predictions are saved for further use.
    """

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

    prediction_file = output
    output_path = u.check_dir(output)
    output = open(output, 'w', 0)
    number_of_tests = None
    if resume:
        number_of_tests = u.file_number_of_lines(test_set)
        if test_set_header:
            number_of_tests -= 1
    # Remote predictions: predictions are computed in bigml.com and stored
    # in a file named after the model in the following syntax:
    #     model_[id of the model]__predictions.csv
    # For instance,
    #     model_50c0de043b563519830001c2_predictions.csv
    if remote:
        remote_predict(models, headers, output_path, number_of_tests, resume,
                       verbosity, test_reader, exclude, fields, api,
                       prediction_file, method, tags, objective_field,
                       session_file, test_set_header, log, debug)
    # Local predictions: Predictions are computed locally using models' rules
    # with MultiModel's predict method
    else:
        message = u.dated("Creating local predictions.\n")
        u.log_message(message, log_file=session_file, console=verbosity)
        # For a small number of models, we build a MultiModel using all of
        # the given models and issue a combined prediction
        if len(models) < max_models:
            local_predict(models, headers, test_reader, exclude, fields,
                          method, objective_field, output, test_set_header)
        # For large numbers of models, we split the list of models in chunks
        # and build a MultiModel for each chunk, issue and store predictions
        # for each model and combine all of them eventually.
        else:
            local_batch_predict(models, headers, test_reader, exclude, fields,
                                resume, output_path, max_models,
                                number_of_tests, api, output,
                                verbosity, method, objective_field,
                                session_file, debug)
    output.close()
