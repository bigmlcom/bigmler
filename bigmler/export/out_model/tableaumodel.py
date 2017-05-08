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

"""Tree level output for Tableau

This module defines functions that generate Tableau code to make local
predictions
"""
import sys

from bigmler.export.out_tree.tableautree import TableauTree

from bigml.model import Model

class TableauModel(Model):


    def __init__(self, model, api=None, fields=None):
        """Empty attributes to be overriden

        """
        self.tree_class = TableauTree
        Model.__init__(self, model, api, fields)

    def plug_in(self, out=sys.stdout, hadoop=False,
                filter_id=None, subtree=True):
        """Returns a basic Tableau function that implements the model.

        `out` is file descriptor to write the tableau code.

        """
        ids_path = self.get_ids_path(filter_id)
        if hadoop:
            return "Hadoop output not available."
        else:
            response = self.tableau(out, ids_path=ids_path,
                                    subtree=subtree)
            if response:
                out.write(u"END\n")
            else:
                sys.exit(u"\nFailed to represent this model in "
                         u"in Tableau syntax. Currently, only "
                         u"models with categorical and numeric fields "
                         u"can be generated.\n")
            out.flush()
            return None

    def tableau(self, out, ids_path=None, subtree=True):
        """Writes a Tableau function that implements the model.

        """
        body = self.tree.tableau_body(ids_path=ids_path, subtree=subtree)
        if not body:
            return False
        out.write(body)
        out.flush()
        return True
