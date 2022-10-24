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

from bigml.tree_utils import (
    INDENT, PYTHON_OPERATOR, COMPOSED_FIELDS, NUMERIC_VALUE_FIELDS)
from bigml.predict_utils.common import mintree_split, get_predicate, get_node, \
    missing_branch
from bigml.predict_utils.common import OPERATION_OFFSET, \
    VALUE_OFFSET, TERM_OFFSET, MISSING_OFFSET
from bigml.generators.tree_common import filter_nodes
from bigml.util import NUMERIC


def value_to_print(value, optype):
    """String of code that represents a value according to its type

    """
    if value is None:
        return "NA"
    if optype in NUMERIC_VALUE_FIELDS:
        return value
    return "\"%s\"" % value.replace('"', '\\"')


def missing_check_code(tree, offsets, fields, objective_id,
                       field, depth, cmv, metric):
    """Builds the code to predict when the field is missing

    """

    node = get_node(tree)
    code = "%sif (is.na(%s)){\n" % \
           (INDENT * depth,
            fields[field]['dotted'])
    value = value_to_print(node[offsets["output"]],
                           fields[objective_id]['optype'])
    indent_depth = INDENT * (depth + 1)
    code += "%sreturn(list(prediction=%s, %s=%s))\n%s}\n" % \
           (indent_depth,
            value, metric, node[offsets["confidence"]], INDENT * depth)
    cmv.append(fields[field]['dotted'])
    return code

def missing_prefix_code(tree, fields, field, cmv):
    """Part of the condition that checks for missings when missing_splits
    has been used

    """

    predicate = get_predicate(tree)
    missing = predicate[MISSING_OFFSET]
    operator = "==" if missing else "!="
    connection = "||" if missing else "&&"
    if not missing:
        cmv.append(fields[field]['dotted'])
    return "%s%s %s is.na(%s) " % (fields[field]['dotted'],
                               operator,
                               connection,
                               fields[field]['dotted'])

def split_condition_code(tree, fields, field, depth,
                         pre_condition, term_analysis_fields,
                         item_analysis_fields, cmv):
    """Condition code for the split

    """
    predicate = get_predicate(tree)
    optype = fields[field]['optype']
    operator = PYTHON_OPERATOR[predicate[OPERATION_OFFSET]]
    value = value_to_print(predicate[VALUE_OFFSET], optype)

    if optype in COMPOSED_FIELDS:
        if optype == 'text':
            term_analysis_fields.append((field,
                                         predicate[TERM_OFFSET]))
            matching_function = "termMatches"
        else:
            item_analysis_fields.append((field,
                                         predicate[TERM_OFFSET]))
            matching_function = "itemMatches"

        return "%sif (%s%s(%s, %s, %s)%s%s) {\n" % \
            (INDENT * depth, pre_condition, matching_function,
             fields[field]['dotted'],
             value_to_print(fields[field]['dotted'], 'categorical'),
             value_to_print(predicate[TERM_OFFSET], 'categorical'),
             operator,
             value)
    if value is None:
        cmv.append(fields[field]['dotted'])
    return "%sif (%s%s %s %s) {\n" % \
        (INDENT * depth, pre_condition,
         fields[field]['dotted'],
         operator,
         value)

def plug_in_body(tree, offsets, fields, objective_id,
                 depth=1, cmv=None, ids_path=None, subtree=True):
    """Translate the model into a set of "if" r statements.

    `depth` controls the size of indentation. If `cmv` (control missing
    values) is set to True then as soon as a value is missing to
    evaluate a predicate the output at that node is returned without
    further evaluation.

    """
    node = get_node(tree)
    metric = "error" if fields[objective_id]["optype"] == NUMERIC \
        else "confidence"
    if cmv is None:
        cmv = []
    body = ""
    term_analysis_fields = []
    item_analysis_fields = []
    field_obj = fields[objective_id]
    children = filter_nodes([] if node[offsets["children#"]] == 0 \
        else node[offsets["children"]], offsets, ids=ids_path, subtree=subtree)

    if children:
        # field used in the split
        field = mintree_split(children)

        has_missing_branch = missing_branch(children)
        # the missing is singled out as a special case only when there's
        # no missing branch in the children list
        one_branch = not (has_missing_branch or
            fields[field]['optype'] in COMPOSED_FIELDS)
        if (one_branch and
                not fields[field]['dotted'] in cmv):
            body += missing_check_code(tree, offsets, fields, objective_id,
                                       field, depth, cmv, metric)

        for child in children:
            [_, field, value, _, _] = get_predicate(child)

            pre_condition = ""
            # code when missing_splits has been used
            if has_missing_branch and field not in COMPOSED_FIELDS \
                    and value is not None:
                pre_condition = missing_prefix_code(child, fields, field, cmv)

            # complete split condition code
            body += split_condition_code( \
                child, fields, field, depth, pre_condition,
                term_analysis_fields, item_analysis_fields, cmv)

            # value to be determined in next node
            next_level = plug_in_body(child, offsets, fields, objective_id,
                                      depth + 1, cmv=cmv[:],
                                      ids_path=ids_path,
                                      subtree=subtree)
            body += next_level[0]
            body += "%s}\n" % (INDENT * depth)
            term_analysis_fields.extend(next_level[1])
            item_analysis_fields.extend(next_level[2])
    else:
        value = value_to_print(node[offsets["output"]],
                               field_obj['optype'])
        body = "%sreturn(list(prediction=%s, %s=%s))\n" % \
              (INDENT * depth,
               value, metric, node[offsets["confidence"]])
    return body, term_analysis_fields, item_analysis_fields
