# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014 BigML
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

"""Tree level output for R

This module defines functions that generate R code to make local
predictions
"""
import sys

from bigml.tree_utils import (
    to_camel_js, sort_fields, docstring_comment, slugify,
    INDENT, MAX_ARGS_LENGTH, TERM_OPTIONS, ITEM_OPTIONS,
    TM_TOKENS, TM_FULL_TERM, TM_ALL)

from bigml.model import Model
from bigmler.export.out_tree.rtree import RTree
from bigmler.reports import BIGMLER_SCRIPT


# templates for static javascript
TERM_TEMPLATE = "%s/static/out_model/term_analysis.R" % BIGMLER_SCRIPT
ITEMS_TEMPLATE = "%s/static/out_model/items_analysis.R" % BIGMLER_SCRIPT


def dot(name):
    """Creates a dot-separated name

    """
    return slugify(name.replace(" ", "."))


class RModel(Model):

    def __init__(self, model, api=None, fields=None):
        """Empty attributes to be overriden

        """
        self.tree_class = RTree
        Model.__init__(self, model, api, fields)

    def plug_in(self, out=sys.stdout, filter_id=None, subtree=True):
        """Writes an R function that implements the model.

        """
        # fill the dotted variable names with the R_KEYWORDS restrictions
        objective_field = self.tree.fields[self.tree.objective_id]
        camelcase = to_camel_js(objective_field['name'], False)
        objective_field['CamelCase'] = camelcase
        default = "NA"
        args = []
        for field in [(key, val) for key, val in
                      sort_fields(self.tree.fields)]:
            field_obj = self.tree.fields[field[0]]
            field_obj['dotted'] = dot(field_obj['name'])
            args.append("%s=%s" % (field_obj['dotted'], default))

        body, term_analysis_predicates, item_analysis_predicates = \
            self.tree.plug_in_body()
        terms_body = ""
        items_body = ""
        if term_analysis_predicates:
            terms_body = self.r_term_analysis_body(term_analysis_predicates)
        if item_analysis_predicates:
            items_body = self.r_item_analysis_body(item_analysis_predicates)

        predictor_definition = ("predict%s <- function" %
                                camelcase)
        depth = len(predictor_definition) + 1
        predictor = "%s(%s){\n" % (predictor_definition,
                                   (",\n" + " " * depth).join(args))
        join_str = "\n#"
        docstring = join_str.join(self.docstring().split("\n"))
        predictor_doc = ("# " + docstring +
                         "\n" + "#\n")
        output = predictor_doc + predictor
        output += terms_body + items_body + body
        output += "%sreturn(NA)\n}\n" % INDENT
        out.write(output)
        out.flush()

    def r_term_analysis_body(self, term_analysis_predicates):
        """ Writes auxiliary functions to handle the term analysis fields

        """
        term_analysis_options = set([x[0] for x in term_analysis_predicates])
        term_analysis_predicates = set(term_analysis_predicates)

        body = ""
        # static content
        body += """
    TERM_ANALYSIS <- list("""
        lines = []
        for field_id in term_analysis_options:
            inner_lines = []
            field = self.tree.fields[field_id]
            lines.append("""
        \"%s\"=list(""" % field['dotted'])
            options = sorted(field['term_analysis'].keys())
            for option in options:
                if option in TERM_OPTIONS:
                    value = repr(field['term_analysis'][option])
                    value = value if not value.startswith("u") else value[1:]
                    if value == 'True':
                        value = 'TRUE'
                    elif value == 'False':
                        value = 'FALSE'
                    inner_lines.append("""\
                \"%s\"= %s""" % (option, value))
            if inner_lines:
                lines[-1] = lines[-1] + "\n" + ",\n".join(inner_lines)
        lines[-1] = lines[-1] + """
        )"""
        body += ",\n".join(lines) + """
    )"""

        if term_analysis_predicates:
            term_forms = {}
            fields = self.tree.fields
            for field_id, term in term_analysis_predicates:
                alternatives = []
                field = fields[field_id]
                if field['dotted'] not in term_forms:
                    term_forms[field['dotted']] = {}
                all_forms = field['summary'].get('term_forms', {})
                if all_forms:
                    alternatives = all_forms.get(term, [])
                    if alternatives:
                        terms = [term]
                        terms.extend(all_forms.get(term, []))
                        term_forms[field['dotted']][term] = terms

            body += """
    TERM_FORMS <- list("""
            lines = []
            for field in term_forms:
                inner_lines = []
                lines.append("""
        \"%s\"=list(""" % field)
                terms = sorted(term_forms[field].keys())
                for term in terms:
                    terms_list = "list(\"" + \
                        "\", \"".join(term_forms[field][term])
                    terms_list += "\")"
                    inner_lines.append("""\
            \"%s\"=%s""" % (term,
                            terms_list))
                if inner_lines:
                    lines[-1] = lines[-1] + "\n" + ",\n".join(inner_lines)
            lines[-1] = lines[-1] + """
        )"""
            body += ",\n".join(lines) + """
    )
"""
        body += """
    TM_TOKENS <- "%s"
    TM_FULL_TERM <- "%s"
    TM_ALL <- "%s"\
""" % (TM_TOKENS, TM_FULL_TERM, TM_ALL)

        with open(TERM_TEMPLATE) as template_handler:
            body += template_handler.read()
        return body

    def r_item_analysis_body(self, item_analysis_predicates):
        """ Writes auxiliary functions to handle the item analysis fields

        """
        item_analysis_options = set([x[0] for x in item_analysis_predicates])
        item_analysis_predicates = set(item_analysis_predicates)

        body = ""
        # static content
        body += """
    ITEM_ANALYSIS <- list("""
        lines = []
        for field_id in item_analysis_options:
            inner_lines = []
            field = self.tree.fields[field_id]
            lines.append("""
        \"%s\"=list(""" % field['dotted'])
            for option in field['item_analysis']:
                if option in ITEM_OPTIONS and field['item_analysis'][option] \
                        is not None:
                    value = repr(field['item_analysis'][option])
                    value = value if not value.startswith("u") else value[1:]
                    inner_lines.append("""\
                \"%s\"=%s""" % (option, value))
            if inner_lines:
                lines[-1] = lines[-1] + "\n" + ",\n".join(inner_lines)
        lines[-1] = lines[-1] + """
        )"""
        body += ",\n".join(lines) + """
    )
"""

        with open(ITEMS_TEMPLATE) as template_handler:
            body += template_handler.read()
        return body
