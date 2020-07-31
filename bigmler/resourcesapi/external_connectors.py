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

import bigml.api

from bigmler.utils import (dated, log_message, check_resource,
                           check_resource_error, log_created_resources)
from bigmler.reports import report

from bigmler.resourcesapi.common import set_basic_args, \
    update_json_args, get_env_connection_info

from bigmler.resourcesapi.common import EXTERNAL_CONNECTION_ATTRS


def set_external_connector_args(args, name=None):
    """Return external connector arguments dict

    """
    if name is None:
        name = args.name
    external_connector_args = set_basic_args(args, name)

    source = "postgresql" if args.source is None else args.source
    external_connector_args.update({"source": source})

    connection_keys = list(EXTERNAL_CONNECTION_ATTRS.values())
    connection_keys.remove("source")

    connection_info = {}
    for key in connection_keys:
        if hasattr(args, key) and getattr(args, key):
            connection_info.update({key: getattr(args, key)})
    if not connection_info:
        # try to read environment variables
        connection_info = get_env_connection_info()
    args.connection_info = connection_info

    if args.hosts:
        args.connection_info.update({"hosts": args.hosts.split(",")})

    # rare arguments must be provided in a JSON file
    if args.connection_json_:
        args.connection_info.update(args.connection_json_)

    if 'external_connector' in args.json_args:
        update_json_args(external_connector_args,
                         args.json_args.get('external_connector'), None)

    return external_connector_args


def create_external_connector(external_connector_args, args, api=None,
                              session_file=None, path=None, log=None):
    """Creates remote external connector

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Creating external connector.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    external_connector = api.create_external_connector( \
        args.connection_info, external_connector_args)
    log_created_resources( \
        "external_connector", path,
        bigml.api.get_external_connector_id(external_connector),
        mode='a')
    external_connector_id = check_resource_error( \
        external_connector,
        "Failed to create external connector: ")
    try:
        external_connector = check_resource( \
            external_connector, api=api, raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished external connector: %s" % \
            str(exception))
    message = dated("External connector \"%s\" has been created.\n" %
                    external_connector['object']['name'])
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % external_connector_id, log_file=log)
    try:
        if args.reports:
            report(args.reports, path, external_connector)
    except AttributeError:
        pass
    return external_connector


def update_external_connector(external_connector_args, args,
                              api=None, session_file=None, log=None):
    """Updates external connector properties

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Updating external connector attributes.\n")
    log_message(message, log_file=session_file,
                console=args.verbosity)
    external_connector = api.update_external_connector( \
        args.external_connector_id, external_connector_args)
    check_resource_error(external_connector,
                         "Failed to update external connector: %s"
                         % external_connector['resource'])
    message = dated("External connector \"%s\" has been updated.\n" %
                    external_connector['resource'])
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % args.external_connector_id, log_file=log)
    return external_connector
