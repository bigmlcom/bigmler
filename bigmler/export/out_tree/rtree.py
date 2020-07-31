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

"""Tree level output in R

This module defines functions that generate R output for the tree
"""

from bigml.tree_utils import (sort_fields, filter_nodes, missing_branch,
                              split, INDENT, PYTHON_OPERATOR, COMPOSED_FIELDS,
                              NUMERIC_VALUE_FIELDS)

from bigml.tree import Tree


def value_to_print(value, optype):
    """String of code that represents a value according to its type

    """
    if value is None:
        return "NA"
    if optype in NUMERIC_VALUE_FIELDS:
        return value
    return "\"%s\"" % value.replace('"', '\\"')


class RTree(Tree):

    def missing_check_code(self, field, depth, cmv, metric):
        """Builds the code to predict when the field is missing

        """

        code = "%sif (is.na(%s)){\n" % \
               (INDENT * depth,
                self.fields[field]['dotted'])
        value = value_to_print(self.output,
                               self.fields[self.objective_id]['optype'])
        indent_depth = INDENT * (depth + 1)
        code += "%sreturn(list(prediction=%s, %s=%s))\n%s}\n" % \
               (indent_depth,
                value, metric, self.confidence, INDENT * depth)
        cmv.append(self.fields[field]['dotted'])
        return code

    def missing_prefix_code(self, field, cmv):
        """Part of the condition that checks for missings when missing_splits
        has been used

        """

        operator = "==" if self.predicate.missing else "!="
        connection = "||" if self.predicate.missing else "&&"
        if not self.predicate.missing:
            cmv.append(self.fields[field]['dotted'])
        return "%s%s %s NA %s " % (self.fields[field]['dotted'],
                                    operator,
                                    connection)

    def split_condition_code(self, field, depth,
                             pre_condition, term_analysis_fields,
                             item_analysis_fields):
        """Condition code for the split

        """
        optype = self.fields[field]['optype']
        operator = PYTHON_OPERATOR[self.predicate.operator]
        value = value_to_print(self.predicate.value, optype)

        if optype in COMPOSED_FIELDS:
            if optype == 'text':
                term_analysis_fields.append((field,
                                             self.predicate.term))
                matching_function = "termMatches"
            else:
                item_analysis_fields.append((field,
                                             self.predicate.term))
                matching_function = "itemMatches"

            return "%sif (%s%s(%s, %s, %s)%s%s) {\n" % \
                (INDENT * depth, pre_condition, matching_function,
                 self.fields[field]['dotted'],
                 value_to_print(self.fields[field]['dotted'], 'categorical'),
                 value_to_print(self.predicate.term, 'categorical'),
                 operator,
                 value)
        if self.predicate.value is None:
            cmv.append(self.fields[field]['dotted'])
        return "%sif (%s%s %s %s) {\n" % \
            (INDENT * depth, pre_condition,
             self.fields[field]['dotted'],
             operator,
             value)

    def plug_in_body(self, depth=1, cmv=None, ids_path=None, subtree=True):
        """Translate the model into a set of "if" r statements.

        `depth` controls the size of indentation. If `cmv` (control missing
        values) is set to True then as soon as a value is missing to
        evaluate a predicate the output at that node is returned without
        further evaluation.

        """
        metric = "error" if self.regression else "confidence"
        if cmv is None:
            cmv = []
        body = ""
        term_analysis_fields = []
        item_analysis_fields = []
        field_obj = self.fields[self.objective_id]
        children = filter_nodes(self.children, ids=ids_path,
                                subtree=subtree)

        if children:
            # field used in the split
            field = split(children)

            has_missing_branch = missing_branch(children)
            # the missing is singled out as a special case only when there's
            # no missing branch in the children list
            one_branch = not (has_missing_branch or
                self.fields[field]['optype'] in COMPOSED_FIELDS)
            if (one_branch and
                    not self.fields[field]['dotted'] in cmv):
                body += self.missing_check_code(field, depth, cmv,
                                                metric)

            for child in self.children:
                field = child.predicate.field
                pre_condition = ""
                # code when missing_splits has been used
                if has_missing_branch and field not in COMPOSED_FIELDS \
                        and child.predicate.value is not None:
                    pre_condition = self.missing_prefix_code(child, field, cmv)

                # complete split condition code
                body += child.split_condition_code( \
                    field, depth, pre_condition,
                    term_analysis_fields, item_analysis_fields)

                # value to be determined in next node
                next_level = child.plug_in_body(depth + 1, cmv=cmv[:],
                                                ids_path=ids_path,
                                                subtree=subtree)
                body += next_level[0]
                body += "%s}\n" % (INDENT * depth)
                term_analysis_fields.extend(next_level[1])
                item_analysis_fields.extend(next_level[2])
        else:
            value = value_to_print(self.output,
                                   self.fields[self.objective_id]['optype'])
            body = "%sreturn(list(prediction=%s, %s=%s))\n" % \
                  (INDENT * depth,
                   value, metric, self.confidence)
        return body, term_analysis_fields, item_analysis_fields
