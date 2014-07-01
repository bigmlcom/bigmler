import os
import time
import csv
import json
from lettuce import step, world
from subprocess import check_call, CalledProcessError
from bigml.api import check_resource
from bigmler.checkpoint import file_number_of_lines
from common_steps import check_debug


def shell_execute(command, output, test=None, options=None):
    """Excute bigmler command in shell

    """
    command = check_debug(command)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            if test is not None:
                world.test_lines = file_number_of_lines(test)
                if options is None or options.find('--prediction-header') == -1:
                    # test file has headers in it, so first line must be ignored
                    world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


@step(r'I create BigML resources uploading train "(.*?)" file to create centroids for "(.*?)" and log predictions in "([^"]*)"$')
def i_create_all_cluster_resources(step, data=None, test=None, output=None):
    if data is None or test is None or output is None:
        assert False
    command = ("bigmler cluster --train " + data + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


@step(r'I check that the cluster has been created')
def i_check_create_cluster(step):
    cluster_file = "%s%sclusters" % (world.directory, os.sep)
    try:
        cluster_file = open(cluster_file, "r")
        cluster = check_resource(cluster_file.readline().strip(),
                                 world.api.get_cluster)
        world.clusters.append(cluster['resource'])
        world.cluster = cluster
        cluster_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)


@step(r'I check that the centroids are ready')
def i_check_create_centroids(step):

    previous_lines = -1
    predictions_lines = 0
    try:
        predictions_file = world.output
        predictions_file = open(predictions_file, "r")
        predictions_lines = 0
        for line in predictions_file:
            predictions_lines += 1
        if predictions_lines == world.test_lines:
            assert True
        else:
            assert False, "predictions lines: %s, test lines: %s" % (predictions_lines, world.test_lines)
        predictions_file.close()
    except Exception, exc:
        print str(exc)
        assert False, str(exc)


@step(r'the local centroids file is like "(.*)"')
def i_check_centroids(step, check_file):
    predictions_file = world.output
    try:
        predictions_file = csv.reader(open(predictions_file, "U"), lineterminator="\n")
        check_file = csv.reader(open(check_file, "U"), lineterminator="\n")
        for row in predictions_file:
            check_row = check_file.next()
            if len(check_row) != len(row):
                assert False
            for index in range(len(row)):
                if check_row[index] != row[index]:
                    print row, check_row
                    assert False
        assert True
    except Exception, exc:
        assert False, str(exc)


@step(r'I create BigML resources using dataset to find centroids for "(.*)" and log predictions in "(.*)"')
def i_create_cluster_resources_from_dataset(step, test=None, output=None):
    if test is None or output is None:
        assert False
    command = ("bigmler cluster --dataset " +
               world.dataset['resource'] + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


@step(r'I create BigML resources using source to find centroids for "(.*)" and log predictions in "(.*)"')
def i_create_cluster_resources_from_source(step, test=None, output=None):
    if test is None or output is None:
        assert False
    command = ("bigmler cluster --source " +
               world.source['resource'] + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


@step(r'I create BigML resources using cluster to find centroids for "(.*)" and log predictions in "(.*)"')
def i_create_cluster_resources_from_cluster(step, test=None, output=None):
    if test is None or output is None:
        assert False
    command = ("bigmler cluster --cluster " +
               world.cluster['resource'] + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


@step(r'I create BigML resources using clusters in file "(.*)" to find centroids for "(.*)" and log predictions in "(.*)"')
def i_create_cluster_resources_from_clusters_file(step, clusters_file=None, test=None, output=None):
    if test is None or output is None or clusters_file is None:
        assert False
    command = ("bigmler cluster --clusters " +
               clusters_file + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


@step(r'I create BigML resources uploading train "(.*?)" file to find centroids for "(.*?)" remotely with mapping file "(.*)" and log predictions in "([^"]*)"$')
def i_create_all_cluster_resources_with_mapping(step, data=None, test=None, fields_map=None, output=None):
    if data is None or test is None or output is None or fields_map is None:
        assert False
    command = ("bigmler cluster --remote --train " + data + " --test " + test +
               " --fields-map " + fields_map +
               " --store --output " + output)
    shell_execute(command, output, test=test)

