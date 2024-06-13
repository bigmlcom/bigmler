.. toctree::
   :maxdepth: 2
   :hidden:

.. _bigmler-sample:

Sample subcommand
=================

You can extract samples from your datasets in BigML using the
``bigmler sample`` subcommand. When a new sample is requested, a copy
of the dataset is stored in a special format in an in-memory cache.
This sample can then be used, before its expiration time, to
extract data from the related dataset by setting some options like the
number of rows or the fields to be retrieved. You can either begin from
scratch uploading your data to BigML, creating the corresponding source and
dataset and extracting your sample from it

.. code-block:: bash

    bigmler sample --train data/iris.csv --rows 10 --row-offset 20

This command will create a source, a dataset, a sample object, whose id will
be stored in the ``samples`` file in the output directory,
and extract 10 rows of data
starting from the 21st that will be stored in the ``sample.csv`` file.

You can reuse an existing sample by using its id in the command.



.. code-block:: bash

    bigmler sample --sample sample/53b1f71437203f5ac303d5c0 \
                   --sample-header --row-order-by="-petal length" \
                   --row-fields "petal length,petal width" --mode linear

will create a new ``sample.csv`` file with a headers row where only the
``petal length`` and ``petal width`` are retrieved. The ``--mode linear``
option will cause the first available rows to be returned and the
``--row-order-by="-petal length"`` option returns these rows sorted in
descending order according to the contents of ``petal length``.

You can also add to the sample rows some statistical information by using the
``--stat-field`` or ``--stat-fields`` options. Adding them to the command
will generate a ``stat-info.json`` file where the Pearson's and Spearman's
correlations, and linear regression terms will be stored in a JSON format.

You can also apply a filter to select the sample rows by the values in
their fields using the ``--fields-filter`` option. This must be set to
a string containing the conditions that must be met using field ids
and values.



.. code-block:: bash

    bigmler sample --sample sample/53b1f71437203f5ac303d5c0 \
                   --fields-filter "000001=&!000004=Iris-setosa"

With this command, only rows where field id ``000001`` is missing and
field id ``000004`` is not ``Iris-setosa`` will be retrieved. You can check
the available operators and syntax in the
`samples' developers doc <https://bigml.com/api/samples#filtering-ro>`_ .
More available
options can be found in the `Samples subcommand Options <#samples-option>`_
section.


.._sample_options:


Samples Subcommand Options
^^^^^^^^^^^^^^^^^^^^^^^^^^

============================================= =================================
``--sample`` *SAMPLE*                         BigML sample Id
``--samples`` *PATH*                          Path to a file containing
                                              sample/ids.
                                              One sample per line
                                              (e.g., sample/4f824203ce80051)
``--no-sample``                               No sample will be generated
``--sample-fields`` *FIELD_NAMES*             Comma-separated list of fields
                                              that
                                              will be used in the sample
                                              detector construction
``--sample-attributes`` *PATH*                Path to a JSON file containing
                                              attributes (any of the updatable
                                              attributes described in the
                                              `developers section <https://bigml.com/api/samples#sp_sample_properties>`_ )
                                              to
                                              be used in the sample creation
                                              call
``--fields-filter`` *QUERY*                   Query string that will be used as
                                              filter before selecting the
                                              sample
                                              rows. The query string can be
                                              built
                                              using the field ids, their
                                              values and
                                              the usual operators. You can see
                                              some
                                              examples in the
                                              `developers section <https://bigml.com/api/samples#filtering-rows-from-a-sample>`_
``--sample-header``                           Adds a headers row to the
                                              sample.csv
                                              output
``--row-index``                               Prepends acolumn to the sample
                                              rows
                                              with the absolute row number
``--occurrence``                              Prepends a column to the sample
                                              rows
                                              with the number of occurences of
                                              each
                                              row. When used with --row-index,
                                              the occurrence column will be
                                              placed
                                              after the index column
``--precision``                               Decimal numbers precision
``--rows SIZE``                               Number of rows returned
``--row-offset`` *OFFSET*                     Skip the given number of rows
``--row-order-by`` *FIELD_NAME*               Field name whose values will be
                                              used
                                              to sort the returned rows
``--row-fields`` *FIELD_NAMES*                Comma-separated list of fields
                                              that
                                              will be returned in the sample
``--stat-fields`` *FIELD_NAME,FIELD_NAME*     Two comma-separated numeric field
                                              names
                                              that will be used to compute
                                              their
                                              Pearson's and Spearman's
                                              correlations
                                              and linear regression terms
``--stat-field`` *FIELD_NAME*                 Numeric field that will be used
                                              to compute
                                              Pearson's and Spearman's
                                              correlations
                                              and linear regression terms
                                              against
                                              the rest of numeric fields in the
                                              sample
``--unique``                                  Repeated rows are removed from
                                              the sample
============================================= =================================
