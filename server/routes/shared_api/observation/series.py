# Copyright 2022 Google LLC
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

import logging
import math

from flask import Blueprint
from flask import request

from server.lib import fetch
from server.lib import shared
from server.lib.cache import cache
from server.routes import TIMEOUT

# Maximum number of concurrent series the server will fetch
_MAX_BATCH_SIZE = 2000

# Maps enclosed place type -> places with too many of the enclosed type
# Determines when to make batched API calls to avoid server errors.
_BATCHED_CALL_PLACES = {
    "CensusTract": [
        "geoId/06",  # California
        "geoId/12",  # Florida
        "geoId/36",  # New York (State)
        "geoId/48",  # Texas
    ],
    "City": ["country/USA"],
    "County": ["country/USA"]
}

# Define blueprint
bp = Blueprint("series", __name__, url_prefix='/api/observations/series')


@bp.route('', strict_slashes=False)
@cache.cached(timeout=TIMEOUT, query_string=True)
def series():
  """Handler to get preferred time series given multiple stat vars and entities."""
  entities = list(filter(lambda x: x != "", request.args.getlist('entities')))
  variables = list(filter(lambda x: x != "", request.args.getlist('variables')))
  if not entities:
    return 'error: must provide a `entities` field', 400
  if not variables:
    return 'error: must provide a `variables` field', 400
  facet_ids = list(filter(lambda x: x != "", request.args.getlist('facetIds')))
  return fetch.series_core(entities, variables, False, facet_ids)


@bp.route('/all')
@cache.cached(timeout=TIMEOUT, query_string=True)
def series_all():
  """Handler to get all the time series given multiple stat vars and places."""
  entities = list(filter(lambda x: x != "", request.args.getlist('entities')))
  variables = list(filter(lambda x: x != "", request.args.getlist('variables')))
  if not entities:
    return 'error: must provide a `entities` field', 400
  if not variables:
    return 'error: must provide a `variables` field', 400
  return fetch.series_core(entities, variables, True)


@bp.route('/within')
@cache.cached(timeout=TIMEOUT, query_string=True)
def series_within():
  """Gets the observation for child entities of a certain type contained in a
  parent entity at a given date.

  Note: the preferred facet is returned.
  """
  parent_entity = request.args.get('parentEntity')
  if not parent_entity:
    return 'error: must provide a `parentEntity` field', 400

  child_type = request.args.get('childType')
  if not child_type:
    return 'error: must provide a `childType` field', 400

  variables = list(filter(lambda x: x != "", request.args.getlist('variables')))
  if not variables:
    return 'error: must provide a `variables` field', 400

  facet_ids = list(filter(lambda x: x != "", request.args.getlist('facetIds')))

  # Make batched calls there are too many child places for server to handle
  batch_size = _MAX_BATCH_SIZE // len(variables)
  if parent_entity in _BATCHED_CALL_PLACES.get(child_type, []):
    try:
      logging.info("Fetching child places series in batches")
      child_places = fetch.descendent_places([parent_entity],
                                             child_type).get(parent_entity, [])
      merged_response = {}
      batch_count = 1
      for batch in shared.divide_into_batches(child_places, batch_size):
        logging.info(
            f"Batch {batch_count} of {math.ceil(len(child_places) / batch_size)}"
        )
        new_response = fetch.series_core(batch, variables, False, facet_ids)
        merged_response = shared.merge_responses(merged_response, new_response)
        batch_count += 1
      return merged_response, 200
    except Exception as e:
      logging.error(e)
      return 'error: Error encountered when attempting to make batch calls', 400
  return fetch.series_within_core(parent_entity, child_type, variables, False,
                                  facet_ids)


@bp.route('/within/all')
@cache.cached(timeout=TIMEOUT, query_string=True)
def series_within_all():
  """Gets the observation for child entities of a certain type contained in a
  parent entity at a given date.

  Note: all the facets are returned.
  """
  parent_entity = request.args.get('parentEntity')
  if not parent_entity:
    return 'error: must provide a `parentEntity` field', 400

  child_type = request.args.get('childType')
  if not child_type:
    return 'error: must provide a `childType` field', 400

  variables = list(filter(lambda x: x != "", request.args.getlist('variables')))
  if not variables:
    return 'error: must provide a `variables` field', 400

  return fetch.series_within_core(parent_entity, child_type, variables, True)
