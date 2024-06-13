.. toctree::
   :maxdepth: 2
   :hidden:


.. _bigmler-dataset:

Dataset subcommand
==================

In addition to the main BigMLer capabilities explained so far, there's a
subcommand ``bigmler dataset`` that can be used to create datasets either
from data files and sources or by transforming datasets.

.. code-block:: bash

    bigmler dataset --file iris.csv \
                    --output-dir my_directory

will create a source and a dataset by uploading the ``iris.csv`` file to
BigML.

You can also create datasets by applying many transformations to one or
several existing datasets.

To merge datasets, you can use the ``--merge`` option

.. code-block:: bash

    bigmler dataset --datasets my_datasets/dataset \
                    --merge \
                    --output-dir my_directory

The file ``my_datasets/dataset`` should contain dataset IDs, one per line.
The datasets to be merged are expected to share the same fields structure and
their rows will be just added in a single resulting dataset, whose ID will
be stored in a ``my_directory/dataset_multi`` file.

Datasets can also be juxtaposed.

.. code-block:: bash

    bigmler dataset --datasets my_datasets/dataset \
                    --juxtapose \
                    --output-dir my_directory

In this case, the generated dataset ID will be stored in the
``my_directory/dataset_gen`` file. Each row of the new dataset
will contain all the fields of the datasets found in ``my_datasets/dataset``.


If you need to join datasets, you can do so by using an SQL expression like:

.. code-block:: bash

    bigmler dataset --datasets-json "[{\"id\": \"dataset/5357eb2637203f1668000004\", \"id\": \"dataset/5357eb2637203f1668000007\"}]" \
                    --sql-query "select A.*,B.* from A join B on A.\`000000\` = \`B.000000\`" \
                    --output-dir my_directory

the ``--datasets-json`` option should contain a JSON string that describes the
datasets to be used in the SQL query. Letters from  ``A`` to ``Z`` are used
to refer to these datasets in the SQL expression. First dataset in the list is
represented by ``A``, the second by ``B``, etc.

Similarly, the SQL expression can be used to generate an aggregation.

.. code-block:: bash

    bigmler dataset --dataset dataset/5357eb2637203f1668000004 \
                    --sql-query "select A.\`species\`, avg(\`petal length\`) as apl from A group by A.\`species\`" \
                    --output-dir my_directory

or to use for pivoting

.. code-block:: bash

    bigmler dataset --dataset dataset/5357eb2637203f1668000004 \
                    --sql-query "select cat_avg(\`petal length\`, \`species\`, 'Iris-setosa') from A group by A.\`petal width\`" \
                    --output-dir my_directory

that will create the average of the ``petal length`` field value for the rows
whose ``species`` field contains the ``Iris-setosa`` category.

Dataset subcommand Options
^^^^^^^^^^^^^^^^^^^^^^^^^^

===================================== =========================================
``--file``                            Path to the data file
``--merge``                           Causes the datasets in the command to
                                      be merged
``--juxtapose``                       Causes the rows in the datasets
                                      referenced in the command to be juxtaposed
``--sql-query`` *QUERY*               SQL expression describing the transformation
``--json-query`` *PATH*               Path to a JSON file that contains the
                                      SQL query describing the transformation
``--sql-output-fields`` *PATH*        Path to a JSON file describing the fields
                                      types and properties created as output
                                      of the SQL transformation created with
                                      ``--sql-query`` or ``--json-query``
===================================== =========================================
