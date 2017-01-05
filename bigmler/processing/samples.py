# -*- coding: utf-8 -*-
#
# Copyright 2015-2017 BigML
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

"""BigMLer - Resources processing: creation, update and retrieval of samples

"""
from __future__ import absolute_import

import bigmler.utils as u
import bigmler.resources as r
import bigmler.checkpoint as c

from bigml.fields import Fields, DEFAULT_MISSING_TOKENS


def has_samples(args):
    """Returns whether there's some kind of sample option in the command

    """
    return args.sample or args.samples or args.sample_tag


def needs_sample_fields(args):
    """checks whether there's any argument that needs the sample fields
       structure to be translated into field ids

    """
    return (args.sample_header or args.row_order_by or args.row_fields_ or
            args.stat_fields_ or args.stat_field or args.export_fields)


def samples_processing(datasets, samples, sample_ids,
                       api, args, resume,
                       session_file=None, path=None,
                       log=None):
    """Creates or retrieves samples from the input data

    """

    # If we have a dataset but not a sample, we create the sample if the
    # no_sample flag hasn't been set up.
    if datasets and not (has_samples(args) or args.no_sample):
        sample_ids = []
        samples = []

        # Only 1 sample per bigmler command at present
        number_of_samples = 1
        if resume:
            resume, sample_ids = c.checkpoint(
                c.are_samples_created, path, number_of_samples,
                debug=args.debug)
            if not resume:
                message = u.dated("Found %s samples out of %s. Resuming.\n"
                                  % (len(sample_ids),
                                     number_of_samples))
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)

            samples = sample_ids
            number_of_samples -= len(sample_ids)

        sample_args = r.set_sample_args(args)
        samples, sample_ids = r.create_samples(datasets, samples,
                                               sample_args, args, api,
                                               path, session_file, log)
    # If a sample is provided, we use it.
    elif args.sample:
        sample_ids = [args.sample]
        samples = sample_ids[:]

    elif args.samples or args.sample_tag:
        samples = sample_ids[:]

    # We must retrieve the samples' output to store them as CSV files
    if sample_ids and needs_sample_fields(args):
        samples, sample_ids = r.get_samples(samples, args, api,
                                            session_file=session_file)

    return samples, sample_ids, resume


def get_sample_fields(sample, csv_properties, args):
    """Retrieves fields info from sample resource

    """

    if not csv_properties:
        csv_properties = {}
    csv_properties.update(verbose=True)
    if args.user_locale is None:
        args.user_locale = sample['object'].get('locale', None)
    csv_properties.update(data_locale=args.user_locale)
    csv_properties.update(missing_tokens=DEFAULT_MISSING_TOKENS)
    return Fields(sample, **csv_properties)
