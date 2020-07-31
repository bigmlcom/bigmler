# -*- coding: utf-8 -*-
#
# Copyright 2012-2020 BigML
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


import sys


import bigmler.dispatchers as bd
from bigmler.parser import SUBCOMMANDS
from bigmler.utils import BIGML_SYS_ENCODING


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
        if not args[0].lower().strip("\n") in SUBCOMMANDS:
            new_args = ["main"]
            new_args.extend(args)
        else:
            new_args = args
        # checks if the old --delete syntax is used
        new_args = check_delete_option(new_args)

        subcommand = new_args[0].lower().strip("\n")
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
        subcommands = SUBCOMMANDS
        subcommands.sort()
        subcommands_text = "\n\n  ".join(["bigmler %s --help" % subcommand
                                          for subcommand in subcommands])
        sys.exit("BigMLer used with no arguments.\n\nCheck:"
                 "\n\n  %s \n\nfor a list of options" % subcommands_text)

if __name__ == '__main__':
    main(sys.argv[1:])
