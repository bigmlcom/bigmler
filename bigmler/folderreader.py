# -*- coding: utf-8 -*-
#
# Copyright (c) 2022-2024 BigML, Inc
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


"""Defines a Reader object to return the files in a folder """

import os


class FolderReader():
    """Adapter to read files in a folder

    """
    def __init__(self, folder, filter_fn=None, header=None):
        """Constructor method for the reader

        """
        self.folder = folder
        self.filter_fn = lambda x: True if filter_fn is None else filter_fn
        self.header = header
        self.reader = [] if header is None else [[header]]

    def open_reader(self):
        """exploring the folder

        """
        self.reader.extend([[filename] for filename in
            os.listdir(self.folder) if self.filter_fn(filename)])
        for filename in self.reader:
            yield filename
