# -*- coding: utf-8 -*-
#
# Copyright 2014-2015 BigML
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

"""BigMLer - delete processing dispatching

"""
from __future__ import absolute_import

import sys
import os
import datetime

import bigml.api
import bigmler.utils as u
import bigmler.processing.args as a

from bigmler.defaults import DEFAULTS_FILE
from bigmler.command import Command, StoredCommand
from bigmler.dispatcher import (SESSIONS_LOG, command_handling,
                                clear_log_files)

COMMAND_LOG = u".bigmler_delete"
DIRS_LOG = u".bigmler_delete_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
ROWS_LIMIT = 15
INDENT_IDS = 26
RESOURCES_LOG_FILES = set(['source', 'dataset', 'dataset_train',
                           'dataset_test', 'dataset_gen',  'dataset_cluster',
                           'dataset_parts', 'dataset_multi', 'models',
                           'ensembles', 'evaluations',
                           'clusters', 'batch_prediction', 'batch_centroid',
                           'anomalies', 'batch_anomaly_score', 'sample'])

def retrieve_resources(directory):
    """Searches recusively the user-given directory for resource log files
       and returns its ids.

    """
    log_ids = []
    if os.path.isdir(directory):
        for root, dirs, files in os.walk(directory):
            for resources_file in files:
                if resources_file in RESOURCES_LOG_FILES:
                    for line in open(os.path.join(root, resources_file)):
                        resource_id = bigml.api.get_resource_id(line.strip())
                        if resource_id is not None:
                            log_ids.append(resource_id)
    return list(set(log_ids))
 

def time_interval_qs(args, api):
    """Building the query string from the time interval user parameters.

    """
    query_string_list = []
    time_intervals = [(args.older_than, "created__lt=%s"),
                      (args.newer_than, "created__gt=%s")]
    for time_interval, expression in time_intervals:
        if time_interval:
            date_str = get_date(time_interval, api)
            if date_str:
                query_string_list.append(expression % date_str)
            else:
                sys.exit("The --older-than and --newer-than flags only accept "
                         "integers (number of days), dates in YYYY-MM-DD "
                         " format and resource ids."
                         " Please, double-check your input.")
    return query_string_list


def get_delete_list(args, api, query_list):
    """Building the list of resources to be deleted by adding the tag
       filtering user options to the
       previous ones for all the filtered resource types.

    """
    resource_selectors = filtered_selectors(args, api)
    delete_list = []

    if resource_selectors:
        for selector, api_call, filter_linked in resource_selectors:
            query_value = args.all_tag
            type_query_list = query_list[:]
            if args.all_tag or selector:
                if selector:
                    query_value = selector
                type_query_list.append("tags__in=%s" % query_value)
            if type_query_list and filter_linked:
                type_query_list.append(filter_linked)
            if type_query_list:
                delete_list.extend(u.list_ids(api_call,
                                              ";".join(type_query_list)))
    return delete_list


def get_date(reference, api):
    """Extract the date from a given reference in days from now, date format
       or existing resource

    """
    days = None
    date = None
    try:
        days = int(reference)
        date = datetime.datetime.now() - datetime.timedelta(days=days)
    except ValueError:
        try:
            date = datetime.datetime.strptime(reference, '%Y-%m-%d')
            date = date.strftime('%Y-%m-%dT%H:%M:%S.%f')
        except ValueError:
            try:
                resource_type = bigml.api.get_resource_type(reference)
                resource = bigml.api.check_resource(reference,
                                                    api.getters[resource_type])
                date = resource['object']['created']
            except (TypeError, KeyError):
                return None
    return date


def resources_by_type(resources_list):
    """Sorts resources by type. Datasets are shifted to the bottom of the
       list to avoid problems deleting cluster-related datasets, if possible.
       Returns aggregations by type.
    """
    type_summary = {}
    resources_list.sort()
    for resource in resources_list:
        resource_type = bigml.api.get_resource_type(resource)
        if not resource_type in type_summary:
            type_summary[resource_type] = 0
        type_summary[resource_type] += 1
    return type_summary


def filter_resource_types(delete_list, resource_types):
    """Filters the ids using the user-given resource types to ensure that
       only those resources will be deleted.

    """
    if resource_types is not None:
        delete_list = [resource for resource in delete_list if
                       bigml.api.get_resource_type(resource) in resource_types]
    return delete_list


def filtered_selectors(args, api):
    """Returns the selectors for the user-given resource types to ensure that
       only those resources will be deleted.

    """

    resource_selectors = [
        ("cluster", args.cluster_tag, api.list_clusters, None),
        ("source", args.source_tag, api.list_sources, None),
        ("dataset", args.dataset_tag, api.list_datasets,
         "cluster_status=false"),
        ("model", args.model_tag, api.list_models, "ensemble=false"),
        ("prediction", args.prediction_tag, api.list_predictions,
         None),
        ("ensemble", args.ensemble_tag, api.list_ensembles, None),
        ("evaluation", args.evaluation_tag, api.list_evaluations,
         None),
        ("batchprediction", args.batch_prediction_tag,
         api.list_batch_predictions, None),
        ("centroid", args.centroid_tag, api.list_centroids, None),
        ("batchcentroid", args.batch_centroid_tag,
         api.list_batch_centroids, None),
        ("anomaly", args.anomaly_tag, api.list_anomalies, None),
        ("anomalyscore", args.anomaly_score_tag, api.list_anomaly_scores,
         None),
        ("batchanomalyscore", args.batch_anomaly_score_tag,
         api.list_batch_anomaly_scores, None)]

    if args.all_tag is None and any([resource[1] is not None for resource in
                                     resource_selectors]):
        # choose which selectors by tag are used and keep only these
        # selected by resource_tag
        resource_selectors = [resource for resource in resource_selectors if
                              resource[1] is not None]

    # selected by resource_types (on top of the tag selectors)
    selectors = [resource[1:] for resource in resource_selectors
                 if args.resource_types_ is None or
                 resource[0] in args.resource_types_]
    return selectors


def delete_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    command = command_handling(args, COMMAND_LOG)

    # Parses command line arguments.
    command_args = a.parse_and_check(command)
    resume = command_args.resume
    if command_args.resume:
        # Keep the debug option if set
        debug = command_args.debug
        # Restore the args of the call to resume from the command log file
        stored_command = StoredCommand(args, COMMAND_LOG, DIRS_LOG)
        command = Command(None, stored_command=stored_command)
        # Logs the issued command and the resumed command
        session_file = os.path.join(stored_command.output_dir, SESSIONS_LOG)
        stored_command.log_command(session_file=session_file)
        # Parses resumed arguments.
        command_args = a.parse_and_check(command)
    else:
        if command_args.output_dir is None:
            command_args.output_dir = a.NOW
        directory = u.check_dir(os.path.join(command_args.output_dir, "tmp"))
        session_file = os.path.join(directory, SESSIONS_LOG)
        u.log_message(command.command + "\n", log_file=session_file)
        try:
            defaults_file = open(DEFAULTS_FILE, 'r')
            contents = defaults_file.read()
            defaults_file.close()
            defaults_copy = open(os.path.join(directory, DEFAULTS_FILE),
                                 'w', 0)
            defaults_copy.write(contents)
            defaults_copy.close()
        except IOError:
            pass
        u.sys_log_message(u"%s\n" % os.path.abspath(directory),
                          log_file=DIRS_LOG)

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    # Creates the corresponding api instance
    if resume and debug:
        command_args.debug = True
    api = a.get_api_instance(command_args, u.check_dir(session_file))

    delete_resources(command_args, api)
    u.log_message("_" * 80 + "\n", log_file=session_file)


def delete_resources(command_args, api):
    """Deletes the resources selected by the user given options

    """
    if command_args.output_dir is None:
        path = a.NOW
    else:
        path = command_args.output_dir
    session_file = os.path.join(path, SESSIONS_LOG)
    message = u.dated("Retrieving objects to delete.\n")
    u.log_message(message, log_file=session_file,
                  console=command_args.verbosity)
    # Parses resource types to filter
    if command_args.resource_types is not None:
        resource_types = [resource_type.strip() for resource_type in
                          command_args.resource_types.split(',')]
        command_args.resource_types_ = resource_types
    else:
        command_args.resource_types_ = None

    delete_list = []
    # by ids
    if command_args.delete_list:
        delete_list = [resource_id.strip() for resource_id in
                       command_args.delete_list.split(',')]
    # in file
    if command_args.delete_file:
        if not os.path.exists(command_args.delete_file):
            sys.exit("File %s not found" % command_args.delete_file)
        with open(command_args.delete_file, "r") as delete_file:
            resource_id = bigml.api.get_resource_id(
                delete_file.readline().strip())
            if resource_id:
                delete_list.append(resource_id)
    # from directory
    if command_args.from_dir:
        delete_list.extend(retrieve_resources(command_args.from_dir))

    # filter resource_types if any
    delete_list = filter_resource_types(delete_list,
                                        command_args.resource_types_)

    # by time interval and tag (plus filtered resource_types)
    time_qs_list = time_interval_qs(command_args, api)
    delete_list.extend(get_delete_list(command_args, api, time_qs_list))

    types_summary = resources_by_type(delete_list)
    message = u.dated("Deleting %s objects.\n" % len(delete_list))
    u.log_message(message, log_file=session_file,
                  console=command_args.verbosity)
    for resource_type, instances in types_summary.items():
        message = "%s%ss: %s\n" % (" " * INDENT_IDS, resource_type,
                                   instances)
        u.log_message(message, log_file=session_file,
                      console=command_args.verbosity)
    if len(delete_list) > ROWS_LIMIT:
        pre_indent = INDENT_IDS - 4
        message = ("\n%s%s\n" % ((" " * pre_indent),
                                 ("Showing only the first %s resources.\n%s"
                                  "See details in bigmler_sessions"
                                  " file.\n") % (ROWS_LIMIT,
                                                 " " * pre_indent)))
        u.log_message(message, log_file=None,
                      console=command_args.verbosity)
    # Partial console message. Limited number of rows
    segment = delete_list[0: ROWS_LIMIT]
    message = ("\n%s" % (" " * INDENT_IDS)).join(segment)
    message = ("%s" % (" " * INDENT_IDS)) + message + "\n"
    u.log_message(message, log_file=None,
                  console=command_args.verbosity)
    # Complete message in session file
    message = ("\n%s" % (" " * INDENT_IDS)).join(delete_list)
    message = ("%s" % (" " * INDENT_IDS)) + message + "\n"
    u.log_message(message, log_file=session_file)
    if not command_args.dry_run:
        u.delete(api, delete_list)
    u.print_generated_files(path, log_file=session_file,
                            verbosity=command_args.verbosity)
