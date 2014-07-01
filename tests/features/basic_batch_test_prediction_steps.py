import os
import time
import csv
import json
from lettuce import step, world
from subprocess import check_call, CalledProcessError
from bigml.api import check_resource


@step(r'I check that the batch prediction has been created')
def i_check_create_batch_prediction(step):
    batch_prediction_file = "%s%sbatch_prediction" % (world.directory, os.sep)
    try:
        batch_prediction_file = open(batch_prediction_file, "r")
        batch_prediction = check_resource(batch_prediction_file.readline().strip(),
                                          world.api.get_batch_prediction)
        world.batch_predictions.append(batch_prediction['resource'])
        world.batch_prediction = batch_prediction
        batch_prediction_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)


@step(r'I check that the source has been created from the test file')
def i_check_create_test_source(step):
    test_source_file = "%s%ssource_test" % (world.directory, os.sep)
    try:
        test_source_file = open(test_source_file, "r")
        test_source = check_resource(test_source_file.readline().strip(),
                                     world.api.get_source)
        world.sources.append(test_source['resource'])
        world.test_source = test_source
        test_source_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)


@step(r'I check that the dataset has been created from the test file')
def i_check_create_test_dataset(step):
    test_dataset_file = "%s%sdataset_test" % (world.directory, os.sep)
    try:
        test_dataset_file = open(test_dataset_file, "r")
        test_dataset = check_resource(test_dataset_file.readline().strip(),
                                      world.api.get_dataset)
        world.datasets.append(test_dataset['resource'])
        world.test_dataset = test_dataset
        test_dataset_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)


@step(r'I check that the batch centroid prediction has been created')
def i_check_create_batch_centroid(step):
    batch_prediction_file = "%s%sbatch_centroid" % (world.directory, os.sep)
    try:
        batch_prediction_file = open(batch_prediction_file, "r")
        batch_centroid = check_resource(batch_prediction_file.readline().strip(),
                                          world.api.get_batch_centroid)
        world.batch_centroids.append(batch_centroid['resource'])
        world.batch_centroid = batch_centroid
        batch_prediction_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)
