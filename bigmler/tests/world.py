# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2017 BigML
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

from __future__ import absolute_import

import os
import shutil
import time
import pkg_resources
import datetime

from bigml.api import BigML
from bigml.api import HTTP_OK, HTTP_NO_CONTENT, HTTP_UNAUTHORIZED

from subprocess import check_call

MAX_RETRIES = 10
RESOURCE_TYPES = [
    'cluster',
    'source',
    'dataset',
    'model',
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
    'association',
    'logisticregression',
    'topicmodel',
    'topicdistribution',
    'batchtopicdistribution',
    'script',
    'library',
    'execution']
IRREGULAR_PLURALS = {
    'anomaly': 'anomalies',
    'batchprediction': 'batch_predictions',
    'batchcentroid': 'batch_centroids',
    'anomalyscore': 'anomaly_scores',
    'batchanomalyscore': 'batch_anomaly_scores',
    'logisticregression': 'logistic_regressions',
    'topicmodel': 'topic_models',
    'topicdistribution': 'topic_distributions',
    'batchtopicdistribution': 'batch_topic_distributions',
    'library': 'libraries'}
TRANSLATED_RESOURCES = {
    'batchprediction': 'batch_prediction',
    'batchcentroid': 'batch_centroid',
    'anomalyscore': 'anomaly_score',
    'batchanomalyscore': 'batch_anomaly_score',
    'logisticregression': 'logistic_regression',
    'topicmodel': 'topic_model',
    'topicdistribution': 'topic_distribution',
    'batchtopicdistribution': 'batch_topic_distributions'}


def show_doc(self, examples=None):
    """ Shows the name and documentation of the method passed as argument

    """
    print "%s:\n%s" % (self.__name__, self.__doc__)
    if examples:
        print "                |%s" % \
            "\n                |".join(["|".join([str(item)
                                                  for item in example]) for
                                        example in examples])


def plural(resource_type):
    """Creates the plural form of a resource type

    """
    return IRREGULAR_PLURALS.get(resource_type, "%ss" % resource_type)


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
    except OSError as e:
        pass


class World(object):

    def __init__(self):
        self.USERNAME = None
        self.API_KEY = None
        self.api = None
        self.api_dev_mode = None
        self.debug = False
        self.api_debug = False
        self.source_lower = None
        self.source_upper = None
        self.source_reference = None
        self.reset_api()
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
        self.USERNAME = os.environ.get('BIGML_USERNAME')
        self.API_KEY = os.environ.get('BIGML_API_KEY')
        try:
            self.debug = bool(os.environ.get('BIGMLER_DEBUG', 0))
            self.api_debug = bool(os.environ.get('BIGML_DEBUG', 0))
        except ValueError:
            pass
        if self.USERNAME is None or self.API_KEY is None:
            assert False, ("Tests use the BIGML_USERNAME and BIGML_API_KEY"
                           " environment variables to authenticate the"
                           " connection, but they seem to be unset. Please,"
                           "set them before testing.")
        else:
            assert True
        self.api = BigML(self.USERNAME, self.API_KEY, debug=self.api_debug)
        print self.api.connection_info()
        output_dir = "./last_run"
        for _, subFolders, _ in os.walk("./"):
            for folder in subFolders:
                if folder.startswith("scenario"):
                    bigmler_delete(folder, output_dir=output_dir)
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

    def count_resources(self, time_tag, changed=False):
        """Counts the existing resources and stores it keyed by time_tag.
           If changed is set to True, only resources that are logged as
           changed are listed.
        """
        print "Counting resources (%s)." % time_tag
        for resource_type in RESOURCE_TYPES:
            resource_type = plural(resource_type)
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
                        assert False, ("HTTP returned code %s for %s" %
                                       (resources['code'], resource_type))
                    if (not resource_type in self.counters):
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

    def reset_api(self):
        """Reset the api connection values

        """
        self.api = BigML(self.USERNAME, self.API_KEY, debug=self.api_debug)
        self.api_dev_mode = BigML(self.USERNAME, self.API_KEY, dev_mode=True,
                                  debug=self.api_debug)

    def delete_resources(self):
        """Deletes the created objects

        """
        for resource_type in RESOURCE_TYPES:
            object_list = getattr(self, plural(resource_type))
            if object_list:
                print "Deleting %s %s" % (len(object_list),
                                          plural(resource_type))
                delete_method = self.api.deleters[resource_type]
                for obj_id in object_list:
                    counter = 0
                    result = delete_method(obj_id)
                    while (result['code'] != HTTP_NO_CONTENT and
                           counter < MAX_RETRIES):
                        print "Delete failed for %s. Retrying" % obj_id
                        time.sleep(3)
                        counter += 1
                        result = delete_method(obj_id)
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

world = World()

def res_filename(file):
    return pkg_resources.resource_filename('bigmler', "../../../%s" % file)


def common_setup_module():
    """Operations to be performed before each module

    """
    world.reset_api()
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
        project_stats = world.api.get_project( \
            world.project_id)['object']['stats']
        for resource_type, value in project_stats.items():
            if value['count'] != 0:
                print "WARNING: Increment in %s: %s" % (resource_type, value)
        world.api.delete_project(world.project_id)
        world.project_id = None

        for folder in world.folders:
            try:
                shutil.rmtree(folder)
            except:
                pass


def teardown_class():
    """Operations to be performed after each class

    """
    world.output = ""
    world.directory = ""
