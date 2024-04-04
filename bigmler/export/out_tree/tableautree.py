# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017-2024 BigML
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

from bigml.tree_utils import PYTHON_OPERATOR, COMPOSED_FIELDS

from bigml.predict_utils.common import mintree_split, get_predicate, get_node, \
    missing_branch, none_value
from bigml.predict_utils.common import OPERATION_OFFSET, FIELD_OFFSET, \
    VALUE_OFFSET, MISSING_OFFSET
from bigml.generators.tree_common import filter_nodes


T_MISSING_OPERATOR = {
    "=": "ISNULL(",
    "!=": "NOT ISNULL("
}


def value_to_print(value, optype):
    """String of code that represents a value according to its type

    """
    if value is None:
        return "NULL"
    if optype == 'numeric':
        return value
    return "'%s'" % value.replace("'", '\\\'')


def missing_check_code(tree, offsets, fields, objective_id,
                       field, alternate, cmv, conditions, attr=None):
    """Builds the code to predict when the field is missing

    """
    node = get_node(tree)
    conditions.append("ISNULL([%s])" % fields[field]['name'])
    code = "%s %s THEN " % \
        (alternate, " AND ".join(conditions))
    if attr is None:
        value = value_to_print( \
            node[offsets["output"]], fields[objective_id]['optype'])
    else:
        value = node[offsets[attr]]
    code += ("%s\n" % value)
    cmv.append(fields[field]['name'])
    del conditions[-1]

    return code

def missing_prefix_code(tree, fields, field, cmv):
    """Part of the condition that checks for missings when missing_splits
    has been used

    """

    predicate = get_predicate(tree)
    missing = predicate[MISSING_OFFSET]
    negation = "" if missing else "NOT "
    connection = "OR" if missing else "AND"
    if not missing:
        cmv.append(fields[field]['name'])
    return "(%sISNULL([%s]) %s " % ( \
        negation, fields[field]['name'],
        connection)

def split_condition_code(tree, fields, field, conditions,
                         pre_condition, post_condition):
    """Condition code for the split

    """
    predicate = get_predicate(tree)
    optype = fields[field]['optype']
    value = value_to_print(predicate[VALUE_OFFSET], optype)
    operator = ("" if predicate[VALUE_OFFSET] is None else
                PYTHON_OPERATOR[predicate[OPERATION_OFFSET]])
    if predicate[VALUE_OFFSET]  is None:
        pre_condition = (
            T_MISSING_OPERATOR[predicate[OPERATION_OFFSET]])
        post_condition = ")"

    conditions.append("%s[%s]%s%s%s" % (
        pre_condition,
        fields[predicate[FIELD_OFFSET]]['name'],
        operator,
        value,
        post_condition))

def plug_in_body(tree, offsets, fields, objective_id,
                 body="", conditions=None, cmv=None,
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

    node = get_node(tree)

    children = filter_nodes([] if node[offsets["children#"]] == 0 \
        else node[offsets["children"]], offsets, ids=ids_path, subtree=subtree)

    if children:

        field = mintree_split(children)
        has_missing_branch = (missing_branch(children) or
                              none_value(children))
        # the missing is singled out as a special case only when there's
        # no missing branch in the children list
        one_branch = not has_missing_branch or \
            fields[field]['optype'] in COMPOSED_FIELDS
        if (one_branch and
                not fields[field]['name'] in cmv):
            body += missing_check_code(tree, offsets, fields, objective_id,
                                       field, alternate, cmv,
                                       conditions, attr=attr)
            alternate = "ELSEIF"

        for child in children:
            pre_condition = ""
            post_condition = ""
            predicate = get_predicate(child)
            [_, field, value, _, _] = predicate
            if has_missing_branch and value is not None:
                pre_condition = missing_prefix_code(child, fields, field, cmv)
                post_condition = ")"

            split_condition_code(child, fields, field, conditions,
                                 pre_condition, post_condition)

            body = plug_in_body(child, offsets, fields, objective_id,
                                body, conditions[:], cmv=cmv[:],
                                ids_path=ids_path, subtree=subtree,
                                attr=attr)
            del conditions[-1]
    else:
        if attr is None:
            value = value_to_print( \
                node[offsets["output"]], fields[objective_id]['optype'])
        else:
            value = node[offsets[attr]]
        body += "%s %s THEN" % (alternate, " AND ".join(conditions))
        body += " %s\n" % value

    return body
