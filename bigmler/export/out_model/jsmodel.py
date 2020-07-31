# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017-2020 BigML
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

"""Tree level output for JavaScript

This module defines functions that generate JavaScript code to make local
predictions
"""

import sys

from unidecode import unidecode

from bigml.tree_utils import (
    to_camel_js, sort_fields, docstring_comment,
    INDENT, MAX_ARGS_LENGTH, TERM_OPTIONS)

ITEM_OPTIONS = ["separator", "separator_regexp"]

from bigml.model import Model

from bigmler.export.out_tree.jstree import JsTree
from bigmler.reports import BIGMLER_SCRIPT

# templates for static javascript
TERM_TEMPLATE = "%s/static/out_model/term_analysis.js" % BIGMLER_SCRIPT
ITEMS_TEMPLATE = "%s/static/out_model/items_analysis.js" % BIGMLER_SCRIPT

class JsModel(Model):

    def __init__(self, model, api=None, fields=None):
        self.tree_class = JsTree
        Model.__init__(self, model, api, fields)

    def js_comment(self):
        """Returns docstring in a javascript style

        """
        return docstring_comment(self)

    def js_pre_body(self, input_map=False):
        """Implements javascript signature.

        """
        docstring = self.js_comment()
        output = \
"""
/**
*  %s
*  %s
*/
""" % (docstring,
       self.description.replace('\n', '\n *  '))

        output += self.js_signature(input_map=input_map)
        output += " {\n"
        return output

    def plug_in(self, out=sys.stdout, hadoop=False,
                filter_id=None, subtree=True):
        """Generates a basic javascript implementation of local predictions

        `out` is file descriptor to write the javascript code.

        """
        # fill the camelcase variable names with the JS_KEYWORDS restrictions
        objective_field = self.tree.fields[self.tree.objective_id]
        camelcase = to_camel_js(unidecode(objective_field['name']), False)
        objective_field['CamelCase'] = camelcase
        for field in [(key, val) for key, val in
                      sort_fields(self.tree.fields)]:
            field_obj = self.tree.fields[field[0]]
            field_obj['camelCase'] = to_camel_js(unidecode(field_obj['name']))

        body, term_analysis_predicates, item_analysis_predicates = \
            self.tree.plug_in_body()
        terms_body = ""
        items_body = ""
        if term_analysis_predicates:
            terms_body = self.js_term_analysis_body(term_analysis_predicates)
        if item_analysis_predicates:
            items_body = self.js_item_analysis_body(item_analysis_predicates)
        output = self.js_pre_body()
        output += terms_body + items_body + body
        output += "%sreturn null;\n}\n" % INDENT
        out.write(output)
        out.flush()

    def js_signature(self, input_map=False):
        """Returns a the javascript signature for a prediction method.

        """
        objective_field = self.tree.fields[self.tree.objective_id]
        if not 'CamelCase' in objective_field:
            camelcase = to_camel_js(unidecode(objective_field['name']), False)
            objective_field['CamelCase'] = camelcase

        output = "function predict%s(" % objective_field['CamelCase']

        args = []
        if len(self.tree.fields) > MAX_ARGS_LENGTH or input_map:
            args.append("data")
        else:
            for field in [(key, val) for key, val in
                          sort_fields(self.tree.fields)]:
                field_obj = self.tree.fields[field[0]]
                if not 'camelCase' in field_obj:
                    field_obj['camelCase'] = to_camel_js( \
                        unidecode(field_obj['name']))
                if field[0] != self.tree.objective_id:
                    args.append("%s" % field_obj['camelCase'])
        args_string = ", ".join(args)
        output += args_string + ")"

        return output

    def js_term_analysis_body(self, term_analysis_predicates):
        """ Generates the string of
            auxiliary functions to handle the term analysis fields

        """
        term_analysis_options = set([x[0] for x in term_analysis_predicates])
        term_analysis_predicates = set(term_analysis_predicates)

        body = ""
        # static content
        body += """
    var TERM_ANALYSIS = {"""
        for field_id in term_analysis_options:
            field = self.tree.fields[field_id]
            body += """
        \"%s\": {""" % field['camelCase']
            options = sorted(field['term_analysis'].keys())
            for option in options:
                if option in TERM_OPTIONS:
                    value = repr(field['term_analysis'][option])
                    if value.startswith("u"):
                        value = value[1:]
                    if value == 'True':
                        value = 'true'
                    elif value == 'False':
                        value = 'false'
                    body += """
                \"%s\": %s,""" % (option, value)
            body += """
        },"""
        body += """
    }"""

        if term_analysis_predicates:
            term_forms = {}
            fields = self.tree.fields
            for field_id, term in term_analysis_predicates:
                alternatives = []
                field = fields[field_id]
                if field['camelCase'] not in term_forms:
                    term_forms[field['camelCase']] = {}
                all_forms = field['summary'].get('term_forms', {})
                if all_forms:
                    alternatives = all_forms.get(term, [])
                    if alternatives:
                        terms = [term]
                        terms.extend(all_forms.get(term, []))
                        term_forms[field['camelCase']][term] = terms

            body += """
    var TERM_FORMS = {"""
            for field in term_forms:
                body += """
        \"%s\": {""" % field
                terms = sorted(term_forms[field].keys())
                for term in terms:
                    terms_list = "[\"" + \
                        "\", \"".join(term_forms[field][term]) + "\"]"
                    body += """
            \"%s\": %s,""" % (term, terms_list)
                body += """
        },
"""
            body +="""
    }
"""
        with open(TERM_TEMPLATE) as template_handler:
            body += template_handler.read()

        return body

    def js_item_analysis_body(self, item_analysis_predicates):
        """ Writes auxiliary functions to handle the item analysis fields

        """
        item_analysis_options = set([x[0] for x in item_analysis_predicates])
        item_analysis_predicates = set(item_analysis_predicates)

        body = ""
        # static content
        body += """
    var ITEM_ANALYSIS = {"""
        for field_id in item_analysis_options:
            field = self.tree.fields[field_id]
            body += """
        \"%s\": {""" % field['camelCase']
            for option in field['item_analysis']:
                if option in ITEM_OPTIONS and field['item_analysis'][option] \
                        is not None:
                    value = repr(field['item_analysis'][option])
                    if value.startswith("u"):
                        value = value[1:]
                    body += """
                \"%s\": %s,""" % (option, value)
            body += """
        },"""
        body += """
    }"""

        with open(ITEMS_TEMPLATE) as template_handler:
            body += template_handler.read()
        return body
