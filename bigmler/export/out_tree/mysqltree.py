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

"""Tree level output for MySQL function

This module defines functions that generate MySQL SQL code to make local
predictions
"""

from bigml.tree_utils import INDENT
from bigml.generators.model import PYTHON_OPERATOR, missing_branch, \
    none_value
from bigml.predict_utils.common import mintree_split, get_predicate, get_node
from bigml.predict_utils.common import OPERATION_OFFSET, FIELD_OFFSET, \
    VALUE_OFFSET, MISSING_OFFSET
from bigml.generators.tree_common import filter_nodes

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
    if value is None:
        return "NULL"
    if optype == 'numeric':
        return value
    return "'%s'" % value.replace("'", '\\\'')


def missing_check_code(tree, offsets, fields, objective_id,
                       field, alternate, cmv, attr=None):
    """Builds the code to predict when the field is missing

    """
    node = get_node(tree)
    condition = "ISNULL(`%s`)" % fields[field]['name']
    code = ("%s (%s)" %
             (alternate, condition))

    # used when printing the confidence metric
    if attr is not None:
        value = node[offsets[attr]]
    else:
        value = value_to_print( \
            node[offsets["output"]],
            fields[objective_id]['optype'])

    code += (", %s" % value)
    cmv.append(fields[field]['name'])

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
    return "(%sISNULL(`%s`) %s " % ( \
        negation, fields[field]['name'],
        connection)

def split_condition_code(tree, fields, field, alternate,
                         pre_condition):
    """Condition code for the split

    """

    predicate = get_predicate(tree)
    post_condition = ""
    optype = fields[field]['optype']
    value = value_to_print(predicate[VALUE_OFFSET], optype)
    operation = predicate[OPERATION_OFFSET]
    operator = ("" if predicate[VALUE_OFFSET] is None else
                MYSQL_OPERATOR.get(operation,
                                   PYTHON_OPERATOR.get(operation)))
    if predicate[VALUE_OFFSET] is None:
        value = ""
        pre_condition = (
            T_MISSING_OPERATOR[operation])
        post_condition = ")"

    condition = "%s`%s`%s%s%s" % ( \
        pre_condition,
        fields[predicate[FIELD_OFFSET]]['name'],
        operator,
        value,
        post_condition)
    return "%s (%s)" % (alternate, condition)

def plug_in_body(tree, offsets, fields, objective_id, depth=0, cmv=None,
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

    node = get_node(tree)
    children = filter_nodes([] if node[offsets["children#"]] == 0 \
        else node[offsets["children"]], offsets, ids=ids_path, subtree=subtree)

    if children:

        # field used in the split
        field = mintree_split(children)

        has_missing_branch = (missing_branch(children) or
                              none_value(children))
        # the missing is singled out as a special case only when there's
        # no missing branch in the children list
        if (not has_missing_branch and
                not fields[field]['name'] in cmv):
            body += missing_check_code(tree, offsets, fields, objective_id,
                                       field, alternate, cmv, attr)
            depth += 1
            alternate = ",\n%sIF (" % (depth * INDENT)
            post_missing_body += ")"

        for child in children:
            pre_condition = ""
            predicate = get_predicate(child)
            # code when missing splits has been used
            if has_missing_branch and predicate[VALUE_OFFSET] is not None:
                pre_condition = missing_prefix_code(child, fields, field, cmv)

            # complete split condition code
            body += split_condition_code( \
                child, fields, field, alternate, pre_condition)

            depth += 1
            alternate = ",\n%sIF (" % (depth * INDENT)
            body = plug_in_body(child, offsets, fields, objective_id,
                                depth, cmv=cmv[:],
                                ids_path=ids_path, subtree=subtree,
                                body=body, attr=attr)
        body += ", NULL))" + post_missing_body
        post_missing_body = ""
    else:
        if attr is None:
            value = value_to_print( \
                node[offsets["output"]], fields[objective_id]['optype'])
        else:
            try:
                value = node[offsets[attr]]
            except KeyError:
                value = "NULL"
        body += ", %s" % (value)

    return body
