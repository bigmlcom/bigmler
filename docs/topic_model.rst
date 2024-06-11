.. toctree::
   :maxdepth: 2
   :hidden:


.. _bigmler-topic-model:

Topic Model subcommand
----------------------

Using this subcommand you can generate all the
resources leading to finding a ``topic model`` and its ``topic distributions``.
These are unsupervised learning models which find out the topics in a
collection of documents and will then be useful to classify new documents
according to the topics. The ``bigmler topic-model`` subcommand
will follow the steps to generate
``topic models`` and predict the ``topic distribution``, or distribution of
probabilities for the new document to be associated to a certain topic. As
shown in the ``bigmler`` command section, the simplest call is

.. code-block:: bash

    bigmler topic-model --train data/spam.csv

This command will upload the data in the ``data/spam.csv`` file and
generate
the corresponding ``source``, ``dataset`` and ``topic model`` objects in BigML.
You
can use any of the intermediate generated objects to produce new
topic models. For instance, you
could set a subgroup of the fields of the generated dataset to produce a
different topic model by using

.. code-block:: bash

    bigmler topic-model --dataset dataset/53b1f71437203f5ac30004ed \
                        --topic-fields="-Message"

that would exclude the field ``Message`` from the topic model creation input
fields.

Similarly to the models and datasets, the generated topic models can be shared
using the ``--shared`` option, e.g.

.. code-block:: bash

    bigmler topic-model --source source/53b1f71437203f5ac30004e0 \
                        --shared

will generate a secret link for both the created dataset and topic model that
can be used to share the resource selectively.

As models were used to generate predictions (class names in classification
problems and an estimated number for regressions), topic models can be used
to classify a new document in the discovered list of topics. The classification
is run by computing the probability for the document to belonging to the topic
group. The command

.. code-block:: bash

    bigmler topic-model --topic-model topicmodel/58437a277e0a8d38ec028a5f \
                        --test data/my_test.csv

would produce a file ``topic_distributions.csv`` where each row will contain
the probabilities
associated to each topic for the corresponding test input.
When the command is executed, the topic model information is downloaded
to your local computer and the distributions are computed locally, with
no more latencies involved. Just in case you prefer to use BigML to compute
the topic distributions remotely, you can do so too

.. code-block:: bash

    bigmler topic-model --topic-model topicmodel/58437a277e0a8d38ec028a5f \
                        --test data/my_test.csv --remote

would create a remote source and dataset from the test file data,
generate a ``batch topic distribution`` also remotely and finally
download the result
to your computer. If you prefer the result not to be
dowloaded but to be stored as a new dataset remotely, add ``--no-csv`` and
``to-dataset`` to the command line. This can be specially helpful when
dealing with a high number of scores or when adding to the final result
the original dataset fields with ``--prediction-info full``, that may result
in a large CSV to be created as output.

Note that the the topics created in the Topic Model resource are now named
after the more frequent terms that they contain. To return to the previous
``Topic 0`` style naming you can use the ``--minimum-name-terms`` option and
set it to ``0``.



Topic Model Subcommand Options
------------------------------

============================================= =================================
``--topic-model`` *TOPIC_MODEL*               BigML topic model Id
``--topic-models`` *PATH*                     Path to a file containing
                                              topicmodel/ids.
                                              One topic model per line
                                              (e.g., topicmodel/4f824203ce80051)
``--no-topic-model``                          No topic model will be
                                              generated
``--topic-fields`` *TOPIC_FIELDS*             Comma-separated list of fields
                                              that
                                              will be used in the topic
                                              model construction
``--bigrams``                                 Use bigrams in topic search
``--case-sensitive``                          Use case sensitive tokenization
``--excluded-terms`` *EXCLUDED_TERMS*         Comma-separated list of terms
                                              to be excluded from the analysis
``--use-stopwords``                           Use stopwords in the analysis.
``--minimum-name-terms`` *NUMBER_OF_TERMS*    Number of the most frequent terms
                                              in the topic used to name it
``--topic-model-attributes`` *PATH*           Path to a JSON file containing
                                              attributes (any of the updatable
                                              attributes described in the
                                              `developers section <https://bigml.com/api/topicmodels#tm_topic_model_arguments>`_ )
                                              to
                                              be used in the topic model
                                              creation call
``--topic-model-file`` *PATH*                 Path to a JSON file containing
                                              the topic model info
============================================= =================================
