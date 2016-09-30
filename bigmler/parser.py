# -*- coding: utf-8 -*-
#
# Copyright 2014-2016 BigML
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
from __future__ import absolute_import

import argparse
import pkg_resources


from bigmler.options.common import get_common_options
from bigmler.options.delete import get_delete_options
from bigmler.options.source import get_source_options
from bigmler.options.dataset import get_dataset_options
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
from bigmler.options.association import get_association_options
from bigmler.options.logisticregression import get_logistic_regression_options
from bigmler.options.execute import get_execute_options

SUBCOMMANDS = ["main", "analyze", "cluster", "anomaly", "sample",
               "delete", "report", "reify", "project", "association",
               "logistic-regression", "execute", "whizzml"]


MAIN = SUBCOMMANDS[0]


def parser_add_options(parser, options):
    """Adds the options to the sucommand parser

    """
    for option, properties in sorted(options.items(), key=lambda x: x[0]):
        parser.add_argument(option, **properties)


def create_parser(general_defaults={}, constants={}, subcommand=MAIN):
    """Sets the accepted command options, variables, defaults and help

    """

    defaults = general_defaults['BigMLer']

    version = pkg_resources.require("BigMLer")[0].version
    version_text = """\
BigMLer %s - A Higher Level API to BigML's API
Copyright 2012-2016 BigML

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
        '--sample-rate': main_options['--sample-rate'],
        '--missing-splits': main_options['--missing-splits'],
        '--pruning': main_options['--pruning'],
        '--weight-field': main_options['--weight-field'],
        '--replacement': main_options['--replacement'],
        '--ensemble-sample-no-replacement': main_options[ \
            '--ensemble-sample-no-replacement'],
        '--ensemble-sample-rate': main_options['--ensemble-sample-rate'],
        '--seed': main_options['--seed'],
        '--ensemble-sample-seed': main_options['--ensemble-sample-seed'],
        '--objective-weights': main_options['--objective-weights'],
        '--model-attributes': main_options['--model-attributes'],
        '--ensemble-attributes': main_options['--ensemble-attributes'],
        '--tlp': main_options['--tlp'],
        '--randomize': main_options['--randomize'],
        '--no-csv': main_options['--no-csv'],
        '--no-no-csv': main_options['--no-no-csv'],
        '--to-dataset': main_options['--to-dataset'],
        '--datasets': main_options['--datasets'],
        '--dataset-file': main_options['--dataset-file'],
        '--dataset-tag': delete_options['--dataset-tag']})

    defaults = general_defaults["BigMLer cluster"]
    subcommand_options["cluster"] = get_cluster_options(defaults=defaults)
    # general options
    subcommand_options["cluster"].update(common_options)
    subcommand_options["cluster"].update(source_options)
    subcommand_options["cluster"].update(dataset_options)
    subcommand_options["cluster"].update(test_options)
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

    defaults = general_defaults["BigMLer reify"]
    subcommand_options["reify"] = get_reify_options(defaults=defaults)
    reify_common_options_list = ['clear-logs', 'username', 'api-key',
                                 'version',
                                 'dev', 'no-dev', 'output-dir', 'verbosity',
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

    defaults = general_defaults["BigMLer association"]
    subcommand_options["association"] = get_association_options( \
        defaults=defaults)
    # general options
    subcommand_options["association"].update(common_options)
    subcommand_options["association"].update(source_options)
    subcommand_options["association"].update(dataset_options)
    subcommand_options["association"].update(test_options)
    subcommand_options["association"].update({
        '--source-tag': delete_options['--source-tag'],
        '--dataset-tag': delete_options['--dataset-tag'],
        '--association-tag': delete_options['--association-tag'],
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
        '--reports': main_options['--reports'],
        '--remote': main_options['--remote'],
        '--no-batch': main_options['--no-batch'],
        '--to-dataset': main_options['--to-dataset'],
        '--no-csv': main_options['--no-csv'],
        '--fields-map': main_options['--fields-map'],
        '--dataset-off': main_options['--dataset-off'],
        '--max-parallel-evaluations': main_options[
            '--max-parallel-evaluations'],
        '--cross-validation-rate': main_options[
            '--cross-validation-rate'],
        '--number-of-evaluations': main_options[
            '--number-of-evaluations'],
        '--no-no-csv': main_options['--no-no-csv']})

    defaults = general_defaults["BigMLer execute"]
    subcommand_options["execute"] = get_execute_options(defaults=defaults)
    execute_common_options = {}
    for option in common_options:
        execute_common_options.update({option: common_options[option]})
    subcommand_options["execute"].update(execute_common_options)
    subcommand_options["execute"].update(
        {'--project': source_options['--project'],
         '--project-id': source_options['--project-id'],
         '--script-tag': delete_options['--script-tag'],
         '--library-tag': delete_options['--library-tag'],
         '--execution-tag': delete_options['--execution-tag']})

    for subcommand in SUBCOMMANDS:
        subparser = subparsers.add_parser(subcommand)
        parser_add_options(subparser, subcommand_options[subcommand])

    # options to be transmitted from analyze to main
    chained_options = [
        "--debug", "--dev", "--username", "--api-key", "--resources-log",
        "--store", "--clear-logs", "--max-parallel-models",
        "--max-parallel-evaluations", "--objective", "--tag",
        "--no-tag", "--no-debug", "--no-dev", "--model-fields", "--balance",
        "--verbosity", "--resume", "--stack_level", "--no-balance",
        "--args-separator", "--name"]

    return main_parser, chained_options
