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

"""Tree level output for MySQL function

This module defines functions that generate MySQL SQL code to make local
predictions
"""

from bigml.tree_utils import (filter_nodes, split, ruby_string,
                              missing_branch, none_value,
                              one_branch, INDENT)

from bigml.tree import Tree

T_MISSING_OPERATOR = {
    "=": "ISNULL(",
    "!=": "NOT ISNULL("
}

# Map operator str to its corresponding mysql operator
MYSQL_OPERATOR = {
    "/=": "!="}

def value_to_print(value, optype):
    """String of code that represents a value according to its type

    """
    if (value is None):
        return "NULL"
    if (optype == 'numeric'):
        return value
    return "'%s'" % value.replace("'", '\\\'')


class MySQLTree(Tree):


    def missing_check_code(self, field, alternate, cmv, attr=None):
        """Builds the code to predict when the field is missing

        """


        condition = "ISNULL(`%s`)" % self.fields[field]['name']
        code = ("%s (%s)" %
                 (alternate, condition))

        # used when printing the confidence metric
        if attr != None:
            value = getattr(self, attr)
        else:
            value = value_to_print( \
                self.output,
                self.fields[self.objective_id]['optype'])

        code += (", %s" % value)
        cmv.append(self.fields[field]['name'])

        return code

    def missing_prefix_code(self, field, cmv):
        """Part of the condition that checks for missings when missing_splits
        has been used

        """

        negation = "" if child.predicate.missing else "NOT "
        connection = "OR" if child.predicate.missing else "AND"
        if not child.predicate.missing:
            cmv.append(self.fields[field]['name'])
        return "(%sISNULL(`%s`) %s " % ( \
            negation, self.fields[field]['name'],
            connection)

    def split_condition_code(self, field, alternate,
                             pre_condition):
        """Condition code for the split

        """

        post_condition = ""
        optype = self.fields[field]['optype']
        value = value_to_print(self.predicate.value, optype)
        operator = ("" if self.predicate.value is None else
                    MYSQL_OPERATOR.get(self.predicate.operator,
                                       self.predicate.operator))
        if self.predicate.value is None:
            value = ""
            pre_condition = (
                T_MISSING_OPERATOR[self.predicate.operator])
            post_condition = ")"

        condition = "%s`%s`%s%s%s" % ( \
            pre_condition,
            self.fields[self.predicate.field]['name'],
            operator,
            value,
            post_condition)
        return "%s (%s)" % (alternate, condition)

    def plug_in_body(self, depth=0, cmv=None,
                     ids_path=None, subtree=True, body="", attr=None):
        """Translate the model into a mysql function

        `depth` controls the size of indentation. As soon as a value is missing
        that node is returned without further evaluation.
        `attr` is used to decide the value returned by the function. When
        it's set to None, the prediction is returned. When set to the
        name of an attribute (e.g. 'confidence') this attribute is returned

        """

        if cmv is None:
            cmv = []

        if body:
            alternate = ",\n%sIF (" % (depth * INDENT)
        else:
            alternate = "IF ("
        post_missing_body = ""


        children = filter_nodes(self.children, ids=ids_path,
                                subtree=subtree)
        if children:

            # field used in the split
            field = split(children)

            has_missing_branch = (missing_branch(children) or
                                  none_value(children))
            # the missing is singled out as a special case only when there's
            # no missing branch in the children list
            if (not has_missing_branch and
                    not self.fields[field]['name'] in cmv):
                body += self.missing_check_code(field, alternate, cmv, attr)
                depth += 1
                alternate = ",\n%sIF (" % (depth * INDENT)
                post_missing_body += ")"

            for child in children:
                pre_condition = ""
                # code when missing splits has been used
                if has_missing_branch and child.predicate.value is not None:
                    pre_condition = self.missing_prefix_code(child, field, cmv)

                # complete split condition code
                body += child.split_condition_code( \
                    field, alternate, pre_condition)

                depth += 1
                alternate = ",\n%sIF (" % (depth * INDENT)
                body = child.plug_in_body(depth, cmv=cmv[:],
                                          ids_path=ids_path, subtree=subtree,
                                          body=body, attr=attr)
            body += ", NULL))" + post_missing_body
            post_missing_body = ""
        else:
            if attr is None:
                value = value_to_print( \
                    self.output, self.fields[self.objective_id]['optype'])
            else:
                value = getattr(self, attr)
            body += ", %s" % (value)

        return body
