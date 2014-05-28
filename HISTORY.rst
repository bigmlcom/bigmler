.. :changelog:

History
-------

1.8.9 (2014-05-28)
~~~~~~~~~~~~~~~~~~

- Fixing bug when utf8 characters were used in command lines.

1.8.8 (2014-05-27)
~~~~~~~~~~~~~~~~~~

- Adding the --balance flag to the analyze subcommand.
- Fixing bug for analyze. Some common flags allowed were not used.

1.8.7 (2014-05-23)
~~~~~~~~~~~~~~~~~~

- Fixing bug for analyze. User-given objective field was changed when using
  filtered datasets.

1.8.6 (2014-05-22)
~~~~~~~~~~~~~~~~~~

- Fixing bug for analyze. User-given objective field was not used.

1.8.5 (2014-05-19)
~~~~~~~~~~~~~~~~~~

- Docs update and test change to adapt to backend node threshold changes.

1.8.4 (2014-05-07)
~~~~~~~~~~~~~~~~~~

- Fixing bug in analyze --nodes. The default node steps could not be found.

1.8.3 (2014-05-06)
~~~~~~~~~~~~~~~~~~

- Setting dependency of new python bindings version 1.3.1.

1.8.2 (2014-05-06)
~~~~~~~~~~~~~~~~~~

- Fixing bug: --shared and --unshared should be considered only when set
  in the command line by the user. They were always updated, even when absent.
- Fixing bug: --remote predictions were not working when --model was used as
  training start point.

1.8.1 (2014-05-04)
~~~~~~~~~~~~~~~~~~

- Changing the Gazibit report for shared resources to include the model
  shared url in embedded format.
- Fixing bug: train and tests data could not be read from stdin.

1.8.0 (2014-04-29)
~~~~~~~~~~~~~~~~~~

- Adding the ``analyze`` subcommand. The subcommand presents new features,
  such as: 

    ``--cross-validation`` that performs k-fold cross-validation,
    ``--features`` that selects the best features to increase accuracy
    (or any other evaluation metric) using a smart search algorithm and
    ``--nodes`` that selects the node threshold that ensures best accuracy
    (or any other evaluation metric) in user defined range of nodes.

1.7.1 (2014-04-21)
~~~~~~~~~~~~~~~~~~

- Fixing bug: --no-upload flag was not really used.

1.7.0 (2014-04-20)
~~~~~~~~~~~~~~~~~~

- Adding the --reports option to generate Gazibit reports.

1.6.0 (2014-04-18)
~~~~~~~~~~~~~~~~~~

- Adding the --shared flag to share the created dataset, model and evaluation.

1.5.1 (2014-04-04)
~~~~~~~~~~~~~~~~~~

- Fixing bug for model building, when objective field was specified and
  no --max-category was present the user given objective was not used.
- Fixing bug: max-category data stored even when --max-category was not
  used.

1.5.0 (2014-03-24)
~~~~~~~~~~~~~~~~~~

- Adding --missing-strategy option to allow different prediction strategies
  when a missing value is found in a split field. Available for local
  predictions, batch predictions and evaluations.
- Adding new --delete options: --newer-than and --older-than to delete lists
  of resources according to their creation date.
- Adding --multi-dataset flag to generate a new dataset from a list of
  equally structured datasets.

1.4.7 (2014-03-14)
~~~~~~~~~~~~~~~~~~

- Bug fixing: resume from multi-label processing from dataset was not working.
- Bug fixing: max parallel resource creation check did not check that all the
              older tasks ended, only the last of the slot. This caused
              more tasks than permitted to be sent in parallel.
- Improving multi-label training data uploads by zipping the extended file and
  transforming booleans from True/False to 1/0.

1.4.6 (2014-02-21)
~~~~~~~~~~~~~~~~~~

- Bug fixing: dataset objective field is not updated each time --objective
  is used, but only if it differs from the existing objective.

1.4.5 (2014-02-04)
~~~~~~~~~~~~~~~~~~

- Storing the --max-categories info (its number and the chosen `other` label)
  in user_metadata.

1.4.4 (2014-02-03)
~~~~~~~~~~~~~~~~~~

- Fix when using the combined method in --max-categories models.
  The combination function now uses confidence to choose the predicted
  category.
- Allowing full content text fields to be also used as --max-categories
  objective fields.
- Fix solving objective issues when its column number is zero.

1.4.3 (2014-01-28)
~~~~~~~~~~~~~~~~~~

- Adding the --objective-weights option to point to a CSV file containing the
  weights assigned to each class.
- Adding the --label-aggregates option to create new aggregate fields on the
  multi label fields such as count, first or last.

1.4.2 (2014-01-24)
~~~~~~~~~~~~~~~~~~

- Fix in local random forests' predictions. Sometimes the fields used in all
  the models were not correctly retrieved and some predictions could be
  erroneus.

1.4.1 (2014-01-23)
~~~~~~~~~~~~~~~~~~

- Fix to allow the input data for multi-label predictions to be expanded.
- Fix to retrieve from the models definition info the labels that were
  given by the user in its creation in multi-label models. 

1.4.0 (2014-01-20)
~~~~~~~~~~~~~~~~~~

- Adding new --balance option to automatically balance all the classes evenly.
- Adding new --weight-field option to use the field contents as weights for
  the instances.

1.3.0 (2014-01-17)
~~~~~~~~~~~~~~~~~~

- Adding new --source-attributes, --ensemble-attributes,
  --evaluation-attributes and --batch-prediction-attributes options.
- Refactoring --multi-label resources to include its related info in 
  the user_metadata attribute.
- Refactoring the main routine.
- Adding --batch-prediction-tag for delete operations.

1.2.3 (2014-01-16)
~~~~~~~~~~~~~~~~~~

- Fix to transmit --training-separator when creating remote sources.

1.2.2 (2014-01-14)
~~~~~~~~~~~~~~~~~~

- Fix for multiple multi-label fields: headers did not match rows contents in
  some cases.

1.2.1 (2014-01-12)
~~~~~~~~~~~~~~~~~~

- Fix for datasets generated using the --new-fields option. The new dataset
  was not used in model generation.

1.2.0 (2014-01-09)
~~~~~~~~~~~~~~~~~~

- Adding --multi-label-fields to provide a comma-separated list of multi-label
  fields in a file.

1.1.0 (2014-01-08)
~~~~~~~~~~~~~~~~~~

- Fix for ensembles' local predictions when order is used in tie break.
- Fix for duplicated model ids in models file.
- Adding new --node-threshold option to allow node limit in models.
- Adding new --model-attributes option pointing to a JSON file containing
  model attributes for model creation.

1.0.1 (2014-01-06)
~~~~~~~~~~~~~~~~~~

- Fix for missing modules during installation.

1.0 (2014-01-02)
~~~~~~~~~~~~~~~~~~

- Adding the --max-categories option to handle datasets with a high number of
  categories.
- Adding the --method combine option to produce predictions with the sets
  of datasets generated using --max-categories option.
- Fixing problem with --max-categories when the categorical field is not
  a preferred field of the dataset.
- Changing the --datasets option behaviour: it points to a file where
  dataset ids are stored, one per line, and now it reads all of them to be
  used in model and ensemble creation.

0.7.2 (2013-12-20)
~~~~~~~~~~~~~~~~~~

- Adding confidence to predictions output in full format

0.7.1 (2013-12-19)
~~~~~~~~~~~~~~~~~~

- Bug fixing: multi-label predictions failed when the --ensembles option
  is used to provide the ensemble information

0.7.0 (2013-11-24)
~~~~~~~~~~~~~~~~~~

- Bug fixing: --dataset-price could not be set.
- Adding the threshold combination method to the local ensemble.

0.6.1 (2013-11-23)
~~~~~~~~~~~~~~~~~~

- Bug fixing: --model-fields option with absolute field names was not
  compatible with multi-label classification models.
- Changing resource type checking function.
- Bug fixing: evaluations did not use the given combination method.
- Bug fixing: evaluation of an ensemble had turned into evaluations of its
              models.
- Adding pruning to the ensemble creation configuration options

0.6.0 (2013-11-08)
~~~~~~~~~~~~~~~~~~

- Changing fields_map column order: previously mapped dataset column
  number to model column number, now maps model column number to
  dataset column number.
- Adding evaluations to multi-label models.
- Bug fixing: unicode characters greater than ascii-127 caused crash in
  multi-label classification

0.5.0 (2013-10-08)
~~~~~~~~~~~~~~~~~~

- Adapting to predictions issued by the high performance prediction server and
  the 0.9.0 version of the python bindings.
- Support for shared models using the same version on python bindings. 
- Support for different server names using environment variables.

0.4.1 (2013-10-02)
~~~~~~~~~~~~~~~~~~

- Adding ensembles' predictions for multi-label objective fields
- Bug fixing: in evaluation mode, evaluation for --dataset and
  --number-of-models > 1 did not select the 20% hold out instances to test the
  generated ensemble.

0.4.0 (2013-08-15)
~~~~~~~~~~~~~~~~~~

- Adding text analysis through the corresponding bindings

0.3.7 (2013-09-17)
~~~~~~~~~~~~~~~~~~

- Adding support for multi-label objective fields
- Adding --prediction-headers and --prediction-fields to improve
  --prediction-info formatting options for the predictions file
- Adding the ability to read --test input data from stdin
- Adding --seed option to generate different splits from a dataset

0.3.6 (2013-08-21)
~~~~~~~~~~~~~~~~~~

- Adding --test-separator flag

0.3.5 (2013-08-16)
~~~~~~~~~~~~~~~~~~

- Bug fixing: resume crash when remote predictions were not completed
- Bug fixing: Fields object for input data dict building lacked fields
- Bug fixing: test data was repeated in remote prediction function
- Bug fixing: Adding replacement=True as default for ensembles' creation

0.3.4 (2013-08-09)
~~~~~~~~~~~~~~~~~~

- Adding --max-parallel-evaluations flag
- Bug fixing: matching seeds in models and evaluations for cross validation

0.3.3 (2013-08-09)
~~~~~~~~~~~~~~~~~~
- Changing --model-fields and --dataset-fields flag to allow adding/removing
  fields with +/- prefix
- Refactoring local and remote prediction functions
- Adding 'full data' option to the --prediction-info flag to join test input
  data with prediction results in predictions file
- Fixing errors in documentation and adding install for windows info

0.3.2 (2013-07-04)
~~~~~~~~~~~~~~~~~~
- Adding new flag to control predictions file information
- Bug fixing: using default sample-rate in ensemble evaluations
- Adding standard deviation to evaluation measures in cross-validation
- Bug fixing: using only-model argument to download fields in models

0.3.1 (2013-05-14)
~~~~~~~~~~~~~~~~~~

- Adding delete for ensembles
- Creating ensembles when the number of models is greater than one
- Remote predictions using ensembles

0.3.0 (2013-04-30)
~~~~~~~~~~~~~~~~~~

- Adding cross-validation feature
- Using user locale to create new resources in BigML
- Adding --ensemble flag to use ensembles in predictions and evaluations

0.2.1 (2013-03-03)
~~~~~~~~~~~~~~~~~~

- Deep refactoring of main resources management
- Fixing bug in batch_predict for no headers test sets
- Fixing bug for wide dataset's models than need query-string to retrieve all fields
- Fixing bug in test asserts to catch subprocess raise
- Adding default missing tokens to models
- Adding stdin input for --train flag
- Fixing bug when reading descriptions in --field-attributes
- Refactoring to get status from api function
- Adding confidence to combined predictions

0.2.0 (2012-01-21)
~~~~~~~~~~~~~~~~~~
- Evaluations management
- console monitoring of process advance
- resume option
- user defaults
- Refactoring to improve readability

0.1.4 (2012-12-21)
~~~~~~~~~~~~~~~~~~

- Improved locale management.
- Adds progressive handling for large numbers of models.
- More options in field attributes update feature.
- New flag to combine local existing predictions.
- More methods in local predictions: plurality, confidence weighted.

0.1.3 (2012-12-06)
~~~~~~~~~~~~~~~~~~

- New flag for locale settings configuration.
- Filtering only finished resources.

0.1.2 (2012-12-06)
~~~~~~~~~~~~~~~~~~

- Fix to ensure windows compatibility.

0.1.1 (2012-11-07)
~~~~~~~~~~~~~~~~~~

- Initial release.
