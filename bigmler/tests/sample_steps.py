import os
import time
import csv
import json
from world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigmler.checkpoint import file_number_of_lines
from bigmler.utils import SYSTEM_ENCODING
from bigml.api import check_resource
from common_steps import check_debug


#@step(r'I create a new sample from the dataset and get the sample using options "(.*)" storing logs in "(.*)"')
def i_create_sample(step, options=None, output_dir=None):
    if options is None or output_dir is None:
        assert False
    world.directory = output_dir
    world.folders.append(world.directory)
    try:
        command = (u"bigmler sample --dataset " + world.dataset['resource'] +
                   u" --store --output-dir " + output_dir +
                   u" " + options)
        command = check_debug(command)
        retcode = check_call(command.encode(SYSTEM_ENCODING), shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output_dir
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I check that the sample has been created')
def i_check_create_sample(step):
    sample_file = "%s%ssamples" % (world.directory, os.sep)
    try:
        sample_file = open(sample_file, "r")
        sample = check_resource(sample_file.readline().strip(),
                                world.api.get_sample)
        world.samples.append(sample['resource'])
        world.sample = sample
        sample_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)


#@step(r'the sample contains stat-info like in "(.*)"')
def i_check_sample_stat(step, check_sample_json=None):
    if check_sample_json is None:
        assert False
    check_sample_json = res_filename(check_sample_json)
    try:
        sample_json = os.path.join(world.directory, "stat_info.json")
        with open(check_sample_json, "r") as check_sample_file:
            check_sample_contents = check_sample_file.read()
        with open(sample_json, "r") as sample_file:
            sample_file_contents = sample_file.read()
        if check_sample_contents == sample_file_contents:
            assert True
        else:
            assert False, ("File contents:\n%s\nExpected contents:\n%s" %
                           (sample_file_contents, check_sample_contents))
    except Exception, exc:
        assert False, str(exc)


#@step(r'the sample file is like "(.*)"')
def i_check_sample_file(step, check_sample_file=None):
    if check_sample_file is None:
        assert False
    check_sample_file = res_filename(check_sample_file)
    try:
        sample_file = os.path.join(world.directory, "sample.csv")
        with open(check_sample_file, "r") as check_sample_file:
            check_sample_contents = check_sample_file.read()
        with open(sample_file, "r") as sample_file:
            sample_file_contents = sample_file.read()
        if check_sample_contents == sample_file_contents:
            assert True
        else:
            assert False, ("File contents:\n%s\nExpected contents:\n%s" %
                           (sample_file_contents, check_sample_contents))
    except Exception, exc:
        assert False, str(exc)
