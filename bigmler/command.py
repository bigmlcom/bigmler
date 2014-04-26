# -*- coding: utf-8 -*-
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

"""BigMLer - Command  and Stored Command class for command retrieval

"""
from __future__ import absolute_import


import os
import shlex


import bigmler.processing.args as a
import bigmler.utils as u


from bigml.multivote import PLURALITY


from bigmler.defaults import DEFAULTS_FILE
from bigmler.defaults import get_user_defaults
from bigmler.prediction import MAX_MODELS
from bigmler.options import create_parser


def tail(file_handler, window=1):
    """Returns the last n lines of a file.

    """
    bufsiz = 1024
    file_handler.seek(0, 2)
    file_bytes = file_handler.tell()
    size = window + 1
    block = -1
    data = []
    while size > 0 and file_bytes > 0:
        if (file_bytes - bufsiz > 0):
            # Seek back one whole bufsiz
            file_handler.seek(block * bufsiz, 2)
            # read BUFFER
            new_data = [file_handler.read(bufsiz)]
            new_data.extend(data)
            data = new_data
        else:
            # file too small, start from begining
            file_handler.seek(0, 0)
            # only read what was not read
            data.append(file_handler.read(file_bytes))
        lines_found = data[0].count('\n')
        size -= lines_found
        file_bytes -= bufsiz
        block -= 1
    return ''.join(data).splitlines()[-window:]


def get_log_reversed(file_name, stack_level):
    """Reads the line of a log file that has the chosen stack_level

    """
    lines_list = tail(open(file_name, "r"), window=(stack_level + 1))
    return lines_list[0]


class Command(object):
    """Objects derived from user given command and the user defaults file

    """
    def __init__(self, args, stored_command=None):
        self.stored = (args is None and
                       isinstance(stored_command, StoredCommand))
        self.args = args if not self.stored else stored_command.args
        self.resume = not self.stored and '--resume' in self.args
        self.defaults_file = (None if not self.stored else
                              os.path.join(stored_command.output_dir,
                                           DEFAULTS_FILE))
        self.user_defaults = get_user_defaults(self.defaults_file)
        self.command = (a.get_command_message(self.args) if not self.stored
                        else stored_command.command)
        self.parser, self.common_options = create_parser(
            general_defaults=self.user_defaults,
            constants={'NOW': a.NOW,
                       'MAX_MODELS': MAX_MODELS,
                       'PLURALITY': PLURALITY})
        self.flags, self.train_stdin, self.test_stdin = a.get_flags(self.args)


class StoredCommand(object):
    """Objects derived from a stored bigmler command

    """
    def __init__(self, resume_args, command_log, dirs_log, stack_level=0):
        """Constructor that extracts the command from the file

            ``command_log``: file for stored commands
            ``dirs_log``: file for associated work directories
            ``stack_level``: index in the stack for the command to be retrieved
        """
        self.resume_command = a.get_command_message(resume_args)
        self.command = get_log_reversed(command_log, stack_level)
        self.output_dir = get_log_reversed(dirs_log, stack_level)
        self.defaults_file = os.path.join(self.output_dir, DEFAULTS_FILE)
        self.args = shlex.split(self.command)[1:]

    def log_command(self, session_file=None):
        """Logging the resumed command in the sessions_log file

        """
        u.log_message(self.resume_command, log_file=session_file)
        message = "\nResuming command:\n%s\n\n" % self.command
        u.log_message(message, log_file=session_file, console=True)
        try:
            with open(self.defaults_file, 'r') as defaults_handler:
                contents = defaults_handler.read()
            message = "\nUsing the following defaults:\n%s\n\n" % contents
            u.log_message(message, log_file=session_file, console=True)
        except IOError:
            pass
