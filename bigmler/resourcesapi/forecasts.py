# -*- coding: utf-8 -*-
#
# Copyright 2020 BigML
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
"""Resources management functions

"""


import sys

import bigml.api

from bigmler.utils import (dated, get_url, log_message, check_resource,
                           check_resource_error, log_created_resources)
from bigmler.reports import report

from bigmler.resourcesapi.common import set_basic_args, update_json_args


def set_forecast_args(args, fields=None):
    """Return forecast dict

    """
    forecast_args = set_basic_args(args, args.name)
    forecast_args.update({
        "intervals": args.intervals,
    })

    if 'forecast' in args.json_args:
        update_json_args(
            forecast_args,
            args.json_args.get('forecast'),
            fields)

    return forecast_args


def create_forecast(time_series, input_data, forecast_args, args,
                    api=None, session_file=None,
                    path=None, log=None):
    """Creates remote forecast

    """
    if api is None:
        api = bigml.api.BigML()

    message = dated("Creating remote forecast.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    forecast = api.create_forecast(time_series, input_data,
                                   forecast_args,
                                   retries=None)
    log_created_resources("forecast", path,
                          bigml.api.get_forecast_id(forecast),
                          mode='a')
    forecast_id = check_resource_error(
        forecast, "Failed to create forecast: ")
    try:
        forecast = check_resource(forecast, api.get_forecast,
                                  raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished forecast: %s"
                 % str(exception))
    message = dated("Forecast created: %s\n"
                    % get_url(forecast))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % forecast_id, log_file=log)
    if args.reports:
        report(args.reports, path, forecast)
    return forecast
