# -*- coding: utf-8 -*-
#
# Copyright 2012-2014 BigML
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

"""BigMLer analyze main processing

   Functions to process the analyze options


"""
from __future__ import absolute_import

import sys
import os

import bigmler.processing.args as a

from bigml.multivote import PLURALITY

from bigmler.defaults import DEFAULTS_FILE
from bigmler.prediction import (MAX_MODELS, OTHER, COMBINATION,
                                THRESHOLD_CODE)
from bigmler.defaults import get_user_defaults
from bigmler.options import create_parser
from bigmler.analyze.k_fold_cv import create_kfold_cv
from bigmler.utils import check_dir


def analyze_dispatcher(args=sys.argv[1:]):
    """Main processing of the parsed options for BigMLer analyze

    """
    # Parses command line arguments.

    user_defaults = get_user_defaults()
    parser = create_parser(general_defaults=user_defaults,
                           constants={'NOW': a.NOW,
                                      'MAX_MODELS': MAX_MODELS,
                                      'PLURALITY': PLURALITY})

    command_args = parser.parse_args(args)
    if command_args.output_dir:
        path = check_dir("%s%sbigmler_session" % (command_args.output_dir, os.sep))

    # k-fold cross-validation
    if command_args.k_fold_cv is not None and command_args.dataset is not None:
        create_kfold_cv(command_args)
