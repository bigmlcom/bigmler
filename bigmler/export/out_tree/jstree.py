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

"""Tree level output for node/js

This module defines functions that generate node/js code to make local
predictions
"""

from bigml.tree_utils import (
    INDENT, PYTHON_OPERATOR, MAX_ARGS_LENGTH, COMPOSED_FIELDS,
    NUMERIC_VALUE_FIELDS)
from bigml.predict_utils.common import mintree_split, get_predicate, get_node, \
    missing_branch
from bigml.predict_utils.common import OPERATION_OFFSET, FIELD_OFFSET, \
    VALUE_OFFSET, TERM_OFFSET, MISSING_OFFSET
from bigml.generators.tree_common import filter_nodes
from bigml.util import NUMERIC



def value_to_print(value, optype):
    """String of code that represents a value according to its type

    """
    if value is None:
        return "null"
    if optype in NUMERIC_VALUE_FIELDS: # value is numeric for these fields
        return value
    return "\"%s\"" % value.replace('"', '\\"')


def missing_check_code(tree, offsets, fields, objective_id,
                       field, depth, prefix, cmv, metric):
    """Builds the code to predict when the field is missing

    """
    node = get_node(tree)
    code = "%sif (%s%s == null) {\n" % \
        (INDENT * depth,
         prefix,
         fields[field]['camelCase'])
    value = value_to_print(node[offsets["output"]],
                           fields[objective_id]['optype'])
    code += "%sreturn {prediction: %s," \
        " %s: %s}}\n" % \
        (INDENT * (depth + 1), value, metric, node[offsets["confidence"]])
    cmv.append(fields[field]['camelCase'])
    return code


def missing_prefix_code(tree, fields, field, prefix, cmv):
    """Part of the condition that checks for missings when missing_splits
    has been used

    """

    predicate = get_predicate(tree)
    missing = predicate[MISSING_OFFSET]
    operator = "==" if missing else "!="
    connection = "||" if missing else "&&"
    if not missing:
        cmv.append(fields[field]['camelCase'])
    return "%s%s %s null %s " % (prefix,
                                  fields[field]['camelCase'],
                                  operator,
                                  connection)


def split_condition_code(tree, fields, field, depth, prefix,
                         pre_condition, term_analysis_fields,
                         item_analysis_fields, cmv):
    """Condition code for the split

    """
    optype = fields[field]['optype']
    predicate = get_predicate(tree)
    operator = PYTHON_OPERATOR[predicate[OPERATION_OFFSET]]
    value = value_to_print(predicate[VALUE_OFFSET], optype)

    if optype in ['text', 'items']:
        if optype == 'text':
            term_analysis_fields.append((field,
                                         predicate[TERM_OFFSET]))
            matching_function = "termMatches"
        else:
            item_analysis_fields.append((field,
                                         predicate[TERM_OFFSET]))
            matching_function = "itemMatches"

        return "%sif (%s%s(%s%s, %s, %s) %s %s) {\n" % \
            (INDENT * depth,
             pre_condition,
             matching_function,
             prefix,
             fields[field]['camelCase'],
             value_to_print(fields[field]['camelCase'],
                 'categorical'),
             value_to_print(predicate[TERM_OFFSET], 'categorical'),
             operator,
             value)
    if value is None:
        cmv.append(fields[field]['camelCase'])
    return "%sif (%s%s%s %s %s) {\n" % \
        (INDENT * depth, pre_condition,
         prefix,
         fields[field]['camelCase'],
         operator,
         value)


def plug_in_body(tree, offsets, fields, objective_id,
                 depth=1, cmv=None, ids_path=None, subtree=True):
    """Translate the model into a set of "if" javascript statements.

    `depth` controls the size of indentation. As soon as a value is missing
    to evaluate a predicate the output at that node is returned without
    further evaluation.

    """
    if cmv is None:
        cmv = []
    body = ""
    term_analysis_fields = []
    item_analysis_fields = []
    prefix = ""
    field_obj = fields[objective_id]
    metric = "error" if field_obj["optype"] == NUMERIC \
        else "confidence"


    if len(fields) > MAX_ARGS_LENGTH:
        prefix = "data."

    node = get_node(tree)
    children = filter_nodes([] if node[offsets["children#"]] == 0 else \
                            node[offsets["children"]], offsets, ids=ids_path,
                            subtree=subtree)

    if children:

        # field used in the split
        field = mintree_split(children)

        has_missing_branch = missing_branch(children)
        # the missing is singled out as a special case only when there's
        # no missing branch in the children list
        one_branch = not has_missing_branch or \
            fields[field]['optype'] in COMPOSED_FIELDS
        if (one_branch and
                not fields[field]['camelCase'] in cmv):
            body += missing_check_code(tree, offsets, fields, objective_id,
                                       field, depth, prefix, cmv, metric)

        for child in children:

            predicate = get_predicate(child)
            field = predicate[FIELD_OFFSET]

            pre_condition = ""
            # code when missing_splits has been used
            if has_missing_branch and predicate[VALUE_OFFSET] is not None:
                pre_condition = missing_prefix_code(child, fields,
                                                    field, prefix, cmv)

            # complete split condition code
            body += split_condition_code( \
                child, fields,
                field, depth, prefix, pre_condition,
                term_analysis_fields, item_analysis_fields, cmv)

            # value to be determined in next node
            next_level = plug_in_body(child, offsets, fields, objective_id,
                                      depth + 1, cmv=cmv[:],
                                      ids_path=ids_path, subtree=subtree)
            body += next_level[0]
            body += "%s}\n" % (INDENT * depth)
            term_analysis_fields.extend(next_level[1])
            item_analysis_fields.extend(next_level[2])

    else:
        value = value_to_print(node[offsets["output"]],
                               fields[objective_id]['optype'])
        body = "%sreturn {prediction: %s, %s: %s};\n" % ( \
            INDENT * depth,
            value,
            metric,
            node[offsets["confidence"]])
    return body, term_analysis_fields, item_analysis_fields
