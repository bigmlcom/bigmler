# -*- coding: utf-8 -*-
#
# Copyright 2015-2020 BigML
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

"""BigMLer - reify processing dispatching

"""


import sys
import os
import stat
import json
import shutil
import pprint
import nbformat as nbf

from bigml.api_handlers.resourcehandler import get_resource_id
from bigml.api import check_resource

from bigmler.utils import get_last_resource, get_script_id, \
    write_to_utf8
from bigmler.reports import BIGMLER_SCRIPT, HOME
from bigmler.command import get_context
from bigmler.whizzml.dispatcher import whizzml_dispatcher
from bigmler.execute.dispatcher import execute_whizzml
from bigmler.execute.dispatcher import SETTINGS as EXE_SETTINGS


REIFY_PACKAGE_PATH = os.path.join(BIGMLER_SCRIPT, "static", "scripts",
                                  "reify")
BIGMLER_SCRIPTS_DIRECTORY = os.path.join(HOME, "bigmler", "scripts", "reify")

SCRIPT_FILE = {"nb": "python"}


def create_connection(api):
    """ Creates the code that defines the same connection object used
        in bigmler

    """
    args = []
    if api.general_domain != "bigml.io":
        args.append("domain=\"%s\"" % api.general_domain)
    if api.project:
        args.append("project=\"%s\"" % api.project)
    if api.organization:
        args.append("organization=\"%s\"" % api.organization)
    return "BigML(%s)" % ", ".join(args)


def clean_args_references(args):
    """ Removes the information used as reference for the scripts

    """
    if "all_fields" in args and args["all_fields"] and \
            "new_fields" not in args:
        del args["all_fields"]
    if "objective_field" in args and \
            isinstance(args["objective_field"], dict) and \
            "name" in args["objective_field"]:
        del args["objective_field"]["name"]
    return args


def write_nb_output(resource_id, workflow, filename, api):
    """ Write the output to a file in jupyter notebook format

    """
    nb = nbf.v4.new_notebook()
    cells = [nbf.v4.new_markdown_cell("Reified resource: %s" % resource_id),
             nbf.v4.new_markdown_cell("Remember to set your credentials"
                                      " in the BIGML_USERNAME and"
                                      " BIGML_API_KEY environment variables."),
             nbf.v4.new_code_cell("from bigml.api import BigML\napi = %s" %
                                  create_connection(api))]
    for step in workflow:
        for (cell_type, cell_text) in list(step.items()):
            if cell_type == "args":
                args = clean_args_references(json.loads(cell_text))
                cell_text = "args = \\\n    %s" % pprint.pformat( \
                    args).replace("\n", "\n    ")
                cell_type = "code"
            cells.append(getattr(nbf.v4, "new_%s_cell" % cell_type)(cell_text))
    nb["cells"] = cells
    nbf.write(nb, filename)


def python_output(workflow, api):
    """ Content for the script in Python

    """
    lines = ["    from bigml.api import BigML",
             "    api = %s" % create_connection(api)]
    for step in workflow:
        for (cell_type, cell_text) in list(step.items()):
            if cell_type == "args":
                args = json.loads(cell_text)
                args = clean_args_references(args)
                cell_text = "args = \\\n    %s" % pprint.pformat( \
                    args).replace("\n", "\n    ")
                cell_type = "code"
            if cell_type != "markdown":
                cell_text = "    %s" % cell_text.replace("\n", "\n    ")
                lines.append(cell_text)
    return "\n".join(lines)


def whizzml_script(args, api):
    """Returns the ID of the script to be used to generate the output

    """
    # each language has its own script, so first check:
    # - whether the script exists in the account
    # - whether it has the same version
    # else, we act as if we wanted to upgrade the script
    script_dir = os.path.join(REIFY_PACKAGE_PATH,
                              SCRIPT_FILE.get(args.language, args.language))
    if not args.upgrade:
        # the script is retrieved by name
        # Reading the name of the script
        with open(os.path.join(script_dir, "metadata.json")) as meta_file:
            meta = json.load(meta_file)
        # check for the last script used to retrain the model
        query_string = "name=%s" % meta["name"]
        reify_script = get_last_resource( \
            "script",
            api=api,
            query_string=query_string)
    else:
        reify_script = None

    # create or retrieve the script to generate the output
    # if --upgrade, we force rebuilding the scriptified script
    if reify_script is None:
        try:
            shutil.rmtree(os.path.join(BIGMLER_SCRIPTS_DIRECTORY,
                                       SCRIPT_FILE.get(args.language,
                                                       args.language)))
        except Exception:
            pass

    if reify_script is None:
        # new bigmler command: creating the scriptify scripts
        whizzml_command = ['whizzml',
                           '--package-dir', REIFY_PACKAGE_PATH,
                           '--output-dir', BIGMLER_SCRIPTS_DIRECTORY]
        whizzml_dispatcher(args=whizzml_command)
        reify_file = os.path.join(BIGMLER_SCRIPTS_DIRECTORY,
                                  SCRIPT_FILE.get(args.language,
                                                  args.language), "scripts")
        reify_script = get_script_id(reify_file)
    return reify_script


def reify_resources(args, api):
    """ Extracts the properties of the created resources and generates
        code to rebuild them

    """

    resource_id = get_resource_id(args.resource_id)
    if resource_id is None:
        sys.exit("Failed to match a valid resource ID. Please, check: %s"
                 % args.resource_id)

    # check whether the resource exists
    try:
        check_resource(resource_id, raise_on_error=True, api=api)
    except Exception:
        sys.exit("Failed to find the resource %s. Please, check its ID and"
                 " the connection info (domain and credentials)." %
                 resource_id)

    reify_script = whizzml_script(args, api)

    # apply the reify script to the resource
    execute_command = ['execute',
                       '--script', reify_script,
                       '--output-dir', args.output_dir]
    command_args, _, _, _, _ = get_context( \
        execute_command, EXE_SETTINGS)
    command_args.arguments_ = [["res-id", resource_id]]
    command_args.inputs = json.dumps(command_args.arguments_)

    # process the command
    session_file = None
    execute_whizzml(command_args, api, session_file)
    with open("%s.json" % command_args.output) as file_handler:
        exe_output = json.load(file_handler)['result']

    if args.language == "nb":
        write_nb_output(resource_id, \
            exe_output, args.output.replace(".py", ".ipynb"), api)
        return
    elif args.language == "whizzml":
        output = exe_output["source_code"]
        args.output = args.output.replace(".py", ".whizzml")
        exe_output["source_code"] = args.output
        exe_output["kind"] = "script"
        with open(os.path.join(os.path.dirname(args.output),
                               "metadata.json"), "w") as meta_handler:
            meta_handler.write(json.dumps(exe_output))
    else:
        output = python_output(exe_output,
                               api)
        prefix = """\
#!/usr/bin/env python
# -​*- coding: utf-8 -*​-
\"\"\"Python code to reify %s

Generated by BigMLer
\"\"\"


def main():

""" % resource_id
        suffix = """\
if __name__ == "__main__":
    main()
"""
        output = "%s%s\n%s" % (prefix, output, suffix)


    write_to_utf8(args.output, output)

    sts = os.stat(args.output)
    os.chmod(args.output, sts.st_mode | stat.S_IEXEC)
