# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2013 BigML
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
"""TrainReader class

   Manages the training input data, its headers and labels if the objective
   field is a multi-label field

"""
from __future__ import absolute_import

import csv
import sys

from bigml.util import get_csv_delimiter

from bigmler.checkpoint import file_number_of_lines


class TrainReader(object):
    """Retrieves csv info and manages objective fields and multi-labels

    """
    def __init__(self, training_set, training_set_header, objective_field,
                 multi_label=False, labels=None, label_separator=None,
                 training_separator=None):
        """Builds a generator from a csv file 

           `training_set`: path to the training data file
           `training_set_header`: boolean, True means that headers are first
                                 row in the file
           `objective_field`: objective field column or field name
           `labels`: Fields object with the expected fields structure.
        """
        self.training_set = training_set
        self.training_set_header = training_set_header
        self.training_set_handler = None
        self.multi_label = multi_label

        self.training_separator = (training_separator.decode("string_escape")
                                   if training_separator is not None
                                   else get_csv_delimiter())
        if len(self.training_separator) > 1:
            sys.exit("Only one character can be used as test data separator.")
        # opening csv reader
        self.reset()
        self.label_separator = (label_separator.decode("string_escape")
                                if label_separator is not None
                                else get_csv_delimiter())

        if training_set_header:
            self.headers = [unicode(header, "utf-8") for header in
                            self.training_reader.next()]
        else:
            self.headers = [("field_%s" % index) for index in
                            range(0, len(self.training_reader.next()))]
            self.reset()
        if isinstance(objective_field, int):
            self.objective_column = self.objective_field
        elif objective_field is None:
            if self.headers is not None:
                self.objective_column = len(self.headers) - 1
            else:
                self.objective_column = len(self.training_reader.next()) - 1
                self.reset()
        else:
            try:
                self.objective_column = self.headers.index(objective_field)
            except ValueError:
                sys.exit("The %s has been set as objective field but"
                         " it cannot be found in the headers row: \n %s" %
                         (objective_field, 
                          ", ".join(self.headers.encode("utf-8"))))

        self.labels = (map(lambda x: x.strip(), labels.split(',')) 
                       if labels is not None else None)
        self.labels = self.get_labels()


    def reset(self):
        """Starts a new csv reader object

        """
        try:
            self.training_set_handler.close()
        except (IOError, AttributeError):
            pass
        self.training_set_handler = open(self.training_set, "U")
        try:
            self.training_reader = csv.reader(
                self.training_set_handler, delimiter=self.training_separator,
                lineterminator="\n")
        except IOError:
            sys.exit("Error: cannot read training %s" % training_set)

    def __iter__(self):
        """Iterator method

        """
        return self

    def next(self, extended=False):
        """Returns the next row. If extended is True, the row is extended with
           a list of booleans depending on whether the label is in the
           objective field value or not.

        """
        row = self.training_reader.next()
        if extended:
            if self.multi_label and self.labels is None:
                self.labels = self.get_labels()
            aggregated_value = row[self.objective_column]
            objective_values = aggregated_value.split(self.label_separator)
            del(row[self.objective_column])
            labels_row = [label in objective_values for label in self.labels]
            row.extend(labels_row)
        return row

    def number_of_rows(self):
        """Returns the number of rows in the test file

        """
        rows = file_number_of_lines(self.training_set)
        if self.training_set_header:
            rows -= 1
        return rows

    def has_headers(self):
        """Returns whether the training set file has a headers row

        """
        return self.training_set_header

    def get_labels(self):
        """Returns the list of labels in the objective field

        """
        if self.labels is None:
            labels = []
            for row in self:
                objective_value = row[self.objective_column]
                if self.multi_label == False:
                    labels.append(objective_value)
                else:
                    new_labels = objective_value.split(self.label_separator)
                    # TODO: clean user given missing tokens
                    for index in range(0, len(new_labels)):
                        if new_labels[index] == '':
                            del(new_labels[index])
                    if new_labels != []:
                        labels.extend(new_labels)
            self.labels = list(set(labels)) 
        return self.labels

    def get_headers(self, objective_field=True):
        """Returns headers. If objective_field is False, it is excluded from
           the headers set

        """
        if objective_field:
            return self.headers
        new_headers = self.headers[:]
        del new_headers[self.objective_column]
        return new_headers
