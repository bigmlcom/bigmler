# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017-2022 BigML
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

from bigml.model import Model
from bigml.generators.model import get_ids_path

from bigmler.export.out_tree.tableautree import plug_in_body


class TableauModel(Model):
    """Tableau Model output generator class """

    def __init__(self, model, api=None, fields=None):
        """Empty attributes to be overriden

        """
        Model.__init__(self, model, api, fields)

    def plug_in(self, out=sys.stdout,
                filter_id=None, subtree=True, attr=None):
        """Returns a basic Tableau function that implements the model.

        `out` is file descriptor to write the tableau code.

        """
        ids_path = get_ids_path(self, filter_id)
        length = self.tableau(out, ids_path=ids_path,
                              subtree=subtree, attr=attr)
        if length > 0:
            out.write("END\n")
        else:
            sys.exit("\nFailed to represent this model in "
                     "in Tableau syntax. Currently, only "
                     "models with categorical and numeric fields "
                     "can be generated.\n")
        out.flush()

    def tableau(self, out, ids_path=None, subtree=True, attr=None):
        """Writes a Tableau function that implements the model.

        """
        body = plug_in_body(self.tree, self.offsets, self.fields,
                            self.objective_id, ids_path=ids_path,
                            subtree=subtree, attr=attr)
        out.write(body)
        out.flush()
        return len(body)
