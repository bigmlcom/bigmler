.. :changelog:

History
-------

0.3.7 (2013-08-31)
~~~~~~~~~~~~~~~~~~

- Adding support for multi-label objective fields

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
