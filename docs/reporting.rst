.. toctree::
   :maxdepth: 2
   :hidden:


.. _bigmler-report:

Report subcommand
=================

The results of a ``bigmler analyze --features`` or ``bigmler analyze --nodes``
command are a series of k-fold cross-validations made on the training data that
leads to the configuration value that will create the best performant model.
However, the algorithm maximizes only one evaluation metric. To see the global
picture for the rest of metrics at each validation configuration you can build
a graphical report of the results using the ``report`` subcommand. Let's say
you previously ran

.. code-block:: bash

    bigmler analyze --dataset dataset/5357eb2637203f1668000004 \
                    --nodes --output-dir best_recall

and you want to have a look at the results for each ``node_threshold``
configuration. Just say:

.. code-block:: bash

    bigmler report --from-dir best_recall --port 8080

and the command will traverse the directories in ``best_recall`` and summarize
the results found there in a metrics comparison graphic and an ROC curve if
your
model is categorical. Then a simple HTTP server will be started locally and
bound to a port of your choice, ``8080`` in the example (``8085`` will be the
default value), and a new web browser
window will be started to show the results.
You can see an `example <http://bl.ocks.org/mmerce/4b65df897bff119416e2>`_
built on the well known diabetes dataset.

The HTTP server will create an auxiliary ``bigmler/reports`` directory in the
user's home directory, where symbolic links to the reports in each output
directory will be stored and served from.


Report Specific Subcommand Options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

===================================== =========================================
``--from-dir``                        Path to a directory where BigMLer has
                                      stored
                                      its session data and created resources
                                      used in the report
``--port``                            Port number for the HTTP server used to
                                      visualize graphics in ``bigmler report``
``--no-server``                       Not starting HTTP local server to
                                      show the reports
===================================== =========================================
