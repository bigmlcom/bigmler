def check_debug(command):
    """Adds verbosity level and command print.

    """
    debug = False
    verbosity = 0
    if debug:
        verbosity = 1
        print command
    command = "%s --verbosity %s" % (command, verbosity)
    return command  
