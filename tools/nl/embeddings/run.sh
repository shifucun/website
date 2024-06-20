#!/bin/bash
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Usage function
usage() {
  echo "Usage: $0 --embeddings_name <embeddings-name> --gcs_root <gcs-root>"
  exit 1
}

# Parse options
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --embeddings_name)
        embeddings_name="$2"
        shift 2
        ;;
    --gcs_root)
        gcs_root="$2"
        shift 2
        ;;
    *)
        echo "Unknown option: $1"
        usage
        ;;
  esac
done

if [ -z "$gcs_root" ]; then
  gcs_root="gs://datcom-nl-models"
fi

# Print options
echo "Embeddings name: $embeddings_name"
echo "GCS root: $gcs_root"

cd ../../..
python3 -m venv .env
source .env/bin/activate
pip3 install -r nl_server/requirements.txt -q
pip3 install -r tools/nl/embeddings/requirements.txt -q

export TOKENIZERS_PARALLELISM=false

python3 -m tools.nl.embeddings.build_embeddings \
  --embeddings_name=$embeddings_name \
  --gcs_root=$gcs_root

deactivate
cd tools/nl/embeddings