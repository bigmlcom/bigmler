BigMLer - A Higher-Level API to BigML's API
===========================================

BigMLer makes `BigML <https://bigml.com>`_ even easier.

BigMLer wraps `BigML's API Python bindings <http://bigml.readthedocs.org>`_  to
offer a high-level command-line script to easily create and publish datasets and models, create ensembles,
make local predictions from multiple models, and simplify many other machine
learning tasks.

BigMLer is open sourced under the `Apache License, Version
2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>`_.

Support
=======

Please report problems and bugs to our `BigML.io issue
tracker <https://github.com/bigmlcom/io/issues>`_.

Discussions about the different bindings take place in the general
`BigML mailing list <http://groups.google.com/group/bigml>`_. Or join us
in our `Campfire chatroom <https://bigmlinc.campfirenow.com/f20a0>`_.

Requirements
============

Python 2.7 is currently supported by BigMLer.

BigMLer requires `bigml 0.5.1 <https://github.com/bigmlcom/python>`_  or higher.

BigMLer Installation
====================

To install the latest stable release with
`pip <http://www.pip-installer.org/>`_::

    $ pip install bigmler

You can also install the development version of bigmler directly
from the Git repository::

    $ pip install -e git://github.com/bigmlcom/bigmler.git#egg=bigmler

BigML Authentication
====================

All the requests to BigML.io must be authenticated using your username
and `API key <https://bigml.com/account/apikey>`_ and are always
transmitted over HTTPS.

BigML module will look for your username and API key in the environment
variables ``BIGML_USERNAME`` and ``BIGML_API_KEY`` respectively. You can
add the following lines to your ``.bashrc`` or ``.bash_profile`` to set
those variables automatically when you log in::

    export BIGML_USERNAME=myusername
    export BIGML_API_KEY=ae579e7e53fb9abd646a6ff8aa99d4afe83ac291

Otherwise, you can initialize directly when running the BigMLer
script as follows::

    bigmler --train data/iris.csv --username myusername --api_key ae579e7e53fb9abd646a6ff8aa99d4afe83ac291

BigML Development Mode
======================

Also, you can instruct BigMLer to work in BigML's Sandbox
environment by using the parameter ``---dev``::

    bigmler --train data/iris.csv --dev

Using the development flag you can run tasks under 1 MB without spending any of
your BigML credits.

Using BigMLer
=============

To run BigMLer you can use the console script directly. The `--help` option will
describe all the available options::

    bigmler --help

Alternatively you can just call bigmler as follows::

    python bigmler.py --help

This will display the full list of optional arguments. You can read a brief
explanation for each option below.

Quick Start
===========

Let's see some basic usage examples. Check the `installation` and `authentication`
sections in `BigMLer on Read the Docs <http://bigmler.readthedocs.org>`_ if you are not familiar with BigML.

Basics
------

You can create a new model just with ::

    bigmler --train data/iris.csv

If you check your `dashboard at BigML <https://bigml.com/dashboard>`_, you will
see a new source, dataset, and model. Isn't it magic?

You can generate predictions for a test set using::

    bigmler --train data/iris.csv --test data/test_iris.csv

You can also specify a file name to save the newly created predictions::

    bigmler --train data/iris.csv --test data/test_iris.csv --output predictions

If you do not specify the path to an output file, BigMLer will auto-generate one for you under a
new directory named after the current date and time (e.g., `MonNov1212_174715/predictions.csv`).

A different ``objective field`` (the field that you want to predict) can be selected using::

    bigmler --train data/iris.csv --test data/test_iris.csv  --objective 'sepal length'

If you do not explicitly specify an objective field, BigML will default to the last
column in your dataset.

BigMLer will try to use the locale of the model to interpret test data. In case
it fails, it will try `en_US.UTF-8`
or 'English_United States.1252' and a warning message will be printed.
If you want to change this behaviour you can specify your preferred locale::

    bigmler --train data/iris.csv --test data/test_iris.csv --locale "English_United States.1252"

If you check your working directory you will see that BigMLer creates a file with the
model ids that have been generated (e.g., FriNov0912_223645/models).
This file is handy if then you want to use those model ids to generate local
predictions. BigMLer also creates a file with the dataset id that have been
generated (e.g., TueNov1312_003451/dataset).

Prior Versions Compatibility Issues
-----------------------------------

BigMLer will accept flags written with underscore as word separator like
``--clear_logs`` for compatibility with prior versions. Also ``--field-names``
is accepted, although the more complete ``--field-attributes`` flag is
preferred. ``--stat_pruning`` and ``--no_stat_pruning`` are discontinued
and their effects can be achived by setting the actual ``--pruning`` flag
to ``statistical`` or ``no-pruning`` values respectively.

Additional Information
----------------------

For additional information, see
the `full documentation for BigMLer on Read the Docs <http://bigmler.readthedocs.org>`_.
