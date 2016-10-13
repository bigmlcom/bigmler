.. :changelog:

History
-------

3.8.4 (2016-10-13)
~~~~~~~~~~~~~~~~~~

- Fixing bug in bigmler package. Libraries where created more than once.
- Fixing bug in bigmler analyze --features when adding batch prediction.
- Improving bigmler delete when deleting projects and executions. Deleting in
  two steps: first the projects and executions and then the remaining
  resources.

3.8.3 (2016-09-30)
~~~~~~~~~~~~~~~~~~

- Fixing bug in logistic regression evaluation.
- Adding --balance-fields flag to bigmler logistic-regression.
- Refactoring and style changes.
- Adding the logistic regression options to documentation.

3.8.2 (2016-09-23)
~~~~~~~~~~~~~~~~~~

- Changing the bias for Logistic Regressions to a boolean.
- Adding the new attributes to control ensemble's sampling.

3.8.1 (2016-07-06)
~~~~~~~~~~~~~~~~~~

- Adding types of deletable resources to bigmler delete. Adding option
  --execution-only to avoid deleting the output resources of an
  execution when the execution is deleted.
- Fixing bug: directory structure in bigmler whizzml was wrong when components
  were found in metadata.
- Upgrading the underlying Python bindings version.

3.8.0 (2016-07-04)
~~~~~~~~~~~~~~~~~~

- Adding new bigmler whizzml subcommand to create scripts and libraries
  from packages with metadata info.

3.7.1 (2016-06-27)
~~~~~~~~~~~~~~~~~~

- Adding new --field-codings option to bigmler logisitic-regression
  subcommand.
- Changing underlying bindings version

3.7.0 (2016-06-03)
~~~~~~~~~~~~~~~~~~

- Adding the new bigmler execute subcommand, which can create scripts,
  executions and libraries.

3.6.4 (2016-04-08)
~~~~~~~~~~~~~~~~~~

- Fixing bug: the --predictions-csv flag in the bigmler analyze command did
  not work with ensembles (--number-of-models > 1)

3.6.3 (2016-04-04)
~~~~~~~~~~~~~~~~~~

- Adding the --predictions-csv flag to bigmler analyze --features. It
  creates a file which contains all the data tagged with the corresponding
  k-fold and the prediction and confidence values for the best
  score cross-validation.

3.6.2 (2016-04-01)
~~~~~~~~~~~~~~~~~~

- Improving bigmler analyze --features CSV output to reflect the best fields
  set found at each step.

3.6.1 (2016-03-14)
~~~~~~~~~~~~~~~~~~

- Adding the --export-fields and --import-fields to manage field summaries
  and attribute changes in sources and datasets.

3.6.0 (2016-03-08)
~~~~~~~~~~~~~~~~~~

- Adding subcommand bigmler logistic-regression.
- Changing tests to adapt to backend random numbers changes.

3.5.4 (2016-02-09)
~~~~~~~~~~~~~~~~~~

- Fixing bug: wrong types had been added to default options in bigmler.ini
- Updating copyright --version notice.

3.5.3 (2016-02-07)
~~~~~~~~~~~~~~~~~~

- Adding links to docs and changing tests to adapt bigmler reify
  to new automatically generated names for resources.

3.5.2 (2016-01-01)
~~~~~~~~~~~~~~~~~~

- Fixing bug in bigmler reify subcommand for datasets generated from other
  datasets comming from batch resources.

3.5.1 (2015-12-26)
~~~~~~~~~~~~~~~~~~

- Adding docs for association discovery.

3.5.0 (2015-12-24)
~~~~~~~~~~~~~~~~~~

- Adding bigmler association subcommand to manage associations.

3.4.0 (2015-12-21)
~~~~~~~~~~~~~~~~~~

- Adding bigmler project subcommand for project creation and update.

3.3.9 (2015-12-19)
~~~~~~~~~~~~~~~~~~

- Fixing bug: wrong reify output for datasets created from another dataset.
- Improving bigmler reify code style and making file executable.

3.3.8 (2015-11-24)
~~~~~~~~~~~~~~~~~~

- Fixing bug: simplifying bigmler reify output for datasets created from
  batch resources.
- Allowing column numbers as keys for fields structures in
  --source-attributes, --dataset-attributes, etc

3.3.7 (2015-11-18)
~~~~~~~~~~~~~~~~~~

- Adding --datasets as option for bigmler analyze.
- Adding --summary-fields as option for bigmler analyze.

3.3.6 (2015-11-16)
~~~~~~~~~~~~~~~~~~

- Fixing bug: Report title for feature analysis was not shown.

3.3.5 (2015-11-15)
~~~~~~~~~~~~~~~~~~

- Upgrading the underlying bindings version.

3.3.4 (2015-11-10)
~~~~~~~~~~~~~~~~~~

- Fixing bug: bigmler cluster did not use the --prediction-fields option.

3.3.3 (2015-11-04)
~~~~~~~~~~~~~~~~~~

- Adding --status option to bigmler delete. Selects the resources to delete
  according to their status (finished if not set). You can check the available
  status in the
  `developers documentation
  <https://bigml.com/developers/status_codes#sc_resource_status_code_summary>`_.

3.3.2 (2015-10-31)
~~~~~~~~~~~~~~~~~~

- Fixing bug: bigmler reify failed for dataset generated from batch
  predictions, batch centroids or batch anomaly scores.

3.3.1 (2015-10-15)
~~~~~~~~~~~~~~~~~~

- Fixing bug: improving datasets download handling to cope with transmission
  errors.
- Fixing bug: solving failure when using the first column of a dataset as
  objective field in models and ensembles.


3.3.0 (2015-09-14)
~~~~~~~~~~~~~~~~~~

- Adding new bigmler analyze option, --random-fields to analyze performance of
  random forests chaging the number of random candidates.

3.2.1 (2015-09-05)
~~~~~~~~~~~~~~~~~~

- Fixing bug in reify subcommand for unordered reifications.

3.2.0 (2015-08-23)
~~~~~~~~~~~~~~~~~~

- Adding bigmler reify subcommand to script the resource creation.

3.1.1 (2015-08-16)
~~~~~~~~~~~~~~~~~~

- Fixing bug: changing the related Python bindings version to solve encoding
  problem when using Python 3 on Windows.

3.1.0 (2015-08-05)
~~~~~~~~~~~~~~~~~~

- Adding bigmler report subcommand to generate reports for cross-validation
  results in bigmler analyze.

3.0.5 (2015-07-30)
~~~~~~~~~~~~~~~~~~

- Fixing bug: bigmler analyze and filtering datasets failed when the origin
  dataset was a filtered one.

3.0.4 (2015-07-22)
~~~~~~~~~~~~~~~~~~

- Fixing bug: bigmler analyze --features could not analyze phi for a user-given
  category because the metric is called phi_coefficient.
- Modifying the output of bigmler analyze --features and --nodes to include
  the command to generate the best performing model and the command to
  clean all the generated resources.

3.0.3 (2015-07-01)
~~~~~~~~~~~~~~~~~~

- Fixing bug: dataset generation with a filter on a previous dataset
  was not working.

3.0.2 (2015-06-24)
~~~~~~~~~~~~~~~~~~

- Adding the --project-tag option to bigmler delete.
- Fixing that the --test-dataset and related options can be used in model
  evaluation.
- Fixing bug: bigmler anomalies for datasets with more than 1000 fields failed.

3.0.1 (2015-06-12)
~~~~~~~~~~~~~~~~~~

- Adding the --top-n, --forest-size and --anomalies-dataset to the bigmler
  anomaly subcommand.
- Fixing bug: source upload failed when using arguments that contain
  unicodes.
- Fixing bug: bigmler analyze subcommand failed for datasets with more than
  1000 fields.

3.0.0 (2015-04-25)
~~~~~~~~~~~~~~~~~~

- Supporting Python 3 and changing the test suite to nose.
- Adding --cluster-models option to generate the models related to
  cluster datasets.

2.2.0 (2015-04-15)
~~~~~~~~~~~~~~~~~~

- Adding --score flag to create batch anomaly scores for the training set.
- Allowing --median to be used also in ensembles predictions.
- Using --seed option also in ensembles.

2.1.0 (2015-04-10)
~~~~~~~~~~~~~~~~~~

- Adding --median flag to use median instead of mean in single models'
  predictions.
- Updating underlying BigML python bindings' version to 4.0.2 (Python 3
  compatible).


2.0.1 (2015-04-09)
~~~~~~~~~~~~~~~~~~

- Fixing bug: resuming commands failed retrieving the output directory

2.0.0 (2015-03-26)
~~~~~~~~~~~~~~~~~~

- Fixing docs formatting errors.
- Adding --to-dataset and --no-csv flags causing batch predictions,
  batch centroids and batch anomaly scores to be stored in a new remote
  dataset and not in a local CSV respectively.
- Adding the sample subcommand to generate samples from datasets

1.15.6 (2015-01-28)
~~~~~~~~~~~~~~~~~~~

- Fixing bug: using --model-fields with --max-categories failed.

1.15.5 (2015-01-20)
~~~~~~~~~~~~~~~~~~~

- Fixing bug: Failed field retrieval for batch predictions starting from
  source or dataset test data.

1.15.4 (2015-01-15)
~~~~~~~~~~~~~~~~~~~

- Adding the --project and --project-id to manage projects and associate
  them to newly created sources.
- Adding the --cluster-seed and --anomaly-seed options to choose the seed
  for deterministic clusters and anomalies.
- Refactoring dataset processing to avoid setting the objective field when
  possible.

1.15.3 (2014-12-26)
~~~~~~~~~~~~~~~~~~~

- Adding --optimize-category in bigmler analyze subcommands to select
  the category whose evaluations will be optimized.

1.15.2 (2014-12-17)
~~~~~~~~~~~~~~~~~~~

- Fixing bug: k-fold cross-validation failed for ensembles.

1.15.1 (2014-12-15)
~~~~~~~~~~~~~~~~~~~

- Fixing bug: ensembles' evaluations failed when using the ensemble id.
- Fixing bug: bigmler analyze lacked model configuration options (weight-field,
  objective-fields, pruning, model-attributes...)

1.15.0 (2014-12-06)
~~~~~~~~~~~~~~~~~~~

- Adding k-fold cross-validation for ensembles in bigmler analyze.

1.14.6 (2014-11-26)
~~~~~~~~~~~~~~~~~~~

- Adding the --model-file, --cluster-file, --anomaly-file and --ensemble-file
  to produce entirely local predictions.
- Fixing bug: the bigmler delete subcommand was not using the --anomaly-tag,
  --anomaly-score-tag and --batch-anomaly-score-tag options.
- Fixing bug: the --no-test-header flag was not working.

1.14.5 (2014-11-14)
~~~~~~~~~~~~~~~~~~~

- Fixing bug: --field-attributes was not working when used in addition
  to --types option.

1.14.4 (2014-11-10)
~~~~~~~~~~~~~~~~~~~

- Adding the capability of creating a model/cluster/anomaly and its
  corresponding batch prediction from a train/test split using --test-split.

1.14.3 (2014-11-10)
~~~~~~~~~~~~~~~~~~~

- Improving domain transformations for customized private settings.
- Fixing bug: model fields were not correctly set when the origin dataset
  was a new dataset generated by the --new-fields option.

1.14.2 (2014-10-30)
~~~~~~~~~~~~~~~~~~~

- Refactoring predictions code, improving some cases performance and memory
  usage.
- Adding the --fast option to speed prediction by not storing partial results
  in files.
- Adding the --optimize option to the bigmler analyze --features command.

1.14.1 (2014-10-23)
~~~~~~~~~~~~~~~~~~~

- Improving perfomance in individual model predictions.
- Forcing garbage collection to lower memory usage in ensemble's predictions.
- Fixing bug: batch predictions were not adding confidence when
  --prediction-info full was used.

1.14.0 (2014-10-19)
~~~~~~~~~~~~~~~~~~~

- Adding bigmler anomaly as new subcommand to generate anomaly detectors,
  anomaly scores and batch anomaly scores.

1.13.3 (2014-10-13)
~~~~~~~~~~~~~~~~~~~

- Fixing bug: source updates failed when using --locale and --types flags
  together.
- Updating bindings version and fixing code accordingly.
- Adding --k option to bigmler cluster to change the number of centroids.

1.13.2 (2014-10-05)
~~~~~~~~~~~~~~~~~~~

- Fixing bug: --source-attributes and --dataset-attributes where not updated.

1.13.1 (2014-09-22)
~~~~~~~~~~~~~~~~~~~

- Fixing bug: bigmler analyze was needlessly sampling data to evaluate.

1.13.0 (2014-09-10)
~~~~~~~~~~~~~~~~~~~

- Adding the new --missing-splits flag to control if missing values are
  included in tree branches.

1.12.4 (2014-08-03)
~~~~~~~~~~~~~~~~~~~

- Fixing bug: handling unicode command parameters on Windows.

1.12.3 (2014-07-30)
~~~~~~~~~~~~~~~~~~~

- Fixing bug: handling stdout writes of unicodes on Windows.

1.12.2 (2014-07-29)
~~~~~~~~~~~~~~~~~~~

- Fixing but for bigmler analyze: the subcommand failed when used in
  development created resources.

1.12.1 (2014-07-25)
~~~~~~~~~~~~~~~~~~~

- Fixing bug when many models are evaluated in k-fold cross-validations. The
  create evaluation could fail when called with a non-finished model.

1.12.0 (2014-07-15)
~~~~~~~~~~~~~~~~~~~

- Improving delete process. Promoting delete to a subcommand and filtering
  the type of resource to be deleted.
- Adding --dry-run option to delete.
- Adding --from-dir option to delete.
- Fixing bug when Gazibit report is used with personalized URL dashboards.

1.11.0 (2014-07-11)
~~~~~~~~~~~~~~~~~~~

- Adding the --to-csv option to export datasets to a CSV file.

1.10.0 (2014-07-11)
~~~~~~~~~~~~~~~~~~~

- Adding the --cluster-datasets option to generate the datasets related to
  the centroids in a cluster.

1.9.2 (2014-07-07)
~~~~~~~~~~~~~~~~~~

- Fixing bug for the --delete flag. Cluster, centroids and batch centroids
  could not be deleted.

1.9.1 (2014-07-02)
~~~~~~~~~~~~~~~~~~

- Documentation update.

1.9.0 (2014-07-02)
~~~~~~~~~~~~~~~~~~

- Adding cluster subcommand to generate clusters and centroid predictions.

1.8.12 (2014-06-10)
~~~~~~~~~~~~~~~~~~~

- Fixing bug for the analyze subcommand. The --resume flag crashed when no
  --ouput-dir was used.
- Fixing bug for the analyze subcommand. The --features flag crashed when
  many long feature names were used.

1.8.11 (2014-05-30)
~~~~~~~~~~~~~~~~~~~

- Fixing bug for --delete flag, broken by last fix.

1.8.10 (2014-05-29)
~~~~~~~~~~~~~~~~~~~

- Fixing bug when field names contain commas and --model-fields tag is used.
- Fixing bug when deleting all resources by tag when ensembles were found.
- Adding --exclude-features flag to analyze.

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
