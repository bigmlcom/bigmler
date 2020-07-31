# -*- coding: utf-8 -*-
#
# Copyright 2016-2020 BigML
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

"""BigMLer whizzml main processing

   Functions to process the whizzml options


"""


import sys
import os

import bigmler.utils as u

from bigmler.whizzml.package import create_package
from bigmler.dispatcher import SESSIONS_LOG, clear_log_files
from bigmler.command import get_context


COMMAND_LOG = ".bigmler_whizzml"
DIRS_LOG = ".bigmler_whizzml_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]

SETTINGS = {
    "command_log": COMMAND_LOG,
    "sessions_log": SESSIONS_LOG,
    "dirs_log": DIRS_LOG}


def whizzml_dispatcher(args=sys.argv[1:]):
    """Main processing of the parsed options for BigMLer whizzml

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    command_args, command, api, _, resume = get_context(args, SETTINGS)

    # package_dir
    if command_args.package_dir is not None:
        command_args.package_dir = os.path.expanduser(command_args.package_dir)
        create_package(command_args, api, command,
                       resume=resume)
    else:
        sys.exit("You must use the --package-dir flag pointing to the"
                 " directory where the metadata.json file is. Type\n"
                 "    bigmler whizzml --help\n"
                 " to see all the available options.")
