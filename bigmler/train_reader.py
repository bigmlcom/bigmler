# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2013-2014 BigML
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
                 training_separator=None, multi_label_fields=None):
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
        self.training_reader = None
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

        first_row = self.next(reset=not training_set_header)
        self.row_length = len(first_row)

        if training_set_header:
            self.headers = [unicode(header, "utf-8") for header in first_row]
        else:
            self.headers = [("field_%s" % index) for index in
                            range(0, self.row_length)]

        self.multi_label_fields = sorted(self._get_columns(multi_label_fields))
        self.objective_column = self._get_columns([objective_field])[0]
        if not self.objective_column in self.multi_label_fields:
            self.multi_label_fields.append(self.objective_column)
        self.labels = labels
        self.fields_labels = self._get_labels()
        self.labels = self.fields_labels[self.objective_column]
        self.objective_name = self.headers[self.objective_column]

    def _get_columns(self, fields_list):
        """Receives a comma-separated list of fields given by name or
           column number and returns column number list

        """
        column_list = []
        if fields_list is None:
            return column_list
        if not isinstance(fields_list, list):
            fields_list = [fields_list]
        for field in fields_list:
            column = None
            if isinstance(field, int):
                column = field
            elif field is None:
                column = self.row_length - 1
            else:
                try:
                    column = self.headers.index(field)
                except ValueError:
                    sys.exit("The %s has been set as multi-label field but"
                             " it cannot be found in the headers row: \n %s" %
                             (field,
                              ", ".join([header.encode("utf-8")
                                         for header in self.headers])))
            column_list.append(column)
        return column_list

    def reset(self):
        """Starts a new csv reader object

        """
        try:
            self.training_set_handler.close()
        except (IOError, AttributeError):
            pass
        try:
            self.training_set_handler = open(self.training_set, "U")
            self.training_reader = csv.reader(
                self.training_set_handler, delimiter=self.training_separator,
                lineterminator="\n")
        except IOError:
            sys.exit("Error: cannot read training %s" % self.training_set)

    def __iter__(self):
        """Iterator method

        """
        return self

    def next(self, extended=False, reset=False):
        """Returns the next row. If extended is True, the row is extended with
           a list of booleans depending on whether the label is in the
           objective field value or not. If reset is True, the file is
           reopened and pointer starts at the beginning of the file.

        """
        row = self.training_reader.next()
        row = [value.strip() for value in row]
        if extended:
            if self.multi_label and self.labels is None:
                self.fields_labels = self._get_labels()

            for field_column in self.multi_label_fields:
                aggregated_field_value = row[field_column]
                field_values = aggregated_field_value.split(
                    self.label_separator)
                field_values = [value.decode("utf-8").strip() for
                                value in field_values]
                labels_row = [label in field_values for label in
                              self.fields_labels[field_column]]
                row.extend(labels_row)
            aggregated_value = row[self.objective_column]
            del row[self.objective_column]
            row.append(aggregated_value.strip())
        if reset:
            self.reset()
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

    def _get_labels(self):
        """Returns the list of labels in the multi-label fields

        """
        labels = {}
        labels[self.objective_column] = []
        for field_column in self.multi_label_fields:
            labels[field_column] = []
        for row in self:
            for field_column in self.multi_label_fields:
                labels = self._get_field_labels(row, labels,
                                                field_column,
                                                self.label_separator)
        if self.labels is None:
            self.labels = labels[self.objective_column]
        return labels

    def _get_field_labels(self, row, labels, field_column, separator):
        """Returns the list of labels in a multi-label field

        """
        field_value = row[field_column]
        if self.multi_label:
            new_labels = field_value.split(separator)
            new_labels = map(str.strip, new_labels)
            new_labels = [label.decode("utf-8").strip()
                          for label in new_labels]
            # TODO: clean user given missing tokens
            for label_index in range(0, len(new_labels)):
                if new_labels[label_index] == '':
                    del(new_labels[label_index])
            if new_labels != []:
                labels[field_column].extend(new_labels)
        else:
            labels[field_column].append(field_value)
        labels[field_column] = sorted(list(set(labels[field_column])))
        return labels

    def get_headers(self, objective_field=True):
        """Returns headers. If objective_field is False, the objective field
           header is removed.

        """
        if objective_field:
            return self.headers[:]
        new_headers = self.headers[:]
        del new_headers[self.objective_column]
        return new_headers

    def labels_columns(self):
        """List of tuples (label_column, label) describing the label extension

        """
        columns = []
        column = len(self.headers) - 1
        for field_column in self.multi_label_fields:
            labels = self.fields_labels[field_column]
            for label in labels:
                columns.append((column, label))
                column += 1

        return columns
