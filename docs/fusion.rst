.. toctree::
   :maxdepth: 2
   :hidden:


.. _bigmler-fusion:

Fusion subcommand
=================

The ``bigmler fusion`` subcommand generates all the
resources needed to build
a fusion model and use it to predict.
The fusion model is a supervised
learning method for solving both regression and classification problems. It's
a model composed of different supervised models, ensembles, deepnets,
logistic regressions, linear regressions or fusions. The prediction obtained
from a fusion will be an aggregation of the predictions of its component
models. The aggregation will take into account the weight associated to each
of the models in the fusion object. If no specific weight is given on creation,
each model in the fusion will be assigned the same weight.


The simplest call to build a fusion is:

.. code-block:: bash

    bigmler fusion  \
        --fusion-models deepnet/53b1f71437203f5ac30004ed,model/53b1f71437203f5ac32004e2 \
        --output-dir my_fusion

that creates the fusion object for the ``deepnet`` and ``model`` described in
``--fusiion-models``. The fusion ID is stored in a ``fusions`` file in the
directory specified in ``--output-dir``.

As explained, different weights can be applied to the predictions of each
model to generate the final prediction. To set these weights, you can use
a ``--fusion-models-file`` option to point to the JSON file describing the
models and their weights as explained in the
`API developers docs <https://bigml.com/api/fusions#fu_model_weights>`_.

.. code-block:: bash

    bigmler fusion --fusion-models-file components.json \
                    --output-dir my_fusion

An existing fusion can also be used to predict.

.. code-block:: bash

    bigmler fusion --fusion fusion/53b1f71437203f5ac30004cd \
                   --test my_test_data.csv \
                   --output my_predictions.csv

with this code, the ``my_test_data`` file contents are run through the
fusion and a new prediction is asociated to each line in the CSV file. The
results are stored in the ``my_predictions.csv`` file.
The fusion
information is downloaded
to your local computer and the fusion predictions are
computed locally,
with no more latencies involved. Just in case you prefer to use BigML
to compute the predictions remotely, you can do so too

.. code-block:: bash

    bigmler fusion --fusion fusion/53b1f71437203f5ac30004cd \
                   --test my_test_data.csv \
                   --output my_predictions.csv --remote

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


Fusion Subcommand Options
^^^^^^^^^^^^^^^^^^^^^^^^^

============================================= =================================
``--fusion`` *FUSION*                         BigML fusion Id
``--fusions`` *PATH*                          Path to a file containing
                                              fusion/ids.
                                              One fusion per line
                                              (e.g., fusion/4f824203ce80051)
``--fusion-models`` *MODELS*                  Comma-separated list of models
                                              to be aggregated in a fusion
``--fusion-models-file`` *PATH*               Path to the JSON file that
                                              contains the models to be
                                              aggregated in a fusion and its
                                              associated weights
``--no-fusion``                               No fusion will be
                                              generated
``--fusion-attributes`` *PATH*                Path to a JSON file containing
                                              attributes (any of the updatable
                                              attributes described in the
                                              `developers section <https://bigml.com/api/fusions>`_ )
                                              to
                                              be used in the fusion creation
                                              call
``--fusion-file`` *PATH*                      Path to a JSON file containing
                                              the fusion regression info
============================================= =================================
