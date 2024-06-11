.. toctree::
   :maxdepth: 2
   :hidden:


.. _bigmler-logistic-regression:

Logistic-regression subcommand
------------------------------

The ``bigmler logistic-regression`` subcommand generates all the
resources needed to buid
a logistic regression model and use it to predict.
The logistic regression model is a supervised
learning method for solving classification problems. It predicts the
objective field class as logistic function whose argument is a linear
combination of the rest of features. The simplest call to build a logistic
regression is

.. code-block:: bash

    bigmler logistic-regression --train data/iris.csv

uploads the data in the ``data/iris.csv`` file and generates
the corresponding ``source``, ``dataset`` and ``logistic regression``
objects in BigML. You
can use any of the generated objects to produce new logistic regressions.
For instance, you could set a subgroup of the fields of the generated dataset
to produce a different logistic regression model by using

.. code-block:: bash

    bigmler logistic-regression --dataset dataset/53b1f71437203f5ac30004ed \
                    --logistic-fields="-sepal length"

that would exclude the field ``sepal length`` from the logistic regression
model creation input fields. You can also change some parameters in the
logistic regression model, like the ``bias`` (scale of the intercept term),
``c`` (the strength of the regularization map) or ``eps`` (stopping criteria
for solver).

.. code-block:: bash

    bigmler logistic-regression --dataset dataset/53b1f71437203f5ac30004ed \
                                --bias --c 5 --eps 0.5

with this code, the logistic regression is built using an independent term,
the step in the regularization is 5 and the difference between the results
from the current and last iterations is 0.5.

Similarly to the models and datasets, the generated logistic regressions
can be shared using the ``--shared`` option, e.g.

.. code-block:: bash

    bigmler logistic-regression --source source/53b1f71437203f5ac30004e0 \
                                --shared

will generate a secret link for both the created dataset and logistic
regressions, that can be used to share the resource selectively.

The logistic regression can be used to assign a prediction to each new
input data set. The command

.. code-block:: bash

    bigmler logistic-regression \
            --logistic-regression logisticregression/53b1f71435203f5ac30005c0 \
            --test data/test_iris.csv

would produce a file ``predictions.csv`` with the predictions associated
to each input. When the command is executed, the logistic regression
information is downloaded
to your local computer and the logistic regression predictions are
computed locally,
with no more latencies involved. Just in case you prefer to use BigML
to compute the predictions remotely, you can do so too

.. code-block:: bash

    bigmler logistic-regression \
            --logistic-regression logisticregression/53b1f71435203f5ac30005c0 \
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

Logistic regression Subcommand Options
--------------------------------------

============================================= =================================
``--logistic-regression`` *LOGISTIC_R*        BigML logistic regression Id
``--logistic-regressions`` *PATH*             Path to a file containing
                                              logisticregression/ids.
                                              One logistic regression per line
                                              (e.g., logisticregression/4f824203ce80051)
``--no-logistic-regression``                  No logistic regression will be
                                              generated
``--logistic-fields`` *LOGISTIC_FIELDS*       Comma-separated list of fields
                                              that
                                              will be used in the logistic
                                              regression construction
``--normalize``                               Normalize feature vectors in
                                              training and prediction inputs
``--no-missing-numerics``                     Avoids the default behaviour,
                                              which creates a new
                                              coefficient for missings in
                                              numeric fields. Missing rows are
                                              discarded.
``--no-bias``                                 Avoids default behaviour. The
                                              logistic regression will have
                                              no intercept term.
``--no-balance-fields``                       Avoids default behaviour.
                                              No automatic field balance.
``--field-codings`` *FIELD_CODINGS*           Numeric encoding for categorical
                                              fields (default one-hot encoding)
``--c`` *C*                                   Strength of the regularization
                                              step
``--eps`` *EPS*                               Stopping criteria for solver.
``--logistic-regression-attributes`` *PATH*   Path to a JSON file containing
                                              attributes (any of the updatable
                                              attributes described in the
                                              `developers section <https://bigml.com/api/logisticregressions#lr_logistic_regression_arguments>`_ )
                                              to
                                              be used in the logistic
                                              regression creation
                                              call
``--logistic-regression-file`` *PATH*         Path to a JSON file containing
                                              the logistic regression info
============================================= =================================
