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

Let's see some basic usage examples. Check the `installation <#bigmler-installation>`_ and `authentication <#bigml-authentication>`_
sections below if you are not familiar with BigML.

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
or 'English_United States.1252' but a warning message will arise.
If you want to change this behaviour you can specify your preferred locale::

    bigmler --train data/iris.csv --test data/test_iris.csv --locale 'English_United States.1252'

If you check your working directory you will see that BigMLer creates a file with the
model ids that have been generated (e.g., FriNov0912_223645/models).
This file is handy if then you want to use those model ids to generate local
predictions. BigMLer also creates a file with the dataset id that have been
generated (e.g., TueNov1312_003451/dataset).

Remote Sources
--------------

You can create models using remote sources as well. You just need a valid URL that points to your data.
BigML recognizes a growing list of schemas (**http**, **https**, **s3**,
**azure**, **odata**, etc). For example::

    bigmler --train https://test:test@static.bigml.com/csv/iris.csv

    bigmler --train "s3://bigml-public/csv/iris.csv?access-key=AKIAIF6IUYDYUQ7BALJQ&secret-key=XgrQV/hHBVymD75AhFOzveX4qz7DYrO6q8WsM6ny"

    bigmler --train azure://csv/diabetes.csv?AccountName=bigmlpublic

    bigmler --train odata://api.datamarket.azure.com/www.bcn.cat/BCNOFFERING0005/v1/CARRegistration?$top=100

Can you imagine how powerful this feature is? You can create predictive models for huge
amounts of data without using you local CPU, memory, disk or bandwidth. Welcome to the cloud!!!


Ensembles
---------

You can also easily create ensembles. For example, using `bagging <http://en.wikipedia.org/wiki/Bootstrap_aggregating>`_ is as easy as::

    bigmler --train data/iris.csv --test data/test_iris.csv  --number_of_models 10 --sample_rate 0.75 --replacement --tag my_ensemble

We recommend to tag resources when you create multiple models at the same time so that you can retrieve them together to generate predictions locally using the multiple models feature from BigML's Python binding.

To create a `random decision forest <http://www.quora.com/Machine-Learning/How-do-random-forests-work-in-laymans-terms>`_ just use the `--randomize` option::

     bigmler --train data/iris.csv --test data/test_iris.csv  --number_of_models 10 --sample_rate 0.75 --replacement --tag my_ensemble --randomize

The fields to choose from will be randomized at each split creating a random decision forest that when used together will increase the prediction performance of the individual models.

Making your Dastaset and Model Public
-------------------------------------

Creating a model and making it public in BigML's gallery is as easy as::

    bigmler --train data/iris.csv --white_box

If you just want to share it as a black-box model just use::

    bigmler --train data/iris.csv --black_box

If you also want to make public your dataset::

    bigmler --train data/iris.csv --public_dataset

Content
-------

Before making your model public, probably you want to add a name, a category, a description, and tags to your resources. This is easy too. For example::

    bigmler --train data/iris.csv --name "My model" --category 6 --description data/description.txt --tag iris --tag my_tag

Please note:

    - You can get a full list of BigML category codes `here <https://bigml.com/developers/sources#s_categories>`_.
    - Descriptions are provided in a text file that can also include `markdown <http://en.wikipedia.org/wiki/Markdown>`_.
    - Many tags can be added to the same resource.
    - Use --no_tag if you do not want default BigMLer tags to be added.
    - BigMLer will add the name, category, description, and tags to all the newly created resources in each request.


Using previous Sources, Datasets, and Models
--------------------------------------------

You don't need to create a model from scratch every time that you use BigMLer.
You can generate predictions for a test set using a previously generated
model::

    bigmler --model model/50a1f43deabcb404d3000079 --test data/test_iris.csv

You can also use a number of models providing a file with a model/id per line::

    bigmler --models TueDec0412_174148/models --test data/test_iris.csv

Or all the models that were tagged with a specific tag::

    bigmler --model_tag my_tag --test data/test_iris.csv

You can also use a previously generated dataset to create a new model::

    bigmler --dataset dataset/50a1f441035d0706d9000371

You can also input the dataset from a file::

    bigmler --datasets iris_dataset

Finally, a previously generated source can also be used to generate a new
dataset and model::

    bigmler --source source/50a1e520eabcb404cd0000d1

Configuring Datasets and Models
-------------------------------

What if your raw data isn't necessarily in the format that BigML expects? So we
have good news: you can use a number of options to configure your sources,
datasets, and models.

Imagine that you want to alter BigML's default field names or the ones provided by the training set header and capitalize them, you can use a text file with a change per line as follows::

    bigmler --train data/iris.csv --field_names fields.txt

where ``fields.txt`` would be::

    0, 'SEPAL LENGTH'
    1, 'SEPAL WIDTH'
    2, 'PETAL LENGTH'
    3, 'PETAL WIDTH'
    4, 'SPECIES'

The number on the left in each line is the `column number` of the field in your
source.


Similarly you can also alter the auto-detect type behavior from BigML assigning specific
types to specific fields::

    bigml --train data/iris.csv --types types.txt

where ``types.txt`` woud be::

    0, 'numeric'
    1, 'numeric'
    2, 'numeric'
    3, 'numeric'
    4, 'categorical'

You can specify the fields that you want to include in the dataset::

    bigmler --train data/iris.csv --dataset_fields 'sepal length','sepal width','species'

or the fields that you want to include as predictors in the model::

    bigmler --train data/iris.csv --model_fields 'sepal length','sepal width'

Finally, you can also tell BigML whether your training and test set come with a
header row or not. For example, if both come without header::

    bigmler --train data/iris_nh.csv --test data/test_iris_nh.csv --no-train-header --no-test-header

Fitering Sources
----------------

Imagine that you have create a new source and that you want to create a
specific dataset filtering the rows of the source that only meet certain
criteria.  You can do that using a JSON expresion as follows::

    bigmler --source source/50a2bb64035d0706db0006cc --json_filter filter.json

where ``filter.json`` is a file containg a expression like this::

    ["<", 7.00, ["field", "000000"]]

or a LISP expression as follows::

    bigmler --source source/50a2bb64035d0706db0006cc --lisp_filter filter.lisp

where ``filter.lisp`` is a file containing a expression like this::

    (< 7.00 (field "sepal length"))

For more details, see the BigML's API documentation on `filtering rows <https://bigml.com/developers/datasets#d_filteringrows>`_.

Deleting Remote Resources
-------------------------

You have seen that BigMLer is an agile tool that empowers you to create a
great number of resources easily. This is a tremedous help, but it also can
lead to a garbage-prone environment. To keep a control of the each new created
remote resource use the flag `--resources_log` followed by the name of the log
file you choose.::

    bigmler --train data/iris.csv --resources_log my_log.log

Each new resource created by that command will cause its id to be appended as
a new line of the log file.

BigMLer can help you as well in deleting these resources. Using the `--delete`
tag there are many options available. For instance, deleting a comma separated
list of ids::

    bigmler --delete --ids source/50a2bb64035d0706db0006cc,dataset/50a1f441035d0706d9000371

deleting resources listed in a file::

    bigmler --delete --from_file to_delete.log

where `to_delete.log` contains a resource id per line. You can also delete
resources based on the
tags they are associated to::

    bigmler --delete --all_tag my_tag

or restricting the operation to a specific type::

    bigmler --delete --source_tag my_tag
    bigmler --delete --dataset_tag my_tag
    bigmler --delete --model_tag my_tag
    bigmler --delete --prediction_tag my_tag

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

BigMLer requires `bigml 0.4.7 <https://github.com/bigmlcom/python>`_  or higher.

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

--train TRAINING_SET        Full path to a training set. It can be a remote URL to a (gzipped or compressed) csv file. The protocol schemes can be http, https, s3, azure, odata.
--test TEST_SET     Full path to a test set. A file containing the data that you want to input to generate predictions.
--objective OBJECTIVE_FIELD     The name of the Objective Field. The field that you want to predict.
--output PREDICTIONS        Full path to a file to save predictions. If left unspecified, it will default to an auto-generated file created by BigMLer.

Content
-------
--name NAME     Name for the resources in BigML.
--category CATEGORY     Category code. See `full list <https://bigml.com/developers/sources#s_categories>`_.
--description DESCRIPTION       Path to a file with a description in plain text or markdown.
--tag TAG   Tag to later retrieve new resources

Data Configuration
------------------
--no-train-header   The train set file hasn't a header
--no-test-header    The test set file hasn't a header
--field_names PATH  Path to a file describing field names. One definition per line (e.g., 0, 'Last Name')
--types PATH        Path to a file describing field types. One definition per line (e.g., 0, 'numeric')
--dataset_fields DATASET_FIELDS     Comma-separated list of field column numbers to include in the dataset
--model_fields MODEL_FIELDS     Comma-separated list of input fields (predictors) to create the model
--json_filter PATH  Path to a file containing a JSON expression to filter the source
--lisp_filter PATH  Path to a file containing a LISP expression to filter the source
--locale LOCALE     Locale code string


Remote Resources
----------------
--source SOURCE     BigML source Id
--dataset DATASET       BigML dataset Id
--datasets PATH     Path to a file containing a daaset Id
--model MODEL       BigML model Id
--remote        Computes predictions remotely
--models PATH     Path to a file containing model/ids. One model per line (e.g., model/4f824203ce80053)
--model_tag MODEL_TAG
                        Retrieve models that were tagged with tag

Delete Remote Resources
-----------------------
--delete     Starts delete mode
--ids LIST_OF_IDS   Comma separated list of ids to be deleted
--all_tag TAG    Retrieves resources that were tagged with tag to be deleted
--source_tag TAG    Retrieves sources that were tagged with tag to be deleted
--dataset_tag TAG   Retrieves datasets that were tagged with tag to be deleted
--model_tag TAG   Retrieves models that were tagged with tag to be deleted
--prediction_tag TAG   Retrieves predictions that were tagged with tag to be deleted

Ensembles
---------
--number_of_models NUMBER_OF_MODELS
                        Number of models to create.
--sample_rate SAMPLE_RATE
                        Sample rate to use (a float between 0.01 and 1)
--replacement         Use replacement when sampling
--max_parallel_models MAX_PARALLEL_MODELS    Max number of models to create in parallel
--randomize           Use a random set of fields to split on.

Ensembles aren't `first-class citizen <http://en.wikipedia.org/wiki/First-class_citizen>`_ in BigML yet. So make sure that you tag your models conveniently so that you can then retrieve them later to generate predictions. We expect to have ensembles at the first level of our API pretty soon.

Public Resources
----------------
--public_dataset    Makes newly created dataset public
--black_box         Makes newly created model a public black-box
--white_box         Makes newly created model a public white-box

Notice that datasets and models will be made public without assigning any price
to them.

Fancy Options
-------------
--progress_bar  Shows an update on the bytes uploaded when creating a new source. This option might run into issues depending on the locale settings of your OS.

--no_model  Does not create a model. BigMLer will only create a dataset.
--resources_log LOG_FILE   Keeps a log of the resources generated in each command. 

Building the Documentation
==========================

Install the tools required to build the documentation::

    $ pip install sphinx

To build the HTML version of the documentation::

    $ cd docs/
    $ make html

Then launch ``docs/_build/html/index.html`` in your browser.

Additional Information
======================

For additional information, see
the `full documentation for the Python
bindings on Read the Docs <http://bigml.readthedocs.org>`_. For more information about BigML's API, see the
`BigML developer's documentation <https://bigml.com/developers>`_.

How to Contribute
=================

Please follow the next steps:

  1. Fork the project on `github <https://github.com/bigmlcom/bigmler>`_.
  2. Create a new branch.
  3. Commit changes to the new branch.
  4. Send a `pull request <https://github.com/bigmlcom/bigmler/pulls>`_.

For details on the underlying API, see the
`BigML API documentation <https://bigml.com/developers>`_.
