import os

from world import world

from bigml.api import HTTP_OK, HTTP_UNAUTHORIZED

def check_debug(command):
    """Adds verbosity level and command print.

    """
    debug = os.environ.get('BIGMLER_DEBUG', False)
    verbosity = 0
    if debug:
        verbosity = 1
        print command
    command = "%s --verbosity %s" % (command, verbosity)
    return command

def check_http_code(resources):
    """Checks the http code in the resource list

    """
    if resources['code'] == HTTP_OK:
        assert True
    else:
        assert False, "Response code: %s" % resources['code']

def store_init_resources():
    """Store the initial existing resources grouped by resource_type

    """
    world.count_resources('init')

def store_final_resources():
    """Store the final existing resources grouped by resource_type

    """
    world.count_resources('final')

def check_init_equals_final():
    """Checks that the number of resources grouped by type has not changed

    """
    world.check_init_equals_final()

#@step(r'I want to use api in DEV mode')
def i_want_api_dev_mode(step):
    world.api = world.api_dev_mode
    # Update counters of resources for DEV mode
    world.count_resources('init')
