# -*- coding: utf-8 -*-
#
# Copyright 2014-2020 BigML
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Parser for BigMLer

"""


import argparse
import pkg_resources


from bigmler.options.common import get_common_options
from bigmler.options.delete import get_delete_options
from bigmler.options.source import get_source_options
from bigmler.options.dataset import get_dataset_options
from bigmler.options.dataset_trans import get_dataset_trans_options
from bigmler.options.test import get_test_options
from bigmler.options.multilabel import get_multi_label_options
from bigmler.options.main import get_main_options
from bigmler.options.analyze import get_analyze_options
from bigmler.options.whizzml import get_whizzml_options
from bigmler.options.cluster import get_cluster_options
from bigmler.options.anomaly import get_anomaly_options
from bigmler.options.sample import get_sample_options
from bigmler.options.report import get_report_options
from bigmler.options.reify import get_reify_options
from bigmler.options.project import get_project_options
from bigmler.options.export import get_export_options
from bigmler.options.association import get_association_options
from bigmler.options.fusion import get_fusion_options
from bigmler.options.logisticregression import get_logistic_regression_options
from bigmler.options.linearregression import get_linear_regression_options
from bigmler.options.pca import get_pca_options
from bigmler.options.topicmodel import get_topic_model_options
from bigmler.options.timeseries import get_time_series_options
from bigmler.options.deepnet import get_deepnet_options
from bigmler.options.execute import get_execute_options
from bigmler.options.retrain import get_retrain_options
from bigmler.options.externalconnector import get_external_connector_options

SUBCOMMANDS = ["main", "analyze", "cluster", "anomaly", "sample", "dataset",
               "delete", "report", "reify", "project", "association",
               "logistic-regression", "topic-model", "time-series",
               "execute", "whizzml", "export", "deepnet", "retrain",
               "linear-regression", "pca", "fusion", "connector"]


MAIN = SUBCOMMANDS[0]


def parser_add_options(parser, options):
    """Adds the options to the sucommand parser

    """
    for option, properties in sorted(list(options.items()), key=lambda x: x[0]):
        parser.add_argument(option, **properties)


def create_parser(general_defaults={}, constants={}, subcommand=MAIN):
    """Sets the accepted command options, variables, defaults and help

    """

    defaults = general_defaults['BigMLer']

    version = pkg_resources.require("BigMLer")[0].version
    version_text = """\
BigMLer %s - A Higher Level API to BigML's API
Copyright 2012-2020 BigML

Licensed under the Apache License, Version 2.0 (the \"License\"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an \"AS IS\" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.""" % version
    constants['version_text'] = version_text
    main_parser = argparse.ArgumentParser(
        description="A higher level API to BigML's API.",
        epilog="Happy predictive modeling!",
        formatter_class=argparse.RawTextHelpFormatter)
    main_parser.add_argument('--version',
                             action='version', version=version_text)
    subparsers = main_parser.add_subparsers()

    # list of options
    common_options = get_common_options(defaults=defaults, constants=constants)
    delete_options = get_delete_options(defaults=defaults)
    source_options = get_source_options(defaults=defaults)
    dataset_options = get_dataset_options(defaults=defaults)
    test_options = get_test_options(defaults=defaults)
    multi_label_options = get_multi_label_options(defaults=defaults)

    # subcommand options
    subcommand_options = {}
    # specific options
    subcommand_options["main"] = get_main_options(defaults=defaults,
                                                  constants=constants)
    # general options
    subcommand_options["main"].update(common_options)
    subcommand_options["main"].update(source_options)
    subcommand_options["main"].update(dataset_options)
    subcommand_options["main"].update(multi_label_options)
    subcommand_options["main"].update(test_options)
    subcommand_options["main"].update({
        '--source-tag': delete_options['--source-tag'],
        '--dataset-tag': delete_options['--dataset-tag'],
        '--model-tag': delete_options['--model-tag'],
        '--ensemble-tag': delete_options['--ensemble-tag'],
        '--prediction-tag': delete_options['--prediction-tag'],
        '--batch-prediction-tag': delete_options['--batch-prediction-tag']})

    main_options = subcommand_options["main"]

    subcommand_options["dataset"] = dataset_options
    subcommand_options["dataset"].update(get_dataset_trans_options( \
        defaults=defaults))
    subcommand_options["dataset"].update(common_options)
    subcommand_options["dataset"].update(source_options)
    subcommand_options["main"].update(multi_label_options)
    subcommand_options["dataset"].update({
        '--source-tag': delete_options['--source-tag'],
        '--dataset-tag': delete_options['--dataset-tag'],
        '--max-categories': subcommand_options['main']['--max-categories'],
        '--labels': subcommand_options['main']['--labels'],
        '--multi-label': subcommand_options['main']['--multi-label'],
        '--objective': subcommand_options['main']['--objective'],
        '--reports': subcommand_options['main']['--reports']})

    dataset_sampling_options = { \
        '--replacement': main_options['--replacement'],
        '--sample-rate': main_options['--sample-rate'],
        '--seed': main_options['--seed']}

    defaults = general_defaults["BigMLer whizzml"]
    subcommand_options["whizzml"] = get_whizzml_options(defaults=defaults)
    subcommand_options["whizzml"].update(common_options)
    defaults = general_defaults["BigMLer analyze"]
    subcommand_options["analyze"] = get_analyze_options(defaults=defaults)
    subcommand_options["analyze"].update(common_options)
    # we add the options that should be transmitted to bigmler main subcommands
    # in analyze
    subcommand_options["analyze"].update({
        '--dataset': dataset_options['--dataset'],
        '--objective': main_options['--objective'],
        '--max-parallel-models': main_options['--max-parallel-models'],
        '--max-parallel-evaluations': main_options[
            '--max-parallel-evaluations'],
        '--model-fields': main_options['--model-fields'],
        '--balance': main_options['--balance'],
        '--no-balance': main_options['--no-balance'],
        '--number-of-models': main_options['--number-of-models'],
        '--missing-splits': main_options['--missing-splits'],
        '--pruning': main_options['--pruning'],
        '--weight-field': main_options['--weight-field'],
        '--ensemble-sample-no-replacement': main_options[ \
            '--ensemble-sample-no-replacement'],
        '--ensemble-sample-rate': main_options['--ensemble-sample-rate'],
        '--ensemble-sample-seed': main_options['--ensemble-sample-seed'],
        '--objective-weights': main_options['--objective-weights'],
        '--model-attributes': main_options['--model-attributes'],
        '--ensemble-attributes': main_options['--ensemble-attributes'],
        '--boosting': main_options['--boosting'],
        '--boosting-iterations': main_options['--boosting-iterations'],
        '--early-holdout': main_options['--early-holdout'],
        '--no-early-out-of-bag': main_options['--no-early-out-of-bag'],
        '--learning-rate': main_options['--learning-rate'],
        '--no-step-out-of-bag': main_options['--no-step-out-of-bag'],
        '--randomize': main_options['--randomize'],
        '--no-csv': main_options['--no-csv'],
        '--no-no-csv': main_options['--no-no-csv'],
        '--to-dataset': main_options['--to-dataset'],
        '--datasets': main_options['--datasets'],
        '--dataset-file': main_options['--dataset-file'],
        '--dataset-tag': delete_options['--dataset-tag']})
    subcommand_options["analyze"].update(dataset_sampling_options)

    defaults = general_defaults["BigMLer cluster"]
    subcommand_options["cluster"] = get_cluster_options(defaults=defaults)
    # general options
    subcommand_options["cluster"].update(common_options)
    subcommand_options["cluster"].update(source_options)
    subcommand_options["cluster"].update(dataset_options)
    subcommand_options["cluster"].update(test_options)
    subcommand_options["cluster"].update(dataset_sampling_options)
    subcommand_options["cluster"].update({
        '--cpp': main_options['--cpp'],
        '--fields-map': main_options['--fields-map'],
        '--source-tag': delete_options['--source-tag'],
        '--dataset-tag': delete_options['--dataset-tag'],
        '--cluster-tag': delete_options['--cluster-tag'],
        '--centroid-tag': delete_options['--centroid-tag'],
        '--batch-centroid-tag': delete_options['--batch-centroid-tag'],
        '--prediction-info': main_options['--prediction-info'],
        '--prediction-header': main_options['--prediction-header'],
        '--prediction-fields': main_options['--prediction-fields'],
        '--default-numeric-value': main_options['--default-numeric-value'],
        '--reports': main_options['--reports'],
        '--remote': main_options['--remote'],
        '--no-batch': main_options['--no-batch'],
        '--no-csv': main_options['--no-csv'],
        '--no-no-csv': main_options['--no-no-csv'],
        '--to-dataset': main_options['--to-dataset']})

    defaults = general_defaults["BigMLer anomaly"]
    subcommand_options["anomaly"] = get_anomaly_options(defaults=defaults)
    # general options
    subcommand_options["anomaly"].update(common_options)
    subcommand_options["anomaly"].update(source_options)
    subcommand_options["anomaly"].update(dataset_options)
    subcommand_options["anomaly"].update(test_options)
    subcommand_options["anomaly"].update(dataset_sampling_options)
    subcommand_options["anomaly"].update({
        '--cpp': main_options['--cpp'],
        '--fields-map': main_options['--fields-map'],
        '--source-tag': delete_options['--source-tag'],
        '--dataset-tag': delete_options['--dataset-tag'],
        '--anomaly-tag': delete_options['--anomaly-tag'],
        '--anomaly-score-tag': delete_options['--anomaly-score-tag'],
        '--batch-anomaly-score-tag': delete_options[
            '--batch-anomaly-score-tag'],
        '--prediction-info': main_options['--prediction-info'],
        '--prediction-header': main_options['--prediction-header'],
        '--prediction-fields': main_options['--prediction-fields'],
        '--default-numeric-value': main_options['--default-numeric-value'],
        '--reports': main_options['--reports'],
        '--remote': main_options['--remote'],
        '--no-batch': main_options['--no-batch'],
        '--no-csv': main_options['--no-csv'],
        '--no-no-csv': main_options['--no-no-csv'],
        '--to-dataset': main_options['--to-dataset']})

    defaults = general_defaults["BigMLer sample"]
    subcommand_options["sample"] = get_sample_options(defaults=defaults)
    # general options
    subcommand_options["sample"].update(common_options)
    subcommand_options["sample"].update(source_options)
    subcommand_options["sample"].update(dataset_options)
    subcommand_options["sample"].update({
        '--cpp': main_options['--cpp'],
        '--source-tag': delete_options['--source-tag'],
        '--dataset-tag': delete_options['--dataset-tag'],
        '--sample-tag': delete_options['--sample-tag'],
        '--reports': main_options['--reports']})

    subcommand_options["delete"] = delete_options
    subcommand_options["delete"].update(common_options)

    defaults = general_defaults["BigMLer report"]
    subcommand_options["report"] = get_report_options(defaults=defaults)

    defaults = general_defaults["BigMLer export"]
    subcommand_options["export"] = get_export_options(defaults=defaults)
    export_common_options_list = ['clear-logs', 'username', 'api-key',
                                  'version', 'org-project',
                                  'output-dir', 'verbosity',
                                  'resume', 'stack-level', 'debug', 'store']
    export_common_options = {}
    for option in export_common_options_list:
        option = '--%s' % option
        export_common_options.update({option: common_options[option]})
    subcommand_options["export"].update(export_common_options)

    defaults = general_defaults["BigMLer reify"]
    subcommand_options["reify"] = get_reify_options(defaults=defaults)
    reify_common_options_list = ['clear-logs', 'username', 'api-key',
                                 'version', 'org-project',
                                 'output-dir', 'verbosity',
                                 'resume', 'stack-level', 'debug', 'store']
    reify_common_options = {}
    for option in reify_common_options_list:
        option = '--%s' % option
        reify_common_options.update({option: common_options[option]})
    subcommand_options["reify"].update(reify_common_options)

    subcommand_options["project"] = get_project_options(defaults=defaults)
    subcommand_options["project"].update({
        '--project': source_options['--project'],
        '--project-id': source_options['--project-id'],
        '--name': common_options['--name'],
        '--description': common_options['--description'],
        '--category': common_options['--category'],
        '--tag': common_options['--tag'],
        '--resources-file': main_options['--resources-log']})
    project_common_options = {}
    for option in reify_common_options_list:
        option = '--%s' % option
        project_common_options.update({option: common_options[option]})
    subcommand_options["project"].update(project_common_options)

    defaults = general_defaults["BigMLer connector"]
    subcommand_options["connector"] = get_external_connector_options( \
        defaults=defaults)
    subcommand_options["connector"].update({
        '--name': common_options['--name'],
        '--description': common_options['--description'],
        '--category': common_options['--category'],
        '--tag': common_options['--tag'],
        '--project-id': source_options['--project-id'],
        '--resources-file': main_options['--resources-log']})
    connector_common_options = {}
    for option in reify_common_options_list:
        option = '--%s' % option
        connector_common_options.update({option: common_options[option]})
    subcommand_options["connector"].update(connector_common_options)


    defaults = general_defaults["BigMLer association"]
    subcommand_options["association"] = get_association_options( \
        defaults=defaults)
    # general options
    subcommand_options["association"].update(common_options)
    subcommand_options["association"].update(source_options)
    subcommand_options["association"].update(dataset_options)
    subcommand_options["association"].update(test_options)
    subcommand_options["association"].update(dataset_sampling_options)
    subcommand_options["association"].update({
        '--source-tag': delete_options['--source-tag'],
        '--dataset-tag': delete_options['--dataset-tag'],
        '--association-tag': delete_options['--association-tag'],
        '--default-numeric-value': main_options['--default-numeric-value'],
        '--reports': main_options['--reports'],
        '--remote': main_options['--remote'],
        '--no-batch': main_options['--no-batch'],
        '--no-csv': main_options['--no-csv'],
        '--no-no-csv': main_options['--no-no-csv']})

    defaults = general_defaults["BigMLer logistic regression"]
    subcommand_options["logistic-regression"] = \
        get_logistic_regression_options( \
        defaults=defaults)
    # general options
    subcommand_options["logistic-regression"].update(common_options)
    subcommand_options["logistic-regression"].update(source_options)
    subcommand_options["logistic-regression"].update(dataset_options)
    subcommand_options["logistic-regression"].update(test_options)
    subcommand_options["logistic-regression"].update(dataset_sampling_options)
    subcommand_options["logistic-regression"].update({
        '--source-tag': delete_options['--source-tag'],
        '--dataset-tag': delete_options['--dataset-tag'],
        '--logistic-regression-tag': delete_options[
            '--logistic-regression-tag'],
        '--objective': main_options['--objective'],
        '--evaluate': main_options['--evaluate'],
        '--prediction-info': main_options['--prediction-info'],
        '--prediction-header': main_options['--prediction-header'],
        '--prediction-fields': main_options['--prediction-fields'],
        '--default-numeric-value': main_options['--default-numeric-value'],
        '--reports': main_options['--reports'],
        '--remote': main_options['--remote'],
        '--no-batch': main_options['--no-batch'],
        '--to-dataset': main_options['--to-dataset'],
        '--no-csv': main_options['--no-csv'],
        '--fields-map': main_options['--fields-map'],
        '--dataset-off': main_options['--dataset-off'],
        '--operating-point': main_options['--operating-point'],
        '--max-parallel-evaluations': main_options[
            '--max-parallel-evaluations'],
        '--cross-validation-rate': main_options[
            '--cross-validation-rate'],
        '--number-of-evaluations': main_options[
            '--number-of-evaluations'],
        '--batch-prediction-attributes': main_options[
            '--batch-prediction-attributes'],
        '--prediction-attributes': main_options[
            '--prediction-attributes'],
        '--prediction-tag': delete_options['--prediction-tag'],
        '--batch-prediction-tag': delete_options['--batch-prediction-tag'],
        '--no-no-csv': main_options['--no-no-csv']})



    defaults = general_defaults["BigMLer linear regression"]
    subcommand_options["linear-regression"] = \
        get_linear_regression_options( \
        defaults=defaults)
    # general options
    subcommand_options["linear-regression"].update(common_options)
    subcommand_options["linear-regression"].update(source_options)
    subcommand_options["linear-regression"].update(dataset_options)
    subcommand_options["linear-regression"].update(test_options)
    subcommand_options["linear-regression"].update(dataset_sampling_options)
    subcommand_options["linear-regression"].update({
        '--source-tag': delete_options['--source-tag'],
        '--dataset-tag': delete_options['--dataset-tag'],
        '--linear-regression-tag': delete_options[
            '--linear-regression-tag'],
        '--objective': main_options['--objective'],
        '--evaluate': main_options['--evaluate'],
        '--prediction-info': main_options['--prediction-info'],
        '--prediction-header': main_options['--prediction-header'],
        '--prediction-fields': main_options['--prediction-fields'],
        '--default-numeric-value': main_options['--default-numeric-value'],
        '--reports': main_options['--reports'],
        '--remote': main_options['--remote'],
        '--no-batch': main_options['--no-batch'],
        '--to-dataset': main_options['--to-dataset'],
        '--no-csv': main_options['--no-csv'],
        '--fields-map': main_options['--fields-map'],
        '--dataset-off': main_options['--dataset-off'],
        '--field-codings': subcommand_options['logistic-regression'][ \
            '--field-codings'],
        '--bias': subcommand_options['logistic-regression'][ \
            '--bias'],
        '--no-bias': subcommand_options['logistic-regression'][ \
            '--no-bias'],
        '--max-parallel-evaluations': main_options[
            '--max-parallel-evaluations'],
        '--cross-validation-rate': main_options[
            '--cross-validation-rate'],
        '--number-of-evaluations': main_options[
            '--number-of-evaluations'],
        '--batch-prediction-attributes': main_options[
            '--batch-prediction-attributes'],
        '--prediction-attributes': main_options[
            '--prediction-attributes'],
        '--prediction-tag': delete_options['--prediction-tag'],
        '--batch-prediction-tag': delete_options['--batch-prediction-tag'],
        '--no-no-csv': main_options['--no-no-csv']})



    # time-series
    defaults = general_defaults["BigMLer time-series"]
    subcommand_options["time-series"] = get_time_series_options( \
        defaults=defaults)

    subcommand_options["time-series"].update(common_options)
    subcommand_options["time-series"].update(source_options)
    subcommand_options["time-series"].update(dataset_options)
    subcommand_options["time-series"].update(test_options)
    subcommand_options["time-series"].update({
        '--source-tag': delete_options['--source-tag'],
        '--dataset-tag': delete_options['--dataset-tag'],
        '--fields-map': main_options['--fields-map'],
        '--time-series-tag': delete_options[
            '--time-series-tag'],
        '--objective': main_options['--objective'],
        '--evaluate': main_options['--evaluate'],
        '--prediction-header': main_options['--prediction-header'],
        '--default-numeric-value': main_options['--default-numeric-value'],
        '--reports': main_options['--reports'],
        '--remote': main_options['--remote']})


    defaults = general_defaults["BigMLer execute"]
    subcommand_options["execute"] = get_execute_options(defaults=defaults)
    execute_common_options = {}
    for option in common_options:
        execute_common_options.update({option: common_options[option]})
    subcommand_options["execute"].update(execute_common_options)
    subcommand_options["execute"].update(
        {'--project': source_options['--project'],
         '--upgrade': subcommand_options['whizzml']['--upgrade'],
         '--project-id': source_options['--project-id'],
         '--script-tag': delete_options['--script-tag'],
         '--library-tag': delete_options['--library-tag'],
         '--execution-tag': delete_options['--execution-tag']})


    defaults = {}
    subcommand_options["retrain"] = get_retrain_options(defaults=defaults)
    # shared options are like the ones in reify
    subcommand_options["retrain"].update(reify_common_options)
    subcommand_options["retrain"].update( \
        {'--output': subcommand_options['reify']['--output'],
         '--org-project': common_options['--org-project'],
         '--upgrade': subcommand_options['reify']['--upgrade'],
         '--model-tag': delete_options['--model-tag'],
         '--ensemble-tag': delete_options['--ensemble-tag'],
         '--logistic-regression-tag': delete_options['--logistic-regression-tag'],
         '--deepnet-tag': delete_options['--deepnet-tag'],
         '--cluster-tag': delete_options['--cluster-tag'],
         '--anomaly-tag': delete_options['--anomaly-tag'],
         '--association-tag': delete_options['--association-tag'],
         '--time-series-tag': delete_options['--time-series-tag'],
         '--topic-model-tag': delete_options['--topic-model-tag']})


    defaults = general_defaults["BigMLer topic model"]
    subcommand_options["topic-model"] = get_topic_model_options(
        defaults=defaults)
    # general options
    subcommand_options["topic-model"].update(common_options)
    subcommand_options["topic-model"].update(source_options)
    subcommand_options["topic-model"].update(dataset_options)
    subcommand_options["topic-model"].update(test_options)
    subcommand_options["topic-model"].update(dataset_sampling_options)
    subcommand_options["topic-model"].update({
        '--cpp': main_options['--cpp'],
        '--fields-map': main_options['--fields-map'],
        '--source-tag': delete_options['--source-tag'],
        '--dataset-tag': delete_options['--dataset-tag'],
        '--topic-model-tag': delete_options['--topic-model-tag'],
        '--topic-distribution-tag': delete_options['--topic-distribution-tag'],
        '--batch-topic-distribution-tag': delete_options[ \
            '--batch-topic-distribution-tag'],
        '--prediction-info': main_options['--prediction-info'],
        '--prediction-header': main_options['--prediction-header'],
        '--prediction-fields': main_options['--prediction-fields'],
        '--reports': main_options['--reports'],
        '--remote': main_options['--remote'],
        '--no-batch': main_options['--no-batch'],
        '--no-csv': main_options['--no-csv'],
        '--no-no-csv': main_options['--no-no-csv'],
        '--to-dataset': main_options['--to-dataset']})


    defaults = general_defaults["BigMLer deepnet"]
    subcommand_options["deepnet"] = \
        get_deepnet_options(defaults=defaults)
    # general options
    subcommand_options["deepnet"].update(common_options)
    subcommand_options["deepnet"].update(source_options)
    subcommand_options["deepnet"].update(dataset_options)
    subcommand_options["deepnet"].update(test_options)
    subcommand_options["deepnet"].update(dataset_sampling_options)
    subcommand_options["deepnet"].update({
        '--source-tag': delete_options['--source-tag'],
        '--dataset-tag': delete_options['--dataset-tag'],
        '--deepnet-tag': delete_options[
            '--deepnet-tag'],
        '--objective': main_options['--objective'],
        '--evaluate': main_options['--evaluate'],
        '--prediction-info': main_options['--prediction-info'],
        '--prediction-header': main_options['--prediction-header'],
        '--prediction-fields': main_options['--prediction-fields'],
        '--default-numeric-value': main_options['--default-numeric-value'],
        '--reports': main_options['--reports'],
        '--remote': main_options['--remote'],
        '--no-batch': main_options['--no-batch'],
        '--to-dataset': main_options['--to-dataset'],
        '--no-csv': main_options['--no-csv'],
        '--fields-map': main_options['--fields-map'],
        '--operating-point': main_options['--operating-point'],
        '--dataset-off': main_options['--dataset-off'],
        '--max-parallel-evaluations': main_options[
            '--max-parallel-evaluations'],
        '--cross-validation-rate': main_options[
            '--cross-validation-rate'],
        '--number-of-evaluations': main_options[
            '--number-of-evaluations'],
        '--batch-prediction-attributes': main_options[
            '--batch-prediction-attributes'],
        '--prediction-attributes': main_options[
            '--prediction-attributes'],
        '--prediction-tag': delete_options['--prediction-tag'],
        '--batch-prediction-tag': delete_options['--batch-prediction-tag'],
        '--no-no-csv': main_options['--no-no-csv']})

    defaults = general_defaults["BigMLer PCA"]
    subcommand_options["pca"] = \
        get_pca_options( \
        defaults=defaults)
    # general options
    subcommand_options["pca"].update(common_options)
    subcommand_options["pca"].update(source_options)
    subcommand_options["pca"].update(dataset_options)
    subcommand_options["pca"].update(test_options)
    subcommand_options["pca"].update(dataset_sampling_options)
    subcommand_options["pca"].update({
        '--source-tag': delete_options['--source-tag'],
        '--dataset-tag': delete_options['--dataset-tag'],
        '--pca-tag': delete_options[
            '--pca-tag'],
        '--projection-tag': delete_options[
            '--projection-tag'],
        '--batch-projection-tag': delete_options[
            '--batch-projection-tag'],
        '--objective': main_options['--objective'],
        '--evaluate': main_options['--evaluate'],
        '--reports': main_options['--reports'],
        '--remote': main_options['--remote'],
        '--no-batch': main_options['--no-batch'],
        '--to-dataset': main_options['--to-dataset'],
        '--no-csv': main_options['--no-csv'],
        '--fields-map': main_options['--fields-map'],
        '--dataset-off': main_options['--dataset-off'],
        '--no-no-csv': main_options['--no-no-csv']})

    defaults = general_defaults["BigMLer Fusion"]
    subcommand_options["fusion"] = get_fusion_options(defaults=defaults)
    # general options
    subcommand_options["fusion"].update(common_options)
    subcommand_options["fusion"].update(test_options)
    subcommand_options["fusion"].update(source_options)
    subcommand_options["fusion"].update(dataset_options)
    del subcommand_options["fusion"]["--train"]
    del subcommand_options["fusion"]["--source"]
    del subcommand_options["fusion"]["--source-file"]
    del subcommand_options["fusion"]["--dataset"]
    del subcommand_options["fusion"]["--datasets"]
    del subcommand_options["fusion"]["--dataset-file"]
    subcommand_options["fusion"].update({
        '--prediction-info': main_options['--prediction-info'],
        '--prediction-header': main_options['--prediction-header'],
        '--prediction-fields': main_options['--prediction-fields'],
        '--operating-point': main_options['--operating-point'],
        '--reports': main_options['--reports'],
        '--project-id': source_options['--project-id'],
        '--project': source_options['--project'],
        '--remote': main_options['--remote'],
        '--batch-prediction-attributes': main_options[
            '--batch-prediction-attributes'],
        '--prediction-attributes': main_options[
            '--prediction-attributes'],
        '--prediction-tag': delete_options['--prediction-tag'],
        '--batch-prediction-tag': delete_options['--batch-prediction-tag'],
        '--no-batch': main_options['--no-batch'],
        '--evaluate': main_options['--evaluate'],
        '--to-dataset': main_options['--to-dataset'],
        '--no-csv': main_options['--no-csv'],
        '--fields-map': main_options['--fields-map'],
        '--dataset-off': main_options['--dataset-off'],
        '--no-no-csv': main_options['--no-no-csv'],
        '--locale': main_options['--locale'],
        '--training-separator': main_options['--training-separator'],
        '--fusion-tag': delete_options['--fusion-tag']})

    subparser = subparsers.add_parser(subcommand)

    parser_add_options(subparser, subcommand_options[subcommand])

    # options to be transmitted from analyze to main
    chained_options = [
        "--debug", "--username", "--api-key", "--resources-log",
        "--store", "--clear-logs", "--max-parallel-models",
        "--max-parallel-evaluations", "--objective", "--tag",
        "--no-tag", "--no-debug", "--model-fields", "--balance",
        "--verbosity", "--resume", "--stack_level", "--no-balance",
        "--args-separator", "--name"]

    return main_parser, chained_options, subcommand_options
