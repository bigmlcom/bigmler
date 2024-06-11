.. toctree::
   :maxdepth: 2
   :hidden:


.. _bigmler-time-series:

Time Series subcommand
----------------------

Using this subcommand you can generate all the
resources leading to a ``time series`` and its ``forecasts``.
The ``time series`` is a supervised learning model that works on
an ordered sequence of data to extract the patterns needed to make
``forecasts``. The ``bigmler time-series`` subcommand
will follow the steps to generate
``time series`` and predict the ``forecasts`` for every numeric field in
the original dataset that has been set as objective field. As
shown in the ``bigmler`` command section, the simplest call is

.. code-block:: bash

    bigmler time-series --train data/grades.csv

This command will upload the data in the ``data/grades.csv`` file and
generate
the corresponding ``source``, ``dataset`` and ``time series`` objects in BigML.
You
can use any of the intermediate generated objects to produce new
time series. For instance, you
could set a subgroup of the numeric fields in the dataset to be used
as objective fields using the ``--objectives`` option.

.. code-block:: bash

    bigmler time-series --dataset dataset/53b1f71437203f5ac30004ed \
                        --objectives "Assignment,Final"

its value is expected to be a comma-separated list of fields.

Similarly to the models and datasets, the generated clusters can be shared
using the ``--shared`` option, e.g.

.. code-block:: bash

    bigmler time-series --source source/53b1f71437203f5ac30004e0 \
                        --shared

will generate a secret link for both the created dataset and time series that
can be used to share the resource selectively.

As models were used to generate predictions (class names in classification
problems and an estimated number for regressions), time series can be used
to generate forecasts, that is, to predict the value of each objective
field up till the user-given horizon. The command

.. code-block:: bash

    bigmler time-series --time-series timeseries/58437a277e0a8d38ec028a5f \
                        --horizon 10

would produce a file ``forecast_000001.csv`` with ten rows, one per point, and
as many columns as ETS models the time series contains.

When the command is executed, the time series information is downloaded
to your local computer and the forecasts are computed locally, with
no more latencies involved. Just in case you prefer to use BigML to compute
the forecasts remotely, you can do so too

.. code-block:: bash

    bigmler time-series --time-series timeseries/58437a277e0a8d38ec028a5f \
                        --horizon 10 --remote

would create a remote forecast with the specified horizon. You can also
specify more complex inputs for the forecast. For instance, you can set a
different horizon to each objective field and you can give some criteria
to select the models used in the forecast. All of this can be done using
the ``--test`` option pointing to a JSON file that should contain the
input to be used in the forecast as described in the
`API documentation <https://bigml.com/api/forecasts>`_. As an example,
let's set a horizon of 5 points for the ``Final`` field and select the
first model in the time series array of ETS models, and also forecast 7
points for the ``Assignment`` field using the model with less ``aic`` (the one
used by default). The command call should then be:


.. code-block:: bash

    bigmler time-series --time-series timeseries/58437a277e0a8d38ec028a5f \
                        --test test.json

and the ``test.json`` file should contain the following JSON:

.. code-block:: json

    {"Final": {"horizon": 5, "ets_models": {"indices": [0]}},
     "Assignment": {"horizon": 7}}


Time Series Subcommand Options
------------------------------

============================================= =================================
``--time-seriers`` *TIME_SERIES*              BigML time series Id
``--time-series-set`` *PATH*                  Path to a file containing
                                              timeseries/ids
                                              One time series per line
                                              (e.g., timeseries/4f824203ce80051)
``--no-time-series``                          No time series will be
                                              generated.
``--objectives`` *OBJECTIVES*                 Comma-separated list of fields
                                              that
                                              will be used in the time series
                                              as objective fields
``--time-series-attributes`` *PATH*           Path to a JSON file containing
                                              attributes (any of the updatable
                                              attributes described in the
                                              `developers section <https://bigml.com/api/timeseries#ts_time_series_arguments>`_ )
                                              to
                                              be used in the time series
                                              creation call
``--time-series-file`` *PATH*                 Path to a JSON file containing
                                              the time series info
``--all-numeric-objectives``                  When used, all the numeric fields
                                              in the dataset are considered
                                              objective fields
``--default-numeric-value`` *DEFAULT*         The value used by default if
                                              a numeric field is missing.
                                              Spline interpolation is used by
                                              default and other options are
                                              "mean", "median", "minimum",
                                              "maximum" and "zero"
``--error`` *TYPE*                            Type of error considered:
                                              1 - Additive, 2 - Multiplicative
``--period`` *PERIOD*                         Expected period
``--seasonality`` *SEASONALITY*               Type of seasonality: 0 - None,
                                              1 - Additive, 2 - Multiplicative
``--trend`` *TREND*                           Type of trend: 0 - None,
                                              1 - Additive, 2 - Multiplicative
``--range`` *RANGE*                           Comma-separated pair of values
                                              that set the range limits
``--damped-trend``                            When set damping is used in trend
``--forecast``                                When set, the time series default
                                              forecast is produced
``--horizon`` *HORIZON*                       Set to an integer, is the number
                                              of points in the forecast
``--time-start`` *START*                      Time starting point coordinate
``--time-end`` *END*                          Time ending point coordinate
``--time-unit`` *UNIT*                        Unit for the time interval. The
                                              options are described in the
                                              `API documentation <https://bigml.com/api/timeseries#ts_time_series_arguments>`_
``--time-interval`` *INTERVAL*                Time interval between two rows
============================================= =================================
