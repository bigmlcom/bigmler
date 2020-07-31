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



import codecs
import sys


class UTF8Recoder:
    """Iterator that reads an encoded stream and reencodes the input to UTF-8

    """
    def __init__(self, file_name, encoding):
        """Iterator constructor given a file and encoding

        """
        if sys.version > '3':
            self.reader = file_name
        else:
            self.reader = codecs.getreader(encoding)(file_name)

    def __iter__(self):
        """Iterator member

        """
        return self

    def __next__(self):
        """Iterator next method

        """
        if sys.version > '3':
            return next(self.reader)
        return next(self.reader).encode("utf-8")
