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
"""Prediction auxiliary functions

"""
from __future__ import absolute_import

import sys
import ast
import gc

import bigml.api

from bigml.model import Model
from bigml.multimodel import MultiModel, read_votes
from bigml.ensemble import Ensemble
from bigml.util import localize, console_log, get_predictions_file_name
from bigml.io import UnicodeWriter
from bigml.multivote import (PLURALITY_CODE, THRESHOLD_CODE, MultiVote,
                             ws_confidence)

import bigmler.utils as u
import bigmler.checkpoint as c

from bigmler.tst_reader import TstReader as TestReader
from bigmler.resources import (FIELDS_QS, ALL_FIELDS_QS, BRIEF_FORMAT,
                               NORMAL_FORMAT, FULL_FORMAT)
from bigmler.resources import create_batch_prediction
from bigmler.utils import (log_created_resources, check_resource_error, dated,
                           get_url, log_message)

MAX_MODELS = 10
BOOSTING = -1
COMBINATION = -2
AGGREGATION = -3

COMBINATION_LABEL = 'combined'
OTHER = "***** other *****"


def use_prediction_headers(prediction_headers, output, test_reader,
                           fields, args, objective_field,
                           quality="confidence"):
    """Uses header information from the test file in the prediction output

       If --prediction-header is set, adds a headers row to the prediction
       file.
       If --prediction-fields is used, retrieves the fields to exclude
       from the test input in the --prediction-info full format, that includes
       them all by default.

    """
    exclude = []

    try:
        if not objective_field in fields.fields:
            objective_field = fields.field_id(objective_field)
        objective_name = fields.field_name(objective_field)
    except ValueError, exc:
        sys.exit(exc)
    headers = [objective_name]

    if args.prediction_info in [NORMAL_FORMAT, FULL_FORMAT]:
        headers.append(quality)
    if (args.prediction_info == FULL_FORMAT or
            args.prediction_fields is not None):
        # Try to retrieve headers from the test file
        if test_reader.has_headers():
            input_headers = test_reader.raw_headers[:]
            if objective_name in input_headers:
                exclude.append(input_headers.index(objective_name))
        else:
            # if no headers are found in the test file we assume it has the
            # same model input_field structure removing the objective field
            input_headers = [fields[field]['name'] for field in
                             fields.fields_columns if not
                             field == objective_field]

        if args.prediction_fields is not None:
            prediction_fields = [field.strip() for field in
                                 args.prediction_fields.split(',')]
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
    # handles [prediction] or [prediction, confidence, ...] input
    if isinstance(prediction, list):
        prediction, confidence = ((prediction[0], None) if len(prediction) == 1
                                  else prediction)

    row = []
    # input data is added if prediction format is BRIEF (no confidence) or FULL
    if prediction_info != NORMAL_FORMAT:
        if input_data is None:
            input_data = []
        row = input_data
        if exclude:
            for index in exclude:
                del row[index]
    row.append(prediction)
    if prediction_info in [NORMAL_FORMAT, FULL_FORMAT]:
        row.append(confidence)
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
    if prediction_info != BRIEF_FORMAT:
        row.append(prediction.get('confidence', tree.get('confidence', 0)))
        distribution = None
        if 'objective_summary' in tree:
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
    with UnicodeWriter(to_file) as output:
        number_of_tests = len(votes)
        if input_data_list is None or len(input_data_list) != number_of_tests:
            input_data_list = None
        for index in range(0, number_of_tests):
            multivote = votes[index]
            input_data = (None if input_data_list is None
                          else input_data_list[index])
            write_prediction(multivote.combine(method, True), output,
                             prediction_info, input_data, exclude)


def remote_predict_models(models, test_reader, prediction_file, api, args,
                          resume=False, output_path=None,
                          session_file=None, log=None, exclude=None):
    """Retrieve predictions remotely, combine them and save predictions to file

    """
    predictions_files = []
    prediction_args = {
        "tags": args.tag
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
        prediction_file = UnicodeWriter(prediction_file).open_writer()
    for model in models:
        model = bigml.api.get_model_id(model)
        predictions_file = get_predictions_file_name(model,
                                                     output_path)
        predictions_files.append(predictions_file)
        if (not resume or
                not c.checkpoint(c.are_predictions_created, predictions_file,
                                 test_reader.number_of_tests(),
                                 debug=args.debug)[0]):
            if not message_logged:
                message = u.dated("Creating remote predictions.\n")
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)
            message_logged = True
            with UnicodeWriter(predictions_file) as predictions_file:
                for input_data in raw_input_data_list:
                    input_data_dict = test_reader.dict(input_data)
                    prediction = api.create_prediction(model, input_data_dict,
                                                       by_name=test_set_header,
                                                       wait_time=0,
                                                       args=prediction_args)
                    u.check_resource_error(prediction,
                                           "Failed to create prediction: ")
                    u.log_message("%s\n" % prediction['resource'],
                                  log_file=log)
                    prediction_row = prediction_to_row(prediction)
                    predictions_file.writerow(prediction_row)
                    if single_model:
                        write_prediction(prediction_row[0:2], prediction_file,
                                         args.prediction_info,
                                         input_data, exclude)
    if single_model:
        prediction_file.close_writer()
    else:
        combine_votes(predictions_files,
                      Model(models[0]).to_prediction,
                      prediction_file, args.method,
                      args.prediction_info, raw_input_data_list, exclude)


def remote_predict_ensemble(ensemble_id, test_reader, prediction_file, api,
                            args, resume=False, output_path=None,
                            session_file=None, log=None, exclude=None):
    """Retrieve predictions remotely and save predictions to file

    """
    prediction_args = {
        "tags": args.tag,
        "combiner": args.method
    }
    test_set_header = test_reader.has_headers()
    if output_path is None:
        output_path = u.check_dir(prediction_file)

    if (not resume or not c.checkpoint(
            c.are_predictions_created, prediction_file,
            test_reader.number_of_tests(), debug=args.debug)[0]):
        message = u.dated("Creating remote predictions.")
        u.log_message(message, log_file=session_file,
                      console=args.verbosity)

        with UnicodeWriter(prediction_file) as predictions_file:
            for input_data in test_reader:
                input_data_dict = test_reader.dict(input_data)
                prediction = api.create_prediction(ensemble_id,
                                                   input_data_dict,
                                                   by_name=test_set_header,
                                                   wait_time=0,
                                                   args=prediction_args)
                prediction = u.check_resource(prediction,
                                              api.get_prediction)
                u.check_resource_error(prediction,
                                       "Failed to create prediction: ")
                u.log_message("%s\n" % prediction['resource'], log_file=log)
                prediction_row = prediction_to_row(prediction,
                                                   args.prediction_info)
                write_prediction(prediction_row, predictions_file,
                                 args.prediction_info, input_data, exclude)


def local_predict(models, test_reader, output, args, options=None,
                  exclude=None):
    """Get local predictions and combine them to get a final prediction

    """
    single_model = len(models) == 1
    test_set_header = test_reader.has_headers()
    kwargs = {"by_name": test_set_header, "with_confidence": True,
              "missing_strategy": args.missing_strategy}
    if single_model:
        local_model = Model(models[0], api=args.retrieve_api_)
    else:
        local_model = Ensemble(models, max_models=args.max_batch_models,
                               api=args.retrieve_api_)
        kwargs.update({"method": args.method, "options": options,
                       "median": args.median})
    for input_data in test_reader:
        input_data_dict = dict(zip(test_reader.raw_headers, input_data))
        prediction = local_model.predict(
            input_data_dict, **kwargs)

        if single_model and args.median and local_model.tree.regression:
            # only single models' predictions can be based on the median value
            # predict
            prediction[0] = prediction[-1]
        write_prediction(prediction[0: 2],
                         output,
                         args.prediction_info, input_data, exclude)


def retrieve_models_split(models_split, api, query_string=FIELDS_QS,
                          labels=None, multi_label_data=None, ordered=True,
                          models_order=None):
    """Returns a list of full model structures ready to be fed to the
       MultiModel object to produce predictions. Models are also stored
       locally in the output directory when the --store flag is used.

    """
    complete_models = []
    if models_order is None:
        models_order = []
    for model in models_split:
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
        if labels and multi_label_data:
            objective_column = str(multi_label_data['objective_column'])
            labels_info = multi_label_data[
                'generated_fields'][objective_column]
            labels_columns = [label_info[1] for label_info in labels_info
                              if label_info[0] in labels]
            model_objective_id = model['object']['objective_fields'][0]
            model_fields = model['object']['model']['fields']
            model_objective = model_fields[model_objective_id]
            model_column = model_objective['column_number']
            if model_column in labels_columns:
                # When the list of models comes from a --model-tag
                # selection, the models are not retrieved in the same
                # order they were created. We must keep track of the
                # label they are associated with to label their
                # predictions properly
                if not ordered:
                    models_order.append(model_column)
                complete_models.append(model)
        else:
            complete_models.append(model)
    return complete_models, models_order


def aggregate_multivote(multivote, options, labels, models_per_label, ordered,
                        models_order, label_separator=None):
    """Aggregate the model's predictions for multi-label fields in a
       concatenated format into a final prediction

    """

    if label_separator is None:
        label_separator = ","
    predictions = multivote.predictions

    if ordered and models_per_label == 1:
        # as multi-labeled models are created from end to start votes
        # must be reversed to match
        predictions.reverse()
    else:
        predictions = [prediction for (_, prediction)
                       in sorted(zip(models_order, predictions),
                                 key=lambda x: x[0])]

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
                method=AGGREGATION, with_confidence=True, options=options)
            predictions.append({'prediction': prediction,
                                'confidence': confidence})
    for vote_index in range(0, len(predictions)):
        if ast.literal_eval(predictions[vote_index]['prediction']):
            prediction_list.append(labels[vote_index])
            confidence = str(predictions[vote_index]['confidence'])
            confidence_list.append(confidence)
    prediction = [label_separator.join(prediction_list),
                  label_separator.join(confidence_list)]
    return prediction


def combine_multivote(multivote, other_label=OTHER):
    """Combine in a global distribution the distribution of predictions
       obtained with models when each one is built on a subset of training
       data that has a subset of categories.

    """
    predictions = multivote.predictions
    global_distribution = []
    for prediction in predictions:
        prediction_category = None
        prediction_instances = 0
        for category, instances in prediction['distribution']:
            if category != other_label:
                if instances > prediction_instances:
                    prediction_category = category
                    prediction_instances = instances
        if prediction_category is not None:
            prediction_confidence = ws_confidence(
                prediction_category, prediction['distribution'])
            global_distribution.append([prediction_category,
                                        prediction_confidence])
    if global_distribution:
        prediction = sorted(global_distribution, key=lambda x: x[1],
                            reverse=True)[0]
    else:
        prediction = [None, None]
    return prediction


def local_batch_predict(models, test_reader, prediction_file, api, args,
                        resume=False, output_path=None, output=None,
                        method=PLURALITY_CODE, options=None,
                        session_file=None, labels=None, ordered=True,
                        exclude=None, models_per_label=1, other_label=OTHER,
                        multi_label_data=None):

    """Get local predictions form partial Multimodel, combine and save to file

    """

    def draw_progress_bar(current, total):
        """Draws a text based progress report.

        """
        pct = 100 - ((total - current) * 100) / (total)
        console_log("Predicted on %s out of %s models [%s%%]" % (
            localize(current), localize(total), pct), reset=True)

    max_models = args.max_batch_models
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
    # Input data is stored as a list and predictions are made for all rows
    # with each model
    raw_input_data_list = []
    for input_data in test_reader:
        raw_input_data_list.append(input_data)
    total_votes = []
    models_order = []
    models_count = 0
    single_model = models_total == 1
    query_string = FIELDS_QS if single_model else ALL_FIELDS_QS
    # processing the models in slots
    for models_split in models_splits:
        if resume:
            for model in models_split:
                pred_file = get_predictions_file_name(model,
                                                      output_path)
                c.checkpoint(c.are_predictions_created,
                             pred_file,
                             test_reader.number_of_tests(), debug=args.debug)
        # retrieving the full models allowed by --max-batch-models to be used
        # in a multimodel slot
        complete_models, models_order = retrieve_models_split(
            models_split, api, query_string=query_string, labels=labels,
            multi_label_data=multi_label_data, ordered=ordered,
            models_order=models_order)

        # predicting with the multimodel slot
        if complete_models:
            local_model = MultiModel(complete_models, api=api)
            # added to ensure garbage collection at each step of the loop
            gc.collect()
            try:
                votes = local_model.batch_predict(
                    raw_input_data_list, output_path, by_name=test_set_header,
                    reuse=True, missing_strategy=args.missing_strategy,
                    headers=test_reader.raw_headers, to_file=(not args.fast),
                    use_median=args.median)
            except ImportError:
                sys.exit("Failed to find the numpy and scipy libraries needed"
                         " to use proportional missing strategy for"
                         " regressions. Please, install them manually")

            # extending the votes for each input data with the new model-slot
            # predictions
            if not args.fast:
                votes = local_model.batch_votes(output_path)
            models_count += max_models
            if models_count > models_total:
                models_count = models_total
            if args.verbosity:
                draw_progress_bar(models_count, models_total)

            if total_votes:
                for index in range(0, len(votes)):
                    predictions = total_votes[index]
                    predictions.extend(votes[index].predictions)
            else:
                total_votes = votes

    if not single_model:
        message = u.dated("Combining predictions.\n")
        u.log_message(message, log_file=session_file, console=args.verbosity)

    # combining the votes to issue the final prediction for each input data
    for index in range(0, len(total_votes)):
        multivote = total_votes[index]
        input_data = raw_input_data_list[index]

        if single_model:
            # single model predictions need no combination
            prediction = [multivote.predictions[0]['prediction'],
                          multivote.predictions[0]['confidence']]
        elif method == AGGREGATION:
            # multi-labeled fields: predictions are concatenated
            prediction = aggregate_multivote(
                multivote, options, labels, models_per_label, ordered,
                models_order, label_separator=args.label_separator)
        elif method == COMBINATION:
            # used in --max-categories flag: each model slot contains a
            # subset of categories and the predictions for all of them
            # are combined in a global distribution to obtain the final
            # prediction
            prediction = combine_multivote(multivote, other_label=other_label)
        else:
            prediction = multivote.combine(method=method, with_confidence=True,
                                           options=options)

        write_prediction(prediction, output, args.prediction_info, input_data,
                         exclude)


def predict(models, fields, args, api=None, log=None,
            resume=False, session_file=None,
            labels=None, models_per_label=1, other_label=OTHER,
            multi_label_data=None):
    """Computes a prediction for each entry in the `test_set`.

       Predictions computed locally using MultiModels on subgroups of models.
       Chosing a max_batch_models value not bigger than the number_of_models
       flag will lead to the last case, where memory usage is bounded and each
       model predictions are saved for further use.
    """
    test_set = args.test_set
    test_set_header = args.test_header
    objective_field = args.objective_field
    output = args.predictions
    test_reader = TestReader(test_set, test_set_header, fields,
                             objective_field,
                             test_separator=args.test_separator)

    prediction_file = output
    output_path = u.check_dir(output)
    with UnicodeWriter(output) as output:
        # columns to exclude if input_data is added to the prediction field
        exclude = use_prediction_headers(
            args.prediction_header, output, test_reader, fields, args,
            objective_field)

        # Remote predictions: predictions are computed in bigml.com and stored
        # in a file named after the model in the following syntax:
        #     model_[id of the model]__predictions.csv
        # For instance,
        #     model_50c0de043b563519830001c2_predictions.csv
        # Predictions are computed individually only if no_batch flag is set
        if args.remote and args.no_batch and not args.multi_label:
            if args.ensemble is not None:
                remote_predict_ensemble(args.ensemble, test_reader,
                                        prediction_file, api, args, resume,
                                        output_path, session_file, log,
                                        exclude)
            else:
                remote_predict_models(models, test_reader, prediction_file,
                                      api, args, resume, output_path,
                                      session_file, log, exclude)
            return
        # Local predictions: Predictions are computed locally using models'
        # rules with MultiModel's predict method
        message = u.dated("Creating local predictions.\n")
        u.log_message(message, log_file=session_file, console=args.verbosity)
        options = {}
        if args.method == THRESHOLD_CODE:
            options.update(threshold=args.threshold)
            if args.threshold_class is None:
                local_model = Model(models[0])
                # default class is the first class that appears in the dataset
                # objective field summary, which might be different from the
                # objective summary of each model becaus model are built with
                # sampling
                objective_field = local_model.objective_id
                distribution = local_model.tree.fields[objective_field][ \
                    "summary"]["categories"]
                args.threshold_class = distribution[0][0]
            options.update(category=args.threshold_class)
        # For a model we build a Model and for a small number of models,
        # we build a MultiModel using all of
        # the given models and issue a combined prediction
        if (len(models) <= args.max_batch_models \
                and args.fast and \
                not args.multi_label and args.max_categories == 0 \
                and args.method != COMBINATION):
            local_predict(models, test_reader, output, args, options, exclude)
        elif args.boosting:
            local_predict(args.ensemble, test_reader, output, args,
                          options, exclude)
        # For large numbers of models, we split the list of models in chunks
        # and build a MultiModel for each chunk, issue and store predictions
        # for each model and combine all of them eventually.
        else:
            # Local predictions: predictions are computed locally using
            # models' rules with MultiModel's predict method and combined using
            # aggregation if the objective field is a multi-labelled field
            # or one of the available combination methods: plurality,
            # confidence weighted and probability weighted
            if args.multi_label:
                method = AGGREGATION
            elif args.max_categories > 0:
                method = COMBINATION
            else:
                method = args.method

            # For multi-labelled models, the --models flag keeps the order
            # of the labels and the models but the --model-tag flag
            # retrieves the models with no order, so the correspondence with
            # each label must be restored.
            ordered = True
            if args.multi_label and (args.model_tag is not None
                                     or models_per_label > 1):
                ordered = False
            local_batch_predict(models, test_reader, prediction_file, api,
                                args, resume=resume,
                                output_path=output_path,
                                output=output, method=method, options=options,
                                session_file=session_file, labels=labels,
                                ordered=ordered, exclude=exclude,
                                models_per_label=models_per_label,
                                other_label=other_label,
                                multi_label_data=multi_label_data)
    test_reader.close()


def remote_predict(model, test_dataset, batch_prediction_args, args,
                   api, resume, prediction_file=None, session_file=None,
                   path=None, log=None):
    """Computes a prediction for each entry in the `test_set`.

    Predictions are computed remotely using the batch predictions call.
    """
    if args.ensemble is not None and not args.dataset_off:
        model_or_ensemble = args.ensemble
    elif args.dataset_off:
        if hasattr(args, "ensemble_ids_") and args.ensemble_ids_:
            models = args.ensemble_ids_
        else:
            models = args.model_ids_
        test_datasets = args.test_dataset_ids
    else:
        model_or_ensemble = bigml.api.get_model_id(model)
    # if resuming, try to extract dataset form log files
    if resume:
        message = u.dated("Batch prediction not found. Resuming.\n")
        resume, batch_prediction = c.checkpoint(
            c.is_batch_prediction_created, path, debug=args.debug,
            message=message, log_file=session_file, console=args.verbosity)
    if not resume:
        if not args.dataset_off:
            batch_prediction = create_batch_prediction(
                model_or_ensemble, test_dataset, batch_prediction_args,
                args, api, session_file=session_file, path=path, log=log)
        else:
            batch_predictions = []
            for index, test_dataset_n in enumerate(test_datasets):
                batch_predictions.append(create_batch_prediction( \
                    models[index], test_dataset_n, batch_prediction_args,
                    args, api, session_file=session_file, path=path, log=log))
    if not args.no_csv and not args.dataset_off:
        file_name = api.download_batch_prediction(batch_prediction,
                                                  prediction_file)
        if file_name is None:
            sys.exit("Failed downloading CSV.")
    if args.to_dataset and not args.dataset_off:
        batch_prediction = bigml.api.check_resource(batch_prediction, api=api)
        new_dataset = bigml.api.get_dataset_id(
            batch_prediction['object']['output_dataset_resource'])
        if new_dataset is not None:
            message = u.dated("Batch prediction dataset created: %s\n"
                              % u.get_url(new_dataset))
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
            u.log_created_resources("batch_prediction_dataset",
                                    path, new_dataset, mode='a')
    elif args.to_dataset and args.dataset_off:
        predictions_datasets = []
        for batch_prediction in batch_predictions:
            batch_prediction = bigml.api.check_resource(batch_prediction,
                                                        api=api)
            new_dataset = bigml.api.get_dataset_id(
                batch_prediction['object']['output_dataset_resource'])
            if new_dataset is not None:
                predictions_datasets.append(new_dataset)
                message = u.dated("Batch prediction dataset created: %s\n"
                                  % u.get_url(new_dataset))
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)
                u.log_created_resources("batch_prediction_dataset",
                                        path, new_dataset, mode='a')
        multi_dataset = api.create_dataset(predictions_datasets)
        log_created_resources("dataset_pred", path,
                              bigml.api.get_dataset_id(multi_dataset),
                              mode='a')
        dataset_id = check_resource_error(multi_dataset,
                                          "Failed to create dataset: ")
        try:
            multi_dataset = api.check_resource(multi_dataset)
        except ValueError, exception:
            sys.exit("Failed to get a finished dataset: %s" % str(exception))
        message = dated("Predictions dataset created: %s\n" %
                        get_url(multi_dataset))
        log_message(message, log_file=session_file, console=args.verbosity)
        log_message("%s\n" % dataset_id, log_file=log)
        if not args.no_csv:
            file_name = api.download_dataset(dataset_id, prediction_file)
            if file_name is None:
                sys.exit("Failed downloading CSV.")
