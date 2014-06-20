# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2014 BigML
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
from __future__ import absolute_import


import os
import sys
import tempfile
import shutil
import requests

import bigml.api

from bigmler.utils import is_shared, check_dir, get_url


URL_TEMPLATE = "%%BIGML_%s%%"
SECTION_START = "\n%%BIGML_START_%s%%"
SECTION_START_PREFIX = SECTION_START[2: 15]
SECTION_END = "\n%%BIGML_END_%s%%"
SECTION_END_PREFIX = SECTION_END[2: 13]
TITLE_TAG = "%REPORT_TITLE%"
DESC_TAG = "%REPORT_DESC%"
REPORTS_DIR = "reports"
EMBEDDED_RESOURCES = ["MODEL"]
GAZIBIT = "gazibit"
BIGMLER_SCRIPT = os.path.dirname(__file__)
GAZIBIT_PRIVATE = "%s/static/gazibit_private.json" % BIGMLER_SCRIPT
GAZIBIT_SHARED = "%s/static/gazibit_shared.json" % BIGMLER_SCRIPT
GAZIBIT_TOKEN = "GAZIBIT_TOKEN"
GAZIBIT_CREATE_URL = "http://gazibit.com/api/v1/create"
GAZIBIT_HEADERS = {"X-Gazibit-API-Token": os.environ.get(GAZIBIT_TOKEN),
                   "Expect": "100-continue",
                   'content-type': 'application/x-www-form-urlencoded',
                   'Content-Length': 12544,
                   'User-Agent': ('curl/7.22.0 (x86_64-pc-linux-gnu)'
                                  ' libcurl/7.22.0 OpenSSL/1.0.1'
                                  ' zlib/1.2.3.4 libidn/1.23 librtmp/2.3')}

XPOS_TEMPLATE = "%XPOS%"

GAZIBIT_TEMPLATE = "%s/static/gazibit.json" % BIGMLER_SCRIPT
IMPRESS_TEMPLATE = "%s/static/impress.html" % BIGMLER_SCRIPT
REVEAL_TEMPLATE = "%s/static/reveal.html" % BIGMLER_SCRIPT


TEMPLATES = {'gazibit':GAZIBIT_TEMPLATE,'impress':IMPRESS_TEMPLATE,'reveal':REVEAL_TEMPLATE}
HTTP_CREATED = 201

def private_name(path):
    head,ext = os.path.splitext(path)
    return head + '_private' + ext

def shared_name(path):
    head,ext = os.path.splitext(path)
    return head + '_shared' + ext

def report(report_types_list, output_dir=None, resource=None):
    """Generate the requested reports

    """
    shared = is_shared(resource)
    for report_type in report_types_list:
        REPORTS[report_type](resource,output_dir, shared)

def get_or_create_template(template,path,shared=False):
    tmppath = os.path.join(path,os.path.basename(template))
    head,ext = os.path.splitext(tmppath)
    if shared:
        realpath = head + '_shared' + ext
    else:
        realpath = head + '_private' + ext
    if not os.path.isfile(realpath):
        with open(template) as fid:
            with open(realpath,'w') as output_file:
                content = fid.read()
                if shared:
                    content = content.replace(TITLE_TAG,"BigMLer Report - Shared Resources")
                    content = content.replace(DESC_TAG,"BigMLer results report: shared resources")
                else:
                    content = content.replace(TITLE_TAG,"BigMLer Report - Private Resources")
                    content = content.replace(DESC_TAG,"BigMLer results report: private resources")
                output_file.write(content)
    return realpath


def add_report_links(resource,report_type,output_dir=None,shared=False,replace_extras=None):
    """ Adds the link to the resource in the corresponding section of the
    report template

    """
    try:
        tmp = TEMPLATES[report_type]
        path = check_dir(os.path.join(output_dir,
                                      REPORTS_DIR,
                                      os.path.basename(tmp)))
        input_file = get_or_create_template(tmp,path,shared)
        output_file = tempfile.NamedTemporaryFile(
            mode="w", dir=output_dir, delete=False)

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
    except IOError, exc:
        os.remove(output_file.name)
        sys.exit("Failed to generate the %s output report. %s"
                % (report_type,str(exc)))

def add_gazibit_links(resource, output_dir=None, shared=False):
    add_report_links(resource,'gazibit',
                     output_dir=output_dir,shared=shared)

def add_impress_links(resource, output_dir=None, shared=False):
    add_report_links(resource,'impress',
                     output_dir=output_dir,shared=shared)

def add_reveal_links(resource, output_dir=None, shared=False):
    add_report_links(resource,'reveal',
                     output_dir=output_dir,shared=shared)


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
                    if 'impress' in input_file:
                        x = 0
                        while content.find(XPOS_TEMPLATE) > 0:
                            content = content.replace(XPOS_TEMPLATE,str(x),1)
                            x += 1200
                    report_output.write(content)
            os.remove(input_file)
            os.rename(output_file.name, input_file)
        except IOError, exc:
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
    except IOError, excio:
        sys.exit("ERROR: failed to read report file: %s" % str(excio))
    except ValueError:
        sys.exit("Malformed response")
    except requests.ConnectionError, exc:
        sys.exit("Connection error: %s" % str(exc))
    except requests.Timeout:
        sys.exit("Request timed out")
    except requests.RequestException:
        sys.exit("Ambiguous exception occurred")


REPORTS = {'gazibit': add_gazibit_links,'impress':add_impress_links,'reveal':add_reveal_links}
