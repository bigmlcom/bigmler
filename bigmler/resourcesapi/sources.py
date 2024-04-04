# -*- coding: utf-8 -*-
#
# Copyright 2020-2024 BigML
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
import os
import json

import bigml.api

from bigml.util import bigml_locale
from bigml.constants import TINY_RESOURCE

from bigmler.utils import (dated, get_url, log_message, check_resource,
                           check_resource_error, log_created_resources)

from bigmler.resourcesapi.common import set_basic_args, check_fields_struct, \
    update_attributes, update_json_args, set_config_attrs, hasattr_

from bigmler.resourcesapi.common import ALL_FIELDS_QS, LOCALE_DEFAULT
from bigmler.reports import report
from bigmler.processing.annotations import bigml_metadata


IMAGE_ATTRS = ["dimensions", "average_pixels", "level_histogram"]


def set_source_args(args, name=None, multi_label_data=None,
                    data_set_header=None, fields=None, update=False):
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

    # image feature generation
    image_analysis = False
    extracted_features = []
    image_config = {}
    for attr in IMAGE_ATTRS:
        if hasattr_(args, attr) and getattr(args, attr):
            extracted_features.append(attr)
            image_analysis = True
    if hasattr_(args, "hog") and getattr(args, "hog"):
        extracted_features.append("histogram_of_gradients")
        image_analysis = True
    if hasattr_(args, "ws_level"):
        extracted_features.append(["wavelet_subbands", args.ws_level])
        image_analysis = True
    if hasattr_(args, "pretrained_cnn"):
        extracted_features.append(["pretrained_cnn", args.pretrained_cnn])
        image_analysis = True
    if extracted_features:
        args.image_analysis = True
    if hasattr_(args, "image_analysis"):
        image_config.update({"enabled": args.image_analysis})
        if extracted_features:
            image_config.update({"extracted_features": extracted_features})
        image_analysis = True
    if image_analysis:
        source_args.update({"image_analysis": image_config})

    if update:
        exclusive_attrs = ["add_sources_", "remove_sources_",
                           "delete_sources_", "closed", "sources_"]
        attr_aliases = {"add_sources_": "add_sources",
                        "remove_sources_": "remove_sources",
                        "delete_sources_": "delete_sources",
                        "sources_": "sources"}
        set_config_attrs(args, exclusive_attrs,
                         source_args, attr_aliases=attr_aliases, exclusive=True)

        row_attrs = ["row_components", "row_indices", "row_values"]
        set_config_attrs(args, row_attrs, source_args)
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
    if data_set is not None and not isinstance(data_set, str):
        # creating source from stream
        source = api.create_source(data_set, source_args)
    else:
        # annotated sources for images
        try:
            if os.path.exists(data_set) and not os.path.isdir(data_set):
                # --train metadata.json
                with open(data_set) as data_handler:
                    try:
                        source_info = json.load(data_handler)
                    except (UnicodeDecodeError, json.decoder.JSONDecodeError):
                        source_info = None
                if source_info is not None and isinstance(source_info, dict):
                    # could be a metadata.json file describing annotated images
                    source_attrs = source_info.keys()
                    if "annotations" in source_attrs and \
                            "images_file" in source_attrs:
                        source = api.create_annotated_source(data_set,
                                                             source_args)
                    else:
                        source = api.create_source(data_set, source_args)
                else:
                    # --train iris.csv
                    source = api.create_source(data_set, source_args)
            elif args.images_dir and args.annotations_file:
                # --train images_dir
                source = api.create_annotated_source(bigml_metadata(args),
                                                     source_args)
            else:
                source = api.create_source(data_set, source_args)
        except (IOError, TypeError):
            # empty composite source, for instance
            source = api.create_source(args.sources_, source_args)
    if path is not None:
        suffix = "_" + source_type if source_type else ""
        log_created_resources(
            "source%s" % suffix, path,
            source['resource'], mode='ab',
            comment=("%s\n" % source.get('object', {}).get('name')))
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
    if hasattr(args, "reports") and args.reports:
        report(args.reports, path, source)
    if hasattr(source_args, "sources_"):
        # if we used the list of sources to create a composite, we don't
        # want the argument to be used in the update step
        args.sources_ = None
    return source


def clone_source(source, args, api=None, path=None,
                 session_file=None, log=None):
    """Clones the source to open it for editing

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Cloning source to open it for editing\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    source = api.clone_source(source)
    source_id = check_resource_error(source, "Failed to clone source: ")
    try:
        source = check_resource(source, api.get_source,
                                query_string=ALL_FIELDS_QS,
                                raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished source: %s" % str(exception))
    log_created_resources("source", path, source['resource'], mode='ab',
        comment=("%s\n" % source['object']['name']))
    message = dated("Source created: %s\n" % get_url(source))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % source_id, log_file=log)
    return source


def data_to_source(args):
    """Extracts the flags info to create a source object

    """
    data_set = None
    data_set_header = None
    if (args.training_set and not args.source and not
            (hasattr(args, "dataset") and args.dataset) and
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
                  api=None, verbosity=True, session_file=None, log=None):
    """Updates source properties

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Updating source. %s\n" %
                    get_url(source))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    source_min = api.get_source(source, query_string=TINY_RESOURCE)
    if source_min["object"].get("closed", False):
        message = dated("Source was closed. Cloning %s\n" %
                        get_url(source))
        log_message(message, log_file=session_file,
                    console=verbosity)
        source = api.clone_source(source)
        message = "Source created: %s\n" % get_url(source)
        log_message(message, log_file=session_file, console=args.verbosity)
        log_message("%s\n" % source["object"]["resource"], log_file=log)

    if args.annotations_file and args.images_file:
        source = api.update_composite_annotations(
            source, args.images_file, args.annotations_file,
            new_fields=None,
            source_changes=source_args)

    source = api.update_source(source, source_args)
    check_resource_error(source, "Failed to update source: ")
    source = check_resource(source, api.get_source)
    return source
