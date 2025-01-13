BigMLer - A command-line tool for BigML's API
=============================================

BigMLer makes `BigML <https://bigml.com>`_ even easier.

BigMLer wraps `BigML's API Python bindings <http://bigml.readthedocs.org>`_  to
offer a high-level command-line script to easily create and publish datasets
and models, create ensembles,
make local predictions from multiple models, clusters and simplify many other
machine learning tasks.

BigMLer is open sourced under the `Apache License, Version
2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>`_.

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Basic BigMLer Workflows

   quick_start

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: BigMLer Subcommands

   connector
   project
   source
   dataset
   sample
   linear_reg
   logistic_reg
   deepnet
   time_series
   fusion
   pca
   cluster
   anomaly
   topic_model
   association

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Automating and Retraining

   tuning
   scripting

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Managing and Scripting

   managing
   reporting

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Multilabel Models

   multilabels


Requirements
============

BigMLer needs Python 3.8 or higher versions to work.
Compatibility with Python 2.X was discontinued in version 3.27.2.

BigMLer requires `bigml 9.8.1 <https://github.com/bigmlcom/python>`_  or
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
:ref:bigmler-windows section.

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
explained in the `Requirements <#requirements>`_ section.

BigML Authentication on Unix or Mac OS
======================================

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
:ref:bigmler-windows section.


.. _bigmler-windows:


BigMLer Install and Authentication on Windows
=============================================

To install BigMLer on Windows environments, you'll need Python installed.
The code has been tested with Python 3.10 and you can create a *conda*
environment with that Python version or download it from `Python for Windows
<http://www.python.org/download/>`_ and install it. In the latter case, you'll
also need too install the ``pip`` tool to install BigMLer.

To install ``pip``, first you need to open your command terminal window
(write ``cmd`` in
the input field that appears when you click on ``Start`` and hit ``enter``).
Then you can follow the steps described, for example, in this `guide
<https://monovm.com/blog/how-to-install-pip-on-windows-linux/#How-to-install-PIP-on-Windows?-[A-Step-by-Step-Guide]>`_
to install its latest version.

And finally, to install BigMLer in its basic capacities, just type

.. code-block:: bash

    python -m pip install bigmler

and BigMLer should be installed in your computer or conda environment. Then
issuing

.. code-block:: bash

    bigmler --version

should show BigMLer version information.

Extensions of BigMLer to use images are usually not available in Windows.
The libraries needed for those models are not available usually for that
operating system. If your Machine Learning project involves images, we
recommend that you choose a Linux based operating system.

Finally, to start using BigMLer to handle your BigML resources, you need to
set your credentials in BigML for authentication. If you want them to be
permanently stored in your system, use

.. code-block:: bash

    setx BIGML_USERNAME myusername
    setx BIGML_API_KEY ae579e7e53fb9abd646a6ff8aa99d4afe83ac291

Note that ``setx`` will not change the environment variables of your actual
console, so you will need to open a new one to start using them.


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


BigMLer subcommands
===================

In addition to the ``BigMLer`` simple command, that covers the main
functionality, there are some additional subcommands:

Usual workflows' subcommands
----------------------------

``bigmler connector``:


Used to generate external connectors to databases. See
:ref:`bigmler-connector`.


``bigmler source``:


Used to generate sources from data files.
See :ref:`bigmler-source`.

``bigmler dataset``:

Used to generate datasets from data files, sources and transformations
on other datasets
See :ref:`bigmler-dataset`.

``bigmler cluster``:


Used to generate clusters and centroids' predictions
See :ref:`bigmler-cluster`.

``bigmler anomaly``:


Used to generate anomaly detectors and anomaly scores.
See :ref:`bigmler-anomaly`.

``bigmler sample``:

Used to generate samples of data from your existing datasets.
See :ref:`bigmler-sample`.

``bigmler association``:


Used to generate association rules from your datasets. See
:ref:`bigmler-association`.

``bigmler logistic-regression``:


Used to generate logistic regression models and predictions. See
:ref:`bigmler-logistic-regression`.

``bigmler linear-regression``:


Used to generate linear regression models and predictions. See
:ref:`bigmler-linear-regression`.

``bigmler topic-model``:


Used to generate topic models and topic distributions. See
:ref:`bigmler-topic-model`.

``bigmler time-series``:


Used to generate time series and forecasts. See
:ref:`bigmler-time-series`.

``bigmler deepnet``:


Used to generate deepnets and their predictions. See
:ref:`bigmler-deepnet`.


``bigmler fusion``:


Used to generate fusions and their predictions. See
:ref:`bigmler-fusion`.


``bigmler pca``:


Used to generate PCAs and their projections. See
:ref:`bigmler-pca`.


``bigmler project``:


Used to generate and manage projects for organization purposes. See
:ref:`bigmler-project`.


Management subcommands
----------------------

``bigmler delete``:


Used to delete the remotely created resources. See
:ref:`bigmler-delete`.

``bigmler.export``:

Used to generate the code you need to predict locally with no connection
to BigML. See
:ref:`bigmler-export`.

Reporting subcommands
---------------------

``bigmler report``:


Used to generate reports for the analyze subcommand showing the ROC curve and
evaluation metrics of cross-validations. See
:ref:`bigmler-report`.

Model tuning subcommands
------------------------

``bigmler analyze``:


Used for feature analysis, node threshold analysis and
k-fold cross-validation. See :ref:`bigmler-analyze`.


Scripting subcommands
---------------------


``bigmler reify``:


Used to generate scripts to reproduce the existing resources in BigML. See
:ref:`bigmler-reify`.


``bigmler execute``:


Used to create WhizzML libraries or scripts and execute them. See
:ref:`bigmler-execute`.


``bigmler whizzml``:


Used to create WhizzML packages of libraries or scripts based on the
information of the ``metadata.json`` file in the package directory. See
:ref:`bigmler-whizzml`


``bigmler retrain``:


Used to retrain models by adding new data to the existing datasets and
building a new model from it. See
:ref:`bigmler-retrain`


BigML Development Mode
======================

The Sandbox environment that could be reached by using the flag ``--dev``
has been deprecated and. Right now, there's only one mode to work with BigML:
the previous ``Production Model``, so the flag is no longer available.

Using BigMLer
=============

To run BigMLer you can use the console script directly. The ``--help``
option will describe all the available options

.. code-block:: bash

    bigmler --help

Alternatively you can just call bigmler as follows

.. code-block:: bash

    python bigmler.py --help

This will display the full list of optional arguments. You can read a brief
explanation for each option below.


Building the Documentation
==========================

Install the tools required to build the documentation

.. code-block:: bash

    $ pip install sphinx
    $ pip install sphinx-rtd-theme

To build the HTML version of the documentation

.. code-block:: bash

    $ cd docs/
    $ make html

Then launch ``docs/_build/html/index.html`` in your browser.

Additional Information
======================

For additional information, see
the `full documentation for the Python
bindings on Read the Docs <http://bigml.readthedocs.org>`_. For more
information about BigML's API, see the
`BigML developer's documentation <https://bigml.com/api>`_.

Support
=======

Please report problems and bugs to our `BigML.io issue
tracker <https://github.com/bigmlcom/io/issues>`_.

Discussions about the different bindings take place in the general
`BigML mailing list <http://groups.google.com/group/bigml>`_.

How to Contribute
=================

Please follow the next steps:

  1. Fork the project on `github <https://github.com/bigmlcom/bigmler>`_.
  2. Create a new branch.
  3. Commit changes to the new branch.
  4. Send a `pull request <https://github.com/bigmlcom/bigmler/pulls>`_.

For details on the underlying API, see the
`BigML API documentation <https://bigml.com/api>`_.
