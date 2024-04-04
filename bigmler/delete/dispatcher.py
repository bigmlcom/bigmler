# -*- coding: utf-8 -*-
#
# Copyright 2014-2024 BigML
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


import sys
import os
import datetime
import shutil

import bigml.api

from bigml.api import get_resource_type
from bigml.constants import RENAMED_RESOURCES

import bigmler.utils as u
import bigmler.processing.args as a

from bigmler.defaults import DEFAULTS_FILE
from bigmler.command import get_stored_command, command_handling
from bigmler.dispatcher import SESSIONS_LOG, clear_log_files

COMMAND_LOG = ".bigmler_delete"
DIRS_LOG = ".bigmler_delete_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
ROWS_LIMIT = 15
INDENT_IDS = 26
RESOURCES_LOG_FILES = set(['project', 'source', 'dataset', 'dataset_train',
                           'dataset_test', 'dataset_gen', 'dataset_cluster',
                           'dataset_parts', 'dataset_multi', 'models',
                           'ensembles', 'evaluations', 'optimls',
                           'clusters', 'batch_prediction', 'batch_centroid',
                           'anomalies', 'batch_anomaly_score', 'sample',
                           'associations', 'time_series', "deepnets",
                           'fusions', 'pcas', 'batch_projection',
                           'linear_regressions', 'logistic_regressions',
                           'scripts', 'library', 'execution',
                           'external_connector'])
STATUS_CODES = {
    "finished": bigml.api.FINISHED,
    "faulty": bigml.api.FAULTY,
    "waiting": bigml.api.WAITING,
    "queued": bigml.api.QUEUED,
    "started": bigml.api.STARTED,
    "in progress": bigml.api.IN_PROGRESS,
    "summarized": bigml.api.SUMMARIZED,
    "uploading": bigml.api.UPLOADING,
    "unknown": bigml.api.UNKNOWN,
    "runnable": bigml.api.RUNNABLE
}

GROUP_RESOURCES = ["project", "execution"]
SYNCHRONOUS_RESOURCES = ["project", "prediction", "centroid", "anomalyscore",
    "topicdistribution", "associationset", "forecast", "projection"]
TRASH_BIN = "Trash bin"

ALL_RESOURCE_TYPES = [
    "project", "execution", "script", "library", "optiml", "fusion",
    "batchprediction", "batchcentroid", "batchanomalyscore",
    "batchtopicdistribution", "batchprojection", "prediction", "anomalyscore",
    "associationset", "centroid", "forecast", "projection",
    "topicdistribution", "cluster", "ensemble", "model", "anomaly",
    "sample", "association", "logisticregression", "topicmodel",
    "timeseries", "deepnet", "pca", "linearregression", "externalconnector",
    "evaluation", "dataset", "source"]

SELECTOR_FILTERS = {
    "fusion": "fusion_status=false",
    "model": "ensemble=false;optiml_status=false;fusion_status=false",
    "ensemble": "optiml_status=false;fusion_status=false",
    "logisticregression": "optiml_status=false;fusion_status=false",
    "linearregression": "optiml_status=false;fusion_status=false",
    "deepnet": "optiml_status=false;fusion_status=false",
    "dataset": "cluster_status=false"}


def to_new_project(api, project_name, resource_ids):
    """Creates a new project and updates the resources to link them to the
    project. If the resources are projects, then prepends the name to the
    original name.
    """
    project_ids = []
    non_project_ids = []
    for resource_id in resource_ids:
        if resource_id.startswith("project/"):
            project_ids.append(resource_id)
        else:
            non_project_ids.append(resource_id)
    for project_id in project_ids:
        project = api.get_project(project_id)
        api.update_project(project_id, {"name": "%s: %s" % (project_name,
            project.get("object", {}).get("name"))})
    new_project_id = None
    if non_project_ids:
        new_project = api.create_project({"name": project_name})
        new_project_id = new_project["resource"]
    for resource_id in non_project_ids:
        resource_type = get_resource_type(resource_id)
        api.updaters[resource_type](resource_id, {"project": new_project_id})


def retrieve_resources(directory):
    """Searches recusively the user-given directory for resource log files
       and returns its ids.

    """
    log_ids = []
    if os.path.isdir(directory):
        for root, _, files in os.walk(directory):
            for resources_file in files:
                if resources_file in RESOURCES_LOG_FILES:
                    with open(os.path.join(root, resources_file)) as reader:
                        for line in reader:
                            resource_id = bigml.api.get_resource_id(
                                line.strip())
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


def filter_qs(args):
    """Building the query string from the filter.

    """
    query_string_list = []
    if args.filter:
        query_string_list.append(args.filter)
    return query_string_list


def get_delete_list(args, api, query_list):
    """Building the list of resources to be deleted by adding the tag
       filtering user options to the
       previous ones for all the filtered resource types.

    """
    resource_selectors = filtered_selectors(args, api)
    delete_list = []

    if resource_selectors:
        for res_type, selector, api_call, filter_linked in resource_selectors:
            query_value = args.all_tag
            type_query_list = query_list[:]
            if args.all_tag or selector:
                if selector:
                    query_value = selector
                type_query_list.append("tags__in=%s" % query_value)
            if type_query_list and filter_linked:
                type_query_list.append(filter_linked)
            if type_query_list:
                status_code = STATUS_CODES[args.status]
                if res_type in SYNCHRONOUS_RESOURCES:
                    status_code = None
                delete_list.extend(u.list_ids(api_call,
                                              "&".join(type_query_list),
                                              status_code=status_code))
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
    """Sorts resources by type and summarizes their number """
    type_summary = {}
    sorted_resources = resources_list[:]
    sorted_resources.sort()
    for resource in resources_list:
        resource_type = bigml.api.get_resource_type(resource)
        if not resource_type in type_summary:
            type_summary[resource_type] = 0
        type_summary[resource_type] += 1
    return type_summary, sorted_resources


def filter_resource_types(delete_list, resource_types):
    """Filters the ids using the user-given resource types to ensure that
       only those resources will be deleted.

    """
    if resource_types is not None and resource_types:
        delete_list = [resource for resource in delete_list if
                       bigml.api.get_resource_type(resource) in resource_types]
    return delete_list


def filtered_selectors(args, api):
    """Returns the selectors for the user-given resource types to ensure that
       only those resources will be deleted.

    """

    resource_selectors = [
        (resource_type, getattr(args, "%s_tag" % RENAMED_RESOURCES.get(
         resource_type, resource_type)),
         api.listers[resource_type], SELECTOR_FILTERS.get(resource_type)) for
        resource_type in ALL_RESOURCE_TYPES]

    if args.all_tag is None and any(resource[1] is not None for resource in
                                     resource_selectors):
        # choose which selectors by tag are used and keep only these
        # selected by resource_tag
        resource_selectors = [resource for resource in resource_selectors if
                              resource[1] is not None]

    # selected by resource_types (on top of the tag selectors)
    selectors = [resource for resource in resource_selectors
                 if args.resource_types_ is None or
                 resource[0] in args.resource_types_]
    return selectors


#pylint: disable=locally-disabled,dangerous-default-value
def delete_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    command = command_handling(args, COMMAND_LOG)

    # Parses command line arguments.
    command_args = a.parse_and_check(command)
    if command_args.resume:
        command_args, session_file, _ = get_stored_command(
            args, command_args.debug, command_log=COMMAND_LOG,
            dirs_log=DIRS_LOG, sessions_log=SESSIONS_LOG)
    else:
        if command_args.output_dir is None:
            command_args.output_dir = a.OUTPUT_DIR
        directory = u.check_dir(os.path.join(command_args.output_dir, "tmp"))
        session_file = os.path.join(directory, SESSIONS_LOG)
        u.log_message(command.command + "\n", log_file=session_file)
        try:
            shutil.copy(DEFAULTS_FILE, os.path.join(directory, DEFAULTS_FILE))
        except IOError:
            pass
        u.sys_log_message("%s\n" % os.path.abspath(directory),
                          log_file=DIRS_LOG)

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    # Creates the corresponding api instance
    api = a.get_api_instance(command_args, u.check_dir(session_file))

    delete_resources(command_args, api)
    u.log_message("_" * 80 + "\n", log_file=session_file)


def delete_resources(command_args, api, deleted_list=None, step=0):
    """Deletes the resources selected by the user given options

    """
    if deleted_list is None:
        deleted_list = []

    # deletion will be done in 3 steps. First projects and executions, then
    # composed resources (ensembles, etc.) and finally the rest of resources
    if step == 0:
        types = GROUP_RESOURCES
    elif step == 1:
        types = u.COMPOSED_RESOURCES
    else:
        types = [res_type for res_type in ALL_RESOURCE_TYPES if
                 res_type not in GROUP_RESOURCES and
                 res_type not in u.COMPOSED_RESOURCES]
    if command_args.output_dir is None:
        path = a.OUTPUT_DIR
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
        if command_args.exclude_types:
            # if that flag is set, the given resource_types are excluded
            command_args.resource_types_ = [
                resource_type for resource_type in types
                if command_args.resource_types is None or
                resource_type not in resource_types]
        else:
            command_args.resource_types_ = [
                res_type for res_type in resource_types if res_type in types]
    else:
        command_args.resource_types_ = types

    if command_args.resource_types_:
        delete_list = []
        # by ids
        if command_args.delete_list:
            message = u.dated("Resources selected from a user-given list of ids."
                              "\n\n")
            u.log_message(message, log_file=session_file,
                          console=command_args.verbosity)
            delete_list = [resource_id.strip() for resource_id in
                           command_args.delete_list.split(',')]
        # in file
        if command_args.delete_file:
            message = u.dated("Resources selected from user-given file.\n\n")
            u.log_message(message, log_file=session_file,
                          console=command_args.verbosity)
            if not os.path.exists(command_args.delete_file):
                sys.exit("File %s not found" % command_args.delete_file)
            with open(command_args.delete_file, "r") as delete_file:
                resource_id = bigml.api.get_resource_id(
                    delete_file.readline().strip())
                if resource_id:
                    delete_list.append(resource_id)
        # from directory
        if command_args.from_dir:
            message = u.dated("Resources extracted from directory logs.\n\n")
            u.log_message(message, log_file=session_file,
                          console=command_args.verbosity)

            delete_list.extend(retrieve_resources(command_args.from_dir))

        # by time interval and tag (plus filtered resource_types)
        qs_list = time_interval_qs(command_args, api)

        # by filter expression (plus filtered resource_types)
        filter_qs_list = filter_qs(command_args)

        qs_list.extend(filter_qs_list)
        if qs_list:
            message = u.dated("Resources filtered by expression:\n    %s\n\n" %
                "&".join(qs_list))
            u.log_message(message, log_file=session_file,
                          console=command_args.verbosity)

        delete_list.extend(get_delete_list(command_args, api, qs_list))

        # filter resource_types if any
        delete_list = filter_resource_types(delete_list,
                                            command_args.resource_types_)

        delete_list = [resource_id for resource_id in delete_list \
            if resource_id not in deleted_list]


        # if there are projects or executions, delete them first
        bulk_deletion = not command_args.bin and not command_args.dry_run and \
            any(resource_id.startswith("project/") or \
            (not command_args.execution_only and \
             resource_id.startswith("execution/")) for resource_id in delete_list)
        aprox = "*" if bulk_deletion else ""
        # ensure uniqueness
        delete_list = list(set(delete_list))
        types_summary, delete_list = resources_by_type( \
            delete_list)

        if types_summary.keys():
            message = ("Found resources with the following types: %s.\n"
                       % ",".join(types_summary.keys()))
            u.log_message(message, log_file=session_file,
                          console=command_args.verbosity)

            action_text = "Moving to Trash bin project" if command_args.bin else \
                "Deleting"
            action_text = "Dry-run for deleting" if command_args.dry_run else \
                action_text
            message = u.dated("%s %s objects%s.\n" % (action_text,
                len(delete_list), aprox))
            u.log_message(message, log_file=session_file,
                          console=command_args.verbosity)
            for resource_type, instances in list(types_summary.items()):
                message = "%s%ss: %s\n" % (" " * INDENT_IDS, resource_type,
                                           instances)
                u.log_message(message, log_file=session_file,
                              console=command_args.verbosity)
            if aprox != "":
                message = ("* WARNING: Deleting a project or an execution will delete"
                           " also its associated resources. Note that their IDs"
                           " may not be listed in this report.\n")
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
            if command_args.bin:
                to_new_project(api, TRASH_BIN, delete_list)
            elif not command_args.dry_run:
                command_args.qs = '' if not hasattr(command_args, "qs") else \
                    command_args.qs
                message = "Deleting...\n"
                u.log_message(message, log_file=session_file)
                u.delete(
                    api, delete_list,
                    exe_outputs=not command_args.execution_only,
                    query_string=command_args.qs)
        else:
            message = ("No resources found with the following types: %s.\n"
                       % ",".join(command_args.resource_types_))
            u.log_message(message, log_file=session_file,
                          console=command_args.verbosity)
        if step < 2:
            message = "Deleting...\n"
            u.log_message(message, log_file=session_file)
            # if projects and executions have already been deleted,
            # delete the rest
            deleted_list.extend(delete_list)
            delete_resources(command_args, api, deleted_list=deleted_list,
                             step=step + 1)

    if step == 2 and deleted_list:
        u.print_generated_files(path, log_file=session_file,
                                verbosity=command_args.verbosity)
