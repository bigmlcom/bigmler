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

import bigml.api

import bigmler.utils as u
import bigmler.checkpoint as c


from bigml.model import Model
from bigml.multimodel import MultiModel
from bigml.util import (localize, console_log, get_csv_delimiter,
                        get_predictions_file_name)
from bigml.multivote import PLURALITY_CODE

from bigmler.resources import FIELDS_QS

MAX_MODELS = 10


def remote_predict(models, test_reader, prediction_file, api,
                   resume=False,
                   verbosity=True, output_path=None,
                   method=PLURALITY_CODE, tags="",
                   session_file=None, log=None, debug=False,
                   prediction_info=None):
    """Retrieve predictions remotely, combine them and save predictions to file

    """

    predictions_files = []
    prediction_args = {
        "tags": tags
    }
    test_set_header = test_reader.has_headers()
    if output_path is None:
        output_path = u.check_dir(prediction_file)
    message_logged = False
    for model in models:
        model = bigml.api.get_model_id(model)
        predictions_file = get_predictions_file_name(model,
                                                     output_path)
        predictions_files.append(predictions_file)
        if (not resume or
            not c.checkpoint(c.are_predictions_created, predictions_file,
                             test_reader.number_of_tests(), debug=debug)):
            if not message_logged:
                message = u.dated("Creating remote predictions.")
                u.log_message(message, log_file=session_file,
                              console=verbosity)
            message_logged = True

            predictions_file = csv.writer(open(predictions_file, 'w', 0),
                                          lineterminator="\n")
            raw_input_data_list = []
            for input_data in test_reader:
                raw_input_data_list.append(input_data)
                input_data_dict = test_reader.dict(input_data)
                prediction = api.create_prediction(model, input_data_dict,
                                                   by_name=test_set_header,
                                                   wait_time=0,
                                                   args=prediction_args)
                u.check_resource_error(prediction,
                                       "Failed to create prediction: ")
                u.log_message("%s\n" % prediction['resource'], log_file=log)
                prediction_row = u.prediction_to_row(prediction)
                predictions_file.writerow(prediction_row)
    u.combine_votes(predictions_files,
                    Model(models[0]).to_prediction,
                    prediction_file, method,
                    prediction_info, raw_input_data_list)


def remote_predict_ensemble(ensemble_id, test_reader, prediction_file, api,
                            resume=False,
                            verbosity=True, output_path=None,
                            method=PLURALITY_CODE, tags="",
                            session_file=None, log=None, debug=False,
                            prediction_info=None):
    """Retrieve predictions remotely and save predictions to file

    """

    prediction_args = {
        "tags": tags,
        "combiner": method
    }
    test_set_header = test_reader.has_headers()
    if output_path is None:
        output_path = u.check_dir(prediction_file)

    if (not resume or
        not c.checkpoint(c.are_predictions_created, prediction_file,
                         test_reader.number_of_tests(), debug=debug)):
        message = u.dated("Creating remote predictions.")
        u.log_message(message, log_file=session_file,
                      console=verbosity)

        predictions_file = csv.writer(open(prediction_file, 'w', 0),
                                      lineterminator="\n")
        for input_data in test_reader:
            input_data_dict = test_reader.dict(input_data)
            prediction = api.create_prediction(ensemble_id, input_data_dict,
                                               by_name=test_set_header,
                                               wait_time=0,
                                               args=prediction_args)
            prediction = bigml.api.check_resource(prediction,
                                                  api.get_prediction)
            u.check_resource_error(prediction,
                                   "Failed to create prediction: ")
            u.log_message("%s\n" % prediction['resource'], log_file=log)
            prediction_row = u.prediction_to_row(prediction, prediction_info)
            if prediction_info == u.FULL_FORMAT:
                input_data.append(prediction_row[0])
                prediction_row = input_data
            predictions_file.writerow(prediction_row)


def local_predict(models, test_reader, output, method, prediction_info=None):
    """Get local predictions and combine them to get a final prediction

    """
    local_model = MultiModel(models)
    test_set_header = test_reader.has_headers()
    for input_data in test_reader:
        input_data_dict = test_reader.dict(input_data)
        prediction = local_model.predict(input_data_dict,
                                         by_name=test_set_header,
                                         method=method,
                                         with_confidence=True)
        u.write_prediction(prediction, output,
                           prediction_info, input_data)


def local_batch_predict(models, test_reader, prediction_file, api,
                        max_models=MAX_MODELS,
                        resume=False, output_path=None, output=None,
                        verbosity=True, method=PLURALITY_CODE,
                        session_file=None, debug=False, prediction_info=None):
    """Get local predictions form partial Multimodel, combine and save to file

    """
    def draw_progress_bar(current, total):
        """Draws a text based progress report.

        """
        pct = 100 - ((total - current) * 100) / (total)
        console_log("Predicted on %s out of %s models [%s%%]" % (
            localize(current), localize(total), pct))

    test_set_header = test_reader.has_headers()
    if output_path is None:
        output_path = u.check_dir(prediction_file)
    if output is None:
        try:
            output = open(prediction_file, 'w', 0)
        except IOError:
            raise IOError("Failed to write in %s" % prediction_file)
    models_total = len(models)
    models_splits = [models[index:(index + max_models)] for index
                     in range(0, models_total, max_models)]

    input_data_list = []
    raw_input_data_list = []
    for input_data in test_reader:
        raw_input_data_list.append(input_data)
        input_data_list.append(test_reader.dict(input_data))
    total_votes = []
    models_count = 0
    for models_split in models_splits:
        if resume:
            for model in models_split:
                pred_file = get_predictions_file_name(model,
                                                      output_path)
                c.checkpoint(c.are_predictions_created,
                             pred_file,
                             test_reader.number_of_tests(), debug=debug)
        complete_models = []
        for index in range(len(models_split)):
            model = models_split[index]
            if (isinstance(model, basestring) or
                    bigml.api.get_status(model)['code'] != bigml.api.FINISHED):
                try:
                    model = bigml.api.check_resource(model, api.get_model,
                                                     FIELDS_QS)
                except ValueError, exception:
                    sys.exit("Failed to get model: %s" % (model,
                                                          str(exception)))
            complete_models.append(model)

        local_model = MultiModel(complete_models)
        local_model.batch_predict(input_data_list,
                                  output_path,
                                  by_name=test_set_header,
                                  reuse=True)
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
    for index in range(0, len(total_votes)):
        multivote = total_votes[index]
        input_data = raw_input_data_list[index]
        u.write_prediction(multivote.combine(method, True), output,
                           prediction_info, input_data)


def predict(test_set, test_set_header, models, fields, output,
            objective_field, remote=False, api=None, log=None,
            max_models=MAX_MODELS, method=0, resume=False,
            tags=None, verbosity=1, session_file=None, debug=False,
            ensemble_id=None, prediction_info=None):
    """Computes a prediction for each entry in the `test_set`.

       Predictions can be computed remotely, locally using MultiModels built
       on all the models or locally using MultiModels on subgroups of models.
       Chosing a max_batch_models value not bigger than the number_of_models
       flag will lead to the last case, where memory usage is bounded and each
       model predictions are saved for further use.
    """

    test_reader = TestReader(test_set, test_set_header, fields,
                             objective_field)
    prediction_file = output
    output_path = u.check_dir(output)
    output = csv.writer(open(output, 'w', 0), lineterminator="\n")
    # Remote predictions: predictions are computed in bigml.com and stored
    # in a file named after the model in the following syntax:
    #     model_[id of the model]__predictions.csv
    # For instance,
    #     model_50c0de043b563519830001c2_predictions.csv
    if remote:
        if ensemble_id is not None:
            remote_predict_ensemble(ensemble_id, test_reader, prediction_file,
                                    api, resume, verbosity, output_path,
                                    method, tags, session_file, log, debug,
                                    prediction_info)
        else:
            remote_predict(models, test_reader, prediction_file, api, resume,
                           verbosity, output_path,
                           method, tags,
                           session_file, log, debug, prediction_info)
    # Local predictions: Predictions are computed locally using models' rules
    # with MultiModel's predict method
    else:
        message = u.dated("Creating local predictions.\n")
        u.log_message(message, log_file=session_file, console=verbosity)
        # For a small number of models, we build a MultiModel using all of
        # the given models and issue a combined prediction
        if len(models) < max_models:
            local_predict(models, test_reader, output, method, prediction_info)
        # For large numbers of models, we split the list of models in chunks
        # and build a MultiModel for each chunk, issue and store predictions
        # for each model and combine all of them eventually.
        else:
            local_batch_predict(models, test_reader, prediction_file, api,
                                max_models, resume, output_path, output,
                                verbosity, method, session_file, debug,
                                prediction_info)


class TestReader(object):
    """Retrieves csv info and builds a input data dict

    """
    def __init__(self, test_set, test_set_header, fields, objective_field):
        """Builds a generator from a csv file and the fields' model structure

        """
        self.test_set = test_set
        self.test_set_header = test_set_header
        self.fields = fields
        self.objective_field = objective_field
        try:
            self.test_reader = csv.reader(open(test_set, "U"),
                                          delimiter=get_csv_delimiter(),
                                          lineterminator="\n")
        except IOError:
            sys.exit("Error: cannot read test %s" % test_set)

        self.headers = None
        self.exclude = []
        if test_set_header:
            self.headers = self.test_reader.next()
            # validate headers against model fields excluding objective_field,
            # that may be present or not
            objective_field = fields.field_column_number(objective_field)
            fields_names = [fields.fields[fields.field_id(i)]
                            ['name'] for i in
                            sorted(fields.fields_by_column_number.keys())
                            if i != objective_field]
            self.headers = [unicode(header, "utf-8")
                            for header in self.headers]
            self.exclude = [i for i in range(len(self.headers))
                            if not self.headers[i] in fields_names]

            self.exclude.reverse()
            if self.exclude:
                if len(self.headers) > len(self.exclude):
                    print (u"WARNING: predictions will be processed but some "
                           u"data might not be used. The used fields will be:"
                           u"\n\n%s"
                           u"\n\nwhile the headers found in the test file are:"
                           u"\n\n%s" %
                           (",".join(fields_names),
                            ",".join(self.headers))).encode("utf-8")
                    for index in self.exclude:
                        del self.headers[index]
                else:
                    raise Exception((u"No test field matches the model fields."
                                     u"\nThe expected fields are:\n\n%s\n\n"
                                     u"while "
                                     u"the headers found in the test file are:"
                                     u"\n\n%s\n\n"
                                     u"Use --no-test-header flag if first li"
                                     u"ne should not be interpreted as"
                                     u" headers." %
                                     (",".join(fields_names),
                                      ",".join(self.headers))).encode("utf-8"))

    def __iter__(self):
        """Iterator method

        """
        return self

    def next(self):
        """Returns the next row

        """
        return self.test_reader.next()

    def dict(self, row):
        """Returns the row in a dict format according to the given headers

        """
        for index in self.exclude:
            del row[index]
        return self.fields.pair(row, self.headers, self.objective_field)

    def number_of_tests(self):
        """Returns the number of tests in the test file

        """
        tests = c.file_number_of_lines(self.test_set)
        if self.test_set_header:
            tests -= 1
        return tests

    def has_headers(self):
        """Returns wether the test set file has a headers row

        """
        return self.test_set_header
