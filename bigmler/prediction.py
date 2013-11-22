# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012, 2013 BigML
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
import ast

import bigml.api

import bigmler.utils as u
import bigmler.checkpoint as c


from bigml.model import Model
from bigml.multimodel import MultiModel, read_votes
from bigml.util import (localize, console_log, get_predictions_file_name)
from bigml.multivote import PLURALITY_CODE, MultiVote

from bigmler.test_reader import TestReader
from bigmler.resources import FIELDS_QS, ALL_FIELDS_QS
from bigmler.labels import MULTI_LABEL_LABEL

MAX_MODELS = 10
BRIEF_FORMAT = 'brief'
NORMAL_FORMAT = 'normal'
FULL_FORMAT = 'full'
AGGREGATION = -1


def use_prediction_headers(prediction_headers, output, test_reader,
                           fields, args, objective_field):
    """Uses header information from the test file in the prediction output

       If --prediction-header is set, adds a headers row to the prediction
       file.
       If --prediction-fields is used, retrieves the fields to exclude
       from the test input in the --prediction-info full format, that includes
       them all by default.

    """
    exclude = []
    objective_name = fields.fields[objective_field]['name']
    headers = [objective_name]

    if args.prediction_info == NORMAL_FORMAT:
        headers.append("confidence")
    if (args.prediction_info == FULL_FORMAT or
            args.prediction_fields is not None):
        # Try to retrieve headers from the test file
        if test_reader.has_headers():
            input_headers = test_reader.raw_headers
            if objective_name in input_headers:
                exclude.append(input_headers.index(objective_name))
        else:
            # if no headers are found in the test file we assume it has the
            # same model input_field structure removing the objective field
            input_headers = [fields[field]['name'] for field in
                             fields.fields_columns if not
                             field == objective_field]

        if args.prediction_fields is not None:
            prediction_fields = map(str.strip,
                                    args.prediction_fields.split(','))
            # Filter input_headers adding only those chosen by the user
            number_of_headers = len(input_headers)
            for index in range(0, number_of_headers):
                if not input_headers[index] in prediction_fields:
                    exclude.append(index)
        exclude = sorted(list(set(exclude)), reverse=True)
        for index in exclude:
            del input_headers[index]
        input_headers.extend(headers)
        headers = input_headers
    if prediction_headers:
        output.writerow(headers)
    return exclude


def write_prediction(prediction, output=sys.stdout,
                     prediction_info=NORMAL_FORMAT, input_data=None,
                     exclude=None):
    """Writes the final combined prediction to the required output

       The format of the output depends on the `prediction_info` value.
       There's a brief format, that writes only the predicted value,
       a normal format (default) that writes the prediction followed by its
       confidence, and a full data format that writes first the input data
       used to predict followed by the prediction.

    """
    confidence = False
    # handles (prediction, confidence) input
    if isinstance(prediction, tuple):
        prediction, confidence = prediction
    # handles "prediction" input
    if isinstance(prediction, basestring):
        prediction = prediction.encode("utf-8")
    # handles [prediction] or [prediction, confidence, ...] input
    if isinstance(prediction, list):
        prediction, confidence = ((prediction[0], None) if len(prediction) == 1
                                  else prediction)
    row = [prediction]
    if prediction_info == NORMAL_FORMAT:
        row.append(confidence)
    elif prediction_info == FULL_FORMAT:
        if input_data is None:
            input_data = []
        row = input_data
        if exclude:
            for index in exclude:
                del row[index]
        row.append(prediction)
    try:
        output.writerow(row)
    except AttributeError:
        try:
            output.write(row)
        except AttributeError:
            raise AttributeError("You should provide a writeable object")


def prediction_to_row(prediction, prediction_info=NORMAL_FORMAT):
    """Returns a csv row to store main prediction info in csv files.

    """
    prediction = prediction['object']
    prediction_class = prediction['objective_fields'][0]
    tree = prediction.get('prediction_path', prediction)
    row = [prediction['prediction'][prediction_class]]
    if not prediction_info == BRIEF_FORMAT:
        row.append(prediction.get('confidence', tree.get('confidence', 0)))
        distribution = None
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


def combine_votes(votes_files, to_prediction, to_file, method=0,
                  prediction_info=NORMAL_FORMAT, input_data_list=None,
                  exclude=None):
    """Combines the votes found in the votes' files and stores predictions.

       votes_files: should contain the list of file names
       to_prediction: is the Model method that casts prediction to numeric
                      type if needed
       to_file: is the name of the final output file.
    """
    votes = read_votes(votes_files, to_prediction)

    u.check_dir(to_file)
    output = csv.writer(open(to_file, 'w', 0),
                        lineterminator="\n")
    number_of_tests = len(votes)
    if input_data_list is None or len(input_data_list) != number_of_tests:
        input_data_list = None
    for index in range(0, number_of_tests):
        multivote = votes[index]
        input_data = (None if input_data_list is None
                      else input_data_list[index])
        write_prediction(multivote.combine(method, True), output,
                         prediction_info, input_data, exclude)


def remote_predict(models, test_reader, prediction_file, api,
                   resume=False,
                   verbosity=True, output_path=None,
                   method=PLURALITY_CODE, tags="",
                   session_file=None, log=None, debug=False,
                   prediction_info=NORMAL_FORMAT, exclude=None):
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

    raw_input_data_list = []
    for input_data in test_reader:
        raw_input_data_list.append(input_data)
    single_model = len(models) == 1
    if single_model:
        prediction_file = csv.writer(open(prediction_file, 'w', 0),
                                     lineterminator="\n")
    for model in models:
        model = bigml.api.get_model_id(model)
        predictions_file = get_predictions_file_name(model,
                                                     output_path)
        predictions_files.append(predictions_file)
        if (not resume or
            not c.checkpoint(c.are_predictions_created, predictions_file,
                             test_reader.number_of_tests(), debug=debug)[0]):
            if not message_logged:
                message = u.dated("Creating remote predictions.\n")
                u.log_message(message, log_file=session_file,
                              console=verbosity)
            message_logged = True
            predictions_file = csv.writer(open(predictions_file, 'w', 0),
                                          lineterminator="\n")

            for input_data in raw_input_data_list:
                input_data_dict = test_reader.dict(input_data)
                prediction = api.create_prediction(model, input_data_dict,
                                                   by_name=test_set_header,
                                                   wait_time=0,
                                                   args=prediction_args)
                u.check_resource_error(prediction,
                                       "Failed to create prediction: ")
                u.log_message("%s\n" % prediction['resource'], log_file=log)
                prediction_row = prediction_to_row(prediction)
                predictions_file.writerow(prediction_row)
                if single_model:
                    write_prediction(prediction_row[0:2], prediction_file,
                                     prediction_info, input_data, exclude)
    if not single_model:
        combine_votes(predictions_files,
                      Model(models[0]).to_prediction,
                      prediction_file, method,
                      prediction_info, raw_input_data_list, exclude)


def remote_predict_ensemble(ensemble_id, test_reader, prediction_file, api,
                            resume=False,
                            verbosity=True, output_path=None,
                            method=PLURALITY_CODE, tags="",
                            session_file=None, log=None, debug=False,
                            prediction_info=NORMAL_FORMAT, exclude=None):
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
                         test_reader.number_of_tests(), debug=debug)[0]):
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
            prediction = u.check_resource(prediction,
                                          api.get_prediction)
            u.check_resource_error(prediction,
                                   "Failed to create prediction: ")
            u.log_message("%s\n" % prediction['resource'], log_file=log)
            prediction_row = prediction_to_row(prediction, prediction_info)
            write_prediction(prediction_row, predictions_file,
                             prediction_info, input_data, exclude)


def local_predict(models, test_reader, output, method,
                  prediction_info=NORMAL_FORMAT, exclude=None):
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
        write_prediction(prediction, output,
                         prediction_info, input_data, exclude)


def local_batch_predict(models, test_reader, prediction_file, api,
                        max_models=MAX_MODELS,
                        resume=False, output_path=None, output=None,
                        verbosity=True, method=PLURALITY_CODE,
                        session_file=None, debug=False,
                        prediction_info=NORMAL_FORMAT,
                        labels=None, label_separator=None, ordered=True,
                        exclude=None, models_per_label=1):

    """Get local predictions form partial Multimodel, combine and save to file

    """
    def draw_progress_bar(current, total):
        """Draws a text based progress report.

        """
        pct = 100 - ((total - current) * 100) / (total)
        console_log("Predicted on %s out of %s models [%s%%]" % (
            localize(current), localize(total), pct))
    if labels is None:
        labels = []
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
    if not ordered:
        models_order = []
    single_model = models_total == 1
    query_string = FIELDS_QS if single_model else ALL_FIELDS_QS
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
                    model = u.check_resource(model, api.get_model,
                                             query_string)
                except ValueError, exception:
                    sys.exit("Failed to get model: %s. %s" % (model,
                                                              str(exception)))
            # When user selects the labels in multi-label predictions, we must
            # filter the models that will be used to predict
            if labels:
                model_objective_id = model['object']['objective_fields'][0]
                model_fields = model['object']['model']['fields']
                model_label = model_fields[model_objective_id]['label']
                if (model_label.startswith(MULTI_LABEL_LABEL) and
                        model_label[len(MULTI_LABEL_LABEL):] in labels):
                    # When the list of models comes from a --model-tag
                    # selection, the models are not retrieved in the same
                    # order they were created. We must keep track of the
                    # label they are associated with to label their
                    # predictions properly
                    if not ordered:
                        label = model_label[len(MULTI_LABEL_LABEL):]
                        label_index = labels.index(label)
                        models_order.append(label_index)
                    complete_models.append(model)
            else:
                complete_models.append(model)

        if complete_models:
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

    if label_separator is None:
        label_separator = ","
    for index in range(0, len(total_votes)):
        multivote = total_votes[index]
        input_data = raw_input_data_list[index]
        if method == AGGREGATION:
            predictions = multivote.predictions

            if ordered and models_per_label == 1:

                # as multi-labelled models are created from end to start votes
                # must be reversed to match
                predictions.reverse()
            else:
                predictions = [prediction for (order, prediction)
                               in sorted(zip(models_order, predictions))]
            if (labels is None or
                    len(labels) * models_per_label != len(predictions)):
                sys.exit("Failed to make a multi-label prediction. No"
                         " valid label info is found.")
            prediction_list = []
            confidence_list = []
            # In the following case, we must vote each label using the models
            # in the ensemble and the chosen method

            if models_per_label > 1:
                label_predictions = [predictions[i: i + models_per_label] for
                                     i in range(0, len(predictions),
                                                models_per_label)]
                predictions = []
                for label_prediction in label_predictions:
                    label_multivote = MultiVote(label_prediction)
                    prediction, confidence = label_multivote.combine(
                        method, True)
                    predictions.append({'prediction': prediction,
                                        'confidence': confidence})
            for vote_index in range(0, len(predictions)):
                if ast.literal_eval(predictions[vote_index]['prediction']):
                    prediction_list.append(labels[vote_index])
                    confidence = str(predictions[vote_index]['confidence'])
                    confidence_list.append(confidence)
            prediction = [label_separator.join(prediction_list),
                          label_separator.join(confidence_list)]
        else:
            prediction = multivote.combine(method, True)

        write_prediction(prediction, output, prediction_info, input_data,
                         exclude)


def predict(test_set, test_set_header, models, fields, output,
            objective_field, args, api=None, log=None,
            max_models=MAX_MODELS, resume=False, session_file=None,
            labels=None, models_per_label=1):
    """Computes a prediction for each entry in the `test_set`.

       Predictions can be computed remotely, locally using MultiModels built
       on all the models or locally using MultiModels on subgroups of models.
       Chosing a max_batch_models value not bigger than the number_of_models
       flag will lead to the last case, where memory usage is bounded and each
       model predictions are saved for further use.
    """

    test_reader = TestReader(test_set, test_set_header, fields,
                             objective_field,
                             test_separator=args.test_separator)
    prediction_file = output
    output_path = u.check_dir(output)
    output = csv.writer(open(output, 'w', 0), lineterminator="\n")
    # columns to exclude if input_data is added to the prediction field
    exclude = use_prediction_headers(
        args.prediction_header, output, test_reader, fields, args,
        objective_field)

    # Remote predictions: predictions are computed in bigml.com and stored
    # in a file named after the model in the following syntax:
    #     model_[id of the model]__predictions.csv
    # For instance,
    #     model_50c0de043b563519830001c2_predictions.csv
    if args.remote and not args.multi_label:
        if args.ensemble is not None:
            remote_predict_ensemble(args.ensemble, test_reader,
                                    prediction_file, api, resume,
                                    args.verbosity, output_path,
                                    args.method, args.tag, session_file, log,
                                    args.debug, args.prediction_info, exclude)
        else:
            remote_predict(models, test_reader, prediction_file, api, resume,
                           args.verbosity, output_path,
                           args.method, args.tag,
                           session_file, log, args.debug, args.prediction_info,
                           exclude)
    # Local predictions: Predictions are computed locally using models' rules
    # with MultiModel's predict method
    else:
        message = u.dated("Creating local predictions.\n")
        u.log_message(message, log_file=session_file, console=args.verbosity)
        # For a small number of models, we build a MultiModel using all of
        # the given models and issue a combined prediction
        if len(models) < max_models and not args.multi_label:
            local_predict(models, test_reader, output,
                          args.method, args.prediction_info, exclude)
        # For large numbers of models, we split the list of models in chunks
        # and build a MultiModel for each chunk, issue and store predictions
        # for each model and combine all of them eventually.
        else:
            # Local predictions: predictions are computed locally using
            # models' rules with MultiModel's predict method and combined using
            # aggregation if the objective field is a multi-labelled field
            # or one of the available combination methods: plurality,
            # confidence weighted and probability weighted
            method = AGGREGATION if args.multi_label else args.method
            # For multi-labelled models, the --models flag keeps the order
            # of the labels and the models but the --model-tag flag
            # retrieves the models with no order, so the correspondence with
            # each label must be restored.
            ordered = True

            models_per_label = args.number_of_models
            if args.multi_label and (args.model_tag is not None
                                     or models_per_label > 1):
                ordered = False
            local_batch_predict(models, test_reader, prediction_file, api,
                                max_models, resume, output_path,
                                output,
                                args.verbosity, method,
                                session_file, args.debug,
                                args.prediction_info, labels,
                                args.label_separator, ordered, exclude,
                                models_per_label)
