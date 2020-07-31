# -*- coding: utf-8 -*-
#
# Copyright 2018-2020 BigML
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

"""BigMLer dispatcher for subcommands

"""


from bigmler.dispatcher import main_dispatcher
from bigmler.sample.dispatcher import sample_dispatcher
from bigmler.analyze.dispatcher import analyze_dispatcher
from bigmler.cluster.dispatcher import cluster_dispatcher
from bigmler.anomaly.dispatcher import anomaly_dispatcher
from bigmler.delete.dispatcher import delete_dispatcher
from bigmler.report.dispatcher import report_dispatcher
from bigmler.reify.dispatcher import reify_dispatcher
from bigmler.project.dispatcher import project_dispatcher
from bigmler.association.dispatcher import association_dispatcher
from bigmler.logisticregression.dispatcher import logistic_regression_dispatcher
from bigmler.linearregression.dispatcher import linear_regression_dispatcher
try:
    from bigmler.topicmodel.dispatcher import topic_model_dispatcher
    NO_STEMMER = False
except ImportError:
    NO_STEMMER = True
from bigmler.timeseries.dispatcher import time_series_dispatcher
from bigmler.deepnet.dispatcher import deepnet_dispatcher
from bigmler.execute.dispatcher import execute_dispatcher
from bigmler.whizzml.dispatcher import whizzml_dispatcher
from bigmler.export.dispatcher import export_dispatcher
from bigmler.retrain.dispatcher import retrain_dispatcher
from bigmler.pca.dispatcher import pca_dispatcher
from bigmler.fusion.dispatcher import fusion_dispatcher
from bigmler.dataset.dispatcher import dataset_dispatcher
from bigmler.externalconnector.dispatcher import connector_dispatcher


def subcommand_dispatcher(subcommand, args):
    """ Calls the corresponding subcommand dispatcher

    """

    return globals()["%s_dispatcher" % subcommand.replace("-", "_")](args)
