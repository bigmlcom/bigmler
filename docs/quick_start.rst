.. toctree::
   :maxdepth: 2
   :hidden:

Quick Start
===========

Let's see some basic usage examples. Check the
`installation <#bigmler-installation>`_ and
`authentication <#bigml-authentication>`_
sections below if you are not familiar with BigML.

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
one for you under a ``.bigmler_outputs`` directory.
The new directory will be named after the current date and time
(e.g., `MonNov1212_174715/predictions.csv`). With ``--prediction-info``
flag set to ``brief`` only the prediction result will be stored (default is
``normal`` and includes confidence information). You can also set it to
``full`` if you prefer the result to be presented as a row with your test
input data followed by the corresponding prediction. To include a headers row
in the prediction file you can set ``--prediction-header``. For both the
``--prediction-info full`` and ``--prediction-info brief`` options, if you
want to include a subset of the fields in your test file you can select them by
setting ``--prediction-fields`` to a comma-separated list of them. Then


.. code-block:: bash

    bigmler --train data/iris.csv --test data/test_iris.csv \
            --prediction-info full --prediction-header \
            --prediction-fields 'petal length','petal width'

will include in the generated predictions file a headers row


.. code-block:: bash

    petal length,petal width,species,confidence

and only the values of ``petal length`` and ``petal width`` will be shown
before the objective field prediction ``species``.

A different ``objective field`` (the field that you want to predict) can be
selected using


.. code-block:: bash

    bigmler --train data/iris.csv --test data/test_iris.csv \
            --objective 'sepal length'

If you do not explicitly specify an objective field, BigML will default to the
last
column in your dataset. You can also use as selector the field column number
instead of the name (when --no-train-header is used, for instance).

Also, if your test file uses a particular field separator for its data,
you can tell BigMLer using ``--test-separator``.
For example, if your test file uses the tab character as field separator the
call should be like


.. code-block:: bash

    bigmler --train data/iris.csv --test data/test_iris.tsv \
            --test-separator '\t'

The model's predictions in BigMLer are based on the mean of the distribution
of training values in the predicted node. In case you would like to use the
median instead, you could just add the ``--median`` flag to your command

.. code-block:: bash

    bigmler --train data/grades.csv --test data/test_grades.csv \
            --median

Note that this flag can only be applied to regression models.

If you don't provide a file name for your training source, BigMLer will try to
read it from the standard input

.. code-block:: bash

    cat data/iris.csv | bigmler --train

or you can also read the test info from there

.. code-block:: bash

    cat data/test_iris.csv | bigmler --train data/iris.csv --test

BigMLer will try to use the locale of the model both to create a new source
(if the ``--train`` flag is used) and to interpret test data. In case
it fails, it will try ``en_US.UTF-8``
or ``English_United States.1252`` and a warning message will be printed.
If you want to change this behaviour you can specify your preferred locale

.. code-block:: bash

    bigmler --train data/iris.csv --test data/test_iris.csv \
            --locale "English_United States.1252"

If you check the ``.bigmler_outputs`` folder in your working directory
you will see that BigMLer creates a file with the
model ids that have been generated (e.g., FriNov0912_223645/models).
This file is handy if then you want to use those model ids to generate local
predictions. BigMLer also creates a file with the dataset id that has been
generated (e.g., TueNov1312_003451/dataset) and another one summarizing
the steps taken in the session progress: ``bigmler_sessions``. You can also
store a copy of every created or retrieved resource in your output directory
(e.g., .bigmler_outputs/TueNov1312_003451/model_50c23e5e035d07305a00004f)
by setting the flag ``--store``.

Remote Predictions
------------------

All the predictions we saw in the previous section are computed locally in
your computer. BigMLer allows you to ask for a remote computation by adding
the ``--remote`` flag. Remote computations are treated as batch computations.
This means that your test data will be loaded in BigML as a regular source and
the corresponding dataset will be created and fed as input data to your
model to generate a remote ``batch prediction`` object. BigMLer will download
the predictions file created as a result of this ``batch prediction`` and
save it to local storage just as it did for local predictions

.. code-block:: bash

    bigmler --train data/iris.csv --test data/test_iris.csv \
            --remote --output my_dir/remote_predictions.csv

This command will create a source, dataset and model for your training data,
a source and dataset for your test data and a batch prediction using the model
and the test dataset. The results will be stored in the
``my_dir/remote_predictions.csv`` file. If you prefer the result not to be
dowloaded but to be stored as a new dataset remotely, add ``--no-csv`` and
``to-dataset`` to the command line. This can be specially helpful when
dealing with a high number of scores or when adding to the final result
the original dataset fields with ``--prediction-info full``, that may result
in a large CSV to be created as output. Other output configurations can be
set by using the ``--batch-prediction-attributes`` option pointing to a JSON
file that contains the desired attributes, like:

.. code-block:: json

    {"probabilities": true,
     "all_fields": true}



In case you prefer BigMLer to issue
one-by-one remote prediction calls, you can use the ``--no-batch`` flag

.. code-block:: bash

    bigmler --train data/iris.csv --test data/test_iris.csv \
            --remote --no-batch

External Connectors
-------------------

Data can be uploaded from local and remote public files in BigML as you will
see in the `sources <#remote-sources>`_ section. It can also be extracted
from an external database manager like PostgreSQL, MySQL, Elasticsearch or
SQL Server. An ``externalconnector`` resource can be created in BigML to use it
as data feed.

.. code-block:: bash

    bigmler connector --host my_data.hostname.com \
                      --port 1234                 \
                      --engine postgresql         \
                      --user my_username          \
                      --password my_password      \
                      --database my_database      \
                      --output-dir out

This command will generate the ``externalconnector`` and the corresponding
external connector ID will be stored in the ``external_connector`` file of
your ``out`` directory. Using this ID as reference and the query of choice
when creating a ``source`` in BigML, you will be able to connect and upload
data to the platform.


Remote Sources
--------------

You can create models using remote sources as well. You just need a valid URL
that points to your data.
BigML recognizes a growing list of schemas (**http**, **https**, **s3**,
**azure**, **odata**, etc). For example

.. code-block:: bash

    bigmler --train https://test:test@static.bigml.com/csv/iris.csv

    bigmler --train "s3://bigml-public/csv/iris.csv?access-key=[your-access-key]&secret-key=[your-secret-key]"

    bigmler --train azure://csv/diabetes.csv?AccountName=bigmlpublic

    bigmler --train odata://api.datamarket.azure.com/www.bcn.cat/BCNOFFERING0005/v1/CARRegistration?$top=100

Also, you can use an existing connector to an external source (see the
`external connectors section <#external-connectors>`_). The connector
ID and the particular query must be placed in a JSON file:

.. code-block:: bash

    bigmler --train my_connector.json

where the JSON file should contain the following structure:

.. code-block:: bash

    {"source": "postgresql",
     "externalconnector_id": "51901f4337203f3a9a000215",
     "query": "select * from my_table"}


Can you imagine how powerful this feature is? You can create predictive
models for huge
amounts of data without using you local CPU, memory, disk or bandwidth.
Welcome to the cloud!!!

To learn more about other sources and options, please check the
:ref:`bigmler-source` subcommand.


Ensembles
---------

You can also easily create ensembles. For example, using
`bagging <http://en.wikipedia.org/wiki/Bootstrap_aggregating>`_ is as easy as

.. code-block:: bash

    bigmler --train data/iris.csv --test data/test_iris.csv \
            --number-of-models 10 --sample-rate 0.75 --replacement \
            --tag my_ensemble

To create a
`random decision forest <http://www.quora.com/Machine-Learning/How-do-random-forests-work-in-laymans-terms>`_
just use the `--randomize` option

.. code-block:: bash

     bigmler --train data/iris.csv --test data/test_iris.csv \
             --number-of-models 10 --sample-rate 0.75 --replacement \
             --tag my_random_forest --randomize

The fields to choose from will be randomized at each split creating a random
decision forest that when used together will increase the prediction
performance of the individual models.

To create a boosted trees' ensemble use the `--boosting` option

.. code-block:: bash

     bigmler --train data/iris.csv --test data/test_iris.csv \
             --boosting --tag my_boosted_trees

or add the ``--boosting-iterations` limit

.. code-block:: bash

     bigmler --train data/iris.csv --test data/test_iris.csv \
             --booting-iterations 10 --sample-rate 0.75 --replacement \
             --tag my_boosted_trees

Once you have an existing ensemble, you can use it to predict.
You can do so with the command

.. code-block:: bash

    bigmler --ensemble ensemble/51901f4337203f3a9a000215 \
            --test data/test_iris.csv

Or if you want to evaluate it

.. code-block:: bash

    bigmler --ensemble ensemble/51901f4337203f3a9a000215 \
            --test data/iris.csv --evaluate

There are some more advanced options that can help you build local predictions
with your ensembles.
When the number of local models becomes quite large holding all the models in
memory may exhaust your resources. To avoid this problem you can use the
``--max_batch_models`` flag which controls how many local models are held
in memory at the same time

.. code-block:: bash

    bigmler --train data/iris.csv --test data/test_iris.csv \
            --number-of-models 10 --sample-rate 0.75 --max-batch-models 5

The predictions generated when using this option will be stored in a file per
model and named after the
models' id (e.g. `model_50c23e5e035d07305a00004f__predictions.csv"). Each line
contains the prediction, its confidence, the node's distribution and the node's
total number of instances. The default value for ``max-batch-models`` is 10.

When using ensembles, model's predictions are combined to issue a final
prediction. There are several different methods to build the combination.
You can choose ``plurality``, ``confidence weighted``, ``probability weighted``
or ``threshold`` using the ``--method`` flag

.. code-block:: bash

    bigmler --train data/iris.csv --test data/test_iris.csv \
            --number-of-models 10 --sample-rate 0.75 \
            --method "confidence weighted"

For classification ensembles, the combination is made by majority vote:
``plurality`` weights each model's prediction as one vote,
``confidence weighted`` uses confidences as weight for the prediction,
``probability weighted`` uses the probability of the class in the distribution
of classes in the node as weight, and ``threshold`` uses an integer number
as threshold and a class name to issue the prediction: if the votes for
the chosen class reach the threshold value, then the class is predicted
and plurality for the rest of predictions is used otherwise

.. code-block:: bash

    bigmler --train data/iris.csv --test data/test_iris.csv \
            --number-of-models 10 --sample-rate 0.75 \
            --method threshold --threshold 4 --class 'Iris-setosa'

For regression ensembles, the predicted values are averaged: ``plurality``
again weights each predicted value as one,
``confidence weighted`` weights each prediction according to the associated
error and ``probability weighted`` gives the same results as ``plurality``.

As in the model's case, you can base your prediction on the median of the
predicted node's distribution by adding ``--median`` to your BigMLer command.

It is also possible to enlarge the number of models that build your prediction
gradually. You can build more than one ensemble for the same test data and
combine the votes of all of them by using the flag ``combine_votes``
followed by the comma separated list of directories where predictions are
stored. For instance

.. code-block:: bash

    bigmler --train data/iris.csv --test data/test_iris.csv \
            --number-of-models 20 --sample-rate 0.75 \
            --output ./dir1/predictions.csv
    bigmler --dataset dataset/50c23e5e035d07305a000056 \
            --test data/test_iris.csv  --number-of-models 20 \
            --sample-rate 0.75 --output ./dir2/predictions.csv
    bigmler --combine-votes ./dir1,./dir2

would generate a set of 20 prediction files, one for each model, in ``./dir1``,
a similar set in ``./dir2`` and combine all of them to generate the final
prediction.


Making your Dataset and Model public or sharing it privately
------------------------------------------------------------

Creating a model and making it public in BigML's gallery is as easy as

.. code-block:: bash

    bigmler --train data/iris.csv --white-box

If you just want to share it as a black-box model just use

.. code-block:: bash

    bigmler --train data/iris.csv --black-box

If you also want to make public your dataset

.. code-block:: bash

    bigmler --train data/iris.csv --public-dataset

You can also share your datasets, models and evaluations privately with
whomever you choose by generating a private link. The ``--shared`` flag will
create such a link

.. code-block:: bash

    bigmler --dataset dataset/534487ef37203f0d6b000894 --shared --no-model

and the link will be listed in the output of the command

.. code-block:: bash

    bigmler --dataset dataset/534487ef37203f0d6b000894 --shared --no-model
    [2014-04-18 09:29:27] Retrieving dataset. https://bigml.com/dashboard/dataset/534487ef37203f0d6b000894
    [2014-04-18 09:29:30] Updating dataset. https://bigml.com/dashboard/dataset/534487ef37203f0d6b000894
    [2014-04-18 09:29:30] Shared dataset link. https://bigml.com/shared/dataset/8VPwG7Ny39g1mXBRD1sKQLuHrqE


or can also be found in the information pannel for the resource through the
web interface.

Descriptive information
^^^^^^^^^^^^^^^^^^^^^^^

Before making your model public, probably you want to add a name, a category,
a description, and tags to your resources. This is easy too. For example

.. code-block:: bash

    bigmler --train data/iris.csv --name "My model" --category 6 \
            --description data/description.txt --tag iris --tag my_tag

Please note:

    - You can get a full list of BigML category codes `here <https://bigml.com/api/sources#s_categories>`_.
    - Descriptions are provided in a text file that can also include `markdown <http://en.wikipedia.org/wiki/Markdown>`_.
    - Many tags can be added to the same resource.
    - Use ``--no_tag`` if you do not want default BigMLer tags to be added.
    - BigMLer will add the name, category, description, and tags to all the
      newly created resources in each request.

Projects
--------

Each resource created in BigML can be associated to a ``project``. Projects are
intended for organizational purposes, and BigMLer can create projects
each time a ``source`` is created using a ``--project``
option. For instance

.. code-block:: bash

    bigmler --train data/iris.csv --project "my new project"

will first check for the existence of a project by that name. If it exists,
will associate the source, dataset and model resources to this project.
If it doesn't, a new ``project`` is created and then associated.

You can also associate resources to any ``project`` in your account
by specifying the option ``--project-id`` followed by its id

.. code-block:: bash

    bigmler --train data/iris.csv --project-id project/524487ef37203f0d6b000894

Note: Once a ``source`` has been associated to a ``project``, all the resources
derived from this ``source`` will be automatically associated to the same
``project``.

You can also create projects or update their properties by using the `bigmler
project <#bigmler-project>`_ subcommand. In particular, when projects need
to be created in an ``organization``, the ``--organization`` option has to
be added to inform about the ID of the organization where the project should
be created:

.. code-block:: bash

    bigmler project --organization organization/524487ef37203f0d6b000594 \
                    --name "my new project"

Only allowed users can create projects in ``organizations``. If you are not the
owner or an administrator, please check your permissions with them first.
You can learn more about organizations at the
`API documentation <https://bigml.com/api/organizations/>`_.

You can also create resources in an organization's project if your user
has the right privileges. In order to do that, you should add the
``--org-project`` option followed by the organization's project ID.

.. code-block:: bash

    bigmler --train data/iris.csv \
            --org-project project/524487ef37203f0d6b000894


Using the existing resources in BigML
-------------------------------------

You don't need to create a model from scratch every time that you use BigMLer.
You can generate predictions for a test set using a previously generated
model, cluster, etc. The example shows how you would do that for a tree model:

.. code-block:: bash

    bigmler --model model/50a1f43deabcb404d3000079 --test data/test_iris.csv

You can also use a number of models providing a file with a model/id per line

.. code-block:: bash

    bigmler --models TueDec0412_174148/models --test data/test_iris.csv

Or all the models that were tagged with a specific tag

.. code-block:: bash

    bigmler --model-tag my_tag --test data/test_iris.csv

The same can be extended to any other subcomamnd, like ``bigmler cluster``
using the correct option (``--cluster cluster/50a1f43deabcb404d3000da2``,
``--clusters TueDec0412_174148/clusters`` and ``cluster-tag my_tag``).
Please, check each subcommand available options for details.

You can also use a previously generated dataset to create a new model

.. code-block:: bash

    bigmler --dataset dataset/50a1f441035d0706d9000371

You can also input the dataset from a file

.. code-block:: bash

    bigmler --datasets iris_dataset

A previously generated source can also be used to generate a new
dataset and model

.. code-block:: bash

    bigmler --source source/50a1e520eabcb404cd0000d1

And test sources and datasets can also be referenced by id in new
BigMLer requests for remote predictions

.. code-block:: bash

    bigmler --model model/52af53a437203f1cfe0001f0 --remote \
            --test-source source/52b0cbe637203f1d3e0015db

    bigmler --model model/52af53a437203f1cfe0001f0 --remote \
            --test-dataset dataset/52b0fb5637203f5c4f000018

Evaluations
-----------

BigMLer can also help you to measure the performance of your supervised
models (decision trees, ensembles, deepnets, linear regressions
and logistic regressions). The
simplest way to build a model and evaluate it all at once is

.. code-block:: bash

    bigmler --train data/iris.csv --evaluate

which will build the source, dataset and model objects for you using 80% of
the data in your training file chosen at random. After that, the remaining 20%
of the data will be run through the model to obtain
the corresponding evaluation.

The same procedure is available for ensembles:

.. code-block:: bash

    bigmler --train data/iris.csv --number-of-models 10 --evaluate

for deepnets

.. code-block:: bash

    bigmler deepnet --train data/iris.csv --evaluate

for linear regressions

.. code-block:: bash

    bigmler linear-regression --train data/iris.csv --evaluate

and for logistic regressions:

.. code-block:: bash

    bigmler logistic-regression --train data/iris.csv --evaluate

You can use the same procedure with a previously
existing source or dataset

.. code-block:: bash

    bigmler --source source/50a1e520eabcb404cd0000d1 --evaluate
    bigmler --dataset dataset/50a1f441035d0706d9000371 --evaluate

The results of an evaluation are stored both in txt and json files. Its
contents will follow the description given in the
`Developers guide, evaluation section <https://bigml.com/api/evaluations>`_
and vary depending on the model being a classification or regression one.

Finally, you can also evaluate a preexisting model using a separate set of
data stored in a file or a previous dataset

.. code-block:: bash

    bigmler --model model/50a1f43deabcb404d3000079 --test data/iris.csv \
            --evaluate
    bigmler --model model/50a1f43deabcb404d3000079 \
            --test-dataset dataset/50a1f441035d0706d9000371 --evaluate

As for predictions, you can specify a particular file name to store the
evaluation in

.. code-block:: bash

    bigmler --train data/iris.csv --evaluate --output my_dir/evaluation

Cross-validation
----------------

If you need cross-validation techniques to ponder which parameters (like
the ones related to different kinds of pruning) can improve the quality of your
models, you can use the ``--cross-validation-rate`` flag to settle the
part of your training data that will be separated for cross validation. BigMLer
will use a Monte-Carlo cross-validation variant, building ``2*n`` different
models, each of which is constructed by a subset of the training data,
holding out randomly ``n%`` of the instances. The held-out data will then be
used to evaluate the corresponding model. For instance, both

.. code-block:: bash

    bigmler --train data/iris.csv --cross-validation-rate 0.02
    bigmler --dataset dataset/519029ae37203f3a9a0002bf \
            --cross-validation-rate 0.02

will hold out 2% of the training data to evaluate a model built upon the
remaining 98%. The evaluations will be averaged and the result saved
in json and human-readable formats in ``cross-validation.json`` and
``cross-validation.txt`` respectively. Of course, in this kind of
cross-validation you can choose the number of evaluations yourself by
setting the ``--number-of-evaluations`` flag. You should just keep in mind
that it must be high enough to ensure low variance, for instance

.. code-block:: bash

    bigmler --train data/iris.csv --cross-validation-rate 0.1 \
            --number-of-evaluations 20

The ``--max-parallel-evaluations`` flag will help you limit the number of
parallel evaluation creation calls.

.. code-block:: bash

    bigmler --train data/iris.csv --cross-validation-rate 0.1 \
            --number-of-evaluations 20 --max-parallel-evaluations 2


Configuring Datasets and Models
-------------------------------

What if your raw data isn't necessarily in the format that BigML expects? So we
have good news: you can use a number of options to configure your sources,
datasets, and models.

Most resources in BigML contain information about the fields used in the
resource construction. Sources contain information about the name, label,
description and type of the fields detected in the data you upload.
In addition to that, datasets contain the information of the values that
each field contains, whether they have missing values or errors and even
if they are ``preferred`` fields or non-preferred (fields that are not expected
to convey real information to the model, like user IDs or constant fields).
This information is available in the "fields" attribute of each resource,
but BigMLer can extract it and build a CSV file with a summary of it.

.. code-block:: bash

    bigmler --source source/50a1f43deabcb404d3010079 \
            --export-fields fields_summary.csv \
            --output-dir summary

By using this command, BigMLer will create a ``fields_summary.csv`` file
in a ``summary`` output directory. The file will contain a headers row and
the fields information available in the source, namely the field column,
field ID, field name, field label and field description of each field. If you
execute the same command on a dataset

.. code-block:: bash

    bigmler --dataset dataset/50a1f43deabcb404d3010079 \
            --export-fields fields_summary.csv \
            --output-dir summary

you will also see the number of missing values and errors found in each field
and an excerpt of the values and errors.

But then, imagine that you want to alter BigML's default field names
or the ones provided
by the training set header and capitalize them, even to add a label or a
description to each field. You can use several methods. Write a text file
with a change per line as
follows

.. code-block:: bash

    bigmler --train data/iris.csv --field-attributes fields.csv

where ``fields.csv`` would be

.. code-block:: bash

    0,'SEPAL LENGTH','label for SEPAL LENGTH','description for SEPAL LENGTH'
    1,'SEPAL WIDTH','label for SEPAL WIDTH','description for SEPAL WIDTH'
    2,'PETAL LENGTH','label for PETAL LENGTH','description for PETAL LENGTH'
    3,'PETAL WIDTH','label for PETAL WIDTH','description for PETAL WIDTH'
    4,'SPECIES','label for SPECIES','description for SPECIES'

The number on the left in each line is the `column number` of the field in your
source and is followed by the new field's name, label and description.


Similarly you can also alter the auto-detect type behavior from BigML assigning
specific types to specific fields

.. code-block:: bash

    bigmler --train data/iris.csv --types types.txt

where ``types.txt`` would be

.. code-block:: bash

    0, 'numeric'
    1, 'numeric'
    2, 'numeric'
    3, 'numeric'
    4, 'categorical'

Finally, the same summary file that could be built with the ``--export-fields``
option can be used to modify the updatable information in sources
and datasets. Just edit the CSV file with your favourite editor setting
the new values for the fields and use:

.. code-block:: bash

    bigmler --source source/50a1f43deabcb404d3010079 \
            --import-fields summary/fields_summary.csv

to update the names, labels, descriptions or types of the fields with the ones
in the ``summary/fields_summary.csv`` file.

You could
also use this option to change the ``preferred`` attributes for each
of the fields. This transformation is made at the dataset level,
so in the prior code it will be applied once a dataset is created from
the referred source. You might as well act
on an existing dataset:

.. code-block:: bash

    bigmler --dataset dataset/50a1f43deabcb404d3010079 \
            --import-fields summary/fields_summary.csv


In order to update more detailed
source options, you can use the ``--source-attributes`` option pointing
to a file path that contains the configuration settings to be modified
in JSON format

.. code-block:: bash

    bigmler --source source/52b8a12037203f48bc00000a \
            --source-attributes my_dir/attributes.json --no-dataset

Let's say this source has a text field with id ``000001``. The
``attributes.json`` to change its text parsing mode to full field contents
would read

.. code-block:: bash

    {"fields": {"000001": {"term_analysis": {"token_mode": "full_terms_only"}}}}

you can also reference the fields by its column number in this JSON structures.
If the field to be modified is in the second column (column index starts at 0)
then the contents of the ``attributes.json`` file could be as well

.. code-block:: bash

    {"fields": {"1": {"term_analysis": {"token_mode": "full_terms_only"}}}}

The ``source-attributes`` JSON can contain any of the updatable attributes
described in the
`developers section <https://bigml.com/api/sources#sr_source_properties>`_
You can specify the fields that you want to include in the dataset by naming
them explicitly

.. code-block:: bash

    bigmler --train data/iris.csv \
            --dataset-fields 'sepal length','sepal width','species'

or the fields that you want to include as predictors in the model

.. code-block:: bash

    bigmler --train data/iris.csv --model-fields 'sepal length','sepal width'

You can also specify the chosen fields by adding or removing the ones you
choose to the list of preferred fields of the previous resource. Just prefix
their names with ``+`` or ``-`` respectively. For example,
you could create a model from an existing dataset using all their fields but
the ``sepal length`` by saying

.. code-block:: bash

    bigmler --dataset dataset/50a1f441035d0706d9000371 \
            --model-fields -'sepal length'


When evaluating, you can map the fields of the evaluated model to those of
the test dataset by writing in a file the field column of the model and
the field column of the dataset separated by a comma and using `--fields-map`
flag to specify the name of the file

.. code-block:: bash

    bigmler --dataset dataset/50a1f441035d0706d9000371 \
            --model model/50a1f43deabcb404d3000079 --evaluate \
            --fields-map fields_map.txt

where ``fields_map.txt`` would contain

.. code-block:: bash

    0, 1
    1, 0
    2, 2
    3, 3
    4, 4

if the first two fields had been reversed.

Finally, you can also tell BigML whether your training and test set come with a
header row or not. For example, if both come without header

.. code-block:: bash

    bigmler --train data/iris_nh.csv --test data/test_iris_nh.csv \
            --no-train-header --no-test-header


Splitting Datasets
------------------

When following the usual proceedings to evaluate your models you'll need to
separate the available data in two sets: the training set and the test set. With
BigMLer you won't need to create two separate physical files. Instead, you
can set a ``--test-split`` flag that will set the percentage of data used to
build the test set and leave the rest for training. For instance

.. code-block:: bash

    bigmler --train data/iris.csv --test-split 0.2 --name iris --evaluate

will build a source with your entire file contents, create the corresponding
dataset and split it in two: a test dataset with 20% of instances and a
training dataset with the remaining 80%. Then, a model will be created based on
the training set data and evaluated using the test set. By default, split is
deterministic, so that every time you issue the same command will get the
same split datasets. If you want to generate
different splits from a unique dataset you can set the ``--seed`` option to a
different string in every call

.. code-block:: bash

    bigmler --train data/iris.csv --test-split 0.2 --name iris \
            --seed my_random_string_382734627364 --evaluate


Advanced Dataset management
---------------------------

As you can find in the BigML's API documentation on
`datasets <https://bigml.com/api/datasets>`_ besides the basic name,
label and description that we discussed in previous sections, there are many
more configurable options in a dataset resource.
As an example, to publish a dataset in the
gallery and set its price you could use

.. code-block:: bash

    {"private": false, "price": 120.4}

Similarly, you might want to add fields to your existing dataset by combining
some of its fields or simply tagging their rows. Using BigMLer, you can set the
``--new-fields`` option to a file path that contains a JSON structure that
describes the fields you want to select or exclude from the original dataset,
or the ones you want to combine and
the `Flatline expression <https://github.com/bigmlcom/flatline>`_ to
combine them. This structure
must follow the rules of a specific languange described in the `Transformations
item of the developers
section <https://bigml.com/api/transformations>`_

.. code-block:: bash

    bigmler --dataset dataset/52b8a12037203f48bc00000a \
            --new-fields my_dir/generators.json

To see a simple example, should you want to include all the fields but the
one with id ``000001`` and add a new one with a label depending on whether
the value of the field ``sepal length`` is smaller than 1,
you would write in ``generators.json``

.. code-block:: bash

    {"all_but": ["000001"], "new_fields": [{"name": "new_field", "field": "(if (< (f \"sepal length\") 1) \"small\" \"big\")"}]}

Or, as another example, to tag the outliers of the same field one coud use

.. code-block:: bash

    {"new_fields": [{"name": "outlier?", "field": "(if (within-percentiles? \"sepal length\" 0.5 0.95) \"normal\" \"outlier\")"}]}

You can also export the contents of a generated dataset by using the
``--to-csv`` option. Thus,

.. code-block:: bash

    bigmler --dataset dataset/52b8a12037203f48bc00000a \
            --to-csv my_dataset.csv --no-model

will create a CSV file named ``my_dataset.csv`` in the default directory
created by BigMLer to place the command output files. If no file name is given,
the file will be named after the dataset id.

A dataset can also be generated as the union of several datasets using the
flag ``--multi-dataset``. The datasets will be read from a file specified
in the ``--datasets`` option and the file must contain one dataset id per line.


.. code-block:: bash

    bigmler --datasets my_datasets --multi-dataset --no-model

This syntax is used when all the datasets in the ``my_datasets`` file share
a common field structre, so the correspondence of the fields of all the
datasets is straight forward. In the general case, the multi-dataset will
inherit the field structure of the first component dataset.
If you want to build a multi-dataset with
datasets whose fields share not the same column disposition, you can specify
which fields are correlated to the ones of the first dataset
by mapping the fields of the rest of datasets to them.
The option ``--multi-dataset-attributes`` can point to a JSON
file that contains such a map. The command line syntax would then be

.. code-block:: bash

    bigmler --datasets my_datasets --multi-dataset \
            --multi-dataset-attributes my_fields_map.json \
            --no-model

and for a simple case where the second dataset had flipped the first and second
fields with respect to the first one, the file would read

.. code-block::

    {"fields_maps": {"dataset/53330bce37203f222e00004b": {"000000": "000001",
                                                          "000001": "000000"}}
    }

where ``dataset/53330bce37203f222e00004b`` would be the id of the
second dataset in the multi-dataset.


Model Weights
-------------

To deal with imbalanced datasets, BigMLer offers three options: ``--balance``,
``--weight-field`` and ``--objective-weights``.

For classification models, the ``--balance`` flag will cause all the classes
in the dataset to
contribute evenly. A weight will be assigned automatically to each
instance. This weight is
inversely proportional to the number of instances in the class it belongs to,
in order to ensure even distribution for the classes.

You can also use a field in the dataset that contains the weight you would like
to use for each instance. Using the ``--weight-field`` option followed by
the field name or column number will cause BigMLer to use its data as instance
weight. This is valid for both regression and classification models.

The ``--objective-weights`` option is used in classification models to
transmit to BigMLer what weight is assigned to each class. The option accepts
a path to a CSV file that should contain the ``class``,``weight`` values one
per row

.. code-block:: bash

    bigmler --dataset dataset/52b8a12037203f48bc00000a \
            --objective-weights my_weights.csv

where the ``my_weights.csv`` file could read

.. code-block:: bash

    Iris-setosa,5
    Iris-versicolor,3

so that BigMLer would associate a weight of ``5`` to the ``Iris-setosa``
class and ``3`` to the ``Iris-versicolor`` class. For additional classes
in the model, like ``Iris-virginica`` in the previous example,
weight ``1`` is used as default. All specified weights must be non-negative
numbers (with either integer or real values) and at least one of them must
be non-zero.

Predictions' missing strategy
-----------------------------

Sometimes the available data lacks some of the features our models use to
predict. In these occasions, BigML offers two different ways of handling
input data with missing values, that is to say, the missing strategy. When the
path to the prediction reaches a split point that checks
the value of a field which is missing in your input data, using the
``last prediction`` strategy the final prediction will be the prediction for
the last node in the path before that point, and using the ``proportional``
strategy it will be a weighted average of all the predictions for the final
nodes reached considering that both branches of the split are possible.

BigMLer adds the ``--missing-strategy`` option, that can be set either to
``last`` or ``proportional`` to choose the behavior in such cases. Last
prediction is the one used when this option is not used.

.. code-block:: bash

    bigmler --model model/52b8a12037203f48bc00001a \
            --missing-strategy proportional --test my_test.csv


Models with missing splits
--------------------------

Another configuration argument that can change models when
the training data has instances with missing values in some of its features
is ``--missing-splits``. By setting this flag, the model building algorithm
will be able to include the instances
that have missing values for the field used to split the data in each node
in one of the stemming branches. This will, obviously, affect also the
predictions given by the model for input data with missing values. Here's an
example to build
a model using missing-splits and predict with it.

.. code-block:: bash

    bigmler --dataset dataset/52b8a12037203f48bc00023b \
            --missing-splits --test my_test.csv


Fitering Sources
----------------

Imagine that you have create a new source and that you want to create a
specific dataset filtering the rows of the source that only meet certain
criteria.  You can do that using a JSON expresion as follows

.. code-block:: bash

    bigmler --source source/50a2bb64035d0706db0006cc --json-filter filter.json

where ``filter.json`` is a file containg a expression like this

.. code-block:: bash

    ["<", 7.00, ["field", "000000"]]

or a LISP expression as follows

.. code-block:: bash

    bigmler --source source/50a2bb64035d0706db0006cc --lisp-filter filter.lisp

where ``filter.lisp`` is a file containing a expression like this

.. code-block:: bash

    (< 7.00 (field "sepal length"))

For more details, see the BigML's API documentation on
`filtering rows <https://bigml.com/api/datasets#d_filteringrows>`_.


High number of Categories
-------------------------

In BigML there's a limit in the number of categories of a categorical
objective field. This limit is set to ensure the quality of the resulting
models. This may become a restriction when dealing with
categorical objective fields with a high number of categories. To cope with
these cases, BigMLer offers the --max-categories option. Setting to a number
lower than the mentioned limit, the existing categories will be organized in
subsets of that size. Then the original dataset will be copied many times, one
per subset, and its objective field will only keep the categories belonging to
each subset plus a generic ``***** other *****`` category that will summarize
the rest of categories. Then a model will be created from each dataset and
the test data will be run through them to generate partial predictions. The
final prediction will be extracted by choosing the class with highest
confidence from the distributions obtained for
each model's prediction ignoring the ``***** other ******`` generic category.
For instance, to use the same ``iris.csv`` example, you could do

.. code-block:: bash

    bigmler --train data/iris.csv --max-categories 1 \
            --test data/test_iris.csv --objective species

This command would generate a source and dataset object, as usual, but then,
as the total number of categories is three and --max-categories is set to 1,
three more datasets will be created, one per each category. After generating
the corresponding models, the test data will be run through them and their
predictions combined to obtain the final predictions file. The same procedure
would be applied if starting from a preexisting source or dataset using the
``--source`` or ``--dataset`` options. Please note that the ``--objective``
flag is mandatory in this case to ensure that the right categorical field
is selected as objective field.

``--method`` option accepts a new ``combine`` value to use such kind of
combination. You can use it if you need to create a new group of predictions
based on the same models produced in the first example. Filling the path to the
model ids file

.. code-block:: bash

    bigmler --models my_dir/models --method combine \
            --test data/new_test.csv

the new predictions will be created. Also, you could use the set of datasets
created in the first case as starting point. Their ids are stored in a
``dataset_parts`` file that can be found in the output location

.. code-block:: bash

    bigmler --dataset my_dir/dataset_parts --method combine \
            --test data/test.csv

This command would cause a new set of models, one per dataset, to be generated
and their predictions would be combined in a final predictions file.


Additional Features
===================

Using local models to predict
-----------------------------

Most of the previously described commands need the remote resources to
be downloaded to work. For instance, when you want to create a new
model from an existing dataset, BigMLer is going to download the dataset
JSON structure to extract the fields and objective field information,
and only then ask for the model creation. As mentioned,
the ``--store`` flag forces BigMLer to store the downloaded JSON
structures in local files inside your output directory. If you use that flag
when building a model with BigMLer, then the model is stored in your computer.
This model file contains all the information you need in order to make
new predictions, so you can use the
``--model-file`` option to set the path to this file and predict
the value of your objective field for new input data with no reference at all
to your remote resources. You could even delete the original remote model and
work exclusively with the locally downloaded file

.. code-block:: bash

    bigmler --model-file my_dir/model_532db2b637203f3f1a000136 \
            --test data/test_iris.csv

The same is available for clusters

.. code-block:: bash

    bigmler cluster --cluster-file my_dir/cluster_532db2b637203f3f1a000348 \
                    --test data/test_diabetes.csv

anomaly detectors

.. code-block:: bash

    bigmler anomaly --anomaly-file my_dir/anomaly_532db2b637203f3f1a00053a \
                    --test data/test_kdd.csv

logistic regressions

.. code-block:: bash

    bigmler logistic-regression \
            --logistic-file my_dir/logisticregression_532db2b637203f3f1a00053a \
            --test data/test_diabetes.csv

linear regressions

.. code-block:: bash

    bigmler linear-regression \
            --linear-file my_dir/linearregression_532db2b637203f3f1a00053a \
            --test data/test_diabetes.csv

topic models

.. code-block:: bash

    bigmler topic-model \
            --topic-model-file my_dir/topicmodel_532db2b637203f3f1a00053a \
            --test data/test_spam.csv

time series

.. code-block:: bash

    bigmler time-series \
            --time-series-file my_dir/timeseries_532db2b637203f5f1a00053a \
            --horizon 20


deepnets

.. code-block:: bash

    bigmler deepnets --deepnet-file my_dir/deepnet_532db2b637203f5f1a00053a \
                     --test data/test_diabetes.csv

Even for ensembles

.. code-block:: bash

    bigmler --ensemble-file my_dir/ensemble_532db2b637203f3f1a00053b \
            --test data/test_iris.csv

In this case, the models included in the ensemble are expected to be
stored also in
the same directory where the local file for the ensemble is. They are
downloaded otherwise.

Resuming Previous Commands
--------------------------

Network connections failures or other external causes can break the BigMLer
command process. To resume a command ended by an unexpected event you
can issue

.. code-block:: bash

    bigmler --resume

BigMLer keeps track of each command you issue in a ``.bigmler`` file and of
the output directory in ``.bigmler_dir_stack`` of your working directory.
Then ``--resume`` will recover the last issued command and try to continue
work from the point it was stopped. There's also a ``--stack-level`` flag

.. code-block:: bash

    bigmler --resume --stack-level 1

to allow resuming a previous command in the stack. In the example, the one
before the last.


Building reports
----------------

The resources generated in the execution of a BigMLer command are listed in
the standard output by default,
but they can be summarized as well in a ``Gazibit`` format.
`Gazibit <http://gazibit.com/>`_ is a platform where you can create interactive
presentations in a
flexible and dynamic way. Using BigMLer's ``--reports gazibit`` option you'll
be able to generate a ``Gazibit`` summary report of your newly created
resources. In
case you use also the ``--shared`` flag, a second template will be generated
where the links for the shared resources will be used. Both reports will be
stored in the ``reports`` subdirectory of your output directory, where all of
the files generated by the BigMLer command are. Thus,



.. code-block:: bash

    bigmler --train data/iris.csv --reports gazibit --shared \
            --output-dir my_dir

will generate two files: ``gazibit.json`` and ``gazibit_shared.json`` in a
``reports`` subdirectory of your ``my_dir`` directory. In case you provide
your ``Gazibit token`` in the ``GAZIBIT_TOKEN`` environment variable, they will
also be uploaded to your account in ``Gazibit``. Upload can be avoided, by
using the ``--no-upload`` flag.


User Chosen Defaults
--------------------

BigMLer will look for ``bigmler.ini`` file in the working directory where
users can personalize the default values they like for the most relevant flags.
The options should be written in a config style, e.g.

.. code-block:: bash


    [BigMLer]
    dev = true
    resources_log = ./my_log.log

as you can see, under a ``[BigMLer]`` section the file should contain one line
per option. Dashes in flags are transformed to undescores in options.
The example would keep development mode on and would log all created
resources to ``my_log.log`` for any new ``bigmler`` command issued under the
same working directory if none of the related flags are set.

Naturally, the default value options given in this file will be overriden by
the corresponding flag value in the present command. To follow the previous
example, if you use

.. code-block:: bash

    bigmler --train data/iris.csv --resources-log ./another_log.log

in the same working directory, the value of the flag will be preeminent and
resources will be logged in ``another_log.log``. For boolean-valued flags,
such as ``--replacement`` itself, you'll need to use the associated negative
flags to
overide the default behaviour. That is, following the former example if you
want to avoid storing the downloaded resource JSON information,
you should use the ``--no-store`` flag.

.. code-block:: bash

    bigmler --train data/iris.csv --no-store

The set of negative flags is:


==============================  ===============================================
``--no-debug``                  as opposed to ``--debug``
``--no-train-header``           as opposed to ``--train-header``
``--no-test-header``            as opposed to ``--test-header``
``--local``                     as opposed to ``--remote``
``--no-replacement``            as opposed to ``--replacement``
``--no-randomize``              as opposed to ``--randomize``
``--no-no-tag``                 as opposed to ``--no-tag``
``--no-public-dataset``         as opposed to ``--public-dataset``
``--no-black-box``              as opposed to ``--black-box``
``--no-white-box``              as opposed to ``--white-box``
``--no-progress-bar``           as opposed to ``--progress-bar``
``--no-no-dataset``             as opposed to ``--no-dataset``
``--no-no-model``               as opposed to ``--no-model``
``--no-clear-logs``             as opposed to ``--clear-logs``
``--no-store``                  as opposed to ``--store``
``--no-multi-label``            as opposed to ``--multi-label``
``--no-prediction-header``      as opposed to ``--prediction-header``
``--batch``                     as opposed to ``--no-batch``
``--no-balance``                as opposed to ``--balance``
``--no-multi-dataset``          as opposed to ``--multi-dataset``
``--unshared``                  as opposed to ``--shared``
``--upload``                    as opposed to ``--no-upload``
``--fast``                      as opposed to ``--no-fast``
``--no-no-csv``                 as opposed to ``--no-csv``
``--no-median``                 as opposed to ``--median``
``--no-score``                  as opposed to ``--score``
``--server``                    as opposed to ``--no-server``
==============================  ===============================================


BigMLer encodings and locale
============================

All data uploaded to BigML (and used in BigMLer) is expected to be ``UTF-8``
encoded. The data itself, besides its encoding,
can contain information in different languages. English is the default
language, but that can be set to a different value using --locale. Setting
the language determines the conventions for parsing number literals
(decimal separator), dates, etc.

Also, BigMLer will write information to your console and local files.
Most Operating Systems will also accept ``UTF-8`` output, which is used
by default. However, Windows systems may need a different encoding.
We allow the user to specify this enconding
as an environment variable ``BIGML_SYS_ENCODING``. In this case, BigMLer will
try to guess the system encoding when absent.


Optional Arguments
==================

General configuration
---------------------

==============   ==============================================================
``--username``   BigML's username. If left unspecified, it will default to the
                 values of the ``BIGML_USERNAME`` environment variable
``--api-key``    BigML's api_key. If left unspecified, it will default to the
                 values of the ``BIGML_API_KEY`` environment variable
``--debug``      Activates debug level and shows log info for each https
                 request
==============   ==============================================================

Basic Functionality
-------------------

===========================================================   =================
``--train`` *TRAINING_SET*                                    Full path to a
                                                              training set.
                                                              It can be a
                                                              remote URL to
                                                              a (gzipped or
                                                              compressed) CSV
                                                              file. The
                                                              protocol schemes
                                                              can be http,
                                                              https, s3, azure,
                                                              odata
``--test`` *TEST_SET*                                         Full path to a
                                                              test set. A file
                                                              containing
                                                              the data that
                                                              you want to input
                                                              to generate
                                                              predictions
``--objective`` *OBJECTIVE_FIELD*                             The column number
                                                              of the Objective
                                                              Field
                                                              (the field that
                                                              you want to
                                                              predict) or its
                                                              name
``--output`` *PREDICTIONS*                                    Full path to a
                                                              file to save
                                                              predictions.
                                                              If unspecified,
                                                              it will default
                                                              to an
                                                              auto-generated
                                                              file created by
                                                              BigMLer. It
                                                              overrides
                                                              ``--output-dir``
``--output-dir`` *DIRECTORY*                                  Directory where
                                                              all the session
                                                              files
                                                              will be stored.
                                                              It is overriden
                                                              by ``--output``
``--method`` *METHOD*                                         Prediction method
                                                              used:
                                                              ``plurality``,
                                                              ``"confidence
                                                              weighted"``,
                                                              ``"probability
                                                              weighted"``,
                                                              ``threshold``
                                                              or ``combined``
``--pruning`` *PRUNING_TYPE*                                  The pruning
                                                              applied in
                                                              building the
                                                              model.
                                                              It's allowed
                                                              values are
                                                              ``smart``,
                                                              ``statistical``
                                                              and
                                                              ``no-pruning``
                                                              The default value
                                                              is ``smart``
``--missing-strategy`` *STRATEGY*                             The strategy
                                                              applied
                                                              predicting
                                                              when a
                                                              missing value is
                                                              found in a model
                                                              split.
                                                              It's allowed
                                                              values are
                                                              ``last`` or
                                                              ``proportional``.
                                                              The default value
                                                              is ``last``
``--missing-splits``                                          Turns on the
                                                              missing_splits
                                                              flag in model
                                                              creation. The
                                                              model splits can
                                                              include
                                                              in one of its
                                                              branches the data
                                                              with
                                                              missing values
``--evaluate``                                                Turns on
                                                              evaluation mode
``--resume``                                                  Retries command
                                                              execution
``--stack-level`` *LEVEL*                                     Level of the
                                                              retried command
                                                              in the stack
``--cross-validation-rate`` *RATE*                            Fraction of the
                                                              training data
                                                              held
                                                              out for
                                                              Monte-Carlo
                                                              cross-validation
``--number-of-evaluations`` *NUMBER_OF_EVALUATIONS*           Number of runs
                                                              that will be
                                                              used in
                                                              cross-validation
``--max-parallel-evaluations`` *MAX_PARALLEL_EVALUATIONS*     Maximum number of
                                                              evaluations
                                                              to create in
                                                              parallel
``--project`` *PROJECT_NAME*                                  Project name for
                                                              the project to be
                                                              associated to
                                                              newly created
                                                              sources
``--project-id`` *PROJECT_ID*                                 Project id for
                                                              the project to be
                                                              associated to
                                                              newly created
                                                              sources
``--org-project`` *PROJECT_ID*                                Project id for
                                                              the project of an
                                                              Organization
``--no-csv``                                                  Causes the output
                                                              of a batch
                                                              prediction,
                                                              batch centroid or
                                                              batch anomaly
                                                              score
                                                              not to be
                                                              downloaded as a
                                                              CSV file
``--to-dataset``                                              Causes the output
                                                              of a batch
                                                              prediction,
                                                              batch centroid or
                                                              batch anomaly
                                                              score
                                                              to be stored
                                                              remotely as a new
                                                              dataset
``--median``                                                  Predictions for
                                                              single models are
                                                              returned
                                                              based on the
                                                              median of the
                                                              distribution
                                                              in the predicted
                                                              node
===========================================================   =================

Content
-------

=============================== ===============================================
``--name`` *NAME*               Name for the resources in BigML.
``--category`` *CATEGORY*       Category code. See
                                `full list <https://bigml.com/api/sources#s_categories>`_.
``--description`` *DESCRIPTION* Path to a file with a description in plain text
                                or markdown
``--tag`` *TAG*                 Tag to later retrieve new resources
``--no-tag``                    Puts BigMLer default tag if no other tag is
                                given
=============================== ===============================================

Data Configuration
------------------

========================================= =====================================
``--no-train-header``                     The train set file hasn't a header
``--no-test-header``                      The test set file hasn't a header
``--field-attributes`` *PATH*             Path to a file describing field
                                          attributes
                                          One definition per line
                                          (e.g., 0,'Last Name')
``--types`` *PATH*                        Path to a file describing field
                                          types.
                                          One definition per line
                                          (e.g., 0, 'numeric')
``--test-field-attributes`` *PATH*        Path to a file describing test field
                                          attributes. One definition per line
                                          (e.g., 0,'Last Name')
``--test-types`` *PATH*                   Path to a file describing test field
                                          types.
                                          One definition per line
                                          (e.g., 0, 'numeric')
``--dataset-fields`` *DATASET_FIELDS*     Comma-separated list of field column
                                          numbers to include in the dataset
``--model-fields`` *MODEL_FIELDS*         Comma-separated list of input fields
                                          (predictors) to create the model
``--source-attributes`` *PATH*            Path to a file containing a JSON
                                          expression
                                          with attributes to be used as
                                          arguments (any of the updatable
                                          attributes described in the
                                          `developers section <https://bigml.com/api/sources#sr_source_properties>`_ )
                                          in create source calls
``--dataset-attributes`` *PATH*           Path to a file containing a JSON
                                          expression
                                          with attributes to be used as
                                          arguments (any of the updatable
                                          attributes described in the
                                          `developers section <https://bigml.com/api/datasets#ds_dataset_properties>`_ )
                                          in create dataset calls
``--model-attributes`` *PATH*             Path to a file containing a JSON
                                          expression
                                          with attributes to be used as
                                          arguments (any of the updatable
                                          attributes described in the
                                          `developers section <https://bigml.com/api/models#md_model_properties>`_ )
                                          in create model calls
``--ensemble-attributes`` *PATH*          Path to a file containing a JSON
                                          expression
                                          with attributes to be used as
                                          arguments (any of the updatable
                                          attributes described in the
                                          `developers section <https://bigml.com/api/ensembles#es_ensemble_properties>`_ )
                                          in create ensemble calls
``--evaluation-attributes`` *PATH*        Path to a file containing a JSON
                                          expression
                                          with attributes to be used as
                                          arguments (any of the updatable
                                          attributes described in the
                                          `developers section <https://bigml.com/api/evaluations#ev_evaluation_properties>`_ )
                                          in create evaluation calls
``--batch-prediction-attributes`` *PATH*  Path to a file containing a JSON
                                          expression
                                          with attributes to be used as
                                          arguments (any of the updatable
                                          attributes described in the
                                          `developers section <https://bigml.com/api/batch_predictions#bp_batch_prediction_properties>`_ )
                                          in create batch prediction calls
``--json-filter`` *PATH*                  Path to a file containing a JSON
                                          expression
                                          to filter the source
``--lisp-filter`` *PATH*                  Path to a file containing a LISP
                                          expression
                                          to filter the source
``--locale`` *LOCALE*                     Locale code string
``--fields-map`` *PATH*                   Path to a file containing the dataset
                                          to
                                          model fields map for evaluation
``--test-separator`` *SEPARATOR*          Character used as test data field
                                          separator
``--prediction-header``                   Include a headers row in the
                                          prediction
                                          file
``--prediction-fields`` *TEST_FIELDS*     Comma-separated list of fields of the
                                          test
                                          file to be included in the
                                          prediction file
``--max-categories`` *CATEGORIES_NUMBER*  Sets the maximum number of
                                          categories that
                                          will be used in a dataset. When more
                                          categories are found, new datasets
                                          are
                                          generated to analize the remaining
                                          categories
``--new-fields`` *PATH*                   Path to a file containing a JSON
                                          expression
                                          used to generate a new dataset with
                                          new
                                          fields created via `Flatline <https://github.com/bigmlcom/flatline>`
                                          by combining or setting their values
``--node-threshold``                      Maximum number or nodes to grow the
                                          tree with
``--balance``                             Automatically balance data to treat
                                          all classes evenly
``--weight-field`` *FIELD*                Field name or column number that
                                          contains
                                          the weights to be used for each
                                          instance
``--shared``                              Creates a secret link for every
                                          dataset, model or evaluation used
                                          in the
                                          command
``--reports``                             Report formats: "gazibit"
``--no-upload``                           Disables reports upload
``--dataset-off``                         Sets the evaluation mode that uses
                                          the list of test datasets and
                                          extracts
                                          one each time to test the model built
                                          with the rest of them (k-fold
                                          cross-validation)
``--args-separator``                      Character used as separator in
                                          multi-valued
                                          arguments (default is comma)
``--no-missing-splits``                   Turns off the missing_splits flag in
                                          model
                                          creation.
========================================= =====================================

Remote Resources
----------------

================================= =============================================
``--source`` *SOURCE*             BigML source Id
``--dataset`` *DATASET*           BigML dataset Id
``--datasets`` *PATH*             Path to a file containing a dataset Id
``--model`` *MODEL*               BigML model Id
``--models`` *PATH*               Path to a file containing model/ids. One
                                  model per
                                  line (e.g., model/4f824203ce80053)
``--ensemble`` *ENSEMBLE*         BigML ensemble Id
``--ensembles`` *PATH*            Path to a file containing ensembles Ids
``--test-source`` *SOURCE*        BigML test source Id (only for remote
                                  predictions)
``--test-dataset`` *DATASET*      BigML test dataset Id (only for remote
                                  predictions)
``--test-datasets`` *PATH*        Path to the file that contains datasets ids
                                  used
                                  in evaluations, one id per line.
``--source`` *SOURCE*             BigML source Id
``--dataset`` *DATASET*           BigML dataset Id
``--remote``                      Computes predictions remotely (in batch mode
                                  by default)
``--no-batch``                    Remote predictions are computed individually
``--no-fast``                     Ensemble's local predictions are computed
                                  storing the predictions of each model in
                                  a separate local file before combining them
                                  (the default is --fast, that keeps in memory
                                  each model's prediction)
``--model-tag`` *MODEL_TAG*       Retrieve models that were tagged with tag
``--ensemble-tag`` *ENSEMBLE_TAG* Retrieve ensembles that were tagged with tag
================================= =============================================


Ensembles
---------

================================================= =============================
``--number-of-models`` *NUMBER_OF_MODELS*         Number of models to create
``--sample-rate`` *SAMPLE_RATE*                   Sample rate to use (a float
                                                  between
                                                  0.01 and 1)
``--replacement``                                 Use replacement when sampling
``--max-parallel-models`` *MAX_PARALLEL_MODELS*   Max number of models to
                                                  create in parallel
``--max-batch-models`` *MAX_BATCH_MODELS*         Max number of local models
                                                  to be
                                                  predicted from in parallel.
                                                  For
                                                  ensembles with a number of
                                                  models
                                                  over
                                                  it, predictions are stored in
                                                  files as
                                                  they are computed and
                                                  retrived and
                                                  combined eventually
``--randomize``                                   Use a random set of fields to
                                                  split on
``--combine-votes`` *LIST_OF_DIRS*                Combines the votes of models
                                                  generated
                                                  in a list of directories
``--ensemble-sample-rate`` *RATE*                 Ensemble sampling rate for
                                                  bagging
``--ensemble-sample-seed`` *SEED*                 Value used as seed in
                                                  ensembles random selections
``--ensemble-sample-no-replacement``              Don't use replacement when
                                                  bagging
``--boosting``                                    Create a boosted ensemble
``--boosting-iterations`` *ITERATIONS*            Maximum number of iterations
                                                  used in boosted ensembles.
``--early-holdout`` *HOLDOUT*                     The portion of the dataset
                                                  that will be held out for
                                                  testing at the end of every
                                                  iteration in boosted
                                                  ensembles (between 0 and 1)
``--no-early-out-of-bag``                         Causes the out of bag samples
                                                  not to be tested after
                                                  every iteration in boosted
                                                  ensembles.
``--learning-rate`` *RATE*                        It controls how aggressively
                                                  the boosting algorithm
                                                  will fit the data in boosted
                                                  ensembles (between 0 and 1)
``--no-step-out-of-bag``                          Causes the out of bag samples
                                                  not to be tested after
                                                  every iteration to choose the
                                                  gradient step size
                                                  in boosted ensembles.
================================================= =============================


If you are not choosing to create an ensemble,
make sure that you tag your models conveniently so that you can
then retrieve them later to generate predictions.


Public Resources
----------------

======================== ======================================================
``--public-dataset``     Makes newly created dataset public
``--black-box``          Makes newly created model a public black-box
``--white-box``          Makes newly created model a public white-box
``--model-price``        Sets the price for a public model
``--dataset-price``      Sets the price for a public dataset
``--cpp``                Sets the credits consumed by prediction
======================== ======================================================

Notice that datasets and models will be made public without assigning any price
to them.

Local Resources
---------------

==========================   ==================================================
``--model-file`` *PATH*      Path to a JSON file containing the model info
``--ensemble-file`` *PATH*   Path to a JSON file containing the ensemble info
==========================   ==================================================


Fancy Options
-------------

================================= =============================================
``--no-dataset``                  Does not create a model. BigMLer will only
                                  create a source
``--no-model``                    Does not create a model. BigMLer will only
                                  create a dataset
``--resources-log`` *LOG_FILE*    Keeps a log of the resources generated in
                                  each command
``--version``                     Shows the version number
``--verbosity`` *LEVEL*           Turns on (1) or off (0) the verbosity.
``--clear-logs``                  Clears the ``.bigmler``,
                                  ``.bigmler_dir_stack``,
                                  ``.bigmler_dirs`` and user log file given in
                                  ``--resources-log`` (if any)
``--store``                       Stores every created or retrieved resource in
                                  your output directory
================================= =============================================
