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
"""Time-series forecast auxiliary functions

"""



import sys

import bigml.api

from bigml.timeseries import TimeSeries
from bigml.io import UnicodeWriter

import bigmler.utils as u
import bigmler.checkpoint as c

from bigmler.resourcesapi.forecasts import create_forecast


def write_forecasts(forecast, output):
    """Writes the final forecast to the required output

    The function creates a new file per field used in the forecast input data.
    The id of the field will be appended to the name provided in the `output`
    parameter.
    """

    for objective_id, forecast_value in list(forecast.items()):
        headers = [f["model"] for f in forecast_value]
        points = []
        if not forecast_value:
            sys.exit("No forecasts available")
        for index in range(len(forecast_value[0]["point_forecast"])):
            points.append([f["point_forecast"][index] for f in forecast_value])
        output_file = "%s_%s.csv" % (output, objective_id)
        with UnicodeWriter(output_file, lineterminator="\n") as out_handler:
            out_handler.writerow(headers)
            for row in points:
                out_handler.writerow(row)


def forecast(time_series, args, session_file=None):
    """Computes a time-series forecast

    """

    local_time_series = TimeSeries(time_series,
                                   api=args.retrieve_api_)

    output = args.predictions
    # Local forecasts: Forecasts are computed locally
    message = u.dated("Creating local forecasts.\n")
    u.log_message(message, log_file=session_file, console=args.verbosity)
    input_data = []
    if args.test_set is not None:
        input_data = [u.read_json(args.test_set)]
    elif args.horizon is not None:
        input_data = [{local_time_series.objective_id: { \
            "horizon": args.horizon}}]
    write_forecasts(local_time_series.forecast(*input_data),
                    output)


def remote_forecast(time_series,
                    forecast_args, args,
                    api, resume, session_file=None,
                    path=None, log=None):
    """Computes a remote forecast.

    """

    time_series_id = bigml.api.get_time_series_id( \
        time_series)
    # if resuming, try to extract dataset form log files
    if resume:
        message = u.dated("Forecast not found. Resuming.\n")
        resume, forecast = c.checkpoint(
            c.is_forecast_created, path, debug=args.debug,
            message=message, log_file=session_file, console=args.verbosity)
    if not resume:
        local_time_series = TimeSeries(time_series,
                                       api=args.retrieve_api_)
        output = args.predictions
        if args.test_set is not None:
            input_data = u.read_json(args.test_set)
        elif args.horizon is not None:
            input_data = {local_time_series.objective_id: { \
                "horizon": args.horizon}}

        forecast = create_forecast(
            time_series_id, input_data, forecast_args,
            args, api, session_file=session_file, path=path, log=log)

        write_forecasts(forecast["object"]["forecast"]["result"], output)
