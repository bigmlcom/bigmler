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

"""Tree level output for tableau

This module defines functions that generate tableau code to make local
predictions
"""

from bigml.tree_utils import (filter_nodes, split, ruby_string,
                              missing_branch, none_value,
                              one_branch, PYTHON_OPERATOR, COMPOSED_FIELDS)

from bigml.tree import Tree

T_MISSING_OPERATOR = {
    "=": "ISNULL(",
    "!=": "NOT ISNULL("
}


def value_to_print(value, optype):
    """String of code that represents a value according to its type

    """
    if (value is None):
        return "NULL"
    if (optype == 'numeric'):
        return value
    return "'%s'" % value.replace("'", '\\\'')


class TableauTree(Tree):

    def missing_check_code(self, field, alternate, cmv, conditions, attr=None):
        """Builds the code to predict when the field is missing

        """
        conditions.append("ISNULL([%s])" % self.fields[field]['name'])
        code = "%s %s THEN " % \
            (alternate, " AND ".join(conditions))
        if attr is None:
            value = value_to_print( \
                self.output, self.fields[self.objective_id]['optype'])
        else:
            value = getattr(self, attr)
        code += ("%s\n" % value)
        cmv.append(self.fields[field]['name'])
        del conditions[-1]

        return code

    def missing_prefix_code(self, field, cmv):
        """Part of the condition that checks for missings when missing_splits
        has been used

        """

        negation = "" if self.predicate.missing else "NOT "
        connection = "OR" if self.predicate.missing else "AND"
        if not self.predicate.missing:
            cmv.append(self.fields[field]['name'])
        return "(%sISNULL([%s]) %s " % ( \
            negation, self.fields[field]['name'],
            connection)

    def split_condition_code(self, field, conditions,
                             pre_condition, post_condition):
        """Condition code for the split

        """
        optype = self.fields[field]['optype']
        value = value_to_print(self.predicate.value, optype)
        operator = ("" if self.predicate.value is None else
                    PYTHON_OPERATOR[self.predicate.operator])
        if self.predicate.value is None:
            pre_condition = (
                T_MISSING_OPERATOR[self.predicate.operator])
            post_condition = ")"

        conditions.append("%s[%s]%s%s%s" % (
            pre_condition,
            self.fields[self.predicate.field]['name'],
            operator,
            value,
            post_condition))

    def plug_in_body(self, body="", conditions=None, cmv=None,
                     ids_path=None, subtree=True, attr=None):
        """Translate the model into a set of "if" statemets in tableau syntax

        `depth` controls the size of indentation. As soon as a value is missing
        that node is returned without further evaluation.

        """

        if cmv is None:
            cmv = []

        if body:
             alternate = "ELSEIF"
        else:
            if conditions is None:
                conditions = []
            alternate = "IF"

        children = filter_nodes(self.children, ids=ids_path,
                                subtree=subtree)
        if children:

            field = split(children)
            has_missing_branch = (missing_branch(children) or
                                  none_value(children))
            # the missing is singled out as a special case only when there's
            # no missing branch in the children list
            one_branch = not has_missing_branch or \
                self.fields[field]['optype'] in COMPOSED_FIELDS
            if (one_branch and
                    not self.fields[field]['name'] in cmv):
                body += self.missing_check_code(field, alternate, cmv,
                                                conditions, attr=attr)
                alternate = "ELSEIF"

            for child in children:
                pre_condition = ""
                post_condition = ""
                if has_missing_branch and child.predicate.value is not None:
                    pre_condition = self.missing_prefix_code(child, field, cmv)
                    post_condition = ")"

                child.split_condition_code(field, conditions,
                                           pre_condition, post_condition)

                body = child.plug_in_body(body, conditions[:], cmv=cmv[:],
                                          ids_path=ids_path, subtree=subtree,
                                          attr=attr)
                del conditions[-1]
        else:
            if attr is None:
                value = value_to_print( \
                    self.output, self.fields[self.objective_id]['optype'])
            else:
                value = getattr(self, attr)
            body += "%s %s THEN" % (alternate, " AND ".join(conditions))
            body += " %s\n" % value

        return body
