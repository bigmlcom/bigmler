# -*- coding: utf-8 -*-
#
# Copyright 2012-2020 BigML
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

"""BigMLer report utilities

"""



import os
import sys
import tempfile
import shutil
import json
import re
import copy

import requests

import bigml.api

from bigmler.utils import is_shared, check_dir, get_url, log_created_resources
from bigmler.options.analyze import OPTIMIZE_OPTIONS


URL_TEMPLATE = "%%BIGML_%s%%"
SECTION_START = "\n%%BIGML_START_%s%%"
SECTION_START_PREFIX = SECTION_START[2: 15]
SECTION_END = "\n%%BIGML_END_%s%%"
SECTION_END_PREFIX = SECTION_END[2: 13]
REPORTS_DIR = "reports"
ANALYZE_PATH = "test"
ANALYZE_DIR = "analyze"
EMBEDDED_RESOURCES = ["MODEL"]
GAZIBIT = "gazibit"
BIGMLER_SCRIPT = os.path.dirname(__file__)
# templates for reports
ANALYZE_TEMPLATE = "%s/static/analyze.html" % BIGMLER_SCRIPT
GAZIBIT_PRIVATE = "%s/static/gazibit.json" % BIGMLER_SCRIPT
GAZIBIT_SHARED = "%s/static/gazibit_shared.json" % BIGMLER_SCRIPT

# gazibit API data
GAZIBIT_TOKEN = "GAZIBIT_TOKEN"
GAZIBIT_CREATE_URL = "http://gazibit.com/api/v1/create"
GAZIBIT_HEADERS = {"X-Gazibit-API-Token": os.environ.get(GAZIBIT_TOKEN),
                   "Expect": "100-continue",
                   'content-type': 'application/x-www-form-urlencoded',
                   'Content-Length': 12544,
                   'User-Agent': ('curl/7.22.0 (x86_64-pc-linux-gnu)'
                                  ' libcurl/7.22.0 OpenSSL/1.0.1'
                                  ' zlib/1.2.3.4 libidn/1.23 librtmp/2.3')}

#analyze options
CROSS_VALIDATION_FILE = "evaluation.json"
MODEL_KEY = "model"
METRICS_FILE = "metrics.json"
EVALUATIONS_JSON_FILE = "evaluations_json.json"
SERVER_DIRECTORY = os.path.join("bigmler", "reports")
HOME = os.getenv("HOME") or (
    os.path.join(os.getenv("HOMEDRIVE"), os.getenv("HOMEPATH")))

PREFIX = "average_"
SESSION_FILE = "bigmler_sessions"


HTTP_CREATED = 201


def check_subdir(path, subdir):
    """Check whether a directory exists in a path and create it if it doesn't.

    """
    directory = os.path.join(path, subdir)
    try:
        os.stat(directory)
    except OSError:
        os.mkdir(directory)


def report(report_types_list, output_dir=None, resource=None):
    """Generate the requested reports

    """
    shared = is_shared(resource)
    for report_type in report_types_list:
        REPORTS[report_type](resource, output_dir, shared)


def add_gazibit_links(resource, output_dir=None, shared=False):
    """ Adds the link to the resource in the corresponding section of the
        report template

    """
    try:
        gazibit_tmp = GAZIBIT_SHARED if shared else GAZIBIT_PRIVATE
        path = check_dir(os.path.join(output_dir,
                                      REPORTS_DIR,
                                      os.path.basename(gazibit_tmp)))
        input_file = os.path.join(path, os.path.basename(gazibit_tmp))
        output_file = tempfile.NamedTemporaryFile(
            mode="w", dir=output_dir, delete=False)

        if not os.path.isfile(input_file):
            shutil.copyfile(gazibit_tmp, input_file)
        with open(input_file, "r") as report_template:
            with output_file as report_output:
                content = report_template.read()
                resource_type = bigml.api.get_resource_type(resource)
                resource_type = resource_type.upper()
                url_template = URL_TEMPLATE % resource_type
                # For shared reports, use the embedded model tree
                if shared and (resource_type in EMBEDDED_RESOURCES):
                    url = get_url(resource, embedded=True)
                else:
                    url = get_url(resource, shared=shared)
                content = content.replace(url_template, url)
                section_template = SECTION_START % resource_type
                content = content.replace(section_template, "")
                section_template = SECTION_END % resource_type
                content = content.replace(section_template, "")
                report_output.write(content)
        os.remove(input_file)
        os.rename(output_file.name, input_file)
    except IOError as exc:
        os.remove(output_file.name)
        sys.exit("Failed to generate the gazibit output report. %s" % str(exc))


def clear_reports(output_dir):
    """Clears the sections useless sections

    """

    # read report files
    path = check_dir(os.path.join(output_dir, REPORTS_DIR, GAZIBIT_TOKEN))
    for report_file in os.listdir(path):
        input_file = os.path.join(path, report_file)
        output_file = tempfile.NamedTemporaryFile(
            mode="w", dir=output_dir, delete=False)
        try:
            with open(input_file, "r") as report_template:
                with output_file as report_output:
                    content = report_template.read()
                    while content.find(SECTION_START_PREFIX) > 0:
                        start = content.find(SECTION_START_PREFIX)
                        end = content.find("\n",
                                           content.find(SECTION_END_PREFIX))
                        content = "%s%s" % (content[0: start], content[end:])
                    report_output.write(content)
            os.remove(input_file)
            os.rename(output_file.name, input_file)
        except IOError as exc:
            os.remove(output_file.name)
            sys.exit("Failed to generate the output report. %s" % str(exc))


def upload_reports(report_types, output_dir):
    """Uploads the reports to their respective remote location

    """
    if GAZIBIT in report_types:
        if os.environ.get(GAZIBIT_TOKEN) is not None:
            output_file = os.path.join(output_dir, REPORTS_DIR,
                                       os.path.basename(GAZIBIT_PRIVATE))
            gazibit_upload(output_file, exit_flag=True)
            output_file = os.path.join(output_dir, REPORTS_DIR,
                                       os.path.basename(GAZIBIT_SHARED))
            gazibit_upload(output_file)
        else:
            sys.exit("To upload your gazibit report you need to"
                     " set your gazibit token in the GAZIBIT_TOKEN"
                     " environment variable. Failed to find GAZIBIT_TOKEN.")


def gazibit_upload(output_file, exit_flag=False):
    """Uploads the reports to gazibit. For `exit` set, exits if the file is
       not found

    """
    try:
        if os.path.isfile(output_file):
            with open(output_file, "rb") as output:
                content = output.read()
                response = requests.post(GAZIBIT_CREATE_URL,
                                         data=content, headers=GAZIBIT_HEADERS)
            code = response.status_code
            if code != HTTP_CREATED:
                sys.exit("Failed to upload the report. Request returned %s." %
                         code)
        elif exit_flag:
            sys.exit("Failed to find the report file")
    except ValueError:
        sys.exit("Malformed response")
    except requests.ConnectionError as exc:
        sys.exit("Connection error: %s" % str(exc))
    except requests.Timeout:
        sys.exit("Request timed out")
    except requests.RequestException:
        sys.exit("Ambiguous exception occurred")
    except IOError as excio:
        sys.exit("ERROR: failed to read report file: %s" % str(excio))


def evaluations_report(args):
    """Analyze cross-validations in directory and create evaluations report

    """
    metrics = []
    evaluations_json = []
    path = os.path.join(args.from_dir, ANALYZE_PATH)

    for _, directories, _ in os.walk(path):
        for directory in directories:
            file_name = os.path.join(path, directory, CROSS_VALIDATION_FILE)
            kfold_evaluation = json.load(open(file_name))
            kfold_evaluation['name'] = directory.replace('kfold', '#')
            evaluation = kfold_evaluation
            command = get_command_line(os.path.join(path, directory))
            feature, value = parse_test_feature(command)
            evaluation_json = {feature: value,
                               "directory": directory,
                               "time": os.path.getmtime(file_name)}
            kfold_evaluation[feature] = value
            evaluation = evaluation.get(MODEL_KEY, {})

            # read the applicable metrics and add the kfold number info
            for option in OPTIMIZE_OPTIONS:
                new_eval = copy.copy(evaluation_json)
                new_eval["measure"] = option
                if directory.startswith("node_th"):
                    new_eval["kfold"] = int(directory.replace("node_th", ""))
                elif directory.startswith("kfold"):
                    new_eval["kfold"] = int(directory.replace("kfold", ""))
                elif directory.startswith("random"):
                    new_eval["kfold"] = int(directory.replace("random", ""))
                if option in evaluation:
                    new_eval["value"] = evaluation[option]
                    metrics.append(new_eval)
                # check for averaged values too
                else:
                    option_pref = "%s%s" % (PREFIX, option)
                    if option_pref in evaluation:
                        new_eval["value"] = evaluation[option_pref]
                        metrics.append(new_eval)
            evaluations_json.append(kfold_evaluation)

    check_subdir(args.from_dir, REPORTS_DIR)
    check_subdir(os.path.join(args.from_dir, REPORTS_DIR), ANALYZE_DIR)
    # generate summary of metrics values
    json.dump(sorted(metrics, key=lambda x: x['time']),
              open(os.path.join(args.from_dir, REPORTS_DIR,
                                ANALYZE_DIR, METRICS_FILE), "w"))
    # generate list of evaluations
    json.dump(evaluations_json,
              open(os.path.join(args.from_dir, REPORTS_DIR, ANALYZE_DIR,
                                EVALUATIONS_JSON_FILE), "w"))

    # checks the global server directories
    check_subdir(HOME, SERVER_DIRECTORY.split(os.sep)[0])
    check_subdir(HOME, SERVER_DIRECTORY)

    # copy templates to directory
    basename = os.path.basename(ANALYZE_TEMPLATE)
    base_destination_dir = os.path.join(
        os.getcwd(), args.from_dir, REPORTS_DIR)
    destination_dir = os.path.join(base_destination_dir, ANALYZE_DIR)
    destination_file = os.path.join(destination_dir, basename)
    shutil.copyfile(ANALYZE_TEMPLATE, destination_file)
    dirname = os.path.join(HOME, SERVER_DIRECTORY)
    # current_directory = os.getcwd()
    os.chdir(dirname)
    symlink = tempfile.NamedTemporaryFile(dir=dirname).name
    try:
        os.symlink(base_destination_dir, symlink)
    except (AttributeError, OSError):
        os.mkdir(os.path.basename(symlink))
        shutil.copytree(destination_dir, os.path.join(symlink, ANALYZE_DIR))


    #saves the symlink file name in the current reports directory
    log_created_resources("symlink", base_destination_dir,
                          symlink, mode='a')

    # returns the link address relative to the server folder
    return os.path.join(os.path.basename(symlink), ANALYZE_DIR, basename)


def get_command_line(path):
    """Retrieving command line from the session file in the directory

    """
    try:
        command_file = os.path.join(path, SESSION_FILE)
        with open(command_file) as command_file:
            command = command_file.read()
        return command
    except IOError:
        sys.exit("Not enough information to build the report. Some files may"
                 " have been deleted.")

def parse_test_feature(command):
    """Parse the evolving feature from the command line text:
        - model_fields: list of model fields
        - nodes: number of nodes
        - random_candidates: number of random candidates for random forests
    """
    # try to find model_fields
    pattern = re.compile(r'--model-fields (.+?)\s--')
    model_fields = pattern.findall(command)
    model_fields = [] if not model_fields else model_fields[0]
    if model_fields:
        if model_fields.startswith('"'):
            model_fields = model_fields[1:]
        if model_fields.endswith('"'):
            model_fields = model_fields[:-1]
        return ("model_fields", model_fields)
    # try to find node_threshold
    pattern = re.compile(r'--node-threshold (\d+?)\s--')
    nodes = pattern.findall(command)
    if nodes:
        return ("nodes", nodes[0])
    # try to find random_candidates
    pattern = re.compile(r'--random-candidates (\d+?)\s--')
    random_candidates = pattern.findall(command)
    if random_candidates:
        return ("random_candidates", random_candidates[0])


REPORTS = {'gazibit': add_gazibit_links}
