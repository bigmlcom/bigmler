# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2020 BigML
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


""" Testing export model generation

"""



from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, teardown_class)

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.export_steps as export

def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestExport(object):

    def teardown(self):
        """Calling generic teardown for every method

        """
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)
        teardown_class()

    def setup(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def test_scenario1(self):
        """
            Scenario: Successfully exporting models with params in the available languages:
                Given I create BigML resources uploading train "<data>" file using "<source_attributes>" and log in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                And I export the model as a function in "<language>"to "<output>"
                Then the export file is like "<check_file>"

                Examples:
                | data                 | source_attributes             | output                 | language       | check_file
                | ../data/movies.csv   | data/movies_source_attrs.json | ./scenario_exp_1/model | python         | model_function.py

        """
        print(self.test_scenario1.__doc__)
        examples = [
            ['data/movies.csv', 'data/movies_source_attrs.json', 'scenario_exp_1_a/model', 'python', 'check_files/export/model_function.py'],
            ['data/movies.csv', 'data/movies_source_attrs.json', 'scenario_exp_1_b/model', 'javascript', 'check_files/export/model_function.js'],
            ['data/movies.csv', 'data/movies_source_attrs.json', 'scenario_exp_1_c/model', 'r', 'check_files/export/model_function.R'],
            ['data/iris.csv', '', 'scenario_exp_1_d/model', 'tableau', 'check_files/export/model_function.tb'],
            ['data/iris.csv', '', 'scenario_exp_1_e/model', 'mysql', 'check_files/export/model_function.sql'],
            ['data/libros.csv', 'data/libros_source_attrs.json', 'scenario_exp_1_f/model', 'python', 'check_files/export/model_function_utf8.py'],
            ['data/libros.csv', 'data/libros_source_attrs.json', 'scenario_exp_1_g/model', 'r', 'check_files/export/model_function_utf8.R'],
            ['data/libros.csv', 'data/libros_source_attrs.json', 'scenario_exp_1_h/model', 'javascript', 'check_files/export/model_function_utf8.js']]
        for example in examples:
            print("\nTesting with:\n", example)
            export.i_create_all_resources_to_model_with_source_attrs( \
                self, data=example[0], source_attributes=example[1], output=example[2])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_check_create_model(self)
            export.i_export_model(self, language=example[3], output=example[2])
            export.i_check_if_the_output_is_like_expected_file( \
                self, language=example[3], expected_file=example[4])
