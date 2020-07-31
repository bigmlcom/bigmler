# -*- coding: utf-8 -*-
#
# Copyright 2020 BigML
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
"""Resources management functions

"""


import sys
import json

import bigml.api

from bigml.util import bigml_locale

from bigmler.utils import (dated, get_url, log_message, check_resource,
                           check_resource_error, log_created_resources)

from bigmler.resourcesapi.common import set_basic_args, check_fields_struct, \
    update_attributes, update_json_args

from bigmler.resourcesapi.common import ALL_FIELDS_QS, LOCALE_DEFAULT
from bigmler.reports import report


def set_source_args(args, name=None, multi_label_data=None,
                    data_set_header=None, fields=None):
    """Returns a source arguments dict

    """

    if name is None:
        name = args.name
    source_args = set_basic_args(args, name)
    if args.project_id is not None:
        source_args.update({"project": args.project_id})
    # if header is set, use it
    if data_set_header is not None:
        source_args.update({"source_parser": {"header": data_set_header}})
    # If user has given an OS locale, try to add the locale used in bigml.com
    if args.user_locale is not None:
        source_locale = bigml_locale(args.user_locale)
        if source_locale is None:
            log_message("WARNING: %s locale equivalence not found."
                        " Using %s instead.\n" % (args.user_locale,
                                                  LOCALE_DEFAULT),
                        log_file=None, console=True)
            source_locale = LOCALE_DEFAULT
        source_args.update({'source_parser': {}})
        source_args["source_parser"].update({'locale': source_locale})
    # If user has set a training separator, use it.
    if args.training_separator is not None:
        training_separator = args.training_separator
        source_args["source_parser"].update({'separator': training_separator})
    # If uploading a multi-label file, add the user_metadata info needed to
    # manage the multi-label fields
    if (hasattr(args, 'multi_label') and args.multi_label
            and multi_label_data is not None):
        source_args.update({
            "user_metadata": {
                "multi_label_data": multi_label_data}})

    # to update fields attributes or types you must have a previous fields
    # structure (at update time)
    if fields:
        if args.field_attributes_:
            update_attributes(source_args,
                              {"fields": args.field_attributes_},
                              by_column=True, fields=fields)
        if args.types_:
            update_attributes(source_args,
                              {"fields": args.types_},
                              by_column=True, fields=fields)
        if args.import_fields:
            fields_struct = fields.new_fields_structure(args.import_fields)
            check_fields_struct(fields_struct, "source")
            update_attributes(source_args, fields_struct)
        if 'source' in args.json_args:
            update_json_args(source_args, args.json_args.get('source'), fields)
    return source_args


def create_source(data_set, source_args, args, api=None, path=None,
                  session_file=None, log=None, source_type=None):
    """Creates remote source

    """
    if api is None:
        api = bigml.api.BigML()
    suffix = "" if source_type is None else "%s " % source_type
    message = dated("Creating %ssource.\n" % suffix)
    log_message(message, log_file=session_file, console=args.verbosity)
    check_fields_struct(source_args, "source")
    source = api.create_source(data_set, source_args,
                               progress_bar=args.progress_bar)
    if path is not None:
        suffix = "_" + source_type if source_type else ""
        log_created_resources(
            "source%s" % suffix, path,
            source['resource'], mode='ab',
            comment=("%s\n" % source['object']['name']))
    source_id = check_resource_error(source, "Failed to create source: ")
    try:
        source = check_resource(source, api.get_source,
                                query_string=ALL_FIELDS_QS,
                                raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished source: %s" % str(exception))
    message = dated("Source created: %s\n" % get_url(source))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % source_id, log_file=log)
    if args.reports:
        report(args.reports, path, source)
    return source


def data_to_source(args):
    """Extracts the flags info to create a source object

    """
    data_set = None
    data_set_header = None
    if (args.training_set and not args.source and not args.dataset and
            not args.has_models_):
        data_set = args.training_set
        data_set_header = args.train_header
    elif (hasattr(args, 'evaluate') and args.evaluate and args.test_set
          and not args.source):
        data_set = args.test_set
        data_set_header = args.test_header
    if data_set is not None:
        try:
            with open(data_set, 'r') as data_handler:
                content = json.load(data_handler)
                if isinstance(content, dict) and \
                        "externalconnector_id" in content \
                        and "query" in content:
                    data_set = content
        except (IOError, ValueError, TypeError):
            pass

    return data_set, data_set_header


def get_source(source, api=None, verbosity=True,
               session_file=None):
    """Retrieves the source in its actual state and its field info

    """
    if api is None:
        api = bigml.api.BigML()
    if (isinstance(source, str) or
            bigml.api.get_status(source)['code'] != bigml.api.FINISHED):
        message = dated("Retrieving source. %s\n" %
                        get_url(source))
        log_message(message, log_file=session_file,
                    console=verbosity)
        try:
            source = check_resource(source, api.get_source,
                                    query_string=ALL_FIELDS_QS,
                                    raise_on_error=True)
        except Exception as exception:
            sys.exit("Failed to get a finished source: %s" % str(exception))

    return source


def update_source(source, source_args, args,
                  api=None, session_file=None):
    """Updates source properties

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Updating source. %s\n" %
                    get_url(source))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    source = api.update_source(source, source_args)
    check_resource_error(source, "Failed to update source: ")
    source = check_resource(source, api.get_source)
    return source
