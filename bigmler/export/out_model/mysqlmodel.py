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

"""Tree level output for MySQL

This module defines functions that generate MySQL SQL code to make local
predictions
"""
import sys

from bigml.tree_utils import slugify, INDENT, sort_fields, docstring_comment, \
    MAX_ARGS_LENGTH, TERM_OPTIONS
from bigml.model import Model

from bigmler.export.out_tree.mysqltree import MySQLTree

class MySQLModel(Model):


    def __init__(self, model, api=None, fields=None):
        """Empty attributes to be overriden

        """
        self.tree_class = MySQLTree
        Model.__init__(self, model, api, fields)

    def plug_in(self, out=sys.stdout, filter_id=None, subtree=True, attr=None):
        """Generates a basic MySQL SQL expression that implements a function
           describing the model.

        `out`  is file descriptor to write the MySQL code.
        `attr` is used to predict an attribute (e.g 'confidence') other
               than the output

        """
        ids_path = self.get_ids_path(filter_id)
        length = self.mysql(out, ids_path=ids_path, subtree=subtree,
                            attr=attr)
        if length > 0:
            out.write(u"\n\n")
        else:
            sys.exit(u"\nFailed to represent this model "
                     u"in MySQL syntax. Currently only models with "
                     u"categorical and numeric fields can be generated.\n")
        out.flush()

    def mysql(self, out, ids_path=None, subtree=True, attr=None):
        """Writes a MySQL function that implements the model.

        """

        definition = "CREATE FUNCTION predict_%s (%s)" \
                     "\nRETURNS %s DETERMINISTIC\nRETURN "
        args = []
        parameters = sort_fields(self.fields)
        for field_id, field in parameters:
            field_name_to_show = self.fields[field_id]['name'].strip()
            field_type = 'NUMERIC' if field['optype'] == 'numeric' else \
                'VARCHAR(250)'
            if field_name_to_show == "":
                field_name_to_show = field_id
            if field_id != self.objective_id:
                args.append("`%s` %s" % (field_name_to_show,
                                         field_type))
        objective = self.fields[self.objective_id]
        function_name = objective['name']
        return_type = 'NUMERIC' if objective['optype'] == 'numeric' else \
            'VARCHAR(250)'
        if function_name == "":
            function_name = "field_" + self.objective_id
        # when the output is a confidence metric (error/confidence)
        if attr is not None:
            function_name += "_%s" % attr
            return_type = 'NUMERIC'
        definition = definition % (function_name, ", ".join(args), return_type)
        out.write(definition)
        body = self.tree.plug_in_body(ids_path=ids_path, subtree=subtree,
                                      attr=attr)

        out.write(body)
        out.flush()
        return len(body)
