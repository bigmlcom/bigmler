# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2021 BigML
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


""" Testing fusion predictions creation

"""


import os

from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module,
                                 teardown_class)


import bigmler.tests.composite_steps as composite_create
import bigmler.tests.basic_tst_prediction_steps as source_create


def setup_module():
    """Setup for the module

    """
    common_setup_module()


def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestComposite(object):

    def setup(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown(self):
        """Calling generic teardown for every method

        """
        self.world = teardown_class()
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)


    def test_scenario01(self):
        """
        Scenario: Successfully building a composite
            And I create a source from "<data>"
            And I check that the source is ready
            And I create an composite with the source
            And I check that the composite is ready
            And I check that the source is a composite component
            And I remove the source from the composite
            And I check that the composite is empty


        """
        print(self.test_scenario01.__doc__)
        examples = [
            ['data/iris.csv', './scenario41_01']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_create_source( \
                self, data=example[0], output_dir=example[1])
            source_create.i_check_create_source(self)
            self.sources = [world.source["resource"]]
            composite_create.i_create_composite_from_sources( \
                self, sources=",".join(self.sources), output_dir=example[1])
            composite_create.i_check_create_composite(self)
            composite_create.check_sources_in_composite(self)
            composite_create.remove_sources(self, output_dir=example[1])
            composite_create.i_check_create_composite(self)
            self.source = self.sources[0]
            self.sources = []
            composite_create.check_sources_in_composite(self)
            source_create.check_source_exists(self, exists=True)

    def test_scenario02(self):
        """
        Scenario: Successfully building a composite and adding sources
            And I create a source from "<data>"
            And I check that the source is ready
            And I create an empty composite and add the source
            And I check that the composite is ready
            And I check that the source is a composite component

        """
        print(self.test_scenario02.__doc__)
        examples = [
            ['data/iris.csv', './scenario41_02']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_create_source( \
                self, data=example[0], output_dir=example[1])
            source_create.i_check_create_source(self)
            self.sources = [world.source["resource"]]
            composite_create.i_create_empty_composite_and_add_source( \
                self, add_sources=",".join(self.sources),
                output_dir=example[1])
            composite_create.i_check_create_composite(self)
            composite_create.check_sources_in_composite(self)

    def test_scenario03(self):
        """
        Scenario: Successfully building a composite
            And I create a source from "<data>"
            And I check that the source is ready
            And I create an composite with the source
            And I check that the composite is ready
            And I check that the source is a composite component
            And I remove the source from the composite
            And I check that the composite is empty


        """
        print(self.test_scenario03.__doc__)
        examples = [
            ['data/iris.csv', './scenario41_03']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_create_source( \
                self, data=example[0], output_dir=example[1])
            source_create.i_check_create_source(self)
            self.sources = [world.source["resource"]]
            composite_create.i_create_composite_from_sources( \
                self, sources=",".join(self.sources), output_dir=example[1])
            composite_create.i_check_create_composite(self)
            composite_create.check_sources_in_composite(self)
            composite_create.delete_sources(self, output_dir=example[1])
            composite_create.i_check_create_composite(self)
            self.source = self.sources[0]
            self.sources = []
            composite_create.check_sources_in_composite(self)
            source_create.check_source_exists(self, exists=False)

    def test_scenario04(self):
        """
        Scenario: Successfully building an images composite
            And I create a source from a "<zip>" of "<images_number>" images
            And I check that the composite is ready
            And I check that it has "<images_number>" components

        """
        print(self.test_scenario04.__doc__)
        examples = [
            ['data/images/fruits_hist.zip', './scenario41_04']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_create_source( \
                self, data=example[0], output_dir=example[1])
            composite_create.i_check_create_composite(self)
            self.sources = world.source["object"].get("sources", [])
            composite_create.check_images_number_in_composite(self,
                                                              example[0])


    def test_scenario05(self):
        """
        Scenario: Successfully building an images composite from directory
            And I create a source from a "<directory>" of "<images_number>" images
            And I check that the composite is ready
            And I check that it has "<images_number>" components

        """
        print(self.test_scenario05.__doc__)
        examples = [
            ['data/images/fruits_hist/', './scenario41_05']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_create_source( \
                self, data=example[0], output_dir=example[1])
            composite_create.i_check_create_composite(self)
            self.sources = world.source["object"].get("sources", [])
            composite_create.check_images_number_in_composite(self,
                                                              example[0])


    def test_scenario06(self):
        """
        Scenario: Successfully building an annotated images composite
            And I create a source from an "<annotations_file>" and an "<images_file>"
            And I check that the composite is ready
            And I check that it has "<annotation_fields>"
        """
        print(self.test_scenario06.__doc__)
        examples = [
            ['data/images/fruits_hist.zip', 'data/images/annotations.json',
             './scenario41_06']]
        for example in examples:
            print("\nTesting with:\n", example)
            composite_create.i_create_annotated_source( \
                self, images_file=example[0], annotations_file=example[1],
                output_dir=example[2])
            composite_create.i_check_create_composite(self)
            self.sources = world.source["object"].get("sources", [])
            composite_create.check_images_number_in_composite(self,
                                                              example[0])
            composite_create.check_annotation_fields(self, example[1])

    def test_scenario07(self):
        """
        Scenario: Successfully building a <annotations_language> annotated images composite
            And I create a source from an "<annotations_dir>" and an "<images_dir>"
            And I check that the composite is ready
            And I check that it has "<annotation_fields>"
        """
        print(self.test_scenario07.__doc__)
        examples = [
            ['data/images/fruits_hist', 'data/images/VOC_annotations',
             './scenario41_07', 'VOC'],
            ['data/images/YOLO_annotations', 'data/images/YOLO_annotations',
             './scenario41_07', 'YOLO']]
        for example in examples:
            print("\nTesting with:\n", example)
            composite_create.i_create_lang_annotated_source( \
                self, images_dir=example[0], annotations_dir=example[1],
                annotations_language=example[3],
                output_dir=example[2])
            composite_create.i_check_create_composite(self)
            self.sources = world.source["object"].get("sources", [])
            composite_create.check_images_number_in_composite(self,
                                                              example[0])
            composite_create.check_annotation_fields(
                self,
                os.path.join(example[2], "annotations.json"))
