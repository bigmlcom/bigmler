.. toctree::
   :maxdepth: 2
   :hidden:


.. _bigmler-linear-regression:

Linear-regression subcommand
============================

The ``bigmler linear-regression`` subcommand generates all the
resources needed to buid
a linear regression model and use it to predict.
The linear regression model is a supervised
learning method for solving regression problems. It predicts the
objective field class as a linear function whose argument are
the rest of features. The simplest call to build a linear
regression is

.. code-block:: bash

    bigmler linear-regression --train data/grades.csv

uploads the data in the ``data/grades.csv`` file and generates
the corresponding ``source``, ``dataset`` and ``linear regression``
objects in BigML. You
can use any of the generated objects to produce new linear regressions.
For instance, you could set a subgroup of the fields of the generated dataset
to produce a different linear regression model by using

.. code-block:: bash

    bigmler linear-regression --dataset dataset/53b1f71437203f5ac30004ed \
                              --linear-fields="-Prefix"

that would exclude the field ``Prefix`` from the linear regression
model creation input fields. You can also change some parameters in the
linear regression model, like the ``bias`` (intercept term)).

.. code-block:: bash

    bigmler linear-regression --dataset dataset/53b1f71437203f5ac30004ed \
                              --no-bias

with this code, the linear regression is built without using an
independent term.

Similarly to models and datasets, the generated linear regressions
can be shared using the ``--shared`` option, e.g.

.. code-block:: bash

    bigmler linear-regression --source source/53b1f71437203f5ac30004e0 \
                              --shared

will generate a secret link for both the created dataset and linear
regressions, that can be used to share the resource selectively.

Linear regressions can produce a prediction for each new
input data set. The command

.. code-block:: bash

    bigmler linear-regression \
            --linear-regression linearregression/53b1f71435203f5ac30005c0 \
            --test data/test_grades.csv

would produce a file ``predictions.csv`` with the predictions associated
to each input. When the command is executed, the linear regression
information is downloaded
to your local computer and the linear regression predictions are
computed locally,
with no more latencies involved. Just in case you prefer to use BigML
to compute the predictions remotely, you can do so too

.. code-block:: bash

    bigmler linear-regression
            --linear-regression linearregression/53b1f71435203f5ac30005c0 \
            --test data/my_test.csv --remote

would create a remote source and dataset from the test file data,
generate a ``batch prediction`` also remotely and finally
download the result to your computer. If you prefer the result not to be
dowloaded but to be stored as a new dataset remotely, add ``--no-csv`` and
``to-dataset`` to the command line. This can be specially helpful when
dealing with a high number of scores or when adding to the final result
the original dataset fields with ``--prediction-info full``, that may result
in a large CSV to be created as output. Other output configurations can be
set by using the ``--batch-prediction-attributes`` option pointing to a JSON
file that contains the desired attributes, like:

.. code-block:: json

    {"probabilities": true,
     "all_fields": true}



Linear regression Subcommand Options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

============================================= =================================
``--linear-regression`` *LINEAR_R*            BigML linear regression Id
``--linear-regressions`` *PATH*               Path to a file containing
                                              linearregression/ids.
                                              One linear regression per line
                                              (e.g., linearregression/4f824203ce80051)
``--no-linear-regression``                    No linear regression will be
                                              generated
``--linear-fields`` *LINEAR_FIELDS*           Comma-separated list of fields
                                              that
                                              will be used in the linear
                                              regression construction
``--no-bias``                                 Avoids default behaviour. The
                                              linear regression will have
                                              no intercept term.
``--field-codings`` *FIELD_CODINGS*           Numeric encoding for categorical
                                              fields (default one-hot encoding)
``--linear-regression-attributes`` *PATH*     Path to a JSON file containing
                                              attributes (any of the updatable
                                              attributes described in the
                                              `developers section <https://bigml.com/api/linearregressions#ln_linear_regression_arguments>`_ )
                                              to
                                              be used in the linear
                                              regression creation
                                              call
``--linear-regression-file`` *PATH*           Path to a JSON file containing
                                              the linear regression info
============================================= =================================
