.. toctree::
   :maxdepth: 2
   :hidden:


.. _bigmler-cluster:

Cluster subcommand
==================

Just as the simple ``bigmler`` command can generate all the
resources leading to finding models and predictions for a supervised learning
problem, the ``bigmler cluster`` subcommand will follow the steps to generate
clusters and predict the centroids associated to your test data. To mimic what
we saw in the ``bigmler`` command section, the simplest call is

.. code-block:: bash

    bigmler cluster --train data/diabetes.csv

This command will upload the data in the ``data/diabetes.csv`` file and generate
the corresponding ``source``, ``dataset`` and ``cluster`` objects in BigML. You
can use any of the generated objects to produce new clusters. For instance, you
could set a subgroup of the fields of the generated dataset to produce a
different cluster by using

.. code-block:: bash

    bigmler cluster --dataset dataset/53b1f71437203f5ac30004ed \
                    --cluster-fields="-blood pressure"

that would exclude the field ``blood pressure`` from the cluster creation input
fields.

Similarly to the models and datasets, the generated clusters can be shared
using the ``--shared`` option, e.g.

.. code-block:: bash

    bigmler cluster --source source/53b1f71437203f5ac30004e0 \
                    --shared

will generate a secret link for both the created dataset and cluster that
can be used to share the resource selectively.

As models were used to generate predictions (class names in classification
problems and an estimated number for regressions), clusters can be used to
predict the subgroup of data that our input data is more similar to.
Each subgroup is represented by its centroid, and the centroid is labelled
by a centroid name. Thus, a cluster would classify our
test data by assigning to each input an associated centroid name. The command

.. code-block:: bash

    bigmler cluster --cluster cluster/53b1f71437203f5ac30004f0 \
                    --test data/my_test.csv

would produce a file ``centroids.csv`` with the centroid name associated to
each input. When the command is executed, the cluster information is downloaded
to your local computer and the centroid predictions are computed locally, with
no more latencies involved. Just in case you prefer to use BigML to compute
the centroid predictions remotely, you can do so too

.. code-block:: bash

    bigmler cluster --cluster cluster/53b1f71437203f5ac30004f0 \
                    --test data/my_test.csv --remote

would create a remote source and dataset from the test file data,
generate a ``batch centroid`` also remotely and finally download the result
to your computer. If you prefer the result not to be
dowloaded but to be stored as a new dataset remotely, add ``--no-csv`` and
``to-dataset`` to the command line. This can be specially helpful when
dealing with a high number of scores or when adding to the final result
the original dataset fields with ``--prediction-info full``, that may result
in a large CSV to be created as output.

The k-means algorithm used in clustering can only use training data that has
no missing values in their numeric fields. Any data that does not comply with
that is discarded in cluster construction, so you should ensure that enough
number of rows in your training data file has non-missing values in their
numeric fields for the cluster to be built and relevant. Similarly, the cluster
cannot issue a centroid prediction for input data that has missing values in
its numeric fields, so centroid predictions will give a "-" string as output
in this case.

You can change the number of centroids used to group the data in the
clustering procedure

.. code-block:: bash

    bigmler cluster --dataset dataset/53b1f71437203f5ac30004ed \
                    --k 3

And also generate the datasets associated to each centroid of a cluster.
Using the ``--cluster-datasets`` option

    bigmler cluster --cluster cluster/53b1f71437203f5ac30004f0 \
                    --cluster-datasets "Cluster 1,Cluster 2"

you can generate the datasets associated to a comma-separated list of
centroid names. If no centroid name is provided, all datasets are generated.


Similarly, you can generate the models to predict if one instance is associated
to each centroid of a cluster.
Using the ``--cluster-models`` option

    bigmler cluster --cluster cluster/53b1f71437203f5ac30004f0 \
                    --cluster-models "Cluster 1,Cluster 2"

you can generate the models associated to a comma-separated list of
centroid names. If no centroid name is provided, all models are generated.
Models can be useful to see which features are important to determine whether
a certain instance belongs to a concrete cluster.

Cluster Specific Subcommand Options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========================================= =====================================
``--cluster`` *CLUSTER*                   BigML cluster Id
``--clusters`` *PATH*                     Path to a file containing
                                          cluster/ids. One
                                          cluster
                                          per line (e.g.,
                                          cluster/4f824203ce80051)
``--k`` *NUMBER_OF_CENTROIDS*             Number of final centroids in the
                                          clustering
``--no-cluster``                          No cluster will be generated
``--cluster-fields``                      Comma-separated list of fields that
                                          will be
                                          used in the cluster construction
``--cluster-attributes`` *PATH*           Path to a JSON file containing
                                          attributes (any of the updatable
                                          attributes described in the
                                          `developers section <https://bigml.com/api/clusters#cl_cluster_properties>`_ )
                                          to
                                          be used in the cluster creation call
``--cluster-datasets`` *CENTROID_NAMES*   Comma-separated list of centroid
                                          names to
                                          generate the related datasets from a
                                          cluster.
                                          If no CENTROID_NAMES argument is
                                          provided
                                          all datasets are generated
``--cluster-file`` *PATH*                 Path to a JSON file containing the
                                          cluster
                                          info
``--cluster-seed`` *SEED*                 Seed to generate deterministic
                                          clusters
``--centroid-attributes`` *PATH*          Path to a JSON file containing
                                          attributes (any of the updatable
                                          attributes described in the
                                          `developers section <https://bigml.com/api/centroids#ct_centroid_properties>`_ )
                                          to be used in the centroid creation
                                          call
``--batch-centroid-attributes`` *PATH*    Path to a JSON file containing
                                          attributes (any of the updatable
                                          attributes described in the
                                          `developers section <https://bigml.com/api/batch_centroids#bc_batch_centroid_properties>`_ )
                                          to be used in the batch centroid
                                          creation call
``--cluster-models`` *CENTROID_NAMES*     Comma-separated list of centroid
                                          names to
                                          generate the related models from a
                                          cluster.
                                          If no CENTROID_NAMES argument is
                                          provided
                                          all models are generated
``--summary-fields`` *SUMMARY_FIELDS*     Comma-separated list of fields to
                                          be kept for reference but not used
                                          in the cluster bulding process
``--default-numeric-value`` *DEFAULT*     The value used by default if
                                          a numeric field is missing.
                                          Spline interpolation is used by
                                          default and other options are
                                          "mean", "median", "minimum",
                                          "maximum" and "zero"
========================================= =====================================
