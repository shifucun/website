# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import hashlib
import os
import unittest

from nl_server import config_reader
from shared.lib import gcs


class TestIntegrity(unittest.TestCase):
  """Check that the index in catalog.yaml is up to date.

  Read the md5sum of each index index and check it against the _preindex.csv in
  the input directory.
  """

  def test_md5sum(self):
    catalog = config_reader.read_catalog

    for embeddings_name, index_config in catalog().indexes.items():
      if embeddings_name == 'medium_ft':
        continue
      embeddings_dir = os.path.dirname(index_config.embeddings_path)
      md5sum_path = os.path.join(embeddings_dir, 'md5sum.txt')
      if gcs.is_gcs_path(md5sum_path):
        md5sum_path = gcs.maybe_download(md5sum_path)
      with open(md5sum_path) as f:
        got_md5sum = f.read().strip()
      with open(os.path.join(index_config.source_path, '_preindex.csv')) as f:
        expected_md5sum = hashlib.md5(f.read().encode('utf-8')).hexdigest()
      self.assertEqual(got_md5sum, expected_md5sum)
