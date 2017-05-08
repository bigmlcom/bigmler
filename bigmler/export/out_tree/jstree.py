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

"""Tree level output for node/js

This module defines functions that generate node/js code to make local
predictions
"""

from bigml.tree_utils import (
    filter_nodes, missing_branch, java_string, none_value,
    INDENT, PYTHON_OPERATOR, MAX_ARGS_LENGTH)
from bigml.util import split
from bigml.tree import Tree

class JsTree(Tree):


    def plug_in_body(self, depth=1, cmv=None, ids_path=None, subtree=True):
        """Translate the model into a set of "if" javascript statements.

        `depth` controls the size of indentation. As soon as a value is missing
        to evaluate a predicate the output at that node is returned without
        further evaluation.

        """
        if cmv is None:
            cmv = []
        body = u""
        term_analysis_fields = []
        item_analysis_fields = []
        prefix = u""
        field_obj = self.fields[self.objective_id]
        separator = u"" if (field_obj['optype'] == 'numeric') else u"\""
        if len(self.fields) > MAX_ARGS_LENGTH:
            prefix = u"data."
        children = filter_nodes(self.children, ids=ids_path,
                                subtree=subtree)

        if children:
            alternative = u""
            field = split(children)
            has_missing_branch = missing_branch(children)
            # the missing is singled out as a special case only when there's
            # no missing branch in the children list
            if (not has_missing_branch and
                    not self.fields[field]['camelCase'] in cmv):
                body += (u"%sif (%s%s == null) {\n" %
                        (INDENT * depth,
                         prefix,
                         self.fields[field]['camelCase']))

                body += (u"%sreturn %s%s%s;\n" %
                        (INDENT * (depth + 1),
                         separator,
                         java_string(self.output),
                         separator))
                body += u"%s}\n" % (INDENT * depth)
                alternative = u"else "
                cmv.append(self.fields[field]['camelCase'])

            for child in children:
                field = child.predicate.field
                pre_condition = u""
                if has_missing_branch and child.predicate.value is not None:
                    operator = u"==" if child.predicate.missing else u"!="
                    connection = u"||" if child.predicate.missing else u"&&"
                    pre_condition = (u"%s %s null %s " % (
                                     self.fields[field]['camelCase'],
                                     operator,
                                     connection))
                    if not child.predicate.missing:
                        cmv.append(self.fields[field]['camelCase'])

                type_key = self.fields[field]['optype']
                if (type_key in ['numeric', 'text', 'items'] or
                        child.predicate.value is None):
                    value = "%s" % child.predicate.value
                    operator = (" " +
                                PYTHON_OPERATOR[child.predicate.operator] +
                                " ")
                else:
                    value = "\"%s\"" % java_string(child.predicate.value)
                    operator = PYTHON_OPERATOR[child.predicate.operator]

                child_field = self.fields[child.predicate.field]
                if type_key == 'text':
                    body += ( \
                        u"%sif (%stermMatches(%s%s, \"%s\", \"%s\")%s%s) {\n" %
                        (INDENT * depth + alternative, pre_condition,
                         prefix,
                         child_field['camelCase'],
                         child_field['camelCase'],
                         child.predicate.term,
                         operator,
                         value))
                    term_analysis_fields.append((field,
                                                 child.predicate.term))
                elif type_key == 'items':
                    body += ( \
                        u"%sif (%sitemMatches(%s%s, \"%s\", \"%s\")%s%s) {\n" %
                        (INDENT * depth + alternative, pre_condition,
                         prefix,
                         child_field['camelCase'],
                         child_field['camelCase'],
                         child.predicate.term,
                         operator,
                         value))
                    item_analysis_fields.append((field,
                                                 child.predicate.term))
                else:
                    if child.predicate.value is None:
                        cmv.append(self.fields[field]['camelCase'])
                        value = 'null'
                    body += (u"%sif (%s%s%s%s%s) {\n" %
                                 (INDENT * depth + alternative, pre_condition,
                                  prefix,
                                  child_field['camelCase'],
                                  operator,
                                  value))
                next_level = child.plug_in_body(depth + 1, cmv=cmv[:],
                                                ids_path=ids_path,
                                                subtree=subtree)
                body += next_level[0]
                body += u"%s}\n" % (INDENT * depth)
                term_analysis_fields.extend(next_level[1])
                item_analysis_fields.extend(next_level[2])
                alternative = u"else "

        else:
            body = u"%sreturn %s%s%s;\n" % (INDENT * depth,
                                              separator,
                                              java_string(self.output),
                                              separator)
        return body, term_analysis_fields, item_analysis_fields
