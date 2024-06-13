.. toctree::
   :maxdepth: 2
   :hidden:


.. _bigmler-analyze:

Analyze subcommand
==================

In addition to the main BigMLer capabilities explained so far, there's a
subcommand ``bigmler analyze`` with more options to evaluate the performance
of your models. For instance

.. code-block:: bash

    bigmler analyze --dataset dataset/5357eb2637203f1668000004 \
                    --cross-validation --k-folds 5

will create a k-fold cross-validation by dividing the data in your dataset in
the number of parts given in ``--k-folds``. Then evaluations are created by
selecting one of the parts to be the test set and using the rest of data
to build the model for testing. The generated
evaluations are placed in your output directory and its average is stored in
``evaluation.txt`` and ``evaluation.json``.

Similarly, you'll be able to create an evaluation for ensembles. Using the
same command above and adding the options to define the ensembles' properties,
such as ``--number-of-models``, ``--sample-rate``, ``--randomize`` or
``--replacement``

.. code-block:: bash

    bigmler analyze --dataset dataset/5357eb2637203f1668000004 \
                    --cross-validation --k-folds 5 --number-of-models 20
                    --sample-rate 0.8 --replacement

More insights can be drawn from the ``bigmler analyze --features`` command. In
this case, the aim of the command is to analyze the complete set of features
in your dataset to single out the ones that produce models with better
evaluation scores. In this case, we focus on ``accuracy`` for categorical
objective fields and ``r-squared`` for regressions.



.. code-block:: bash

    bigmler analyze --dataset dataset/5357eb2637203f1668000004 \
                    --features

This command uses an algorithm for smart feature selection as described in this
`blog post <http://blog.bigml.com/2014/02/26/smart-feature-selection-with-scikit-learn-and-bigmls-api/>`_
that evaluates models built by using subsets of features. It starts by
building one model per feature, chooses the subset of features used in the
model that scores best and, from there on, repeats the procedure
by adding another of the available features in the dataset to the chosen
subset. The iteration stops when no improvement in score is found for a number
of repetitions that can be controlled using the ``--staleness`` option
(default is ``5``). There's
also a ``--penalty`` option (default is ``0.1%``) that sets the amount that
is substracted from the score per feature added to the
subset. This penalty is intended
to mitigate overfitting, but it also favors models which are quicker to build
and evaluate. The evaluations for the scores are k-fold cross-validations.
The ``--k-folds`` value is set to ``5`` by default, but you can change it
to whatever suits your needs using the ``--k-folds`` option.


.. code-block:: bash

    bigmler analyze --dataset dataset/5357eb2637203f1668000004 \
                    --features --k-folds 10 --staleness 3 --penalty 0.002

Would select the best subset of features using 10-fold cross-validation
and a ``0.2%`` penalty per feature, stopping after 3 non-improving iterations.

Depending on the machine learning problem you intend to tackle, you might
want to optimize other evaluation metric, such as ``precision`` or
``recall``. The ``--optimize`` option will allow you to set the evaluation
metric you'd like to optimize.



.. code-block:: bash

    bigmler analyze --dataset dataset/5357eb2637203f1668000004 \
                    --features --optimize recall

For categorical models, the evaluation values are obtained by counting
the positive and negative matches for all the instances in
the test set, but sometimes it can be more useful to optimize the
performance of the model for a single category. This can be specially
important in highly non-balanced datasets or when the cost function is
mainly associated to one of the existing classes in the objective field.
Using ``--optimize-category`` you can set the category whose evaluation
metrics you'd like to optimize

.. code-block:: bash

    bigmler analyze --dataset dataset/5357eb2637203f1668000004 \
                    --features --optimize recall \
                    --optimize-category Iris-setosa

You should be aware that the smart feature selection command still generates
a high number of BigML resources. Using ``k`` as the ``k-folds`` number and
``n`` as the number of explored feature sets, it will be generating ``k``
datasets (``1/k``th of the instances each), and ``k * n`` models and
evaluations. Setting the ``--max-parallel-models`` and
``--max-parallel-evaluations`` to higher values (up to ``k``) can help you
speed up partially the creation process because resources will be created
in parallel. You must keep in mind, though, that this parallelization is
limited by the task limit associated to your subscription or account type.

As another optimization method, the ``bigmler analyze --nodes`` subcommand
will find for you the best performing model by changing the number of nodes
in its tree. You provide the ``--min-nodes`` and ``--max-nodes`` that define
the range and ``--nodes-step`` controls the increment in each step. The command
runs a k-fold evaluation (see ``--k-folds`` option) on a model built with each
node threshold in you range and tries to optimize the evaluation metric you
chose (again, default is ``accuracy``). If improvement stops (see
the --staleness option) or the node threshold reaches the ``--max-nodes``
limit, the process ends and shows the node threshold that
lead to the best score.

.. code-block:: bash

    bigmler analyze --dataset dataset/5357eb2637203f1668000004 \
                    --nodes --min-nodes 10 \
                    --max-nodes 200 --nodes-step 50


When working with random forest, you can also change the number of
``random_candidates`` or number of fields chosen at random when the models
in the forest are built. Using ``bigmler analyze --random-fields`` the number
of ``random_candidates`` will range from 1 to the number of fields in the
origin dataset, and BigMLer will cross-validate the random forests to determine
which ``random_candidates`` number gives the best performance.

.. code-block:: bash

    bigmler analyze --dataset dataset/5357eb2637203f1668000004 \
                    --random-fields

Please note that, in general, the exact choice of fields selected as random
candidates might be more
important than their actual number. However, in some marginal cases (e.g.
datasets with a high number noise features) the number of random candidates
can impact tree performance significantly.

For any of these options (``--features``, ``--nodes`` and ``--random-fields``)
you can add the ``--predictions-csv`` flag to the ``bigmler analyze``
command. The results will then include a CSV file that stores the predictions
obtained in the evaluations that gave the best score. The file content includes
the data in your original dataset tagged by k-fold and the prediction and
confidence obtained. This file will be placed in an internal folder of your
chosen output directory.

.. code-block:: bash


    bigmler analyze --dataset dataset/5357eb2637203f1668000004 \
                    --features --output-dir my_features --predictions-csv

The output directory for this command is ``my_features`` and it will
contain all the information about the resources generated when testing
the different feature combinations
organized in subfolders. The k-fold datasets'
IDs will be stored in an inner ``test`` directory. The IDs of the resources
created when testing each combination of features will be stored in
``kfold1``, ``kfold2``, etc. folders inside the ``test`` directory.
If the best-scoring prediction
models are the ones in the ``kfold4`` folder, then the predictions CSV file
will be stored in a new folder named ``kfold4_pred``.


Analyze subcommand Options
^^^^^^^^^^^^^^^^^^^^^^^^^^

===================================== =========================================
``--cross-validation``                Sets the k-fold cross-validation mode
``--k-folds``                         Number of folds used in k-fold
                                      cross-validation
                                      (default is 5)
``--features``                        Sets the smart selection features mode
``--staleness`` *INTEGER*             Number of iterations with no improvement
                                      that
                                      is considered the limit for the analysis
                                      to stop
                                      (default is 5)
``--penalty`` *FLOAT*                 Coefficient used to penalyze models with
                                      many
                                      features in the smart selection features
                                      mode
                                      (default is 0.001). Also used in node
                                      threshold
                                      selection (default is 0)
``--optimize`` *METRIC*               Metric that is being optimized in the
                                      smart
                                      selection features mode or the node
                                      threshold
                                      search mode (default is accuracy)
``--optimize-category`` *CATEGORY*    Category whoese metric is being optimized
                                      in
                                      the smart selection features mode or
                                      the node threshold search mode (only for
                                      categorical models)
``--nodes``                           Sets the node threshold search mode
``--min-nodes`` *INTEGER*             Minimum number of nodes to start the node
                                      threshold search mode (default 3)
``--max-nodes`` *INTEGER*             Maximum number of nodes to end the node
                                      threshold
                                      search mode (default 2000)
``--nodes-step`` *INTEGER*            Step in the node threshold search
                                      iteration
                                      (default 50)
``--exclude-features`` *FEATURES*     Comma-separated list of features in the
                                      dataset
                                      to be excluded from the features analysis
``--score``                           Causes the training set to be run
                                      through the anomaly detector generating
                                      a batch anomaly score. Only used with
                                      the ``--remote`` flag.
===================================== =========================================
