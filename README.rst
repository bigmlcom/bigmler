BigMLer - A command-line tool for BigML's API
=============================================

BigMLer makes `BigML <https://bigml.com>`_ even easier.

BigMLer wraps `BigML's API Python bindings <http://bigml.readthedocs.org>`_  to
offer a high-level command-line script to easily create and publish datasets
and models, create ensembles,
make local predictions from multiple models, and simplify many other machine
learning tasks. For additional information, see
the
`full documentation for BigMLer on Read the Docs <http://bigmler.readthedocs.org>`_.

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

BigMLer needs Python 3.8 or higher versions to work.
Compatibility with Python 2.X was discontinued in version 3.27.2.

BigMLer requires `bigml 9.7.1 <https://github.com/bigmlcom/python>`_  or
higher, that contains the bindings providing support to use the ``BigML``
platform to create, update, get and delete resources,
but also to produce local predictions using the
models created in ``BigML``. Most of them will be actionable with the basic
installation, but some additional dependencies are needed
to use local ``Topic Models`` to produce ``Topic Distributions``. These can
be installed using:

.. code-block:: bash

    pip install bigmler[topics]

The bindings also support local predictions for models generated from images.
To use these models, an additional set of libraries needs to be installed
using:

.. code-block:: bash

    pip install bigmler[images]

The external libraries used in this case exist for the majority of recent
Operating System versions. Still, some of them might need especific
compiler versions or dlls, so their installation may require an additional
setup effort.

The full set of libraries can be installed using

.. code-block:: bash

    pip install bigmler[full]


BigMLer Installation
====================

To install the latest stable release with
`pip <http://www.pip-installer.org/>`_

.. code-block:: bash

    $ pip install bigmler

You can also install the development version of bigmler directly
from the Git repository

.. code-block:: bash

    $ pip install -e git://github.com/bigmlcom/bigmler.git#egg=bigmler

For a detailed description of install instructions on Windows see the
:ref:bigmler-on-windows section.

Support for local Topic Distributions (Topic Models' predictions)
and local predictions for datasets that include Images will only be
available as extras, because the libraries used for that are not
usually available in all Operating Systems. If you need to support those,
please check the `Installation Extras <#installation-extras>`_ section.

Installation Extras
===================

Local Topic Distributions support can be installed using:

.. code-block:: bash

    pip install bigmler[topics]

Images local predictions support can be installed using:

.. code-block:: bash

    pip install bigmler[images]

The full set of features can be installed using:

.. code-block:: bash

    pip install bigmler[full]


WARNING: Mind that installing these extras can require some extra work, as
explained in the :ref:requirements section.

BigML Authentication
====================

All the requests to BigML.io must be authenticated using your username
and `API key <https://bigml.com/account/apikey>`_ and are always
transmitted over HTTPS.

BigML module will look for your username and API key in the environment
variables ``BIGML_USERNAME`` and ``BIGML_API_KEY`` respectively. You can
add the following lines to your ``.bashrc`` or ``.bash_profile`` to set
those variables automatically when you log in

.. code-block:: bash

    export BIGML_USERNAME=myusername
    export BIGML_API_KEY=ae579e7e53fb9abd646a6ff8aa99d4afe83ac291

Otherwise, you can initialize directly when running the BigMLer
script as follows

.. code-block:: bash

    bigmler --train data/iris.csv --username myusername \
            --api-key ae579e7e53fb9abd646a6ff8aa99d4afe83ac291

For a detailed description of authentication instructions on Windows see the
`BigMLer on Windows <#bigmler-on-windows>`_ section.


BigMLer on Windows
==================

To install BigMLer on Windows environments, you'll need `Python for Windows
(v.2.7.x) <http://www.python.org/download/>`_ installed.

In addition to that, you'll need the ``pip`` tool to install BigMLer. To
install pip, first you need to open your command line window (write ``cmd`` in
the input field that appears when you click on ``Start`` and hit ``enter``),
download this `python file <http://python-distribute.org/distribute_setup.py>`_
and execute it

.. code-block:: bash

    c:\Python27\python.exe distribute_setup.py

After that, you'll be able to install ``pip`` by typing the following command

.. code-block:: bash

    c:\Python27\Scripts\easy_install.exe pip

And finally, to install BigMLer, just type

.. code-block:: bash

    c:\Python27\Scripts\pip.exe install bigmler

and BigMLer should be installed in your computer. Then
issuing

.. code-block:: bash

    bigmler --version

should show BigMLer version information.

Finally, to start using BigMLer to handle your BigML resources, you need to
set your credentials in BigML for authentication. If you want them to be
permanently stored in your system, use

.. code-block:: bash

    setx BIGML_USERNAME myusername
    setx BIGML_API_KEY ae579e7e53fb9abd646a6ff8aa99d4afe83ac291


BigML Development Mode
======================

Also, you can instruct BigMLer to work in BigML's Sandbox
environment by using the parameter ``---dev``

.. code-block:: bash

    bigmler --train data/iris.csv --dev

Using the development flag you can run tasks under 1 MB without spending any of
your BigML credits.

Using BigMLer
=============

To run BigMLer you can use the console script directly. The `--help` option will
describe all the available options

.. code-block:: bash

    bigmler --help

Alternatively you can just call bigmler as follows

.. code-block:: bash

    python bigmler.py --help

This will display the full list of optional arguments. You can read a brief
explanation for each option below.

Quick Start
===========

Let's see some basic usage examples. Check the `installation` and `authentication`
sections in `BigMLer on Read the Docs <http://bigmler.readthedocs.org>`_ if
you are not familiar with BigML.

Basics
------

You can create a new model just with

.. code-block:: bash

    bigmler --train data/iris.csv

If you check your `dashboard at BigML <https://bigml.com/dashboard>`_, you will
see a new source, dataset, and model. Isn't it magic?

You can generate predictions for a test set using

.. code-block:: bash

    bigmler --train data/iris.csv --test data/test_iris.csv

You can also specify a file name to save the newly created predictions

.. code-block:: bash

    bigmler --train data/iris.csv --test data/test_iris.csv --output predictions

If you do not specify the path to an output file, BigMLer will auto-generate
one for you under a
new directory named after the current date and time
(e.g., `MonNov1212_174715/predictions.csv`).
With ``--prediction-info``
flag set to ``brief`` only the prediction result will be stored (default is
``normal`` and includes confidence information).

A different ``objective field`` (the field that you want to predict) can
be selected using

.. code-block:: bash

    bigmler --train data/iris.csv  \
            --test data/test_iris.csv \
            --objective 'sepal length'

If you do not explicitly specify an objective field, BigML will
default to the last
column in your dataset.

Also, if your test file uses a particular field separator for its data,
you can tell BigMLer using ``--test-separator``.
For example, if your test file uses the tab character as field separator the
call should be like

.. code-block:: bash

    bigmler --train data/iris.csv --test data/test_iris.tsv \
            --test-separator '\t'

If you don't provide a file name for your training source, BigMLer will try to
read it from the standard input

.. code-block:: bash

    cat data/iris.csv | bigmler --train

BigMLer will try to use the locale of the model both to create a new source
(if ``--train`` flag is used) and to interpret test data. In case
it fails, it will try ``en_US.UTF-8``
or ``English_United States.1252`` and a warning message will be printed.
If you want to change this behaviour you can specify your preferred locale

.. code-block:: bash

    bigmler --train data/iris.csv --test data/test_iris.csv \
    --locale "English_United States.1252"

If you check your working directory you will see that BigMLer creates a file
with the
model ids that have been generated (e.g., FriNov0912_223645/models).
This file is handy if then you want to use those model ids to generate local
predictions. BigMLer also creates a file with the dataset id that has been
generated (e.g., TueNov1312_003451/dataset) and another one summarizing
the steps taken in the session progress: ``bigmler_sessions``. You can also
store a copy of every created or retrieved resource in your output directory
(e.g., TueNov1312_003451/model_50c23e5e035d07305a00004f) by setting the flag
``--store``.

Prior Versions Compatibility Issues
-----------------------------------

BigMLer will accept flags written with underscore as word separator like
``--clear_logs`` for compatibility with prior versions. Also ``--field-names``
is accepted, although the more complete ``--field-attributes`` flag is
preferred. ``--stat_pruning`` and ``--no_stat_pruning`` are discontinued
and their effects can be achived by setting the actual ``--pruning`` flag
to ``statistical`` or ``no-pruning`` values respectively.

Running the Tests
-----------------

The tests will be run using `pytest <https://docs.pytest.org/en/7.2.x/>`_.
You'll need to set up your authentication
via environment variables, as explained in the authentication section.
Also some of the tests need other environment
variables like ``BIGML_ORGANIZATION`` to test calls when used by Organization
members and ``BIGML_EXTERNAL_CONN_HOST``, ``BIGML_EXTERNAL_CONN_PORT``,
``BIGML_EXTERNAL_CONN_DB``, ``BIGML_EXTERNAL_CONN_USER``,
``BIGML_EXTERNAL_CONN_PWD`` and ``BIGML_EXTERNAL_CONN_SOURCE``
in order to test external data connectors.

With that in place, you can run the test suite simply by issuing

.. code-block:: bash

    $ pytest

Additional Information
----------------------

For additional information, see
the `full documentation for BigMLer on Read the Docs <http://bigmler.readthedocs.org>`_.
