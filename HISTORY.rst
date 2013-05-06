.. :changelog:

History
-------

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
