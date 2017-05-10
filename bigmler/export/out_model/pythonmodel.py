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

"""Model level output for python

This module defines functions that generate python code to make local
predictions
"""
import sys

from bigml.tree_utils import slugify, INDENT, sort_fields, docstring_comment, \
    MAX_ARGS_LENGTH, TERM_OPTIONS
from bigml.model import Model

from bigmler.export.out_tree.pythontree import PythonTree

PYTHON_CONV = {
    "double": "locale.atof",
    "float": "locale.atof",
    "integer": "lambda x: int(locale.atof(x))",
    "int8": "lambda x: int(locale.atof(x))",
    "int16": "lambda x: int(locale.atof(x))",
    "int32": "lambda x: int(locale.atof(x))",
    "int64": "lambda x: long(locale.atof(x))",
    "day": "lambda x: int(locale.atof(x))",
    "month": "lambda x: int(locale.atof(x))",
    "year": "lambda x: int(locale.atof(x))",
    "hour": "lambda x: int(locale.atof(x))",
    "minute": "lambda x: int(locale.atof(x))",
    "second": "lambda x: int(locale.atof(x))",
    "millisecond": "lambda x: int(locale.atof(x))",
    "day-of-week": "lambda x: int(locale.atof(x))",
    "day-of-month": "lambda x: int(locale.atof(x))"
}

PYTHON_TYPE = {
    "double": "float",
    "float": "float",
    "integer": "int",
    "int8": "int",
    "int16": "int",
    "int32": "int",
    "int64": "long",
    "day": "int",
    "month": "int",
    "year": "int",
    "hour": "int",
    "minute": "int",
    "second": "int",
    "millisecond": "int",
    "day-of-week": "int",
    "day-of-month": "int"
}


PYTHON_KEYWORDS = [
    "and",
    "assert",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "exec",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "not",
    "or",
    "pass",
    "print",
    "raise",
    "return",
    "try",
    "while ",
    "Data",
    "Float",
    "Int",
    "Numeric",
    "Oxphys",
    "array",
    "close",
    "float",
    "int",
    "input",
    "open",
    "range",
    "type",
    "write",
    "zeros",
    "acos",
    "asin",
    "atan",
    "cos",
    "e",
    "exp",
    "fabs",
    "floor",
    "log",
    "log10",
    "pi",
    "sin",
    "sqrt",
    "tan"
]


class PythonModel(Model):


    def __init__(self, model, api=None, fields=None):
        """Empty attributes to be overriden

        """
        self.tree_class = PythonTree
        Model.__init__(self, model, api, fields)

    def plug_in(self, out=sys.stdout, hadoop=False,
                filter_id=None, subtree=True):
        """Returns a basic python function that implements the model.

        `out` is file descriptor to write the python code.

        """
        ids_path = self.get_ids_path(filter_id)
        if hadoop:
            return (self.hadoop_python_mapper(out=out,
                                              ids_path=ids_path,
                                              subtree=subtree) or
                     self.hadoop_python_reducer(out=out))
        else:
            return self.python(out, self.docstring(), ids_path=ids_path,
                               subtree=subtree)


    def hadoop_python_mapper(self, out=sys.stdout, ids_path=None,
                             subtree=True):
        """Returns a hadoop mapper header to make predictions in python

        """
        input_fields = [(value, key) for (key, value) in
                        sorted(self.inverted_fields.items(),
                               key=lambda x: x[1])]
        parameters = [value for (key, value) in
                      input_fields if key != self.tree.objective_id]
        args = []
        for field in input_fields:
            slug = slugify(self.tree.fields[field[0]]['name'])
            self.tree.fields[field[0]].update(slug=slug)
            if field[0] != self.tree.objective_id:
                args.append("\"" + self.tree.fields[field[0]]['slug'] + "\"")
        output = \
u"""#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import csv
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class CSVInput(object):
    \"\"\"Reads and parses csv input from stdin

       Expects a data section (without headers) with the following fields:
       %s

       Data is processed to fall into the corresponding input type by applying
       INPUT_TYPES, and per field PREFIXES and SUFFIXES are removed. You can
       also provide strings to be considered as no content markers in
       MISSING_TOKENS.
    \"\"\"
    def __init__(self, input=sys.stdin):
        \"\"\" Opens stdin and defines parsing constants

        \"\"\"
        try:
            self.reader = csv.reader(input, delimiter=',', quotechar='\"')
""" % ",".join(parameters)

        output += u"\n%sself.INPUT_FIELDS = [%s]\n" % \
            ((INDENT * 3), (",\n " + INDENT * 8).join(args))

        input_types = []
        prefixes = []
        suffixes = []
        count = 0
        fields = self.tree.fields
        for key in [field[0] for field in input_fields
                    if field[0] != self.tree.objective_id]:
            input_type = ('None' if not fields[key]['datatype'] in
                          PYTHON_CONV
                          else PYTHON_CONV[fields[key]['datatype']])
            input_types.append(input_type)
            if 'prefix' in fields[key]:
                prefixes.append("%s: %s" % (count,
                                            repr(fields[key]['prefix'])))
            if 'suffix' in fields[key]:
                suffixes.append("%s: %s" % (count,
                                            repr(fields[key]['suffix'])))
            count += 1
        static_content = "%sself.INPUT_TYPES = [" % (INDENT * 3)
        formatter = ",\n%s" % (" " * len(static_content))
        output += u"\n%s%s%s" % (static_content,
                                 formatter.join(input_types),
                                 "]\n")
        static_content = "%sself.PREFIXES = {" % (INDENT * 3)
        formatter = ",\n%s" % (" " * len(static_content))
        output += u"\n%s%s%s" % (static_content,
                                 formatter.join(prefixes),
                                 "}\n")
        static_content = "%sself.SUFFIXES = {" % (INDENT * 3)
        formatter = ",\n%s" % (" " * len(static_content))
        output += u"\n%s%s%s" % (static_content,
                                 formatter.join(suffixes),
                                 "}\n")
        output += \
u"""            self.MISSING_TOKENS = ['?']
        except Exception, exc:
            sys.stderr.write(\"Cannot read csv\"
                             \" input. %s\\n\" % str(exc))

    def __iter__(self):
        \"\"\" Iterator method

        \"\"\"
        return self

    def next(self):
        \"\"\" Returns processed data in a list structure

        \"\"\"
        def normalize(value):
            \"\"\"Transforms to unicode and cleans missing tokens
            \"\"\"
            value = unicode(value.decode('utf-8'))
            return \"\" if value in self.MISSING_TOKENS else value

        def cast(function_value):
            \"\"\"Type related transformations
            \"\"\"
            function, value = function_value
            if not len(value):
                return None
            if function is None:
                return value
            else:
                return function(value)

        try:
            values = self.reader.next()
        except StopIteration:
            raise StopIteration()
        if len(values) < len(self.INPUT_FIELDS):
            sys.stderr.write(\"Found %s fields when %s were expected.\\n\" %
                             (len(values), len(self.INPUT_FIELDS)))
            raise StopIteration()
        else:
            values = values[0:len(self.INPUT_FIELDS)]
        try:
            values = map(normalize, values)
            for key in self.PREFIXES:
                prefix_len = len(self.PREFIXES[key])
                if values[key][0:prefix_len] == self.PREFIXES[key]:
                    values[key] = values[key][prefix_len:]
            for key in self.SUFFIXES:
                suffix_len = len(self.SUFFIXES[key])
                if values[key][-suffix_len:] == self.SUFFIXES[key]:
                    values[key] = values[key][0:-suffix_len]
            function_tuples = zip(self.INPUT_TYPES, values)
            values = map(cast, function_tuples)
            data = {}
            for i in range(len(values)):
                data.update({self.INPUT_FIELDS[i]: values[i]})
            return data
        except Exception, exc:
            sys.stderr.write(\"Error in data transformations. %s\\n\" % str(exc))
            return False
\n\n
"""
        out.write(output)
        out.flush()

        self.tree.python(out, self.docstring(),
                         input_map=True,
                         ids_path=ids_path,
                         subtree=subtree)

        output = \
u"""
csv = CSVInput()
for values in csv:
    if not isinstance(values, bool):
        print u'%%s\\t%%s' %% (repr(values), repr(predict_%s(values)))
\n\n
""" % fields[self.tree.objective_id]['slug']
        out.write(output)
        out.flush()

    def hadoop_python_reducer(self, out=sys.stdout):
        """Returns a hadoop reducer to make predictions in python

        """
        output = \
u"""#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

count = 0
previous = None

def print_result(values, prediction, count):
    \"\"\"Prints input data and predicted value as an ordered list.

    \"\"\"
    result = \"[%s, %s]\" % (values, prediction)
    print u\"%s\\t%s\" % (result, count)

for line in sys.stdin:
    values, prediction = line.strip().split('\\t')
    if previous is None:
        previous = (values, prediction)
    if values != previous[0]:
        print_result(previous[0], previous[1], count)
        previous = (values, prediction)
        count = 0
    count += 1
if count > 0:
    print_result(previous[0], previous[1], count)
"""
        out.write(output)
        out.flush()

    def term_analysis_body(self, term_analysis_predicates,
                           item_analysis_predicates):
        """ Writes auxiliary functions to handle the term and item
        analysis fields

        """
        body = u""
        # static content
        body += u"""
    import re
"""
        if term_analysis_predicates:
            body += """
    tm_tokens = '%s'
    tm_full_term = '%s'
    tm_all = '%s'

    def term_matches(text, field_name, term):
        \"\"\" Counts the number of occurences of term and its variants in text

        \"\"\"
        forms_list = term_forms[field_name].get(term, [term])
        options = term_analysis[field_name]
        token_mode = options.get('token_mode', tm_tokens)
        case_sensitive = options.get('case_sensitive', False)
        first_term = forms_list[0]
        if token_mode == tm_full_term:
            return full_term_match(text, first_term, case_sensitive)
        else:
            # In token_mode='all' we will match full terms using equals and
            # tokens using contains
            if token_mode == tm_all and len(forms_list) == 1:
                pattern = re.compile(r'^.+\\b.+$', re.U)
                if re.match(pattern, first_term):
                    return full_term_match(text, first_term, case_sensitive)
            return term_matches_tokens(text, forms_list, case_sensitive)


    def full_term_match(text, full_term, case_sensitive):
        \"\"\"Counts the match for full terms according to the case_sensitive
              option

        \"\"\"
        if not case_sensitive:
            text = text.lower()
            full_term = full_term.lower()
        return 1 if text == full_term else 0

    def get_tokens_flags(case_sensitive):
        \"\"\"Returns flags for regular expression matching depending on text
              analysis options

        \"\"\"
        flags = re.U
        if not case_sensitive:
            flags = (re.I | flags)
        return flags


    def term_matches_tokens(text, forms_list, case_sensitive):
        \"\"\" Counts the number of occurrences of the words in forms_list in
               the text

        \"\"\"
        flags = get_tokens_flags(case_sensitive)
        expression = ur'(\\b|_)%%s(\\b|_)' %% '(\\\\b|_)|(\\\\b|_)'.join(forms_list)
        pattern = re.compile(expression, flags=flags)
        matches = re.findall(pattern, text)
        return len(matches)

""" % (TM_TOKENS, TM_FULL_TERM, TM_ALL)

            term_analysis_options = set(map(lambda x: x[0],
                                           term_analysis_predicates))
            print " \n\n{0}\n\n".format(term_analysis_options)
            term_analysis_predicates = set(term_analysis_predicates)
            body += """
    term_analysis = {"""
            for field_id in term_analysis_options:
                field = self.fields[field_id]
                body += """
        \"%s\": {""" % field['slug']
                for option in field['term_analysis']:
                    if option in TERM_OPTIONS:
                        body += """
            \"%s\": %s,""" % (option, repr(field['term_analysis'][option]))
                body += """
        },"""
            body += """
    }"""
            body += """
    term_forms = {"""
            term_forms = {}
            fields = self.fields
            for field_id, term in term_analysis_predicates:
                alternatives = []
                field = fields[field_id]
                if field['slug'] not in term_forms:
                    term_forms[field['slug']] = {}
                all_forms = field['summary'].get('term_forms', {})
                if all_forms:
                    alternatives = all_forms.get(term, [])
                    if alternatives:
                        terms = [term]
                        terms.extend(all_forms.get(term, []))
                        term_forms[field['slug']][term] = terms
            for field in term_forms:
                body += """
        \"%s\": {""" % field
                for term in term_forms[field]:
                    body += """
            u\"%s\": %s,""" % (term, term_forms[field][term])
                body += """
        },"""
            body += """
    }
"""
        if item_analysis_predicates:
            body += """
    def item_matches(text, field_name, item):
        \"\"\" Counts the number of occurrences of item in text

        \"\"\"
        options = item_analysis[field_name]
        separator = options.get('separator', ' ')
        regexp = options.get('separator_regexp')
        if regexp is None:
            regexp = r\"%s\" % re.escape(separator)
        return count_items_matches(text, item, regexp)


    def count_items_matches(text, item, regexp):
        \"\"\" Counts the number of occurrences of the item in the text

        \"\"\"
        expression = r'(^|%s)%s($|%s)' % (regexp, item, regexp)
        pattern = re.compile(expression, flags=re.U)
        matches = re.findall(pattern, text)
        return len(matches)
"""

            item_analysis_options = set(map(lambda x: x[0],
                                        item_analysis_predicates))
            item_analysis_predicates = set(item_analysis_predicates)
            body += """
    item_analysis = {"""
            for field_id in item_analysis_options:
                field = self.fields[field_id]
                body += """
        \"%s\": {""" % field['slug']
                for option in field['item_analysis']:
                    if option in ITEM_OPTIONS:
                        body += """
            \"%s\": %s,""" % (option, repr(field['item_analysis'][option]))
                body += """
        },"""
            body += """
    }
"""
        return body

    def python(self, out, docstring, ids_path=None, subtree=True):
        """Writes a python function that implements the model.

        """
        args = []
        parameters = sort_fields(self.fields)
        input_map = len(parameters) > MAX_ARGS_LENGTH
        reserved_keywords = PYTHON_KEYWORDS if not input_map else None
        prefix = "_" if not input_map else ""
        for field in [(key, val) for key, val in parameters]:
            field_name_to_show = self.fields[field[0]]['name'].strip()
            if field_name_to_show == "":
                field_name_to_show = field[0]
            slug = slugify(field_name_to_show,
                           reserved_keywords=reserved_keywords, prefix=prefix)
            self.fields[field[0]].update(slug=slug)
            if not input_map:
                if field[0] != self.objective_id:
                    args.append("%s=None" % (slug))
        if input_map:
            args.append("data={}")
        function_name = self.fields[self.objective_id]['slug']
        if prefix == "_" and function_name[0] == prefix:
            function_name = function_name[1:]
        if function_name == "":
            function_name = "field_" + self.objective_id

        predictor_definition = (u"def predict_%s" %
                                function_name)
        depth = len(predictor_definition) + 1
        predictor = u"%s(%s):\n" % (predictor_definition,
                                   (",\n" + " " * depth).join(args))
        predictor_doc = (INDENT + u"\"\"\" " + docstring +
                         u"\n" + INDENT + u"\"\"\"\n")
        body, term_analysis_predicates, item_analysis_predicates = \
            self.tree.plug_in_body(input_map=input_map,
                                   ids_path=ids_path,
                                   subtree=subtree)
        terms_body = ""
        if term_analysis_predicates or item_analysis_predicates:
            terms_body = self.term_analysis_body(term_analysis_predicates,
                                                 item_analysis_predicates)
        predictor += predictor_doc + terms_body + body
        out.write(predictor)
        out.flush()
