# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012, 2013 BigML
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

import csv
import sys
import cStringIO

from bigml.util import get_csv_delimiter

from bigmler.checkpoint import file_number_of_lines
from bigmler.utf8recoder import UTF8Recoder


class TestReader(object):
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
            self.encode = "utf-8"
            self.test_set_handler = UTF8Recoder(test_set, self.encode)
        else:
            self.encode = None
            self.test_set_handler = open(test_set, "U")
        self.test_set_header = test_set_header
        self.fields = fields
        self.objective_field = objective_field
        self.test_separator = (test_separator.decode("string_escape")
                               if test_separator is not None
                               else get_csv_delimiter())
        if len(self.test_separator) > 1:
            sys.exit("Only one character can be used as test data separator.")
        try:
            self.test_reader = csv.reader(self.test_set_handler,
                                          delimiter=self.test_separator,
                                          lineterminator="\n")
        except IOError:
            sys.exit("Error: cannot read test %s" % test_set)

        self.headers = None
        self.raw_headers = None
        self.exclude = []
        if test_set_header:
            self.headers = self.test_reader.next()
            self.raw_headers = self.headers
            # validate headers against model fields excluding objective_field,
            # that may be present or not
            objective_field = fields.field_column_number(objective_field)
            fields_names = [fields.fields[fields.field_id(i)]
                            ['name'] for i in
                            sorted(fields.fields_by_column_number.keys())
                            if i != objective_field]
            self.headers = [unicode(header, "utf-8")
                            for header in self.headers]
            self.exclude = [i for i in range(len(self.headers))
                            if not self.headers[i] in fields_names]

            self.exclude.reverse()
            if self.exclude:
                if len(self.headers) > len(self.exclude):
                    print (u"WARNING: predictions will be processed but some "
                           u"data might not be used. The used fields will be:"
                           u"\n\n%s"
                           u"\n\nwhile the headers found in the test file are:"
                           u"\n\n%s" %
                           (",".join(fields_names),
                            ",".join(self.headers))).encode("utf-8")
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

    def __iter__(self):
        """Iterator method

        """
        return self

    def next(self):
        """Returns the next row

        """
        row = self.test_reader.next()
        if self.encode:
            row = [unicode(item, self.encode).strip() for item in row]
        return row

    def dict(self, row):
        """Returns the row in a dict format according to the given headers

        """
        new_row = row[:]
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
