# -*- coding: utf-8 -*-
#
# Copyright 2012-2019 BigML
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
python bigmler.py \
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


import bigmler.dispatchers as bd
from bigmler.parser import SUBCOMMANDS
from bigmler.utils import SYSTEM_ENCODING


PYTHON3 = sys.version_info[0] == 3

def check_delete_option(args):
    """Checks if the --delete option (to be deprecated) is used and changes
       its syntax to the corresponding subcommand

    """
    try:
        delete_index = args.index('--delete')
        args[0] = "delete"
        del args[delete_index]
    except ValueError:
        pass
    return args


def main(args=sys.argv[1:]):
    """Main process

    """
    if args:
        if not args[0].lower() in SUBCOMMANDS:
            new_args = ["main"]
            new_args.extend(args)
        else:
            new_args = args
        # checks if the old --delete syntax is used
        new_args = check_delete_option(new_args)
        if not PYTHON3:
            new_args = [arg.decode(SYSTEM_ENCODING) for arg in new_args]

        subcommand = new_args[0]
        if subcommand == "logistic-regression":
            bd.subcommand_dispatcher("logistic_regression", new_args)
        elif subcommand == "topic-model":
            if bd.NO_STEMMER:
                sys.exit("To use the bigmler topic-model command you need the"
                         " Pystemmer library. Please, install it and"
                         " retry your command.")
            bd.subcommand_dispatcher("topic_model", new_args)
        elif subcommand == "time-series":
            bd.subcommand_dispatcher("time_series", new_args)
        else:
            bd.subcommand_dispatcher(subcommand, new_args)
    else:
        sys.exit("BigMLer used with no arguments. Check:\nbigmler --help\n\nor"
                 "\n\nbigmler sample --help\n\n"
                 "\n\nbigmler analyze --help\n\n"
                 "\n\nbigmler cluster --help\n\n"
                 "\n\nbigmler anomaly --help\n\n"
                 "\n\nbigmler report --help\n\n"
                 "\n\nbigmler reify --help\n\n"
                 "\n\nbigmler project --help\n\n"
                 "\n\nbigmler association --help\n\n"
                 "\n\nbigmler logistic-regression --help\n\n"
                 "\n\nbigmler topic-model --help\n\n"
                 "\n\nbigmler time-series --help\n\n"
                 "\n\nbigmler deepnet --help\n\n"
                 "\n\nbigmler execute --help\n\n"
                 "\n\nbigmler whizzml --help\n\n"
                 "\n\nbigmler export --help\n\n"
                 "\n\nbigmler retrain --help\n\n"
                 "\n\nbigmler delete --help\n\n"
                 " for a list of options")

if __name__ == '__main__':
    main(sys.argv[1:])
