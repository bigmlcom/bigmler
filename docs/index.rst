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
or `English_United States.1252` and a warning message will be printed.
If you want to change this behaviour you can specify your preferred locale::

    bigmler --train data/iris.csv --test data/test_iris.csv --locale "English_United States.1252"

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

    bigmler --train data/iris.csv --test data/test_iris.csv  --number-of-models 10 --sample-rate 0.75 --replacement --tag my_ensemble

We recommend to tag resources when you create multiple models at the same time so that you can retrieve them together to generate predictions locally using the multiple models feature from BigML's Python binding.

To create a `random decision forest <http://www.quora.com/Machine-Learning/How-do-random-forests-work-in-laymans-terms>`_ just use the `--randomize` option::

     bigmler --train data/iris.csv --test data/test_iris.csv  --number-of-models 10 --sample-rate 0.75 --replacement --tag my_ensemble --randomize

The fields to choose from will be randomized at each split creating a random decision forest that when used together will increase the prediction performance of the individual models.

There are some more advance options that can help you build your ensembles. When the number of local models becomes quite large holding all the models in memory may exhaust your resources. To avoid this problem you can use the `--max_batch_models` flag which controls how many local models are held in memory at the same time::

    bigmler --train data/iris.csv --test data/test_iris.csv  --number-of-models 10 --sample-rate 0.75 --max-batch-models 5

The predictions generated when using this option will be stored in a file per model and named after the
models' id (e.g. `model_50c23e5e035d07305a00004f__predictions.csv"). Each line contains the prediction, its confidence, the node's distribution and the node's total number of instances. The default value for `max-batch-models` is 10.

When using ensembles model's predictions are combined to issue a final prediction. There are several different methods
to build the combination. You can choose `plurality`, `confidence weighted` or `probability weighted` using the `--method` flag::

    bigmler --train data/iris.csv --test data/test_iris.csv  --number-of-models 10 --sample-rate 0.75 --method "confidence weighted"

For classification ensembles, the combination is made by majority vote: `plurality` weights each model's prediction as one vote, `confidence weighted` uses confidences as weight for the prediction and `probability weighted` uses the probability of the class in the distribution of classes in the node as weight. For regression ensembles, the predicted values are averaged: `plurality` again weights each predicted value as one, `confidence weighted` weights each prediction according to the associated error and `probability weighted` gives the same results as `plurality`.

It is also possible to enlarge the number of models that build your prediction gradually. You can build more than one ensemble for the same test data and combine the votes of all of them by using the flag `combine_votes` followed by the comma separated list of directories where predictions are stored. For instance::

    bigmler --train data/iris.csv --test data/test_iris.csv  --number-of-models 20 --sample-rate 0.75 --output ./dir1/predictions.csv
    bigmler --dataset dataset/50c23e5e035d07305a000056 --test data/test_iris.csv  --number-of-models 20 --sample-rate 0.75 --output ./dir2/predictions.csv
    bigmler --combine-votes ./dir1,./dir2

would generate a set of 20 prediction files, one for each model, in `./dir1`, a similar set in `./dir2` and combine all of them to generate the final prediction.


Making your Dastaset and Model Public
-------------------------------------

Creating a model and making it public in BigML's gallery is as easy as::

    bigmler --train data/iris.csv --white-box

If you just want to share it as a black-box model just use::

    bigmler --train data/iris.csv --black-box

If you also want to make public your dataset::

    bigmler --train data/iris.csv --public-dataset

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

    bigmler --model-tag my_tag --test data/test_iris.csv

You can also use a previously generated dataset to create a new model::

    bigmler --dataset dataset/50a1f441035d0706d9000371

You can also input the dataset from a file::

    bigmler --datasets iris_dataset

Finally, a previously generated source can also be used to generate a new
dataset and model::

    bigmler --source source/50a1e520eabcb404cd0000d1

Evaluations
-----------

BigMLer can also help you to measure the performance of your models. The
simplest way to build a model and evaluate it all at once is::

    bigmler --train data/iris.csv --evaluate

which will build the source, dataset and model objects for you using an 80% of
the data in your training file chosen at random. After that, the 20% percent
that has not been used to build the model will be run through it to obtain
the corresponding evaluation. You can use the same procedure with a previously
existing source or dataset::

    bigmler --source source/50a1e520eabcb404cd0000d1 --evaluate
    bigmler --dataset dataset/50a1f441035d0706d9000371 --evaluate

The results of an evaluation are stored both in `txt` and `json`. Its contents
will follow the description given in the
`Developers guide, evaluation section <https://bigml.com/developers/evaluations>`_
and vary depending on the model being a classification o regression one.

Finally, you can also evaluate a preexisting model using a separate set of
data stored in a file or a previous dataset::

    bigmler --model model/50a1f43deabcb404d3000079 --test data/iris.csv --evaluate
    bigmler --model model/50a1f43deabcb404d3000079 --dataset dataset/50a1f441035d0706d9000371 --evaluate

As for predictions, you can specify a particular file name to store the
evaluation in::

    bigmler --train data/iris.csv --evaluate --output my_dir/evaluation

Configuring Datasets and Models
-------------------------------

What if your raw data isn't necessarily in the format that BigML expects? So we
have good news: you can use a number of options to configure your sources,
datasets, and models.

Imagine that you want to alter BigML's default field names or the ones provided
by the training set header and capitalize them, even to add a label or a
description to each field. You can use a text file with a change per line as
follows::

    bigmler --train data/iris.csv --field-attributes fields.csv

where ``fields.csv`` would be::

    0,'SEPAL LENGTH','label for SEPAL LENGTH','description for SEPAL LENGTH'
    1,'SEPAL WIDTH','label for SEPAL WIDTH','description for SEPAL WIDTH'
    2,'PETAL LENGTH','label for PETAL LENGTH','description for PETAL LENGTH'
    3,'PETAL WIDTH','label for PETAL WIDTH','description for PETAL WIDTH'
    4,'SPECIES','label for SPECIES','description for SPECIES'

The number on the left in each line is the `column number` of the field in your
source and is followed by the new field's name, label and description.


Similarly you can also alter the auto-detect type behavior from BigML assigning
specific types to specific fields::

    bigml --train data/iris.csv --types types.txt

where ``types.txt`` would be::

    0, 'numeric'
    1, 'numeric'
    2, 'numeric'
    3, 'numeric'
    4, 'categorical'

You can specify the fields that you want to include in the dataset::

    bigmler --train data/iris.csv --dataset-fields 'sepal length','sepal width','species'

or the fields that you want to include as predictors in the model::

    bigmler --train data/iris.csv --model-fields 'sepal length','sepal width'

When evaluating, you can map the fields of the test dataset to those of
the evaluated model by writing in a file the field column of the dataset and
the field column of the model separated by a comma and using `--fields-map`
flag to specify the name of the file::

    bigmler --dataset dataset/50a1f441035d0706d9000371 --model model/50a1f43deabcb404d3000079 --evaluate --fields-map fields_map.txt

where ``fields_map.txt`` would contain::

    0, 1
    1, 0
    2, 2
    3, 3
    4, 4

if the first two fields had been reversed.

Finally, you can also tell BigML whether your training and test set come with a
header row or not. For example, if both come without header::

    bigmler --train data/iris_nh.csv --test data/test_iris_nh.csv --no-train-header --no-test-header

Fitering Sources
----------------

Imagine that you have create a new source and that you want to create a
specific dataset filtering the rows of the source that only meet certain
criteria.  You can do that using a JSON expresion as follows::

    bigmler --source source/50a2bb64035d0706db0006cc --json-filter filter.json

where ``filter.json`` is a file containg a expression like this::

    ["<", 7.00, ["field", "000000"]]

or a LISP expression as follows::

    bigmler --source source/50a2bb64035d0706db0006cc --lisp-filter filter.lisp

where ``filter.lisp`` is a file containing a expression like this::

    (< 7.00 (field "sepal length"))

For more details, see the BigML's API documentation on `filtering rows <https://bigml.com/developers/datasets#d_filteringrows>`_.

Deleting Remote Resources
-------------------------

You have seen that BigMLer is an agile tool that empowers you to create a
great number of resources easily. This is a tremedous help, but it also can
lead to a garbage-prone environment. To keep a control of the each new created
remote resource use the flag `--resources-log` followed by the name of the log
file you choose.::

    bigmler --train data/iris.csv --resources-log my_log.log

Each new resource created by that command will cause its id to be appended as
a new line of the log file.

BigMLer can help you as well in deleting these resources. Using the `--delete`
tag there are many options available. For instance, deleting a comma separated
list of ids::

    bigmler --delete --ids source/50a2bb64035d0706db0006cc,dataset/50a1f441035d0706d9000371

deleting resources listed in a file::

    bigmler --delete --from-file to_delete.log

where `to_delete.log` contains a resource id per line. You can also delete
resources based on the
tags they are associated to::

    bigmler --delete --all-tag my_tag

or restricting the operation to a specific type::

    bigmler --delete --source-tag my_tag
    bigmler --delete --dataset-tag my_tag
    bigmler --delete --model-tag my_tag
    bigmler --delete --prediction-tag my_tag
    bigmler --delete --evaluation-tag my_tag

Resuming Previous Commands
--------------------------

Network connections failures or other external causes can break the BigMLer command process. To resume a command ended by an unexpected event you can issue::

    bigmler --resume

BigMLer keeps track of each command you issue in a ``.bigmler`` file and of the output directory in ``.bigmler_dir_stack`` of your working directory. Then ``--resume`` will recover the last issued command and try to continue work from the point it was stopped. There's also a ``--stack-level`` flag::

    bigmler --resume --stack-level 1

to allow resuming a previous command in the stack. In the example, the one before the last.


User Chosen Defaults
--------------------

BigMLer will look for `.bigmler_defaults` file in the working directory where users can personalize the default values they like for the most relevant flags. The options should be written in a config style, e.g.::


    [BigMLer]
    dev = 1
    resources_log = ./my_log.log

as you can see, under a `[BigMLer]` section the file should contain one line per option. Dashes in flags are transformed to undescores in options. The example would keep development mode on and would log all created resources to `my_log.log` for any new `bigmler` command issued under the same working directory if none of the related flags are set.

Naturally, the default value options given in this file will be overriden by the corresponding flag value in the present command. To follow the previous example, if you use::

    bigmler --train data/iris.csv --resources-log ./another_log.log

in the same working directory, the value of the flag will be preeminent and resources will be logged in ``another_log.log``. For boolean-valued flags, such as ``--dev`` itself, you'll need to use the associated negative flags to overide the default behaviour. Than is, following the former example if you want to override the dev mode used by default you should use::

    bigmler --train data/iris.csv --no-dev

The set of negative flags is:

--no-debug                  as opposed to --debug
--no-dev                    as opposed to --dev
--no-train-header           as opposed to --train-header
--no-test-header            as opposed to --test-header
--local                     as opposed to --remote
--no-replacement            as opposed to --replacement
--no-randomize              as opposed to --randomize
--no-no-tag                 as opposed to --no-tag
--no-public-dataset         as opposed to --public-dataset
--no-black-box              as opposed to --black-box
--no-white-box              as opposed to --white-box
--no-progress-bar           as opposed to --progress-bar
--no-no-dataset             as opposed to --no-dataset
--no-no-model               as opposed to --no-model
--no-clear-logs             as opposed to --clear-logs


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

BigMLer requires `bigml 0.4.9 <https://github.com/bigmlcom/python>`_  or higher.

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

    bigmler --train data/iris.csv --username myusername --api-key ae579e7e53fb9abd646a6ff8aa99d4afe83ac291

BigML Development Mode
======================

Also, you can instruct BigMLer to work in BigML's Sandbox
environment by using the parameter ``--dev``::

    bigmler --train data/iris.csv --dev

Using the development flag you can run tasks under 1 MB without spending any of
your BigML credits.

Using BigMLer
=============

To run BigMLer you can use the console script directly. The ``--help`` option will
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
--username  BigML's username. If left unspecified, it will default to the values of the ``BIGML_USERNAME`` environment variable.
--api-key   BigML's api_key. If left unspecified, it will default to the values of the ``BIGML_API_KEY`` environment variable.
--dev       Uses BigML FREE development environment. Sizes must be under 1MB though.
--debug     Activates debug level and shows log info for each https request.

Basic Functionality
-------------------

--train TRAINING_SET        Full path to a training set. It can be a remote URL to a (gzipped or compressed) csv file. The protocol schemes can be http, https, s3, azure, odata.
--test TEST_SET     Full path to a test set. A file containing the data that you want to input to generate predictions.
--objective OBJECTIVE_FIELD     The name of the Objective Field. The field that you want to predict.
--output PREDICTIONS        Full path to a file to save predictions. If left unspecified, it will default to an auto-generated file created by BigMLer.
--method METHOD             Prediction method used: ``plurality``,  ``"confidence weighted"`` or ``"probability weighted"``.
--pruning PRUNING_TYPE      The pruning applied in building the model. It's allowed values are ``smart``, ``statistical`` and ``no-pruning``. The default value is ``smart``
--evaluate                  Turns on evaluation mode
--resume                    Retries command execution.
--stack-level LEVEL         Level of the retried command in the stack

Content
-------
--name NAME     Name for the resources in BigML.
--category CATEGORY     Category code. See `full list <https://bigml.com/developers/sources#s_categories>`_.
--description DESCRIPTION       Path to a file with a description in plain text or markdown.
--tag TAG   Tag to later retrieve new resources
--no-tag    Puts BigMLer default tag if no other tag is given

Data Configuration
------------------
--no-train-header   The train set file hasn't a header
--no-test-header    The test set file hasn't a header
--field-attribute PATH  Path to a file describing field attributes. One definition per line (e.g., 0,'Last Name')
--types PATH        Path to a file describing field types. One definition per line (e.g., 0, 'numeric')
--dataset-fields DATASET_FIELDS     Comma-separated list of field column numbers to include in the dataset
--model-fields MODEL_FIELDS     Comma-separated list of input fields (predictors) to create the model
--json-filter PATH  Path to a file containing a JSON expression to filter the source
--lisp-filter PATH  Path to a file containing a LISP expression to filter the source
--locale LOCALE     Locale code string
--fields-map PATH   Path to a file containing the dataset to model fields map for evaluation


Remote Resources
----------------
--source SOURCE     BigML source Id
--dataset DATASET   BigML dataset Id
--datasets PATH     Path to a file containing a dataset Id
--model MODEL       BigML model Id
--remote            Computes predictions remotely
--models PATH       Path to a file containing model/ids. One model per line (e.g., model/4f824203ce80053)
--model-tag MODEL_TAG   Retrieve models that were tagged with tag

Delete Remote Resources
-----------------------
--delete            Starts delete mode
--ids LIST_OF_IDS   Comma separated list of ids to be deleted
--from-file FILE_OF_IDS  Path to a file containing the resources' ids to be deleted
--all-tag TAG       Retrieves resources that were tagged with tag to be deleted
--source-tag TAG    Retrieves sources that were tagged with tag to be deleted
--dataset-tag TAG   Retrieves datasets that were tagged with tag to be deleted
--model-tag TAG     Retrieves models that were tagged with tag to be deleted
--prediction-tag TAG   Retrieves predictions that were tagged with tag to be deleted
--evaluation-tag TAG   Retrieves evaluations that were tagged with tag to be deleted

Ensembles
---------
--number-of-models NUMBER_OF_MODELS
                        Number of models to create.
--sample-rate SAMPLE_RATE
                        Sample rate to use (a float between 0.01 and 1)
--replacement         Use replacement when sampling
--max-parallel-models MAX_PARALLEL_MODELS    Max number of models to create in parallel
--max-batch-models MAX_BATCH_MODELS  Max number of local models to be predicted from in parallel. For ensembles with a number of models over it, predictions are stored in files as they are computed and retrived and combined eventually.
--randomize           Use a random set of fields to split on.
--combine-votes LIST_OF_DIRS    Combines the votes of models generated in a list of directories.

Ensembles aren't `first-class citizen <http://en.wikipedia.org/wiki/First-class_citizen>`_ in BigML yet. So make sure that you tag your models conveniently so that you can then retrieve them later to generate predictions. We expect to have ensembles at the first level of our API pretty soon.

Public Resources
----------------
--public-dataset    Makes newly created dataset public
--black-box         Makes newly created model a public black-box
--white-box         Makes newly created model a public white-box
--model-price       Sets the price for a public model
--dataset-price     Sets the price for a public dataset
--cpp               Sets the credits consumed by prediction

Notice that datasets and models will be made public without assigning any price
to them.

Fancy Options
-------------    
--progress-bar              Shows an update on the bytes uploaded when creating a new source. This option might run into issues depending on the locale settings of your OS.
--no-dataset                Does not create a model. BigMLer will only create a source.
--no-model                  Does not create a model. BigMLer will only create a dataset.
--resources-log LOG_FILE    Keeps a log of the resources generated in each command.
--version                   Shows the version number
--verbosity LEVEL           Turns on (1) or off (0) the verbosity.
--clear-logs                Clears the ``.bigmler``, ``.bigmler_dir_stack``,  ``.bigmler_dirs`` and user log file given in ``--resources-log`` (if any).

Prior Versions Compatibility Issues
-----------------------------------

BigMLer will accept flags written with underscore as word separator like ``--clear_logs`` for compatibility with prior versions. Also ``--field-names`` is accepted, although the more complete ``--field-attributes`` flag is preferred. ``--stat_pruning`` and ``--no_stat_pruning`` are discontinued and their effects can be achived by setting the actual ``--pruning`` flag to ``statistical`` or ``no-pruning`` values respectively.

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
