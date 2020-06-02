# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 BigML
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


"""Options for BigMLer time series

"""
import sys


def int_or_none(value):
    """Casts to integer if the value is not None

    """
    if value is not None:
        return int(value)
    return None


def range(value):
    """Creates a range from two comma-separated integers

    """
    if "," not in value:
        sys.exit("Failed to parse a comma-separated pair of integers")
    try:
        min, max = value.split(",")
        return [int(min), int(max)]
    except ValueError:
        sys.exit("Failed to parse a comma-separated pair of integers")


def get_time_series_options(defaults=None):
    """Adding arguments for the time series subcommand

    """

    if defaults is None:
        defaults = {}

    options = {

        # If a BigML logistic regression is provided, the script will
        # use it to generate predictions
        '--time-series': {
            'action': 'store',
            'dest': 'time_series',
            'default': defaults.get('time_series', None),
            'help': "BigML time series Id."},

        # The path to a file containing time series ids.
        '--time-series-set': {
            'action': 'store',
            'dest': 'time_series_set',
            'default': defaults.get('time_series_set', None),
            'help': ("Path to a file containing timeseries/ids."
                     " One timeseries"
                     " per line (e.g., "
                     "timeseries/50a206a8035d0706dc000376"
                     ").")},

        # If a BigML json file containing a time series
        # structure is provided,
        # the script will use it.
        '--time-series-file': {
            'action': 'store',
            'dest': 'time_series_file',
            'default': defaults.get('time_series_file', None),
            'help': "BigML time series JSON structure file."},

        # Setting as objectives all the numeric fields.
        '--all-numeric-objectives': {
            "action": 'store_true',
            "dest": 'all_numeric_objectives',
            "default": defaults.get('all_numeric_objectives', False),
            "help": ("Setting as objective fields all the existing"
                     "numeric fields.")},

        # Not using damping in trends
        '--no-damped-trend': {
            "action": 'store_false',
            "dest": 'damped_trend',
            "default": defaults.get('damped_trend', False),
            "help": ("Use no damping for models with additive or"
                     " multiplicative trend.")},

        # The default numeric value when missing.
        '--default-numeric-value': {
            'action': 'store',
            'dest': 'default_numeric_value',
            'default': defaults.get('default_numeric_value',
                                    None),
            'choices': [None, "mean", "median", "minimum",
                        "maximum", "zero"],
            'help': ("The default numeric value to be used when missing."
                     " Possible values are: mean, "
                     " median, minimum, maximum or zero. The default "
                     "when not used will be spline interpolation.")},

        # Type or submodel according to error
        '--error': {
            'action': 'store',
            'dest': 'error',
            'type': int_or_none,
            'default': defaults.get('error', None),
            'choices': [1, 2],
            'help': ("The error type of the submodel: 1 (additive), 2 "
                     "(multiplicative) or not set.")},

        # Field especific parameters
        '--field-parameters': {
            'action': 'store',
            'dest': 'field_parameters',
            'default': defaults.get('field_parameters', None),
            'help': ("Path to a JSON file describing the field-specific"
                     " parameters to override the top-level ones.")},

        # Number of points to forecast
        '--horizon': {
            'action': 'store',
            'dest': 'horizon',
            'type': int,
            'default': defaults.get('horizon', None),
            'help': ("The number of forecast points to compute for the "
                     "objective field.")},

        # Whether to produce a forecast
        '--forecast': {
            'action': 'store_true',
            'dest': 'forecast',
            'default': defaults.get('forecast', False),
            'help': ("Whether to produce forecasts using the time series.")},

        # objective fields
        '--objectives': {
            'action': 'store',
            'dest': 'objectives',
            'default': defaults.get('objectives', None),
            'help': ("Comma-separated list of fields to be used "
                     "as objective in the time series.")},

        # period
        '--period': {
            'action': 'store',
            'dest': 'period',
            'default': defaults.get('period', 1),
            'help': ("Seasonal period length. The default is 1 and creates"
                     " non-seasonal models")},

        # range of values to be used in the time series
        '--range': {
            'action': 'store',
            'dest': 'range',
            'type': range,
            'default': defaults.get('range', None),
            'metavar': 'min,max',
            'nargs': '?',
            'help': ("Comma-separated list of two values that define the range"
                     " of rows used in the time series.")},

        # Type or submodel according to seasonality
        '--seasonality': {
            'action': 'store',
            'dest': 'seasonality',
            'type': int,
            'default': defaults.get('seasonality', 0),
            'choices': [0, 1, 2],
            'help': ("The seasonality used in the time series: 0 (none),"
                     "1 (additive), 2 "
                     "(multiplicative).")},

        # Type or submodel according to trend
        '--trend': {
            'action': 'store',
            'dest': 'trend',
            'type': int,
            'default': defaults.get('trend', 0),
            'choices': [0, 1, 2],
            'help': ("The trend used in the time series: 0 (none),"
                     "1 (additive), 2 "
                     "(multiplicative).")},

        # Defining the time-range of the data: start
        '--time-start': {
            'action': 'store',
            'dest': 'time_start',
            'type': int_or_none,
            'default': defaults.get('time_start', None),
            'help': ("The epoch, in milliseconds, to be assigned to the"
                     " first objective value. Default is 0.")},

        # Defining the time-range of the data: end
        '--time-end': {
            'action': 'store',
            'dest': 'time_end',
            'type': int_or_none,
            'default': defaults.get('time_end', None),
            'help': ("The epoch, in milliseconds, to be assigned to the"
                     " last objective value.")},

        # Defining the time-range of the data: interval
        '--time-interval': {
            'action': 'store',
            'dest': 'time_interval',
            'type': int_or_none,
            'default': defaults.get('time_interval', None),
            'help': ("Lapse, in milliseconds, between two consecutive values"
                     " of the objective field. Default is 1.")},

        # Defining the time-range of the data: interval
        '--time-interval-unit': {
            'action': 'store',
            'dest': 'time_interval_unit',
            'choices': ["milliseconds", "millisecond", "ms", "MS", "seconds",
                        "second", "s", "S", "minutes", "minute", "m", "hours",
                        "hour", "h", "H", "days", "day", "d", "D", "weeks",
                        "week", "w", "W", "months", "month", "M", "years",
                        "year", "y", "Y"],
            'default': defaults.get('time_interval_unit', None),
            'help': ('One of the available time units: "milliseconds", '
                     '"millisecond", "ms", "MS", "seconds", "second", "s", '
                     '"S", "minutes", "minute", "m", "hours", "hour", "h", '
                     '"H", "days", "day", "d", "D", "weeks", "week", "w", "W",'
                     ' "months", "month", "M", "years", "year", "y", "Y".'
                     ' Default is milliseconds.')},

        # Does not create a time series, just a dataset.
        '--no-time-series': {
            'action': 'store_true',
            'dest': 'no_time_series',
            'default': defaults.get('no_time_series', False),
            'help': "Do not create a logistic regression."},

        # The path to a file containing time series attributes.
        '--time-series-attributes': {
            'action': 'store',
            'dest': 'time_series_attributes',
            'default': defaults.get('time_series_attributes', None),
            'help': ("Path to a JSON file describing time series"
                     " attributes.")},


        # Unsetting as objectives all the numeric fields.
        '--no-numeric-objectives': {
            "action": 'store_false',
            "dest": 'all_numeric_objectives',
            "default": defaults.get('all_numeric_objectives', False),
            "help": ("Unsetting as objective fields all the existing"
                     "numeric fields.")},

        # Using damping in trends
        '--damped-trend': {
            "action": 'store_true',
            "dest": 'damped_trend',
            "default": defaults.get('damped_trend', False),
            "help": ("Use damping for models with additive or"
                     " multiplicative trend.")},

        # Create a time series, not just a dataset.
        '--no-no-time-series': {
            'action': 'store_false',
            'dest': 'no_time_series',
            'default': defaults.get('no_time_series', False),
            'help': "Create a time series."},

        # Wheter to use intervals in forecast
        '--no-intervals': {
            'action': 'store_false',
            'dest': 'intervals',
            'default': defaults.get('intervals', True),
            'help': ("Whether to produce forecasts using the time series.")}}


    return options
