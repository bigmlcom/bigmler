# -*- coding: utf-8 -*-
#
# Copyright 2015-2017 BigML
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

"""BigMLer - reports processing dispatching

"""
from __future__ import absolute_import

import sys
import os
import SimpleHTTPServer
import thread
import webbrowser
import socket

import bigmler.processing.args as a

from bigmler.dispatcher import command_handling
from bigmler.reports import (evaluations_report, SERVER_DIRECTORY,
                             HOME, REPORTS_DIR, ANALYZE_TEMPLATE,
                             ANALYZE_DIR)
from bigmler.report.httpserver import StoppableHTTPServer
from bigmler.options.report import DEFAULT_PORT

COMMAND_LOG = u".bigmler_report"

DEFAULT_HOST = "127.0.0.1"


def get_report_url(args):
    """Checks whether there exist reports in the selected directory and creates
       them if they are not there.

    """
    try:
        with open(os.path.join(args.from_dir, REPORTS_DIR, "symlink")) as lnk:
            symlink = lnk.read()
            # currently there's only one template type
            return os.path.join(os.path.basename(symlink),
                                ANALYZE_DIR,
                                os.path.basename(ANALYZE_TEMPLATE))
    except IOError:
        return evaluations_report(args)


def report_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different report functions

    """

    command = command_handling(args, COMMAND_LOG)

    # Parses command line arguments.
    command_args = a.parse_and_check(command)

    port = DEFAULT_PORT if not command_args.port else command_args.port
    report_url = get_report_url(command_args)
    if not command_args.no_server:
        absolute_report_url = "http://%s:%s/%s" % (DEFAULT_HOST,
                                                   port, report_url)
        current_directory = os.getcwd()
        os.chdir(os.path.join(HOME, SERVER_DIRECTORY))
        httpd = None
        try:
            httpd = StoppableHTTPServer(\
                (DEFAULT_HOST, port),
                SimpleHTTPServer.SimpleHTTPRequestHandler)
            thread.start_new_thread(httpd.serve, ())
        except socket.error, exc:
            print exc
        # Open URL in new browser window
        webbrowser.open_new(absolute_report_url)
        # opens in default browser
        if httpd:
            raw_input("*********************************\n"
                      "Press <RETURN> to stop the server\n"
                      "*********************************\n")
        os.chdir(current_directory)
        if httpd:
            httpd.stop()
