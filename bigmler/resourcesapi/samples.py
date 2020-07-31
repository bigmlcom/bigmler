# -*- coding: utf-8 -*-
#
# Copyright 2020 BigML
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
"""Resources management functions

"""



import sys

import bigml.api

from bigmler.utils import (dated, log_message, check_resource,
                           plural, get_url, is_shared,
                           check_resource_error, log_created_resources)
from bigmler.reports import report

from bigmler.resourcesapi.common import set_basic_args, \
    update_json_args, wait_for_available_tasks


def set_sample_args(args, name=None):
    """Return sample arguments dict

    """
    if name is None:
        name = args.name

    sample_args = set_basic_args(args, name)

    if 'sample' in args.json_args:
        update_json_args(sample_args, args.json_args.get('sample'))
    return sample_args


def create_samples(datasets, sample_ids, sample_args,
                   args, api=None, path=None,
                   session_file=None, log=None):
    """Create remote samples

    """
    if api is None:
        api = bigml.api.BigML()

    samples = sample_ids[:]
    existing_samples = len(samples)
    sample_args_list = []
    datasets = datasets[existing_samples:]
    # if resuming and all samples were created, there will be no datasets left
    if datasets:
        if isinstance(sample_args, list):
            sample_args_list = sample_args

        # Only one sample per command, at present
        number_of_samples = 1
        max_parallel_samples = 1
        message = dated("Creating %s.\n" %
                        plural("sample", number_of_samples))
        log_message(message, log_file=session_file,
                    console=args.verbosity)

        inprogress = []
        for i in range(0, number_of_samples):
            wait_for_available_tasks(inprogress, max_parallel_samples,
                                     api, "sample")
            if sample_args_list:
                sample_args = sample_args_list[i]

            sample = api.create_sample(datasets[i], sample_args, retries=None)
            sample_id = check_resource_error(sample,
                                             "Failed to create sample: ")
            log_message("%s\n" % sample_id, log_file=log)
            sample_ids.append(sample_id)
            inprogress.append(sample_id)
            samples.append(sample)
            log_created_resources("samples", path, sample_id, mode='a')

        if args.verbosity:
            if bigml.api.get_status(sample)['code'] != bigml.api.FINISHED:
                try:
                    sample = check_resource(sample, api.get_sample,
                                            raise_on_error=True)
                except Exception as exception:
                    sys.exit("Failed to get a finished sample: %s" %
                             str(exception))
                samples[0] = sample
            message = dated("Sample created: %s\n" %
                            get_url(sample))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
            if args.reports:
                report(args.reports, path, sample)

    return samples, sample_ids


def update_sample(sample, sample_args, args,
                  api=None, path=None, session_file=None):
    """Updates sample properties

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Updating sample. %s\n" %
                    get_url(sample))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    sample = api.update_sample(sample, sample_args)
    check_resource_error(sample, "Failed to update sample: %s"
                         % sample['resource'])
    sample = check_resource(sample, api.get_sample, raise_on_error=True)
    if is_shared(sample):
        message = dated("Shared sample link. %s\n" %
                        get_url(sample, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, sample)

    return sample


def get_samples(sample_ids, args,
                api=None, session_file=None, query_string=''):
    """Retrieves remote samples in its actual status

    """
    if api is None:
        api = bigml.api.BigML()
    sample_id = ""
    samples = sample_ids
    sample_id = sample_ids[0]
    message = dated("Retrieving %s. %s\n" %
                    (plural("sample", len(sample_ids)),
                     get_url(sample_id)))
    log_message(message, log_file=session_file, console=args.verbosity)
    # only one sample to predict at present
    try:
        sample = api.get_sample(sample_ids[0],
                                query_string=query_string)
        check_resource_error(sample, "Failed to create sample: %s"
                             % sample['resource'])
        sample = check_resource(sample, api=api, query_string=query_string,
                                raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished sample: %s" % str(exception))
    samples[0] = sample

    return samples, sample_ids


def set_publish_sample_args(args):
    """Set args to publish sample

    """
    public_sample = {}
    if args.public_sample:
        public_sample = {"private": False}
    return public_sample
