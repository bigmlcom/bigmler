.. :changelog:

History
-------

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
