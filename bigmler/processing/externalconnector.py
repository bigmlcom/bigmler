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

"""BigMLer - Resource processing: creation, update and retrieval of external
connectors

"""


import bigml.api
import bigmler.resourcesapi.external_connectors as r
import bigmler.utils as u
import bigmler.checkpoint as c


def connector_processing(api, args, resume,
                         session_file=None, path=None, log=None):
    """Creating or retrieving an external connector from input arguments

    """
    # if no external connection info given by the user, we skip
    # processing and no connector will be created
    if not u.has_connection_info(args) and args.external_connector_id is None:
        return None
    external_connector_id = None
    if u.has_connection_info(args):
        # If resuming, try to extract args.external_connector_id form log files

        if resume:
            message = u.dated("External connector ID not found. Resuming.\n")
            resume, external_connector_id = c.checkpoint(
                c.is_external_connector_created, path,
                debug=args.debug, message=message,
                log_file=session_file, console=args.verbosity)

    else:
        external_connector_id = bigml.api.get_external_connector_id( \
            args.external_connector_id)

    # If no external connector is found, we create a new one.
    if external_connector_id is None:
        connector_args = r.set_external_connector_args(\
            args, name=args.name)
        connector = r.create_external_connector(
            connector_args, args, api, session_file, path, log)
        external_connector_id = connector['resource']

    return external_connector_id


def update_external_connector(args, api, resume,
                              session_file=None, path=None, log=None):
    """Updating external connector attributes according to input arguments

    """
    # if no external connector info given by the user, we skip processing and
    # no update will be performed
    if args.external_connector_id is None:
        return None
        # If resuming, try to extract args.external_connector_id form log files

    if resume:
        message = u.dated("External connector not found. Resuming.\n")
        resume, external_connector_id = c.checkpoint(
            c.is_external_connector_created, path,
            debug=args.debug, message=message,
            log_file=session_file, console=args.verbosity)
    elif args.external_connector_id:
        external_connector_id = bigml.api.get_external_connector_id( \
            args.external_connector_id)

    if external_connector_id is not None:
        external_connector_args = r.set_basic_args(args, args.name)
        external_connector = r.update_external_connector(
            external_connector_args, args, api, session_file, log)
        external_connector_id = external_connector['resource']

    return external_connector_id
