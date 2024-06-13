.. toctree::
   :maxdepth: 2
   :hidden:

.. _bigmler-deepnet:

Deepnet subcommand
==================

The ``bigmler deepnet`` subcommand generates all the
resources needed to buid
a deepnet model and use it to predict.
The deepnet model is a supervised
learning method for solving both regression and classification problems. It
uses deep neural networks, a composition of layers of different functions
that when applied to the
input data generate the prediction.


The simplest call to build a deepnet is:

.. code-block:: bash

    bigmler deepnet --train data/iris.csv

uploads the data in the ``data/iris.csv`` file and generates
the corresponding ``source``, ``dataset`` and ``deepnet``
objects in BigML. You
can use any of the generated objects to produce new deepnets.
For instance, you could set a subgroup of the fields of the generated dataset
to produce a different deepnet model by using

.. code-block:: bash

    bigmler deepnet --dataset dataset/53b1f71437203f5ac30004ed \
                    --deepnet-fields="-sepal length"

that would exclude the field ``sepal length`` from the deepnet
model creation input fields. You can also change some parameters in the
deepnet model, like the ``number_of_hidden_layers``, ``max_iterations``
or ``default_numeric_value``. Please check the `Deepnets section
of the API documentation <https://bigml.com/api/deepnets>`_ for a detailed
description of the available arguments.

.. code-block:: bash

    bigmler deepnet --dataset dataset/53b1f71437203f5ac30004ed \
                    --number-of-hidden-layers 3
                    --max-iterations 10 --default-numeric-value mean

with this code, the deepnet is built using 3 hidden layers, approximations
will stop after 10 iterations and the missing numerics will be filled with
the mean of the rest of values in the field.

Similarly to the models and datasets, the generated deepnets
can be shared using the ``--shared`` option, e.g.

.. code-block:: bash

    bigmler deepnet --source source/53b1f71437203f5ac30004e0 \
                    --shared

will generate a secret link for both the created dataset and deepnet,
that can be used to share the resource selectively.

The deepnet can be used to assign a prediction to each new
input data set. The command

.. code-block:: bash

    bigmler deepnet \
            --deepnet deepnet/5331f71435203f5ac30005c0 \
            --test data/test_iris.csv

would produce a file ``predictions.csv`` with the predictions associated
to each input. When the command is executed, the deepnet
information is downloaded
to your local computer and the deepnet predictions are
computed locally,
with no more latencies involved. Just in case you prefer to use BigML
to compute the predictions remotely, you can do so too

.. code-block:: bash

    bigmler deepnet
            --deepnet deepnet/53b1f71435203f5ac30005c0 \
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


Deepnet Subcommand Options
^^^^^^^^^^^^^^^^^^^^^^^^^^

============================================= =================================
``--deepnet`` *DEEPNET*                       BigML deepnet Id
``--deepnets`` *PATH*                         Path to a file containing
                                              deepnet/ids.
                                              One deepnet per line
                                              (e.g., deepnet/4f824203ce80051)
``--no-deepnet``                              No deepnet will be
                                              generated
``--deepnet-fields`` *DEEPNET_FIELDS*         Comma-separated list of fields
                                              that
                                              will be used in the deepnet
                                              construction
``--batch-normalization``                     Specifies whether to normalize
                                              the outputs of a network before
                                              being passed to the activation
                                              function or not.
``--default-numeric-value`` *DFT*             It accepts any of the following
                                              strings to substitute
                                              missing numeric values across
                                              all the numeric fields in the
                                              dataset (options: mean, median
                                              minimum, maximum, zero).
``--dropout-rate`` *RATE*                     A number between 0 and 1
                                              specifying the rate at which to
                                              drop weights during training to
                                              control overfitting.
``--hidden-layers`` *LAYERS*                  A JSON file that contains a list
                                              of maps describing the number
                                              and type of layers in the network
                                              (other than the output layer,
                                              which is determined by the type
                                              of learning problem).
``--learn-residuals``                         Specifies whether alternate
                                              layers should learn a
                                              representation of the residuals
                                              for a given layer rather than
                                              the layer itself or not.
``--learning-rate`` *RATE*                    A number between 0 and 1
                                              specifying the learning rate.
``--max-iterations`` *ITERATIONS*             A number between 100 and 100000
                                              for the maximum number of
                                              gradient steps to take during the
                                              optimization.
``--max-training-time`` *TIME*                The maximum wall-clock training
                                              time, in seconds, for which to
                                              train the network.
``--number-of-hidden-layers`` *#LAYERS*       The number of hidden layers to
                                              use in the network. If the number
                                              is greater than the length of the
                                              list of hidden_layers, the list
                                              is cycled until the desired
                                              number is reached. If the number
                                              is smaller than the length of the
                                              list of hidden_layers, the
                                              list is shortened.
``--number-of-model-candidates`` *#CAND*      An integer specifying the number
                                              of models to try during the model
                                              search.
``--search``                                  During the deepnet creation,
                                              BigML trains and evaluates over
                                              all possible network
                                              configurations, returning the
                                              best networks found for the
                                              problem. The final deepnet
                                              returned by the search is a
                                              compromise between the top n
                                              networks found in the search.
                                              Since this option builds several
                                              networks, it may be significantly
                                              slower than the suggest_structure
                                              technique.
``--missing-numerics``                        Whether to create an additional
                                              binary predictor each numeric
                                              field which denotes a missing
                                              value. If false, these predictors
                                              are not created, and rows
                                              containing missing numeric values
                                              are dropped.
``--tree-embedding``                          Specify whether to learn a
                                              tree-based representation
                                              of the data as engineered
                                              features along with the
                                              raw features, essentially by
                                              learning trees over slices of the
                                              input space and a small amount of
                                              the training data. The theory is
                                              that these engineered features
                                              will linearize obvious non-linear
                                              dependencies before training
                                              begins, and so make learning
                                              proceed more quickly.
``--image-augmentations``                     A comma-separated list of
                                              augmentation strategies to use
                                              for image data. The available
                                              keys are: `flip_horizontal`,
                                              `flip_vertical`, `brightness`
``--include-extracted-features``              Controls the use of features
                                              extracted from images.
                                              Use `all` to include all
                                              generated features, `none`
                                              to include none, or a
                                              comma-separated list of
                                              especific field ids,
                                              corresponding to extracted fields
                                              to add to the default set.
``--no-missing-numerics``                     Avoids the default behaviour,
                                              which creates a new
                                              coefficient for missings in
                                              numeric fields. Missing rows are
                                              discarded.
``--deepnet-attributes`` *PATH*               Path to a JSON file containing
                                              attributes (any of the updatable
                                              attributes described in the
                                              `developers section <https://bigml.com/api/deepnets#dn_deepnet_properties>`_ )
                                              to
                                              be used in the deepnet creation
                                              call
``--deepnet-file`` *PATH*                     Path to a JSON file containing
                                              the deepnet regression info
============================================= =================================
