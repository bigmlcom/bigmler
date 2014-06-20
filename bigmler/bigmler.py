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

"""BigMLer - A Higher Level API to BigML's API

# Basic usage
python bigmler.py \
    --train data/iris.csv \
    --test data/test_iris.csv
    --no-test-header

# Create an 10-model ensemble using bagging
python bigmler.py
    --train train.csv \
    --output submission.csv \
    --objective 0 \
    --types types.txt \
    --name 'Iris Ensemble' \
    --number_of_models 10 \
    --sample_rate 0.75 \
    --replacement \
    --tag my_ensemble

# Make predictions using models tagged with my_ensemble
python bigmler.py \
    --model_tag my_ensemble \
    --test test.csv
    --no-test-header

"""
from __future__ import absolute_import

import sys


from bigmler.dispatcher import main_dispatcher
from bigmler.analyze.dispatcher import analyze_dispatcher
from bigmler.cluster.dispatcher import cluster_dispatcher
from bigmler.parser import SUBCOMMANDS


def main(args=sys.argv[1:]):
    """Main process

    """
    if args:
        if not args[0].lower() in SUBCOMMANDS:
            new_args = ["main"]
            new_args.extend(args)
        else:
            new_args = args
        if new_args[0] == "main":
            main_dispatcher(args=new_args)
        elif new_args[0] == "analyze":
            analyze_dispatcher(args=new_args)
        elif new_args[0] == "cluster":
            cluster_dispatcher(args=new_args)
    else:
        sys.exit("BigMLer used with no arguments. Check:\nbigmler --help\n\nor"
                 "\n\nbigmler analyze --help\n\n for a list of options")

if __name__ == '__main__':
    main(sys.argv[1:])
