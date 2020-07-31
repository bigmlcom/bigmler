# -*- coding: utf-8 -*-
#
# Copyright 2012-2020 BigML
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

"""Evaluation related functions for BigMLer

"""


import os
import json
import numbers
import math

from bigml.util import slugify

import bigmler.utils as u
import bigmler.resourcesapi.evaluations as r
import bigmler.checkpoint as c

from bigmler.resourcesapi.common import shared_changed


def evaluate(models_or_ensembles, datasets, api, args, resume,
             session_file=None, path=None, log=None,
             fields=None, dataset_fields=None,
             labels=None, all_labels=None,
             objective_field=None):
    """Evaluates a list of models or ensembles with the given dataset

    """
    output = args.predictions
    evaluation_files = []
    evaluations, resume = evaluations_process(
        models_or_ensembles, datasets, fields,
        dataset_fields, api, args, resume,
        session_file=session_file, path=path, log=log,
        labels=labels, all_labels=all_labels, objective_field=objective_field)
    if hasattr(args, 'multi_label') and args.multi_label:
        file_labels = [slugify(name) for name in
                       u.objective_field_names(models_or_ensembles, api)]
    for index, evaluation in enumerate(evaluations):
        evaluation = r.get_evaluation(evaluation, api, args.verbosity,
                                      session_file)
        if shared_changed(args.shared, evaluation):
            evaluation_args = {"shared": args.shared}
            evaluation = r.update_evaluation(evaluation, evaluation_args,
                                             args, api=api, path=path,
                                             session_file=session_file)
        file_name = output
        if hasattr(args, 'multi_label') and args.multi_label:
            suffix = file_labels[index]
            file_name += "_%s" % suffix
            evaluation_files.append("%s.json" % file_name)
        if args.test_datasets or args.dataset_off:
            suffix = evaluation['resource'].replace('evaluation/', '_')
            file_name += "_%s" % suffix
            evaluation_files.append("%s.json" % file_name)
        r.save_evaluation(evaluation, file_name, api)
    if (hasattr(args, 'multi_label') and args.multi_label) or \
            args.test_datasets or args.dataset_off:
        mean_evaluation = average_evaluations(evaluation_files)
        r.save_evaluation(mean_evaluation, output, api)
    return resume


def cross_validate(models, dataset, fields, api, args, resume,
                   session_file=None, path=None, log=None):
    """Cross-validates using a MONTE-CARLO variant

    """
    evaluations, resume = evaluations_process(
        models, [dataset],
        fields, fields, api, args, resume,
        session_file=session_file, path=path, log=log)
    if not resume:
        evaluation_files = []
        for evaluation in evaluations:
            evaluation = r.get_evaluation(evaluation, api, args.verbosity,
                                          session_file)
            model_id = evaluation['object']['model']
            file_name = "%s%s%s__evaluation" % (path, os.sep,
                                                model_id.replace("/", "_"))
            evaluation_files.append(file_name + ".json")
            r.save_evaluation(evaluation, file_name, api)
        cross_validation = average_evaluations(evaluation_files)
        file_name = "%s%scross_validation" % (path, os.sep)
        r.save_evaluation(cross_validation, file_name, api)


def evaluations_process(models_or_ensembles, datasets,
                        fields, dataset_fields, api, args, resume,
                        session_file=None, path=None, log=None, labels=None,
                        all_labels=None, objective_field=None):
    """Evaluates models or ensembles against datasets

    """

    existing_evaluations = 0
    evaluations = []
    number_of_evaluations = len(models_or_ensembles)
    if resume:
        resume, evaluations = c.checkpoint(c.are_evaluations_created, path,
                                           number_of_evaluations,
                                           debug=args.debug)
        if not resume:
            existing_evaluations = len(evaluations)
            message = u.dated("Found %s evaluations from %s. Resuming.\n" %
                              (existing_evaluations,
                               number_of_evaluations))
            number_of_evaluations -= existing_evaluations
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
    if not resume:
        if hasattr(args, 'multi_label') and args.multi_label:
            evaluation_args = r.set_label_evaluation_args(
                args, labels, all_labels,
                number_of_evaluations, fields, dataset_fields,
                objective_field)
        else:
            evaluation_args = r.set_evaluation_args(args, fields,
                                                    dataset_fields)
        evaluations.extend(r.create_evaluations(
            models_or_ensembles, datasets, evaluation_args,
            args, api, path=path, session_file=session_file,
            log=log, existing_evaluations=existing_evaluations))

    return evaluations, resume


def standard_deviation(points, mean):
    """Computes the standard deviation

    """
    total = float(len(points))
    if total > 0:
        return math.sqrt(sum([(point - mean) ** 2 for point in points]) /
                         total)
    return float('nan')


def traverse_for_std_dev(tree):
    """Traverses the tree to find measure lists and compute standard deviation

    """
    if isinstance(tree, dict):
        keys = list(tree.keys())
        for key in keys:
            if (isinstance(key, tuple) and
                    key[0].endswith('_standard_deviation')):
                tree[key[0]] = standard_deviation(tree[key], tree[key[1]])
                del tree[key]
            else:
                traverse_for_std_dev(tree[key])
    elif isinstance(tree, list):
        for subtree in tree:
            traverse_for_std_dev(subtree)


def average_evaluations(evaluation_files):
    """Reads the contents of the evaluations files and averages its measures

    """
    averaged_evaluation = {}
    number_of_evaluations = float(len(evaluation_files))
    if number_of_evaluations > 0:
        for evaluation_file in evaluation_files:
            with open(evaluation_file, 'U') as evaluation_file:
                evaluation = json.loads(evaluation_file.read())
                avg_evaluation(averaged_evaluation,
                               evaluation, number_of_evaluations)
        traverse_for_std_dev(averaged_evaluation)
    return averaged_evaluation


def avg_evaluation(total, component, number_of_evaluations):
    """Adds a new set of evaluation measures to the cumulative average

    """
    if number_of_evaluations > 0:
        for key, value in list(component.items()):
            # Handle the non-averageable values in
            # classifications' evaluation data
            if key == "class_names":
                if not key in total:
                    total[key] = []
                total[key].extend(value)
                total[key] = list(set(total[key]))
            elif key == "confusion_matrix":
                if not key in total:
                    total[key] = value
                else:
                    total[key] = add_matrices(total[key], value)
            elif key == "per_class_statistics":
                if not key in total:
                    total[key] = []
                total[key] = avg_class_statistics(total[key], value,
                                                  number_of_evaluations)
            else:
                # Average numerical values
                if isinstance(value, numbers.Number):
                    new_key = (key if key.startswith("average_")
                               else ("average_%s" % key))
                    if not new_key in total:
                        total[new_key] = 0
                    total[new_key] += value / number_of_evaluations
                    sd_key = "%s_standard_deviation" % key
                    if not (sd_key, new_key) in total:
                        total[(sd_key, new_key)] = []
                    total[(sd_key, new_key)].append(value)
                # Handle grouping keys
                elif isinstance(value, (dict, list)):
                    if not key in total:
                        total[key] = [] if isinstance(value, list) else {}
                    avg_evaluation(total[key], value,
                                   number_of_evaluations)


def add_matrices(matrix_a, matrix_b):
    """Add two n x n matrices

    """
    return [[x + y  for x, y in zip(matrix_a[i], matrix_b[i])]
            for i in range(len(matrix_a))]


def avg_class_statistics(total, component, number_of_evaluations):
    """Adds a new set of per class evaluation measures to the total average

    """
    special_keys = ['class_name', 'present_in_test_data', 'occurrences']
    remove_keys = ['ks_statistic', 'max_phi',
                   'per_threshold_confusion_matrices',
                   'roc_curve', 'pr_curve', 'negative_cdf', 'max_phi',
                   'lift_curve', 'ks_statistic', 'gain_curve']

    for class_info in component:
        for key in remove_keys:
            if key in class_info:
                del class_info[key]
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
                    occurrences = float(total_class_info['occurrences'])
                    for key in total_class_info:
                        try:
                            # renormalizing previous average count
                            if not (isinstance(key, tuple) or
                                    key in special_keys):
                                total_class_info[key] *= ((occurrences + 1) /
                                                          occurrences)
                        except (ValueError, TypeError):
                            pass
                if not total_class_info['present_in_test_data']:
                    total_class_info['present_in_test_data'] = flag
                occurrences = float(total_class_info['occurrences'])
                for key in class_info:
                    try:
                        if not (isinstance(key, tuple) or key in special_keys):
                            new_key = (key if key.startswith("average_")
                                       else ("average_%s" % key))
                            if new_key in total_class_info:
                                total_class_info[new_key] += (class_info[key] /
                                                              occurrences)
                            else:
                                total_class_info[new_key] = (class_info[key] /
                                                             occurrences)
                            sd_key = "%s_standard_deviation" % key
                            if not (sd_key, new_key) in total_class_info:
                                total_class_info[(sd_key, new_key)] = []
                            total_class_info[
                                (sd_key, new_key)].append(class_info[key])
                    except (ValueError, TypeError):
                        pass
                break
        if not found:
            flag = class_info['present_in_test_data']
            class_info['occurrences'] = int(number_of_evaluations)
            if not flag:
                class_info['occurrences'] -= 1
            keys = list(class_info.keys())
            for key in keys:
                try:
                    if not key in special_keys:
                        sd_key = "%s_standard_deviation" % key
                        if not key.startswith("average_"):
                            new_key = "average_%s" % key
                            class_info[new_key] = (float(class_info[key]) /
                                                   class_info['occurrences'])
                            if not (sd_key, new_key) in class_info:
                                class_info[(sd_key, new_key)] = []
                            class_info[(sd_key, new_key)].append( \
                                class_info[key])
                            del class_info[key]
                        else:
                            new_key = key
                            class_info[key] = (float(class_info[key]) /
                                               class_info['occurrences'])
                            if not (sd_key, new_key) in class_info:
                                class_info[(sd_key, new_key)] = []
                            class_info[(sd_key, new_key)].append( \
                                class_info[key])
                except (ValueError, TypeError):
                    pass
            total.append(class_info)
    return total
