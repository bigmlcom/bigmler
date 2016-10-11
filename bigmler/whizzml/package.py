# -*- coding: utf-8 -*-
#
# Copyright 2016 BigML
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

"""package creation procedure (whizzml subcommand)

   Functions used in package creation


"""
from __future__ import absolute_import


import os
import sys
import json
import re

import bigml

import bigmler.utils as u

from bigmler.execute.dispatcher import execute_dispatcher

COMMANDS = {"script":
                ("execute --no-execute --code-file %s --output-dir %s"
                 " --store"),
            "library":
                ("execute --no-execute --code-file %s --output-dir %s"
                 " --store --to-library")}

#subcommands
SUBCOMMAND_LOG = u".bigmler_subcmd"
SESSIONS_LOG = u"bigmler_sessions"

#name max length
NAME_MAX_LENGTH = 127

METADATA_FILE = "metadata.json"
WHIZZML_RESOURCES = ["library", "script"]


subcommand_list = []
subcommand_file = None
session_file = None


def set_subcommand_file(output_dir):
    """Creates the subcommand file in the output_dir directory

    """
    global subcommand_file
    global session_file
    subcommand_file = os.path.normpath(os.path.join(output_dir,
                                                    SUBCOMMAND_LOG))
    session_file = os.path.normpath(os.path.join(output_dir, SESSIONS_LOG))


def retrieve_subcommands():
    """Retrieves the executed subcommands in inverse order

    """
    global subcommand_list
    subcommand_list = open(subcommand_file, u.open_mode("r")).readlines()
    if not u.PYTHON3:
        subcommand_list = [subcommand.decode(u.SYSTEM_ENCODING)
                           for subcommand in subcommand_list]
    subcommand_list.reverse()


def rebuild_command(args):
    """Rebuilds a unicode command string prepared to be stored in a file

    """
    return "%s\n" % (u" ".join(args)).replace("\\", "\\\\")


def different_command(next_command, command):
    if next_command == command:
        return False
    else:
        if 'name=BigMLer_' in command:
            # the difference may be due to the timestamp of default name
            # parameter
            pattern = re.compile(r'name=Bigmler_[^\s]+')
            return re.sub(pattern, "", next_command) == re.sub(pattern,
                                                               "", command)
        return False


def read_library_id(path):
    """Reads the library ID from the corresponding library file in the
    path
    """
    with open(os.path.join(path, "library")) as library_handler:
        library_id = bigml.api.get_library_id( \
            library_handler.readline().strip())

    if not library_id:
        sys.exit("Failed to read import library ID from %s" % \
            os.path.join(path, "library"))
    return library_id


def create_package(args, api, common_options, resume=False):
    """Creates the package whizzml resources as referred in the metadata.json
    file.

    """
    set_subcommand_file(args.output_dir)
    if resume:
        retrieve_subcommands()
    # read the metadata.json information
    message = ('Reading the metadata.json files.........\n')
    u.log_message(message, log_file=session_file,
                  console=args.verbosity)
    package_dir = args.package_dir
    output_dir = args.output_dir
    metadata_file = os.path.join(package_dir, METADATA_FILE)
    metadata = None

    with open(metadata_file) as metadata_handler:
        metadata = json.load(metadata_handler)
    # recurse into components/directories, if any
    if metadata.get("kind") == "package" and 'components' in metadata:
        components = metadata.get("components")
        for component in components:
            message = ('Inspecting component %s.........\n' % component)
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
            args.package_dir = os.path.join(package_dir, component)
            create_package(args, api, common_options, resume=resume)
            args.package_dir = package_dir
    else:
        # create libraries or scripts
        imports = []
        if metadata.get("imports") is not None:
            lib_imports = metadata.get("imports")
            for lib_import in lib_imports:
                args.package_dir = os.path.join(package_dir, lib_import)
                # try to read the library id, if it is already there
                try:
                    library_id = read_library_id(os.path.join( \
                        output_dir, os.path.basename(args.package_dir)))
                except IOError:
                    create_package(args, api, common_options, resume=resume)
                    library_id = read_library_id(os.path.join( \
                        output_dir, os.path.basename(args.package_dir)))
                imports.append(library_id)
                args.package_dir = package_dir
        # read the metadata.json information
        message = ('Creating the %s.........\n' % metadata.get("kind"))
        u.log_message(message, log_file=session_file,
                      console=args.verbosity)
        if metadata.get("kind") in WHIZZML_RESOURCES:
            whizzml_code = os.path.join(args.package_dir, \
                metadata.get("source_code", "%s.whizzml" % \
                metadata.get("kind")))
            args.output_dir = os.path.join(output_dir, \
                os.path.basename(package_dir))
            # creating command to create the resource
            command = COMMANDS[metadata.get("kind")] % (whizzml_code,
                                                        args.output_dir)
            command_args = command.split()
            bigml.util.check_dir(args.output_dir)
            # getting inputs and outputs for the script from metadata
            if "inputs" in metadata:
                inputs_file = os.path.join(args.output_dir, "inputs.json")
                with open(inputs_file, "w") as inputs_handler:
                    json.dump(metadata.get("inputs"), inputs_handler)
                command_args.extend(["--declare-inputs", inputs_file])
            if "outputs" in metadata:
                outputs_file = os.path.join(args.output_dir, "outputs.json")
                with open(outputs_file, "w") as outputs_handler:
                    json.dump(metadata.get("outputs"), outputs_handler)
                command_args.extend(["--declare-outputs", outputs_file])
            if "description" in metadata:
                desc_file = os.path.join(args.output_dir, "description.txt")
                with open(desc_file, "w") as desc_handler:
                    desc_handler.write(metadata.get("description"))
                command_args.extend(["--description", desc_file])
            if metadata.get("name"):
                command_args.extend(["--name", metadata.get("name")])
            # adding imports, if any
            if imports:
                command_args.extend(["--imports", ",".join(imports)])
            command_args.extend(["--verbosity", str(args.verbosity)])

            if resume:
                next_command = subcommand_list.pop()
                if different_command(next_command, command):
                    resume = False
                    u.sys_log_message(command, log_file=subcommand_file)
                    execute_dispatcher(args=command_args)
                elif not subcommand_list:
                    execute_dispatcher(args=['execute', '--resume'])
                    resume = False
            else:
                u.sys_log_message(command, log_file=subcommand_file)
                execute_dispatcher(args=command_args)
            args.output_dir = output_dir
