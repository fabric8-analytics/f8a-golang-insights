#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interactions with local filesystem, useful for unit testing.

Copyright © 2018 Red Hat Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import json
import logging
import os

import daiquiri

from insights_engine.data_store.abstract_data_store import AbstractDataStore

daiquiri.setup(level=logging.WARNING)
_logger = daiquiri.getLogger(__name__)


class LocalFileSystem(AbstractDataStore):  # pragma: no cover
    """Wrapper on local filesystem, API similar to s3DataStore."""

    def __init__(self, src_dir):
        """Create a new local filesystem instance.

        :src_dir: The root directory for local filesystem object
        """
        self.src_dir = src_dir

    def get_name(self):
        """Return name of local filesystem root dir."""
        return "Local filesytem dir: " + self.src_dir

    def read_generic_file(self, filename):
        """Read a file and return its contents."""
        with open(os.path.join(self.src_dir, filename), 'rb') as fileObj:
            try:
                return fileObj.read().decode('utf-8')
            except UnicodeDecodeError:
                # return binary data
                return fileObj.read()

    def read_json_file(self, filename):
        """Read JSON file from the data_input source."""
        with open(os.path.join(self.src_dir, filename)) as json_fileobj:
            return json.load(json_fileobj)

    def download_file(self, src, target):
        """Download a file from data_store."""
        with open(os.path.join(self.src_dir, src), 'rb') as inf, open(target, 'wb') as out:
            out.write(inf.read())

    def read_into_file(self, filename):
        """Read from S3 and return stream as a file object."""
        return open(os.path.join(self.src_dir, filename), 'rb')
