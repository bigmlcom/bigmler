.. toctree::
   :maxdepth: 2
   :hidden:

Multi-labeled categories in training data
=========================================

Sometimes the information you want to predict is not a single category but a
set of complementary categories. In this case, training data is usually
presented as a row of features and an objective field that contains the
associated set of categories joined by some kind of delimiter. BigMLer can
also handle this scenario.

Let's say you have a simple file

.. code-block:: bash

    color,year,sex,class
    red,2000,male,"Student,Teenager"
    green,1990,female,"Student,Adult"
    red,1995,female,"Teenager,Adult"

with information about a group of people and we want to predict the ``class``
another person will fall into. As you can see, each record has more
than one ``class`` per person (for example, the first person is labeled as
being both a ``Student`` and a ``Teenager``) and they are all stored in the
``class`` field by concatenating all the applicable labels using ``,`` as
separator. Each of these labels is, 'per se', an objective to be predicted, and
that's what we can rely on BigMLer to do.

The simplest multi-label command in BigMLer is

.. code-block:: bash

    bigmler --multi-label --train data/tiny_multilabel.csv

First, it will analyze the training file to extract all the ``labels`` stored
in the objective field. Then, a new extended file will be generated
from it by adding a new field per label. Each generated field will contain
a boolean set to
``True`` if the associated label is in the objective field and ``False``
otherwise

.. code-block:: bash

    color,year,sex,class - Adult,class - Student,class - Teenager
    red,2000,male,False,True,True
    green,1990,female,True,True,False
    red,1995,female,True,False,True

This new file will be fed to BigML to build a ``source``, a ``dataset`` and
a set of ``models`` using four input fields: the first three fields as
input features and one of the label fields as objective. Thus, each
of the classes that label the training set can be predicted independently using
one of the models.

But, naturally, when predicting a multi-labeled field you expect to obtain
all the labels that qualify the input features at once, as you provide them in
the training data records. That's also what BigMLer does. The syntax to
predict using
multi-labeled training data sets is similar to the single labeled case

.. code-block:: bash

    bigmler --multi-label --train data/tiny_multilabel.csv \
            --test data/tiny_test_multilabel.csv

the main difference being that the ouput file ``predictions.csv`` will have
the following structure

.. code-block:: bash

    "Adult,Student","0.34237,0.20654"
    "Adult,Teenager","0.34237,0.34237"

where the first column contains the ``class`` prediction and the second one the
confidences for each label prediction. If the models predict ``True`` for
more than one label, the prediction is presented as a sequence of labels
(and their corresponding confidences) delimited by ``,``.

As you may have noted, BigMLer uses ``,`` both as default training data fields
separator and as label separator. You can change this behaviour by using the
``--training-separator``, ``--label-separator`` and ``--test-separator`` flags
to use different one-character separators

.. code-block:: bash

    bigmler --multi-label --train data/multilabel.tsv \
            --test data/test_multilabel.tsv --training-separator '\t' \
            --test-separator '\t' --label-separator ':'

This command would use the ``tab`` character as train and test data field
delimiter and ``:`` as label delimiter (the examples in the tests set use
``,`` as field delimiter and ':' as label separator).

You can also choose to restrict the prediction to a subset of labels using
the ``--labels`` flag. The flag should be set to a comma-separated list of
labels. Setting this flag can also reduce the processing time for the
training file, because BigMLer will rely on them to produce the extended
version of the training file. Be careful, though, to avoid typos in the labels
in this case, or no objective fields will be created. Following the previous
example

.. code-block:: bash

    bigmler --multi-label --train data/multilabel.csv \
            --test data/test_multilabel.csv --label-separator ':' \
            --labels Adult,Student

will limit the predictions to the ``Adult`` and ``Student`` classes, leaving
out the ``Teenager`` classification.

Multi-labeled predictions can also be computed using ensembles, one for each
label. To create an ensemble prediction, use the ``--number-of-models`` option
that will set the number of models in each ensemble

.. code-block:: bash

    bigmler --multi-label --train data/multilabel.csv \
            --number-of-models 20 --label-separator ':' \
            --test data/test_multilabel.csv

The ids of the ensembles will be stored in an ``ensembles`` file in the output
directory, and can be used in other predictions by setting the ``--ensembles``
option

.. code-block:: bash

    bigmler --multi-label --ensembles multilabel/ensembles \
            --test data/test_multilabel.csv

or you can retrieve all previously tagged ensembles with ``--ensemble-tag``

.. code-block:: bash

    bigmler --multi-label --ensemble-tag multilabel \
            --test data/test_multilabel.csv


Multi-labeled resources
=======================

The resources generated from a multi-labeled training data file can also be
recovered and used to generate more multi-labeled predictions. As in the
single-labeled case

.. code-block:: bash

    bigmler --multi-label --source source/522521bf37203f412f000100 \
            --test data/test_multilabel.csv

would generate a dataset and the corresponding set of models needed to create
a ``predictions.csv`` file that contains the multi-labeled predictions.

Similarly, starting from a previously created multi-labeled dataset

.. code-block:: bash

    bigmler --multi-label --dataset source/522521bf37203f412fac0135 \
            --test data/test_multilabel.csv --output multilabel/predictions.csv

creates a bunch of models, one per label, and predicts storing the results
of each operation in the ``multilabel`` directory, and finally

.. code-block:: bash

    bigmler --multi-label --models multilabel/models \
            --test data/test_multilabel.csv

will retrieve the set of models created in the last example and use them in new
predictions. In addition, for these three cases you can restrict the labels
to predict to a subset of the complete list available in the original objective
field. The ``--labels`` option can be set to a comma-separated list of the
selected labels in order to do so.

The ``--model-tag`` can be used as well to retrieve multi-labeled
models and predict with them

.. code-block:: bash

    bigmler --multi-label --model-tag my_multilabel \
            --test data/test_multilabel.csv

Finally, BigMLer is also able to handle training files with more than one
multi-labeled field. Using the ``--multi-label-fields`` option you can
settle the fields that will be expanded as containing multiple labels
in the generated source and dataset.

.. code-block:: bash

    bigmler --multi-label --multi-label-fields class,type \
            --train data/multilabel_multi.csv --objective class

This command creates a source (and its corresponding dataset)
where both the ``class`` and ``type`` fields have been analysed
to create a new field per label. Then the ``--objective`` option sets ``class``
to be the objective field and only the models needed to predict this field
are created. You could also create a new multi-label prediction for another
multi-label field, ``type`` in this case, by issuing a new BigMLer command
that uses the previously generated dataset as starting point

.. code-block:: bash

    bigmler --multi-label --dataset dataset/52cafddb035d07269000075b \
            --objective type

This would generate the models needed to predict ``type``. It's important to
remark that the models used to predict ``class`` in the first example will
use the rest of fields (including ``type`` as well as the ones generated
by expanding it) to build the prediction tree. If you don't want this
fields to be used in the model construction, you can set the ``--model-fields``
option to exclude them. For instance, if ``type`` has two labels, ``label1``
and ``label2``, then excluding them from the models that predict
``class`` could be achieved using

.. code-block:: bash

    bigmler --multi-label --dataset dataset/52cafddb035d07269000075b \
            --objective class
            --model-fields=' -type,-type - label1,-type - label2'

You can also generate new fields applying aggregation functions such as
``count``, ``first`` or ``last`` on the labels of the multi label fields. The
option ``--label-aggregates`` can be set to a comma-separated list of these
functions and a new column per multi label field and aggregation function
will be added to your source

.. code-block:: bash

    bigmler --multi-label --train data/multilabel.csv \
            --label-separator ':' --label-aggregates count,last \
            --objective class

will generate ``class - count`` and ``class - last`` in addition to the set
of per label fields.


Multi-label evaluations
-----------------------

Multi-label predictions are computed using a set of binary models
(or ensembles), one for
each label to predict. Each model can be evaluated to check its
performance. In order to do so, you can mimic the commands explained in the
``evaluations`` section for the single-label models and ensembles. Starting
from a local CSV file

.. code-block:: bash

    bigmler --multi-label --train data/multilabel.csv \
            --label-separator ":" --evaluate

will build the source, dataset and model objects for you using a
random 80% portion of data in your training file. After that, the remaining 20%
of the data will be run through each of the models to obtain an evaluation of
the corresponding model. BigMLer retrieves all evaluations and saves
them locally in json and txt format. They are named using the objective field
name and the value of the label that they refer to. Finally, it averages the
results obtained in all the evaluations to generate a mean evaluation stored
in the ``evaluation.txt`` and ``evaluation.json`` files. As an example,
if your objective field name is ``class`` and the labels it contains are
``Adult,Student``, the generated files will be

.. code-block:: bash

Generated files:

 MonNov0413_201326
  - evaluations
  - extended_multilabel.csv
  - source
  - evaluation_class_student.txt
  - models
  - evaluation_class_adult.json
  - dataset
  - evaluation.json
  - evaluation.txt
  - evaluation_class_student.json
  - bigmler_sessions
  - evaluation_class_adult.txt

You can use the same procedure with a previously
existing multi-label source or dataset

.. code-block:: bash

    bigmler --multi-label --source source/50a1e520eabcb404cd0000d1 \
            --evaluate
    bigmler --multi-label --dataset dataset/50a1f441035d0706d9000371 \
            --evaluate

Finally, you can also evaluate a preexisting set of models or ensembles
using a separate set of
data stored in a file or a previous dataset

.. code-block:: bash

    bigmler --multi-label --models MonNov0413_201326/models \
            --test data/test_multilabel.csv --evaluate
    bigmler --multi-label --ensembles MonNov0413_201328/ensembles \
            --dataset dataset/50a1f441035d0706d9000371 --evaluate


Multi-label Options
^^^^^^^^^^^^^^^^^^^

======================================= =======================================
``--multi-label``                       Use multiple labels in the objective
                                        field
``--labels``                            Comma-separated list of labels used
``--training-separator`` *SEPARATOR*    Character used as field separator in
                                        train data field
``--label-separator`` *SEPARATOR*       Character used as label separator in
                                        the multi-labeled objective field
======================================= =======================================
