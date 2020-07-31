# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 BigML
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

"""BigMLer - generates code to use models locally

"""


import sys
import os


import bigmler.utils as u


from bigml.ensemble import Ensemble
try:
    from bigml.out_model.pythonmodel import PythonModel
except ImportError:
    from bigml.model import Model as PythonModel

from bigmler.defaults import DEFAULTS_FILE
from bigmler.command import get_context
from bigmler.dispatcher import SESSIONS_LOG, clear_log_files
from bigmler.export.out_model.jsmodel import JsModel
from bigmler.export.out_model.tableaumodel import TableauModel
from bigmler.export.out_model.mysqlmodel import MySQLModel
from bigmler.export.out_model.rmodel import RModel
from bigmler.export.out_model.pythonlr import PythonLR


COMMAND_LOG = ".bigmler_export"
DIRS_LOG = ".bigmler_export_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]

EXPORTS = {
    "javascript": JsModel,
    "python": PythonModel,
    "tableau": TableauModel,
    "mysql": MySQLModel,
    "r": RModel}

EXTENSIONS = {
    "javascript": "js",
    "python": "py",
    "tableau": "tb",
    "mysql": "sql",
    "r": "R"}

LR_EXPORTS = {
    "python": PythonLR
}

SEPARATE_OUTPUT = ['tableau', 'mysql']

SETTINGS = {
    "command_log": COMMAND_LOG,
    "sessions_log": SESSIONS_LOG,
    "dirs_log": DIRS_LOG,
    "defaults_file": DEFAULTS_FILE}


def export_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different export functions

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    command_args, _, api, session_file, _ = get_context(args, SETTINGS)
    # Creates the corresponding api instance
    resource = command_args.ensemble or command_args.model
    message = "Generating %s code for %s\n\n" % (command_args.language,
                                                 resource)
    u.log_message(message, \
        log_file=session_file, console=command_args.verbosity)
    export_code(command_args, api)
    u.log_message("_" * 80 + "\n", log_file=session_file)

    u.print_generated_files(command_args.output_dir, log_file=session_file,
                            verbosity=command_args.verbosity)


def generate_output(local_model, args, model_type="model", attr="confidence"):
    """Generates the output for the prediction (and confidence) function

    """
    with open(os.path.join(args.output_dir, \
        "%s.%s") % (local_model.resource_id.replace("/", "_"),
                    EXTENSIONS[args.language]), "w") as handler:
        local_model.plug_in(out=handler)
    # creating a separate file to predict confidence
    if args.language in SEPARATE_OUTPUT:
        with open(os.path.join(args.output_dir, \
            "%s_confidence.%s") % (getattr(args, model_type).replace("/", "_"),
                                   EXTENSIONS[args.language]), "w") as handler:
            local_model.plug_in(out=handler, attr=attr)


def export_code(args, api=None):
    """Generates the plugin code in the language required by the user

    """
    args.language = args.language or "javascript"

    if args.model is not None and args.language in EXPORTS:

        local_model = EXPORTS[args.language](args.model, api=api)
        generate_output(local_model, args, model_type="model")

    if args.ensemble is not None and args.language in EXPORTS:
        local_ensemble = Ensemble(args.ensemble, api=api)

        for model_id in local_ensemble.model_ids:
            local_model = EXPORTS[args.language]( \
                model_id,
                api=api,
                fields=local_ensemble.fields,
                boosting=local_ensemble.boosting)
            generate_output(local_model, args, model_type="model")
