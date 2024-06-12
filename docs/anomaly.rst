.. toctree::
   :maxdepth: 2
   :hidden:

.. _bigmler-anomaly:

Anomaly subcommand
------------------

The ``bigmler anomaly`` subcommand generates all the resources needed to buid
an anomaly detection model and/or predict the anomaly scores associated to your
test data. As usual, the simplest call

.. code-block:: bash

    bigmler anomaly --train data/tiny_kdd.csv

uploads the data in the ``data/tiny_kdd.csv`` file and generates
the corresponding ``source``, ``dataset`` and ``anomaly`` objects in BigML. You
can use any of the generated objects to produce new anomaly detectors.
For instance, you could set a subgroup of the fields of the generated dataset
to produce a different anomaly detector by using

.. code-block:: bash

    bigmler anomaly --dataset dataset/53b1f71437203f5ac30004ed \
                    --anomaly-fields="-urgent"

that would exclude the field ``urgent`` from the anomaly detector
creation input fields. You can also change the number of top anomalies
enclosed in the anomaly detector list and the number of trees that the anomaly
detector iforest uses. The default values are 10 top anomalies and 128 trees
per iforest:

.. code-block:: bash

    bigmler anomaly --dataset dataset/53b1f71437203f5ac30004ed \
                    --top-n 15 --forest-size 50

with this code, the anomaly detector is built using an iforest of 50 trees and
will produce a list of the 15 top anomalies.

Similarly to the models and datasets, the generated anomaly detectors
can be shared using the ``--shared`` option, e.g.

.. code-block:: bash

    bigmler anomaly --source source/53b1f71437203f5ac30004e0 \
                    --shared

will generate a secret link for both the created dataset and anomaly detector
that can be used to share the resource selectively.

The anomaly detector can be used to assign an anomaly score to each new
input data set. The anomaly score is a number between 0 (not anomalous)
and 1 (highest anomaly). The command

.. code-block:: bash

    bigmler anomaly --anomaly anomaly/53b1f71437203f5ac30005c0 \
                    --test data/test_kdd.csv

would produce a file ``anomaly_scores.csv`` with the anomaly score associated
to each input. When the command is executed, the anomaly detector
information is downloaded
to your local computer and the anomaly score predictions are computed locally,
with no more latencies involved. Just in case you prefer to use BigML
to compute the anomaly score predictions remotely, you can do so too

.. code-block:: bash

    bigmler anomaly --anomaly anomaly/53b1f71437203f5ac30005c0 \
                    --test data/my_test.csv --remote

would create a remote source and dataset from the test file data,
generate a ``batch anomaly score`` also remotely and finally
download the result to your computer. If you prefer the result not to be
dowloaded but to be stored as a new dataset remotely, add ``--no-csv`` and
``to-dataset`` to the command line. This can be specially helpful when
dealing with a high number of scores or when adding to the final result
the original dataset fields with ``--prediction-info full``, that may result
in a large CSV to be created as output.

Similarly, you can split your data in train/test datasets to build the
anomaly detector and create batch anomaly scores with the test portion of
data

.. code-block:: bash

    bigmler anomaly --train data/tiny_kdd.csv --test-split 0.2 --remote

or if you want to apply the anomaly detector on the same training data set
to create a batch anomaly score, use:

.. code-block:: bash

    bigmler anomaly --train data/tiny_kdd.csv --score --remote

To extract the top anomalies as a new dataset, or to exclude from the training
dataset the top anomalies in the anomaly detector, set the
``--anomalies-dataset`` to ``ìn`` or ``out`` respectively:

.. code-block:: bash

    bigmler anomaly --dataset dataset/53b1f71437203f5ac30004ed \
                    --anomalies-dataset out

will create a new dataset excluding the top anomalous instances according
to the anomaly detector.


Anomaly Specific Subcommand Options
-----------------------------------

============================================= =================================
``--anomaly`` *ANOMALY*                       BigML anomaly Id
``--anomalies`` *PATH*                        Path to a file containing
                                              anomaly/ids.
                                              One anomaly per line
                                              (e.g., anomaly/4f824203ce80051)
``--no-anomaly``                              No anomaly detector will be
                                              generated
``--anomaly-fields``                          Comma-separated list of fields
                                              that
                                              will be used in the anomaly
                                              detector construction
``--top-n``                                   Number of listed top anomalies
``--forest-size``                             Number of models in the anomaly
                                              detector iforest
``--anomaly-attributes`` *PATH*               Path to a JSON file containing
                                              attributes (any of the updatable
                                              attributes described in the
                                              `developers section <https://bigml.com/api/anomalies#an_anomaly_detector_properties>`_ )
                                              to
                                              be used in the anomaly creation
                                              call
``--anomaly-file`` *PATH*                     Path to a JSON file containing
                                              the anomaly info
``--anomaly-seed`` *SEED*                     Seed to generate deterministic
                                              anomalies
``--id-fields`` *SUMMARY_FIELDS*              Comma-separated list of fields to
                                              be kept for reference but not
                                              used in the anomaly detector
                                              bulding process
``--anomaly-score-attributes`` *PATH*         Path to a JSON file containing
                                              attributes (any of the updatable
                                              attributes described in the
                                              `developers section <https://bigml.com/api/anomalyscores#as_anomaly_score_properties>`_ )
                                              to be used in the
                                              anomaly
                                              score creation call
``--batch-anomaly-score-attributes`` *PATH*   Path to a JSON file containing
                                              attributes (any of the updatable
                                              attributes described in the
                                              `developers section <https://bigml.com/api/batch_anomalyscores#ba_batch_anomaly_score_properties>`_ )
                                              to
                                              be used in the batch anomaly
                                              score creation call
``--anomalies-datasets`` *[in |out]*          Separates from the training
                                              dataset the top anomalous
                                              instances enclosed in the
                                              top anomalies list and generates
                                              a new dataset including them
                                              (``in`` option) or excluding
                                              them (``out`` option).
============================================= =================================
