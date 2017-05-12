# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017 BigML
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

import inspect
import json
import pprint

COPYRIGHT = """\
# -*- coding: utf-8 -*-
#
# Copyright BigML
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

"""

IMPORTS = """\
import math
import re

"""

from bigml.util import cast
from bigml.predicate import TM_FULL_TERM, TM_ALL
from bigml.cluster import parse_terms, parse_items, OPTIONAL_FIELDS
from bigml.logistic import LogisticRegression, get_unique_terms, balance_input

CONSTANTS = """
EXPANSION_ATTRIBUTES = {"categorical": "categories", "text": "tag_cloud",
                        "items": "items"}
TM_FULL_TERM = %s
TM_ALL = %s
OPTIONAL_FIELDS = %s

""" % (repr(TM_FULL_TERM), repr(TM_ALL), repr(OPTIONAL_FIELDS))

FUNCTIONS = [cast, parse_terms, parse_items, get_unique_terms,
             balance_input]

CLASS_DEFINITION = """

class BasicLR(object):

    def __init__(self, lr_dict):
        self.__dict__ = lr_dict

"""

CLASS_METHODS = ["predict", "filter_input_data", "category_probability",
                 "get_unique_terms", "get_coefficients", "normalize"]


def summary_example(field):
    """Returns an example of a value in the summary of the field

    """
    distribution_keys = ["categories", "counts", "bins", "tag_cloud", "items"]
    for key in distribution_keys:
        if key in field["summary"]:
            return repr(field["summary"][key][0][0])


class PythonLR(LogisticRegression):

    def plug_in(self, out):
        """Write logistic regression predict method

        """
        out.write(COPYRIGHT)
        out.write(IMPORTS)
        out.write(CONSTANTS)

        for function in FUNCTIONS:
            out.write(inspect.getsource(function))
            out.write("\n\n")
        out.write(CLASS_DEFINITION)
        for method in CLASS_METHODS:
            out.write(inspect.getsource(getattr(self, method)))
            out.write("\n")

        out.write("logistic_regression_json = ")
        pprint.pprint(self.__dict__, out)
        out.write("\n")
        example_field_id = self.input_fields[0]
        if example_field_id == self.objective_id:
            example_field_id = self.input_fields[1]
        example_field_name = self.fields[example_field_id]["name"]
        example = summary_example(self.fields[example_field_id])
        out.write( \
            "local_logistic = BasicLR(logistic_regression_json)\n"
            "# place here your input data as a dictionary\n"
            "input_data = {\"%s\": %s}\n" % (example_field_name, example))
        out.write("local_logistic.predict(input_data)\n")
