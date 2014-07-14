# -*- coding: utf-8 -*-
#
# Copyright 2014 BigML
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
import re
import datetime

import bigml.api
import bigmler.utils as u
import bigmler.resources as r
import bigmler.processing.args as a

from bigmler.defaults import DEFAULTS_FILE
from bigmler.command import Command, StoredCommand
from bigmler.dispatcher import (SESSIONS_LOG, command_handling,
                                clear_log_files)

COMMAND_LOG = ".bigmler_delete"
DIRS_LOG = ".bigmler_delete_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
ROWS_LIMIT = 15
INDENT_IDS = 26


def resources_by_type(resources_list):
    """Sorts resources by type. Datasets are shifted to the bottom of the
       list to avoid problems deleting cluster-related datasets, if possible.
       Returns aggregations by type.
    """
    type_summary = {}
    resources_list.sort()
    for index, resource in enumerate(resources_list):
        resource_type = bigml.api.get_resource_type(resource)
        if not resource_type in type_summary:
            type_summary[resource_type] = 0
        type_summary[resource_type] += 1
    return type_summary


def filter_resource_types(delete_list, resource_types):
    """Filters the ids using the user-given resource types. Only those found
       will be deleted.

    """
    if resource_types is not None:
        delete_list = [resource for resource in delete_list if
                       bigml.api.get_resource_type(resource) in resource_types]
    return delete_list


def filter_selectors(resource_selectors, resource_types):
    """Filters the selectors using the user-given resource types. Only those
       will be deleted.

    """
    if resource_types is not None:
       resource_selectors = [resource for resource in resource_selectors if
                             resource[0] in resource_types]
    return resource_selectors

def delete_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

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
        with open(DIRS_LOG, "a", 0) as directory_log:
            directory_log.write("%s\n" % os.path.abspath(directory))

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
        resource_types = map(lambda x: x.strip(),
                             command_args.resource_types.split(
                             ','))
        command_args.resource_types_ = resource_types
    else:
        command_args.resource_types_ = None

    delete_list = []
    if command_args.delete_list:
        delete_list = map(str.strip,
                          command_args.delete_list.split(','))
    if command_args.delete_file:
        if not os.path.exists(command_args.delete_file):
            sys.exit("File %s not found" % command_args.delete_file)
        delete_list.extend([line for line
                            in open(command_args.delete_file, "r")])

    delete_list = filter_resource_types(delete_list,
                                        command_args.resource_types_)

    resource_selectors = [
        ("cluster", command_args.cluster_tag, api.list_clusters, None),
        ("source", command_args.source_tag, api.list_sources, None),
        ("dataset", command_args.dataset_tag, api.list_datasets,
         ";cluster_status=false"),
        ("model", command_args.model_tag, api.list_models, ";ensemble=false"),
        ("prediction", command_args.prediction_tag, api.list_predictions,
         None),
        ("ensemble", command_args.ensemble_tag, api.list_ensembles, None),
        ("evaluation", command_args.evaluation_tag, api.list_evaluations,
         None),
        ("batchprediction", command_args.batch_prediction_tag,
         api.list_batch_predictions, None),
        ("centroid", command_args.centroid_tag, api.list_centroids, None),
        ("batchcentroid", command_args.batch_centroid_tag,
         api.list_batch_centroids, None)]

    resource_selectors = filter_selectors(resource_selectors,
                                          command_args.resource_types_)

    query_string = None

    if command_args.older_than:
        date_str = get_date(command_args.older_than, api)
        if date_str:
            query_string = "created__lt=%s" % date_str
        else:
            sys.exit("The --older-than and --newer-than flags only accept "
                     "integers (number of days), dates in YYYY-MM-DD format "
                     " and resource ids. Please, double-check your input.")

    if command_args.newer_than:
        date_str = get_date(command_args.newer_than, api)
        if date_str:
            if query_string is None:
                query_string = ""
            else:
                query_string += ";"
            query_string += "created__gt=%s" % date_str
        else:
            sys.exit("The --older-than and --newer-than flags only accept "
                     "integers (number of days), dates in YYYY-MM-DD format "
                     " and resource ids. Please, double-check your input.")

    if (any([selector[1] is not None for selector in resource_selectors]) or
            command_args.all_tag):
        if query_string is None:
            query_string = ""
        else:
            query_string += ";"
        query_value = command_args.all_tag
        for label, selector, api_call, filter_linked in resource_selectors:
            combined_query = query_string
            if not query_value and selector:
                query_value = selector
            if command_args.all_tag or selector:
                combined_query += "tags__in=%s" % query_value
                if filter_linked:
                    combined_query += filter_linked
                delete_list.extend(u.list_ids(api_call, combined_query))
    else:
        if query_string:
            for label, selector, api_call, filter_linked in resource_selectors:
                combined_query = query_string
                if filter_linked:
                    combined_query += filter_linked
                delete_list.extend(u.list_ids(api_call, combined_query))

    types_summary = resources_by_type(delete_list)
    message = u.dated("Deleting %s objects.\n" % len(delete_list))
    u.log_message(message, log_file=session_file,
                  console=command_args.verbosity)
    for resource_type, instances in types_summary.items():
        message = "                          %ss: %s\n" % (resource_type,
                                                           instances)
        u.log_message(message, log_file=session_file,
                      console=command_args.verbosity)
    if len(delete_list) > ROWS_LIMIT:
        pre_indent = INDENT_IDS - 4
        message = ("\n%s%s\n" % ((" " * pre_indent),
                                 ("Showing only the first %s resources.\n%s"
                                  "See details in bigmler_sessions"
                                  " file.\n") %
                                  (ROWS_LIMIT, " " * pre_indent)))
        segment = delete_list[0: ROWS_LIMIT]
        message += ("\n%s" % (" " * INDENT_IDS)).join(segment)
        message += ("%s" % (" " * INDENT_IDS)) + message + "\n"
        u.log_message(message, log_file=None,
                      console=command_args.verbosity)
    message = ("\n%s" % (" " * INDENT_IDS)).join(delete_list)
    message = ("%s" % (" " * INDENT_IDS)) + message + "\n"
    u.log_message(message, log_file=session_file)
    u.delete(api, delete_list)
    if sys.platform == "win32" and sys.stdout.isatty():
        message = (u"\nGenerated files:\n\n" +
                   unicode(u.print_tree(path, " "), "utf-8") + u"\n")
    else:
        message = "\nGenerated files:\n\n" + u.print_tree(path, " ") + "\n"
    u.log_message(message, log_file=session_file,
                  console=command_args.verbosity)
