.. toctree::
   :maxdepth: 2
   :hidden:

.. _bigmler-pca:

PCA subcommand
==============

The ``bigmler pca`` subcommand generates all the
resources needed to buid
a PCA model and use it to predict.
The PCA model is an unsupervised
learning method for dimensionality reduction that tries to find new features
that can maximize the description of the data variation. The new features
are built as linear combinations of the original features in the dataset.


The simplest call to build a PCA is:

.. code-block:: bash

    bigmler pca --train data/iris.csv

uploads the data in the ``data/iris.csv`` file and generates
the corresponding ``source``, ``dataset`` and ``pca``
objects in BigML. You
can use any of the generated objects to produce new PCAs.
For instance, you could set a subgroup of the fields of the generated dataset
to produce a different PCA model by using

.. code-block:: bash

    bigmler pca --dataset dataset/53b1f71437203f5ac30004ed \
                --pca-fields="-sepal length"

that would exclude the field ``sepal length`` from the PCA
model creation input fields.


Similarly to the models and datasets, the generated PCAs
can be shared using the ``--shared`` option, e.g.

.. code-block:: bash

    bigmler pca --source source/53b1f71437203f5ac30004e0 \
                --shared


will generate a secret link for both the created dataset and PCA,
that can be used to share the resource selectively.

The PCA can be used to assign a projection (a set of new components)
to each input data set. The command

.. code-block:: bash

    bigmler pca \
            --pca pca/5331f71435203f5ac30005c0 \
            --test data/test_iris.csv \
            --output projections.csv

would produce a file ``projections.csv`` with the projections associated
to each input. It's important to remark that to build projections for
a supervised learning problem the objective field should never be part of
the PCA input fields. Including the objective in the PCA would cause leakage.
In order to remove the objective field, you can use the ``--exclude-objective``
flag. Also, the train/test split should be done before creating the PCA from
the training dataset to avoid leakage from the test set data
in the new components.

You can also change some parameters in the
PCA model, like the ``--max-components`` or ``--variance-threshold``
to select the number of components to be used in the projection.
Please check the `PCA section
of the API documentation <https://bigml.com/api/pcas>`_ for a detailed
description of the available arguments.

.. code-block:: bash

    bigmler pca --dataset dataset/53b1f71437203f5ac30004ed \
                --max-components 4 \
                --test data/test_iris.csv \
                --output projections.csv

with this code, only the first 4 components of the PCA are used to generate
projections, reducing thus the dimensionality of the dataset to 4.

When previous command is executed, the PCA
information is downloaded
to your local computer and the PCA projections are
computed locally,
with no more latencies involved. Just in case you prefer to use BigML
to compute the projections remotely, you can do so too

.. code-block:: bash

    bigmler pca
            --pca pca/53b1f71435203f5ac30005c0 \
            --test data/my_test.csv --remote

would create a remote source and dataset from the test file data,
generate a ``batch projection`` also remotely and finally
download the result to your computer. If you prefer the result not to be
dowloaded but to be stored as a new dataset remotely, add ``--no-csv`` and
``to-dataset`` to the command line. Some output format configurations can
be controlled using the ``--projection-header`` option, that causes
the headers of the fields to be placed as a first row in the projections file,
or the ``--projection-fields`` option, that can be set to ``all`` or to
a comma-separated list of fields of the original dataset that will be included
in the projections file before the projection components.
Other output configurations can be
set by using the ``--batch-projection-attributes`` option pointing to a JSON
file that contains the desired attributes, like:

.. code-block:: json

    {"output_fields": ["petal length", "sepal length"],
     "all_fields": true}


PCA Subcommand Options
^^^^^^^^^^^^^^^^^^^^^^

============================================= =================================
``--pca`` *PCA*                               BigML PCA Id
``--pcas`` *PATH*                             Path to a file containing
                                              PCA/ids.
                                              One PCA per line
                                              (e.g., pca/4f824203ce80051)
``--no-pca``                                  No PCA will be
                                              generated
``--pca-file`` *PATH*                         Path to a file containing
                                              a JSON PCA structure.
``--pca-fields`` *PCA_FIELDS*                 Comma-separated list of fields
                                              that
                                              will be used in the PCA
                                              construction
``--pca-attributes`` *PATH*                   Path to a JSON file that contains
                                              the attributes to configure
                                              the PCA
``--max-components`` *INTEGER*                Maximum number of components to
                                              be used in projections
``--variance-threshold`` *NUMBER*             Maximum variance covered with
                                              the subset of components to
                                              be used in projections
``--exclude-objective``                       When set, excludes the objective
                                              field in the dataset from
                                              the PCA input fields
``--batch-projection-attributes`` *PATH*      Path to a JSON file that contains
                                              the attributes to configure
                                              the batch projection
``--projection-header``                       When set, adds a headers row at
                                              the top of the generated
                                              projections file
``--projection-fields`` *FIELDS*              Comma-separated list of field
                                              in the test set to be added
                                              to the projections file. Use
                                              ``all`` to include all fields
``--no-no-pca``                               PCA will be generated
============================================= =================================
