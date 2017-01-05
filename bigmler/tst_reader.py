# -*- coding: utf-8 -*-
#
# Copyright 2012-2017 BigML
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
"""TestReader class

   Manages the test input data, its headers and checks them against the
   model fields data to build the dict input_data.

"""
from __future__ import absolute_import

import sys

from bigml.util import get_csv_delimiter
from bigml.io import UnicodeReader

from bigmler.utils import PYTHON3, FILE_ENCODING, SYSTEM_ENCODING
from bigmler.utils import decode2
from bigmler.checkpoint import file_number_of_lines
from bigmler.utf8recoder import UTF8Recoder


class TstReader(object):
    """Retrieves csv info and builds a input data dict

    """
    def __init__(self, test_set, test_set_header, fields, objective_field,
                 test_separator=None):
        """Builds a generator from a csv file and the fields' model structure

           `test_set`: path to the test data file
           `test_set_header`: boolean, True means that headers are first row
                              in the file
           `fields`: Fields object with the expected fields structure.
           `objective_field`: field_id of the objective field
        """
        self.test_set = test_set
        if test_set.__class__.__name__ == "StringIO":
            self.encode = None
            self.test_set = UTF8Recoder(test_set, SYSTEM_ENCODING)
        else:
            self.encode = None if PYTHON3 else FILE_ENCODING
        self.test_set_header = test_set_header
        self.fields = fields
        if (objective_field is not None and
                not objective_field in fields.fields):
            try:
                objective_field = fields.field_id(objective_field)
            except ValueError, exc:
                sys.exit(exc)
        self.objective_field = objective_field
        if test_separator and not PYTHON3:
            test_separator = decode2(test_separator, encoding="string_escape")
        self.test_separator = (test_separator
                               if test_separator is not None
                               else get_csv_delimiter())
        if len(self.test_separator) > 1:
            sys.exit("Only one character can be used as test data separator.")
        try:
            self.test_reader = UnicodeReader(self.test_set,
                                             delimiter=self.test_separator,
                                             lineterminator="\n").open_reader()
        except IOError:
            sys.exit("Error: cannot read test %s" % test_set)

        self.headers = None
        self.raw_headers = None
        self.exclude = []
        if test_set_header:
            self.headers = self.test_reader.next()
            # validate headers against model fields excluding objective_field,
            # that may be present or not
            if objective_field is not None:
                objective_field = fields.field_column_number(objective_field)
            try:
                fields_names = [fields.fields[fields.field_id(i)]
                                ['name'] for i in
                                sorted(fields.fields_by_column_number.keys())
                                if objective_field is None or
                                i != objective_field]
            except ValueError, exc:
                sys.exit(exc)
            self.raw_headers = self.headers[:]

            self.exclude = [i for i in range(len(self.headers))
                            if not self.headers[i] in fields_names]

            self.exclude.reverse()
            if self.exclude:
                if len(self.headers) > len(self.exclude):
                    for index in self.exclude:
                        del self.headers[index]
                else:
                    raise Exception((u"No test field matches the model fields."
                                     u"\nThe expected fields are:\n\n%s\n\n"
                                     u"while "
                                     u"the headers found in the test file are:"
                                     u"\n\n%s\n\n"
                                     u"Use --no-test-header flag if first li"
                                     u"ne should not be interpreted as"
                                     u" headers." %
                                     (",".join(fields_names),
                                      ",".join(self.headers))).encode("utf-8"))
        else:
            columns = fields.fields_columns[:]
            if objective_field is not None:
                if fields.field_column_number(objective_field) in columns:
                    columns.remove(fields.field_column_number(objective_field))
            self.headers = [fields.fields_by_column_number[column] for
                            column in columns]
            self.raw_headers = self.headers

    def __iter__(self):
        """Iterator method

        """
        return self

    def next(self):
        """Returns the next row

        """
        row = self.test_reader.next()
        return row

    def dict(self, row, filtering=True):
        """Returns the row in a dict format according to the given headers

        """
        new_row = row[:]
        if not filtering:
            if self.test_set_header:
                headers = self.raw_headers
            else:
                headers = [self.fields.fields_by_column_number[column] for
                           column in self.fields.fields_columns]
            return dict(zip(headers, new_row))
        for index in self.exclude:
            del new_row[index]
        return self.fields.pair(new_row, self.headers, self.objective_field)

    def number_of_tests(self):
        """Returns the number of tests in the test file

        """
        tests = file_number_of_lines(self.test_set)
        if self.test_set_header:
            tests -= 1
        return tests

    def has_headers(self):
        """Returns whether the test set file has a headers row

        """
        return self.test_set_header

    def close(self):
        """Closing file handler

        """
        self.test_reader.close_reader()
