BigMLer - A Higher-Level API to BigML's API
===========================================

BigMLer makes `BigML <https://bigml.com>`_ even easier.

BigMLer wraps `BigML's API Python bindings <http://bigml.readthedocs.org>`_  to
offer a high-level command-line script to easily create and publish datasets and models, create ensembles,
make local predictions from multiple models, and simplify many other machine
learning tasks.

BigMLer is open sourced under the `Apache License, Version
2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>`_.

Quick Start
===========

You can create a model with just::

    bigmler --train data/iris.csv

You can generate predictions for a::

    bigmler --train data/iris.csv  --test data/test_iris.csv


Creating a model and making it public in BigML's gallery is as easy as:

::

    bigmler --train data/iris.csv --white_box

You can

    bigmler --train https://static.bigml.com/csv/iris.csv

::

    bigmler --train data/iris.csv --test data/test_iris.csv

::

    bigmler --train https://

::
    bigmler --train s3://

::

    bigmler --train azure://

::

    bigmler --train odata://


Support
=======

Please report problems and bugs to our `BigML.io issue
tracker <https://github.com/bigmlcom/io/issues>`_.

Discussions about the different bindings take place in the general
`BigML mailing list <http://groups.google.com/group/bigml>`_. Or join us
in our `Campfire chatroom <https://bigmlinc.campfirenow.com/f20a0>`_.

Requirements
============

Python 2.6 and Python 2.7 are currently supported by BigMLer.

BigML requires `bigml 0.4.3 <https://github.com/bigmlcom/python>`_  or higher.

Installation
============

To install the latest stable release with
`pip <http://www.pip-installer.org/>`_::

    $ pip install bigmler

You can also install the development version of the bindings directly
from the Git repository::

    $ pip install -e git://github.com/bigmlcom/bigmler.git#egg=bigmler_python

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

Also, you can instruct BigMLer to work in BigML's Sandbox
environment by using the parameter ``---dev``::

    bigmler --train data/iris.csv --dev

Using the development flag you can run tasks under 1 MB without spending any of
your BigML credits.

Using the script
================

To run BigML you can use the console script directly. The `--help` option will
describe all the available options::

    bigmler --help

Alternatively you can just call bigmler as follows::

    python bigmler.py --help


Optional Arguments
==================

General configuration
---------------------
--username  BigML's username. If left unspecified, it will default to the values of the `BIGML_USERNAME` environment variable.
--api_key   BigML's api_key. If left unspecified, it will default to the values of the `BIGML_API_KEY` environment variable.
--dev       Uses BigML FREE development environment. Sizes must be under 1MB though.
--debug     Activates debug level and shows log info for each https request.

Basic Functionality
-------------------

--train TRAINING_SET    Training set path. The path can be a URL to a (gzipped or compressed) csv file. The protocol schemes can be http, https, s3, azure, odata.
--test TEST_SET Test set path.
--output SUBMISSION Full path to a file to save predictions.

--objective OBJECTIVE_FIELD The name of the Objective Field. The field that you
want to predict.

Content
-------
--name NAME           Name for the resources in BigML
--category CATEGORY Category code. See `full list <https://bigml.com/developers/sources#s_categories for>`_
--description DESCRIPTION
                        Path to a file with a description in plain text or
                        markdown
--tag TAG             Tag to later retrieve new resources

--field_names FIELD_NAMES
                        Path to a file describing field names. One definition
                       per line (e.g., 0, 'Last Name')


--types TYPES         Path to a file describing field types. One definition
                        per line (e.g., 0, 'numeric')
--dataset_fields DATASET_FIELDS
                        Comma-separated list of field column numbers to
                        include in the dataset
--model_fields MODEL_FIELDS
                        Comma-separated list of input fields (predictors) to
                        create the model
--no-train-header     The train set file hasn't a header
--no-test-header      The test set file hasn't a header


Remote Resources
----------------
--source SOURCE       BigML source Id
--dataset DATASET     BigML dataset Id
--model MODEL         BigML model Id
--remote              Computes predictions remotely
--models MODELS       Path to a file containing model/ids. One model per
                        line (e.g., 0, 'model/4f824203ce80053')

Ensembles
---------

--number_of_models NUMBER_OF_MODELS
                        Number of models to create.
--sample_rate SAMPLE_RATE
                        Sample rate to use (a float between 0.01 and 1)
--replacement         Use replacement when sampling
--max_parallel_models MAX_PARALLEL_MODELS    Max number of models to create in parallel
--randomize           Use a random set of fields to split on.
--model_tag MODEL_TAG
                        Retrieve models that were tagged with tag

Public Resources
----------------
--public_dataset    Make generated dataset public
--black_box         Make generated model black-box
--white_box         Make generated model white-box

Running the Tests
-----------------

To run the tests you will need to install
`lettuce <http://packages.python.org/lettuce/tutorial/simple.html>`_::

    $ pip install lettuce

and set up your authentication via environment variables, as explained
above. With that in place, you can run the test suite simply by::

    $ cd tests
    $ lettuce

Additionally, `Tox <http://tox.testrun.org/>`_ can be used to
automatically run the test suite in virtual environments for all
supported Python versions.  To install Tox::

    $ pip install tox

Then run the tests from the top-level project directory::

    $ tox

Note that tox checks the exit status from the test command (lettuce) to
determine pass/fail, but the latest version of lettuce (0.2.5)
erroneously exits with a non-zero exit status indicating an error. So,
tox will report failures even if the test suite is passing. This
`should be fixed <https://github.com/gabrielfalcao/lettuce/pull/270>`_
in the next release of lettuce.

Building the Documentation
--------------------------

Install the tools required to build the documentation::

    $ pip install sphinx

To build the HTML version of the documentation::

    $ cd docs/
    $ make html

Then launch ``docs/_build/html/index.html`` in your browser.

Additional Information
----------------------

For additional information, see
the `full documentation for the Python
bindings on Read the Docs <http://bigml.readthedocs.org>`_. For more information about BigML's API, see the
`BigML developer's documentation <https://bigml.com/developers>`_.
