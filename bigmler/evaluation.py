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

"""Evaluation related functions for BigMLer

"""
from __future__ import absolute_import

import os
import json
import numbers
import math

import bigml.api
import bigmler.utils as u
import bigmler.resources as r
import bigmler.checkpoint as c


def evaluate(model, dataset, name, description, fields, fields_map, output,
             api, args, resume,
             session_file=None, path=None, log=None):
    """Evaluates a model or an ensemble with the given dataset

    """
    if resume:
        message = u.dated("Evaluation not found. Resuming.\n")
        resume, evaluation = c.checkpoint(
            c.is_evaluation_created, path, debug=args.debug, message=message,
            log_file=session_file, console=args.verbosity)

    if not resume:
        evaluation_args = r.set_evaluation_args(name, description, args,
                                                fields, fields_map)
        if args.ensemble:
            model_or_ensemble = args.ensemble
        else:
            model_or_ensemble = model
        evaluation = r.create_evaluation(model_or_ensemble, dataset,
                                         evaluation_args,
                                         args, api, path, session_file,
                                         log)

    evaluation = r.get_evaluation(evaluation, api, args.verbosity,
                                  session_file)
    r.save_evaluation(evaluation, output, api)
    return resume


def cross_validate(models, dataset, number_of_evaluations, name, description,
                   fields, fields_map, api, args, resume,
                   session_file=None, path=None, log=None):
    """Cross-validates using a MONTE-CARLO variant

    """
    existing_evaluations = 0
    evaluations = []
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
        evaluation_args = r.set_evaluation_args(name, description, args,
                                                fields, fields_map)

        evaluations.extend(r.create_evaluations(models, dataset,
                                                evaluation_args,
                                                args, api, path,
                                                session_file, log,
                                                existing_evaluations))
        evaluations_files = []
        for evaluation in evaluations:
            evaluation = r.get_evaluation(evaluation, api, args.verbosity,
                                          session_file)
            model_id = evaluation['object']['model']
            file_name = "%s%s%s__evaluation" % (path, os.sep,
                                                model_id.replace("/", "_"))
            evaluations_files.append(file_name + ".json")
            r.save_evaluation(evaluation, file_name, api)
        cross_validation = average_evaluations(evaluations_files)
        file_name = "%s%scross_validation" % (path, os.sep)
        r.save_evaluation(cross_validation, file_name, api)


def standard_deviation(points, mean):
    """Computes the standard deviation

    """
    total = float(len(points))
    if total > 0:
        return math.sqrt(sum([(point - mean) ** 2 for point in points]) /
                         total)
    else:
        return float('nan')


def traverse_for_std_dev(tree):
    """Traverses the tree to find measure lists and compute standard deviation

    """
    if isinstance(tree, dict):
        keys = tree.keys()
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
        for key, value in component.items():
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
                elif isinstance(value, list) or isinstance(value, dict):
                    if not key in total:
                        total[key] = [] if isinstance(value, list) else {}
                    avg_evaluation(total[key], value,
                                   number_of_evaluations)


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
                    occurrences = float(total_class_info['occurrences'])
                    for key in total_class_info:
                        # renormalizing previous average count
                        if not (isinstance(key, tuple) or key in special_keys):
                            total_class_info[key] *= ((occurrences + 1) /
                                                      occurrences)
                if not total_class_info['present_in_test_data']:
                    total_class_info['present_in_test_data'] = flag
                occurrences = float(total_class_info['occurrences'])
                for key in class_info:
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
                break
        if not found:
            flag = class_info['present_in_test_data']
            class_info['occurrences'] = int(number_of_evaluations)
            if not flag:
                class_info['occurrences'] -= 1
            keys = class_info.keys()
            for key in keys:
                if not key in special_keys:
                    sd_key = "%s_standard_deviation" % key
                    if not key.startswith("average_"):
                        new_key = "average_%s" % key
                        class_info[new_key] = (float(class_info[key]) /
                                               class_info['occurrences'])
                        if not (sd_key, new_key) in class_info:
                            class_info[(sd_key, new_key)] = []
                        class_info[(sd_key, new_key)].append(class_info[key])
                        del class_info[key]
                    else:
                        new_key = key
                        class_info[key] = (float(class_info[key]) /
                                           class_info['occurrences'])
                        if not (sd_key, new_key) in class_info:
                            class_info[(sd_key, new_key)] = []
                        class_info[(sd_key, new_key)].append(class_info[key])
            total.append(class_info)
    return total
