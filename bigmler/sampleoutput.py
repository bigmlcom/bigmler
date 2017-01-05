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
"""Sample output auxiliary functions

"""
from __future__ import absolute_import


import json
import os

from bigml.io import UnicodeWriter
import bigmler.resources as r


STAT_KEYS = ["spearman_correlation", "pearson_correlation", "slope",
             "intercept", "spearman_correlations", "pearson_correlations",
             "slopes", "intercepts"]
LINEAR_MODE = "linear"

def translate_to_id(value, fields):
    """Tries to translate to the corresponding id a field name maybe
       prefixed by "-"

    """
    try:
        prefix = ""
        if isinstance(value, basestring):
            if value.startswith("-"):
                value = value[1:]
                prefix = "-"
            return "%s%s" % (prefix, fields.field_id(value))
    except ValueError:
        print "WARNING: Failed to find \"%s\" in the sample fields structure"
        return None
    if isinstance(value, list):
        ids = []
        for item in value:
            prefix = ""
            if item.startswith("-"):
                item = item[1:]
                prefix = "-"
            try:
                ids.append("%s%s" % (prefix, fields.field_id(item)))
            except ValueError:
                print ("WARNING: Failed to find \"%s\" in the sample fields"
                       " structure")
        return ids


def sample_query_string(args, fields):
    """Builds the query string to be used in GET calls to retrieve the
       sample output

    """
    query_string = []

    if args.fields_filter:
        query_string.append(args.fields_filter)
    if args.row_index:
        query_string.append('index=true')
    if args.mode:
        query_string.append('mode=%s' % args.mode)
    if args.seed:
        query_string.append('seed=%s'% args.seed)
    if args.occurrence:
        query_string.append('occurrence=true')
    if args.precision is not None:
        query_string.append('precision=%s'% args.precision)
    if args.rows:
        query_string.append('rows=%s' % args.rows)
    if args.row_offset:
        query_string.append('row_offset=%s' % args.row_offset)
    if args.row_order_by:
        if args.mode is None:
            args.mode = LINEAR_MODE
        elif args.mode != LINEAR_MODE:
            print ("WARNING: --row-order-by can only be used with \"linear\""
                   " --mode. Ignoring --row-order-by.")
        else:
            row_order_by_id = translate_to_id(args.row_order_by, fields)
            if row_order_by_id:
                query_string.append('row_order_by=%s' % row_order_by_id)
    if args.row_fields_:
        row_fields_ids = translate_to_id(args.row_fields_, fields)
        if row_fields_ids:
            query_string.append('row_fields=%s' % ','.join(row_fields_ids))
    if args.stat_fields_:
        stat_fields_ids = translate_to_id(args.stat_fields_, fields)
        if stat_fields_ids:
            query_string.append('stat_fields=%s' % ','.join(stat_fields_ids))
    if args.stat_field:
        stat_field_id = translate_to_id(args.stat_field, fields)
        if stat_field_id:
            query_string.append('stat_field=%s' % stat_field_id)
    if args.unique:
        query_string.append('unique=true')

    return ";".join(query_string)


def sample_file(sample, fields, args, api, path=None, session_file=None):
    """Creates a file for each sample with the sample rows.

    """
    query_string = sample_query_string(args, fields)
    sample = r.get_samples([sample], args, api,
                           session_file=session_file,
                           query_string=query_string)[0][0]
    output = args.predictions
    with UnicodeWriter(output, lineterminator="\n") as output:
        headers = [field['name'] for field in
                   sample['object']['sample']['fields']]
        if args.sample_header:
            if args.row_index or args.occurrence:
                new_headers = []
                if args.row_index:
                    new_headers.append("index")
                if args.occurrence:
                    new_headers.append("occurrences")
                    new_headers.extend(headers)
                headers = new_headers
            output.writerow(headers)
        for row in sample['object']['sample']['rows']:
            output.writerow(row)
        if args.stat_field or args.stat_fields:
            stat_info = {}
            sample_obj = sample['object']['sample']
            for key in STAT_KEYS:
                if key in sample_obj:
                    stat_info[key] = sample_obj[key]
            with open(os.path.join(path, "stat_info.json"), "w") as stat_file:
                json.dump(stat_info, stat_file)
