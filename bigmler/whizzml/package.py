# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,global-statement,invalid-name
#
# Copyright 2016-2024 BigML
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



import os
import sys
import json


import bigml

import bigmler.utils as u

from bigmler.command import different_command
from bigmler.execute.dispatcher import execute_dispatcher

COMMANDS = {"script":
                ("execute --no-execute --code-file %s --output-dir %s"
                 " --store"),
            "library":
                ("execute --no-execute --code-file %s --output-dir %s"
                 " --store --to-library")}

#subcommands
SUBCOMMAND_LOG = ".bigmler_subcmd"
SESSIONS_LOG = "bigmler_sessions"

#name max length
NAME_MAX_LENGTH = 127

METADATA_FILE = "metadata.json"
WHIZZML_LIBRARY = "library"
WHIZZML_RESOURCES = [WHIZZML_LIBRARY, "script"]
DFT_CATEGORY = 0 # Miscellaneous
WHIZZML_ATTRS = ["name", "description", "source_code", "imports",
                 "inputs", "outputs", "category", "project", "resource"]

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
    with open(subcommand_file, u.open_mode("r")) as reader:
        subcommand_list = reader.readlines()
    subcommand_list.reverse()


def rebuild_command(args):
    """Rebuilds a unicode command string prepared to be stored in a file

    """
    return "%s\n" % (" ".join(args)).replace("\\", "\\\\")


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


def get_library_code(library_ids, api):
    """Download the code in the libraries and return an array of source codes

    """
    code = []
    for library_id in library_ids:
        source_code = api.get_library(library_id)["object"]["source_code"]
        code.append(source_code)


def create_package(args, api, command_obj, resume=False):
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
            create_package(args, api, command_obj, resume=resume)
            args.package_dir = package_dir
    else:
        # create libraries or scripts
        imports = []
        category = str(metadata.get("category", DFT_CATEGORY))
        if metadata.get("imports") is not None:
            lib_imports = metadata.get("imports")
            for lib_import in lib_imports:
                args.package_dir = os.path.join(package_dir, lib_import)
                if args.embed_libs:
                    library_ref = create_package( \
                        args, api, command_obj, resume=resume)
                    u.log_created_resources("imports",
                                            output_dir, library_ref)
                else:
                    try:
                    # try to read the library id, if it is already there
                        library_ref = read_library_id(os.path.join( \
                            output_dir, os.path.basename(args.package_dir)))
                    except IOError:
                        library_ref = create_package( \
                            args, api, command_obj, resume=resume)
                        library_ref = read_library_id(os.path.join( \
                            output_dir, os.path.basename(args.package_dir)))
                imports.append(library_ref)
                args.package_dir = package_dir
        # read the metadata.json information
        message = ('Creating the %s.........\n' % metadata.get("kind"))
        u.log_message(message, log_file=session_file,
                      console=args.verbosity)
        if metadata.get("kind") in WHIZZML_RESOURCES:
            whizzml_code = os.path.normpath(os.path.join(args.package_dir, \
                metadata.get("source_code", "%s.whizzml" % \
                metadata.get("kind"))))
            if args.embed_libs and metadata.get("kind") == WHIZZML_LIBRARY:
                return whizzml_code

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
                u.write_to_utf8(inputs_file, json.dumps(metadata.get("inputs")))
                command_args.extend(["--declare-inputs", inputs_file])
            if "outputs" in metadata:
                outputs_file = os.path.join(args.output_dir, "outputs.json")
                u.write_to_utf8(outputs_file, json.dumps(metadata.get("outputs")))
                command_args.extend(["--declare-outputs", outputs_file])
            if "description" in metadata:
                desc_file = os.path.join(args.output_dir, "description.txt")
                u.write_to_utf8(desc_file, metadata.get("description"))
                command_args.extend(["--description", desc_file])
            if metadata.get("name"):
                command_args.extend(["--name", metadata.get("name")])
            if args.tag:
                for tag in args.tag:
                    command_args.extend(["--tag", tag])
            command_args.extend(["--category", category])

            # adding imports, if any
            if imports:
                if args.embed_libs:
                    # imports to be embedded are in the same output directory
                    command_args.extend( \
                        ["--embedded-imports", os.path.join(output_dir,
                                                            "imports")])
                else:
                    # imports to be refereced by ID
                    command_args.extend(["--imports", ",".join(imports)])
            command_args.extend(["--verbosity", str(args.verbosity)])
            command_obj.propagate(command_args)
            # u.add_api_context(command_args, args)
            if args.upgrade:
                command_args.extend(["--upgrade"])

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
            return whizzml_code
    return ""


def get_package_structure(resource_id, api, package_structure=None):
    """Downloads the JSON information of the script or library and stores in
    the directory set in api.storage. If the resource imports other resources,
    it recursively downloads them. It returns a dictionary describing the
    resources downloaded and the relations between them.
    """
    if package_structure is None:
        package_structure = {"resources": []}
    elif resource_id in package_structure["resources"]:
        return package_structure
    package_structure["resources"].append(resource_id)

    resource_type = bigml.api.get_resource_type(resource_id)
    resource = api.getters[resource_type](resource_id)
    metadata = {"kind": resource_type}
    for attr in WHIZZML_ATTRS:
        attr_value = resource["object"].get(attr)
        if attr_value:
            metadata.update({attr: attr_value})

    package_structure[resource_id] = metadata
    if metadata.get("imports") is not None:
        for library_id in metadata.get("imports"):
            get_package_structure(library_id, api, package_structure)
    return package_structure


def export_as_package(args, api, command_obj, resume=False):
    """Export the script and/or libraries to the expected file structure of a
    package.

    """
    set_subcommand_file(args.output_dir)
    if resume:
        retrieve_subcommands()
    # read the metadata.json information
    message = ('Reading the WhizzML resources.........\n')
    u.log_message(message, log_file=session_file,
                  console=args.verbosity)

    package_dir = args.package_dir
    os.makedirs(package_dir, exist_ok=True)
    output_dir = args.output_dir
    package_structure = get_package_structure(args.from_id, api)
    write_package(package_structure, args)


def write_package(package_structure, args):
    """Writes the package information in the user-given folder """
    package_dir = args.package_dir
    # write the package information
    message = ('Writting the package structure........\n')
    u.log_message(message, log_file=session_file,
                  console=args.verbosity)

    if len(package_structure["resources"]) == 1:
        # simple case: only one script or library, no structure
        resource_id = package_structure["resources"][0]
        write_code(package_structure[resource_id], package_dir)
    else:
        # complex case: script or library with imports
        write_package_folder(package_structure, package_dir)
    message = ('Local package created.................\n')
    u.log_message(message, log_file=session_file,
                  console=args.verbosity)


def write_package_folder(package_structure, package_dir):
    """Creates folders for every script or library and the metadata.json to
    describes them
    """
    counter = 1
    components = {}

    def write_subfolder(resource_info, counter):
        resource_id = resource_info["resource"]
        components[resource_id] = "%s_%s" % (resource_info["kind"], counter)
        folder = os.path.join(package_dir, components[resource_id])
        os.makedirs(folder, exist_ok=True)
        write_code(resource_info, folder)
        counter += 1
        return counter

    for resource_id in package_structure["resources"]:
        if package_structure[resource_id]["kind"] == WHIZZML_LIBRARY:
            counter = write_subfolder(package_structure[resource_id], counter)

    for resource_id in package_structure["resources"]:
        metadata = package_structure[resource_id]
        if metadata["kind"] != WHIZZML_LIBRARY:
            if metadata.get("imports") is not None:
                import_folders = [os.path.join("..", components[library_id])
                                  for library_id in metadata.get("imports")]
                metadata["imports"] = import_folders
            counter = write_subfolder(metadata, counter)

    first_script = package_structure[package_structure["resources"][0]]
    package_info = {"kind": "package",
                    "components": list(components.values()),
                    "name": first_script["name"],
                    "description": first_script["description"]}
    with open(os.path.join(package_dir, "metadata.json"),
              "wt", encoding="utf-8") as handler:
        json.dump(package_info, handler)


def write_code(resource_info, package_dir):
    """Creates a metadata.json, script.whizzml | library.whizzml and
    a README.md file in the package_dir
    """
    filename = "%s.whizzml" % resource_info["kind"]
    code_file = os.path.join(package_dir, filename)
    with open(code_file, "wt", encoding="utf-8") as handler:
        handler.write(resource_info["source_code"])
    resource_info["source_code"] = filename
    with open(os.path.join(package_dir, "README.md"),
              "wt", encoding="utf-8") as handler:
        project_info = ""
        if resource_info.get("project") is not None:
            project_info = " in project %s " % resource_info["project"]
        content = "Extracted from %s%s by bigmler" % (
            resource_info["resource"], project_info)
        handler.write(content)
    del resource_info["resource"]
    try:
        del resource_info["project"]
    except KeyError:
        pass
    with open(os.path.join(package_dir, "metadata.json"),
              "wt", encoding="utf-8") as handler:
        json.dump(resource_info, handler)
