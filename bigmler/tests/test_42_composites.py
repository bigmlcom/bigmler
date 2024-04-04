# -*- coding: utf-8 -*-
#!/usr/bin/env python
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#
# Copyright 2021-2024 BigML
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
                                 common_teardown_module, show_method)


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


class TestComposite:
    """Testing Composite Sources"""

    def setup_method(self, method):
        """
            Debug information
        """
        self.bigml = {}
        self.bigml["method"] = method.__name__
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown_method(self):
        """Calling generic teardown for every method

        """
        world.clear_paths()
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)
        self.bigml = {}

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
        headers = ["data", "output_dir"]
        examples = [
            ['data/iris.csv', './scenario42_01']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_create_source( \
                self, data=example["data"], output_dir=example["output_dir"])
            source_create.i_check_create_source(self)
            self.sources = [world.source["resource"]]
            composite_create.i_create_composite_from_sources( \
                self, sources=",".join(self.sources),
                output_dir=example["output_dir"])
            composite_create.i_check_create_composite(self)
            composite_create.check_sources_in_composite(self)
            composite_create.remove_sources(
                self, output_dir=example["output_dir"])
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
        headers = ["data", "output_dir"]
        examples = [
            ['data/iris.csv', './scenario42_02']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_create_source(
                self, data=example["data"], output_dir=example["output_dir"])
            source_create.i_check_create_source(self)
            self.sources = [world.source["resource"]]
            composite_create.i_create_empty_composite_and_add_source(
                self, add_sources=",".join(self.sources),
                output_dir=example["output_dir"])
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
        headers = ["data", "output_dir"]
        examples = [
            ['data/iris.csv', './scenario42_03']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_create_source( \
                self, data=example["data"],
                output_dir=example["output_dir"])
            source_create.i_check_create_source(self)
            self.sources = [world.source["resource"]]
            composite_create.i_create_composite_from_sources(
                self, sources=",".join(self.sources),
                output_dir=example["output_dir"])
            composite_create.i_check_create_composite(self)
            composite_create.check_sources_in_composite(self)
            composite_create.delete_sources(
                self, output_dir=example["output_dir"])
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
        headers = ["data", "output_dir"]
        examples = [
            ['data/images/fruits_hist.zip', './scenario42_04']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_create_source( \
                self, data=example["data"], output_dir=example["output_dir"])
            composite_create.i_check_create_composite(self)
            self.sources = world.source["object"].get("sources", [])
            composite_create.check_images_number_in_composite(
                self, example["data"])

    def test_scenario05(self):
        """
        Scenario: Successfully building an images composite from directory
            And I create a source from a "<directory>" in <output_dir>
            And I check that the composite is ready
            And I check that it has the expected components
        """
        print(self.test_scenario05.__doc__)
        headers = ["directory", "output_dir"]
        examples = [
            ['data/images/fruits_hist/', './scenario42_05']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_create_source( \
                self, data=example["directory"],
                output_dir=example["output_dir"])
            composite_create.i_check_create_composite(self)
            self.sources = world.source["object"].get("sources", [])
            composite_create.check_images_number_in_composite(
                self, example["directory"])

    def test_scenario06(self):
        """
        Scenario: Successfully building an annotated images composite
            And I create a source from an "<annotations_file>" and an "<images_file>"
            And I check that the composite is ready
            And I check that it has the expected annotation_fields
        """
        print(self.test_scenario06.__doc__)
        headers = ["images_file", "annotations_file", "output_dir"]
        examples = [
            ['data/images/fruits_hist.zip', 'data/images/annotations.json',
             './scenario42_06']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            composite_create.i_create_annotated_source( \
                self, images_file=example["images_file"],
                annotations_file=example["annotations_file"],
                output_dir=example["output_dir"])
            composite_create.i_check_create_composite(self)
            self.sources = world.source["object"].get("sources", [])
            composite_create.check_images_number_in_composite(
                self, example["images_file"])
            composite_create.check_annotation_fields(
                self, example["annotations_file"])

    def test_scenario07(self):
        """
        Scenario: Successfully building a <annotations_language> annotated images composite
            And I create a source from an "<annotations_dir>" and an "<images_dir>" using <language> and log in <output_dir>
            And I check that the composite is ready
            And I check that it has the expected annotation fields
        """
        print(self.test_scenario07.__doc__)
        headers = ["images_dir", "annotations_dir", "output_dir", "language"]
        examples = [
            ['data/images/fruits_hist', 'data/images/VOC_annotations',
             './scenario42_07_v', 'VOC'],
            ['data/images/YOLO_annotations', 'data/images/YOLO_annotations',
             './scenario42_07_y', 'YOLO']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            composite_create.i_create_lang_annotated_source(
                self, images_dir=example["images_dir"],
                annotations_dir=example["annotations_dir"],
                annotations_language=example["language"],
                output_dir=example["output_dir"])
            composite_create.i_check_create_composite(self)
            self.sources = world.source["object"].get("sources", [])
            composite_create.check_images_number_in_composite(
                self, example["images_dir"])
            composite_create.check_annotation_fields(
                self,
                os.path.join(example["output_dir"], "annotations.json"))

    def test_scenario08(self):
        """
        Scenario: Successfully extracting <type> features from images composite
            And I create a source from a "<zip>" and store output in "<output_dir>" directory
            And I check that the composite is ready
            And I update the source to extract <features>
            And I check that the image analysis reflects the extracted types
        """
        print(self.test_scenario08.__doc__)
        headers = ["zip", "output_dir", "features"]
        examples = [
            ['data/images/fruits_hist.zip', './scenario42_08',
             [["dimensions"], ["level_histogram"], ["dimensions", "HOG"],
              ["dimensions", "average_pixels", "level_histogram", "HOG"]]]]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_create_source( \
                self, data=example["zip"], output_dir=example["output_dir"])
            composite_create.i_check_create_composite(self)
            for extracted_features in example["features"]:
                composite_create.i_extract_features(self, extracted_features,
                    example["output_dir"])
                composite_create.i_check_create_composite(self)
                composite_create.i_check_extracted_features(self,
                    extracted_features)

    def test_scenario09(self):
        """
        Scenario: Successfully extracting <type2> features from images composite
            And I create a source from a "<zip>" and store output in "<output_dir>" directory
            And I check that the composite is ready
            And I update the source to extract <feature> <option>
            And I check that the image analysis reflects the extracted features
        """
        print(self.test_scenario09.__doc__)
        headers = ["zip", "output_dir", "feature", "option"]
        examples = [
            ['data/images/fruits_hist.zip', './scenario42_09',
             "ws-level", 2],
            ['data/images/fruits_hist.zip', './scenario42_09',
             "pretrained-cnn", "mobilenet"]]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_create_source( \
                self, data=example["zip"], output_dir=example["output_dir"])
            composite_create.i_check_create_composite(self)
            composite_create.i_extract_t2_features(self, example["feature"],
                example["option"], example["output_dir"])
            composite_create.i_check_create_composite(self)
            composite_create.i_check_extracted_t2_features(
                self, example["feature"], example["option"])
