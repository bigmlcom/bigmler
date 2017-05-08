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

"""Tree level output for tableau

This module defines functions that generate tableau code to make local
predictions
"""

from bigml.tree_utils import (filter_nodes, split, ruby_string,
                              missing_branch, none_value,
                              one_branch, PYTHON_OPERATOR)

from bigml.tree import Tree

T_MISSING_OPERATOR = {
    "=": "ISNULL(",
    "!=": "NOT ISNULL("
}


class TableauTree(Tree):


    def plug_in_body(self, body=u"", conditions=None, cmv=None,
                     ids_path=None, subtree=True):
        """Translate the model into a set of "if" statemets in tableau syntax

        `depth` controls the size of indentation. As soon as a value is missing
        that node is returned without further evaluation.

        """

        if cmv is None:
            cmv = []

        if body:
             alternate = u"ELSEIF"
        else:
            if conditions is None:
                conditions = []
            alternate = u"IF"

        children = filter_nodes(self.children, ids=ids_path,
                                subtree=subtree)
        if children:
            field = split(children)
            has_missing_branch = (missing_branch(children) or
                                  none_value(children))
            # the missing is singled out as a special case only when there's
            # no missing branch in the children list
            if (not has_missing_branch and
                    not self.fields[field]['name'] in cmv):
                conditions.append("ISNULL([%s])" % self.fields[field]['name'])
                body += (u"%s %s THEN " %
                         (alternate, " AND ".join(conditions)))
                if self.fields[self.objective_id]['optype'] == 'numeric':
                    value = self.output
                else:
                    value = ruby_string(self.output)
                body += (u"%s\n" % value)
                cmv.append(self.fields[field]['name'])
                alternate = u"ELSEIF"
                del conditions[-1]

            for child in children:
                pre_condition = u""
                post_condition = u""
                if has_missing_branch and child.predicate.value is not None:
                    negation = u"" if child.predicate.missing else u"NOT "
                    connection = u"OR" if child.predicate.missing else u"AND"
                    pre_condition = (u"(%sISNULL([%s]) %s " % (
                                     negation, self.fields[field]['name'],
                                     connection))
                    if not child.predicate.missing:
                        cmv.append(self.fields[field]['name'])
                    post_condition = u")"
                optype = self.fields[child.predicate.field]['optype']

                if child.predicate.value is None:
                    value = ""
                elif optype == 'numeric':
                    value = child.predicate.value
                elif optype in ['text', 'items']:
                    return u""
                else:
                    value = repr(child.predicate.value)
                operator = ("" if child.predicate.value is None else
                            PYTHON_OPERATOR[child.predicate.operator])
                if child.predicate.value is None:
                    pre_condition = (
                        T_MISSING_OPERATOR[child.predicate.operator])
                    post_condition = ")"

                conditions.append("%s[%s]%s%s%s" % (
                    pre_condition,
                    self.fields[child.predicate.field]['name'],
                    operator,
                    value,
                    post_condition))
                body = child.plug_in_body(body, conditions[:], cmv=cmv[:],
                                          ids_path=ids_path, subtree=subtree)
                del conditions[-1]
        else:
            if self.fields[self.objective_id]['optype'] == 'numeric':
                value = self.output
            else:
                value = ruby_string(self.output)
            body += (
                u"%s %s THEN" % (alternate, " AND ".join(conditions)))
            body += u" %s\n" % value

        return body
