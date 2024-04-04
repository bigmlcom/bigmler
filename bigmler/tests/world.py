# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2024 BigML
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


""" Mimic World lettuce object

"""



import os
import shutil
import time
import datetime
import re
import math

from subprocess import check_call

import pytest
import pkg_resources


from bigml.api import BigML
from bigml.api import HTTP_OK, HTTP_NO_CONTENT, HTTP_NOT_FOUND
from bigml.constants import IRREGULAR_PLURALS


MAX_RETRIES = 10
RESOURCE_TYPES = [
    'cluster',
    'fusion',
    'optiml',
    'composite',
    'source',
    'dataset',
    'prediction',
    'evaluation',
    'ensemble',
    'batchprediction',
    'centroid',
    'batchcentroid',
    'anomaly',
    'anomalyscore',
    'batchanomalyscore',
    'project',
    'sample',
    'correlation',
    'statisticaltest',
    'logisticregression',
    'model',
    'deepnet',
    'association',
    'associationset',
    'configuration',
    'topicmodel',
    'topicdistribution',
    'timeseries',
    'forecast',
    'pca',
    'projection',
    'batchprojection',
    'linearregression',
    'script',
    'execution',
    'library',
    'externalconnector']

irregular_plurals = {}
irregular_plurals.update(IRREGULAR_PLURALS)
irregular_plurals.update({"timeseries": "time_series_set"})

TRANSLATED_RESOURCES = {
    'batchprediction': 'batch_prediction',
    'batchcentroid': 'batch_centroid',
    'anomalyscore': 'anomaly_score',
    'batchanomalyscore': 'batch_anomaly_score',
    'logisticregression': 'logistic_regression',
    'linearregression': 'linear_regression',
    'topicmodel': 'topic_model',
    'topicdistribution': 'topic_distribution',
    'timeseries': 'time_series',
    'batchtopicdistribution': 'batch_topic_distribution',
    'batchprojection': 'batch_projection',
    'externalconnector': 'external_connector'}


def show_doc(self, examples=None):
    """ Shows the name and documentation of the method passed as argument

    """
    print("%s:\n%s" % (self.__name__, self.__doc__))
    if examples:
        print("                |%s" % \
            "\n                |".join(["|".join([str(item)
                                                  for item in example]) for
                                        example in examples]))


def show_method(self, method, example):
    """Prints the test class and method of the current test"""
    class_name = re.sub(".*'(.*)'.*", "\\1", str(self.__class__))
    print("\nTesting %s %s with:\n" % (class_name, method), example)


def plural(resource_type):
    """Creates the plural form of a resource type

    """
    return irregular_plurals.get(resource_type, "%ss" % resource_type)


def bigmler_delete(directory, output_dir=None):
    """Deletes all remote resources found in the bigmler directory and
       the local directory itself.

    """
    try:
        retcode = check_call("bigmler delete --output-dir " + output_dir +
                             " --from-dir " + directory, shell=True)
        if retcode == 0:
            if os.path.exists(directory):
                shutil.rmtree(directory)
    except OSError:
        pass


def float_round(value, precision=5):
    """Rounding if float"""
    if isinstance(value, float):
        return round(value, precision)
    return value


def eq_(*args, msg=None, precision=None):
    """Wrapper to assert. If precision is set, previous rounding"""
    new_args = list(args)
    if msg is None:
        msg = "Different values: %s" % ", ".join(
            [str(arg) for arg in new_args])
    if precision is not None:
        for index, arg in enumerate(new_args):
            new_args[index] = float_round(arg, precision)
        assert all(new_args[0] == b for b in new_args[1:]), msg
    else:
        assert new_args[0] == new_args[1], msg


#pylint: disable=locally-disabled,inconsistent-return-statements
def ok_error(value, msg=None):
    """Wrapper to return error message"""
    if value:
        return None
    return msg


def ok_(value, msg=None):
    """Wrapper to assert."""
    if msg is None:
        assert value
    else:
        assert value, msg


def approx_error(number_a, number_b, msg=None, precision=5):
    """Wrapper to assert only on approximate error"""
    epsilon = math.pow(0.1, precision)
    if number_a == pytest.approx(number_b, abs=epsilon):
        return None
    return msg


def approx_(number_a, number_b, msg=None, precision=5):
    """Wrapper for pytest approx function"""
    epsilon = math.pow(0.1, precision)
    if msg is None:
        assert number_a == pytest.approx(number_b, abs=epsilon)
    else:
        assert number_a == pytest.approx(number_b, abs=epsilon), msg


class World:
    """Object to store common test resources"""

    def __init__(self):
        self.username = None
        self.api_key = None
        self.api = None
        self.debug = False
        self.api_debug = False
        self.source_lower = None
        self.source_upper = None
        self.source_reference = None
        self.output = None
        self.directory = None
        self.clear()
        self.dataset_ids = []
        self.fields_properties_dict = {}
        self.counters = {}
        self.folders = []
        self.test_project_name = "Test: BigMLer %s" % \
            datetime.datetime.now()
        self.project_id = None
        self.print_connection_info()

    def print_connection_info(self):
        """Prints the variables used for the connection authentication"""
        self.username = os.environ.get('BIGML_USERNAME')
        self.api_key = os.environ.get('BIGML_API_KEY')
        try:
            self.debug = bool(os.environ.get('BIGMLER_DEBUG', 0))
            self.api_debug = bool(os.environ.get('BIGML_DEBUG', 0))
            self.delta = int(os.environ.get('BIGML_DELTA', 1))
        except ValueError:
            pass
        if self.username is None or self.api_key is None:
            assert False, ("Tests use the BIGML_USERNAME and BIGML_API_KEY"
                           " environment variables to authenticate the"
                           " connection, but they seem to be unset. Please,"
                           "set them before testing.")
        else:
            assert True
        self.api = BigML(self.username, self.api_key, debug=self.api_debug)
        print(self.api.connection_info())
        output_dir = "./last_run"
        dirs = []
        for _, sub_folders, _ in os.walk("./"):
            for folder in sub_folders:
                if folder.startswith("scenario"):
                    dirs.append(folder)
        dirs.reverse()
        for folder in dirs:
            bigmler_delete(folder, output_dir=output_dir)
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

    def count_resources(self, time_tag, changed=False):
        """Counts the existing resources and stores it keyed by time_tag.
           If changed is set to True, only resources that are logged as
           changed are listed.
        """
        print("Counting resources (%s)." % time_tag)
        for resource_type in RESOURCE_TYPES:
            if resource_type == "composite":
                resource_type = "source"
            resource_type = plural(resource_type)
            if resource_type == "time_series_set":
                resource_type = "time_series"
            if (not changed or len(getattr(self, resource_type))) > 0:
                resources = getattr(self.api,"list_%s" % resource_type)()
                if resource_type == 'source' and resources['code'] != HTTP_OK:
                    assert False, (
                        "Unable to list your sources. Please check the"
                        " BigML domain and credentials to be:\n\n%s" %
                        self.api.connection_info())
                else:
                    if resources['code'] == HTTP_OK:
                        assert True
                    else:
                        assert False, ("HTTP returned code %s for listing %s" %
                                       (resources['code'], resource_type))
                    if not resource_type in self.counters:
                        self.counters[resource_type] = {}
                    self.counters[resource_type][time_tag] = resources[
                        'meta']['total_count']

    def clear(self):
        """Clears the stored resources' ids

        """
        for resource_type in RESOURCE_TYPES:
            setattr(self, plural(resource_type), [])
            setattr(self, TRANSLATED_RESOURCES.get(resource_type,
                                                   resource_type), None)
        self.source_lower = None
        self.source_upper = None
        self.source_reference = None

    def delete_resources(self):
        """Deletes the created objects

        """
        for resource_type in RESOURCE_TYPES:
            object_list = getattr(self, plural(resource_type))
            object_list.reverse()
            if object_list:
                print("Deleting %s %s" % (len(object_list),
                                          plural(resource_type)))
                kwargs = {}
                if resource_type == "composite":
                    resource_type = "source"
                    kwargs = {"query_string": "delete_all=true"}
                delete_method = self.api.deleters[resource_type]
                for obj_id in object_list:
                    counter = 0
                    print("Deleting %s" % obj_id)
                    result = delete_method(obj_id, **kwargs)
                    while (result['code'] not in [HTTP_NO_CONTENT,
                                                  HTTP_NOT_FOUND] and
                           counter < MAX_RETRIES):
                        print("Delete failed for %s. Retrying" % obj_id)
                        time.sleep(3 * self.delta)
                        counter += 1
                        result = delete_method(obj_id, **kwargs)
                    if counter == MAX_RETRIES:
                        print ("Retries to delete the created resources are"
                               " exhausted. Failed to delete.")

    def check_init_equals_final(self):
        """ Checks if the counters in init and final timestap are unchanged
        """
        for resource_type in RESOURCE_TYPES:
            resource_type = plural(resource_type)
            if getattr(self, resource_type):
                counters = self.counters[resource_type]
                if counters['final'] == counters['init']:
                    assert True
                else:
                    assert False , (
                        "init %s: %s, final %s: %s" %
                        (resource_type, counters['init'],
                         resource_type, counters['final']))

    def clear_paths(self):
        """Cleaning the output paths"""
        self.output = ""
        self.directory = ""

world = World()


def res_filename(filename):
    """Returns path to a data filename"""
    directory = pkg_resources.resource_filename('bigmler', '__init__.py')
    return os.path.join(os.path.dirname(os.path.dirname(directory)), filename)


def common_setup_module():
    """Operations to be performed before each module

    """
    if world.project_id is None:
        world.project_id = world.api.create_project( \
            {"name": world.test_project_name})['resource']
    world.clear()


def common_teardown_module():
    """Operations to be performed after each module

    """
    if os.path.exists('./tmp'):
        shutil.rmtree('./tmp')

    if not world.debug:
        world.delete_resources()
        project_stats = world.api.get_project(
            world.project_id)['object']['stats']
        for resource_type, value in list(project_stats.items()):
            if value['count'] != 0:
                print("WARNING: Increment in %s: %s" % (resource_type, value))
        world.api.delete_project(world.project_id)
        world.project_id = None

        for folder in world.folders:
            try:
                shutil.rmtree(folder)
            except Exception:
                pass
