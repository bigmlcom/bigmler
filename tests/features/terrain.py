# terrain.py
import os
import shutil
import time

from lettuce import before, after, world

from bigml.api import BigML, get_resource_type
from bigml.api import HTTP_NO_CONTENT
from subprocess import check_call
from common_steps import (store_init_resources, store_final_resources,
                          check_init_equals_final)

MAX_RETRIES = 10


def delete(object_list):
    """Deletes the objects in object_list using the api delete method

    """

    for obj_id in object_list:
        counter = 0
        delete_method = world.api.deleters[get_resource_type(obj_id)]
        result = delete_method(obj_id)
        while result['code'] != HTTP_NO_CONTENT and counter < MAX_RETRIES:
            print ("Failed to delete %s with code %s. Retrying." %
                   (obj_id, result['code']))
            time.sleep(3)
            counter += 1
            result = delete_method(obj_id)
        if counter == MAX_RETRIES:
            print ("Retries to delete the created resources are exhausted."
                   " Failed to delete.")
    object_list = []


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


@before.all
def print_connection_info():
    world.USERNAME = os.environ.get('BIGML_USERNAME')
    world.API_KEY = os.environ.get('BIGML_API_KEY')
    if world.USERNAME is None or world.API_KEY is None:
        assert False, ("Tests use the BIGML_USERNAME and BIGML_API_KEY"
                       " environment variables to authenticate the"
                       " connection, but they seem to be unset. Please,"
                       "set them before testing.")
    else:
        assert True
    world.api = BigML(world.USERNAME, world.API_KEY)
    print world.api.connection_info()

    world.folders = []
    output_dir = "./last_run"
    for _, subFolders, _ in os.walk("./"):
        for folder in subFolders:
            if folder.startswith("scenario"):
                bigmler_delete(folder, output_dir=output_dir)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)


@before.each_feature
def setup_resources(feature):
    world.USERNAME = os.environ['BIGML_USERNAME']
    world.API_KEY = os.environ['BIGML_API_KEY']
    assert world.USERNAME is not None
    assert world.API_KEY is not None
    world.api = BigML(world.USERNAME, world.API_KEY)
    world.api_dev_mode = BigML(world.USERNAME, world.API_KEY, dev_mode=True)
    world.test_lines = 0

    store_init_resources()

    world.sources = []
    world.datasets = []
    world.models = []
    world.predictions = []
    world.evaluations = []
    world.ensembles = []
    world.batch_predictions = []
    world.clusters = []
    world.centroids = []
    world.batch_centroids = []
    world.anomalies = []
    world.anomaly_scores = []
    world.batch_anomaly_scores = []
    world.projects = []
    world.samples = []
    world.source_lower = None
    world.source_upper = None
    world.source_reference = None

@after.each_feature
def cleanup_resources(feature):
    if os.path.exists('./tmp'):
        shutil.rmtree('./tmp')

    delete(world.clusters)
    delete(world.sources)
    delete(world.datasets)
    delete(world.models)
    delete(world.predictions)
    delete(world.evaluations)
    delete(world.ensembles)
    delete(world.batch_predictions)
    delete(world.centroids)
    delete(world.batch_centroids)
    delete(world.anomalies)
    delete(world.anomaly_scores)
    delete(world.batch_anomaly_scores)
    delete(world.projects)
    delete(world.samples)

    store_final_resources()
    for folder in world.folders:
        try:
            shutil.rmtree(folder)
        except:
            pass

    check_init_equals_final()


@after.each_scenario
def cleanup_output(scenario):
    world.output = ""
