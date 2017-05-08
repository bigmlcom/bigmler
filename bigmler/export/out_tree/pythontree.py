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

"""Tree level output for python

This module defines functions that generate python code to make local
predictions
"""

from bigml.tree_utils import (
    slugify, sort_fields, filter_nodes, missing_branch, none_value,
    one_branch, split, MAX_ARGS_LENGTH, INDENT, PYTHON_OPERATOR, TM_TOKENS,
    TM_FULL_TERM, TM_ALL, TERM_OPTIONS, ITEM_OPTIONS)

from bigml.tree import Tree

MISSING_OPERATOR = {
    "=": "is",
    "!=": "is not"
}


class PythonTree(Tree):

    def plug_in_body(self, depth=1, cmv=None, input_map=False,
                     ids_path=None, subtree=True):
        """Translate the model into a set of "if" python statements.

        `depth` controls the size of indentation. As soon as a value is missing
        that node is returned without further evaluation.

        """

        def map_data(field, missing=False):
            """Returns the subject of the condition in map format when
               more than MAX_ARGS_LENGTH arguments are used.
            """
            if input_map:
                if missing:
                    return "data.get('%s')" % field
                else:
                    return "data['%s']" % field
            return field
        if cmv is None:
            cmv = []
        body = u""
        term_analysis_fields = []
        item_analysis_fields = []
        children = filter_nodes(self.children, ids=ids_path,
                                subtree=subtree)
        if children:
            field = split(children)
            has_missing_branch = (missing_branch(children) or
                                  none_value(children))
            # the missing is singled out as a special case only when there's
            # no missing branch in the children list
            if (not has_missing_branch and
                not self.fields[field]['slug'] in cmv):
                body += (u"%sif (%s is None):\n" %
                        (INDENT * depth,
                         map_data(self.fields[field]['slug'], True)))
                if self.fields[self.objective_id]['optype'] == 'numeric':
                    value = self.output
                else:
                    value = repr(self.output)
                body += (u"%sreturn %s\n" %
                        (INDENT * (depth + 1),
                         value))
                cmv.append(self.fields[field]['slug'])

            for child in children:
                field = child.predicate.field
                pre_condition = u""
                if has_missing_branch and child.predicate.value is not None:
                    negation = u"" if child.predicate.missing else u" not"
                    connection = u"or" if child.predicate.missing else u"and"
                    pre_condition = (u"%s is%s None %s " % (
                                     map_data(self.fields[field]['slug'],
                                              True),
                                     negation,
                                     connection))
                    if not child.predicate.missing:
                        cmv.append(self.fields[field]['slug'])
                optype = self.fields[field]['optype']

                if (optype == 'numeric' or optype == 'text' or
                        optype == 'items'
                        or child.predicate.value is None):
                    value = child.predicate.value
                else:
                    value = repr(child.predicate.value)
                if optype == 'text' or optype == 'items':
                    if optype == 'text':
                        term_analysis_fields.append((field,
                                                     child.predicate.term))
                        matching_function = "term_matches"
                    else:
                        item_analysis_fields.append((field,
                                                     child.predicate.term))
                        matching_function = "item_matches"

                    body += (u"%sif (%s%s(%s, \"%s\", %s\"%s\") %s "
                             u"%s):\n" %
                            (INDENT * depth, pre_condition, matching_function,
                             map_data(self.fields[field]['slug'],
                             False),
                             self.fields[child.predicate.field]['slug'],
                             'u' if isinstance(child.predicate.term, unicode) else '',
                             child.predicate.term.replace("\"", "\\\""),
                             PYTHON_OPERATOR[child.predicate.operator],
                             value))
                else:
                    operator = (MISSING_OPERATOR[child.predicate.operator] if
                                child.predicate.value is None else
                                PYTHON_OPERATOR[child.predicate.operator])
                    if child.predicate.value is None:
                        cmv.append(self.fields[field]['slug'])
                    body += (u"%sif (%s%s %s %s):\n" %
                            (INDENT * depth, pre_condition,
                             map_data(self.fields[field]['slug'],
                                      False),
                             operator,
                             value))
                next_level = child.plug_in_body(depth + 1, cmv=cmv[:],
                                                input_map=input_map,
                                                ids_path=ids_path,
                                                subtree=subtree)

                body += next_level[0]
                term_analysis_fields.extend(next_level[1])
                item_analysis_fields.extend(next_level[2])
        else:
            if self.fields[self.objective_id]['optype'] == 'numeric':
                value = self.output
            else:
                value = repr(self.output)
            body = u"%sreturn %s\n" % (INDENT * depth, value)

        return body, term_analysis_fields, item_analysis_fields
