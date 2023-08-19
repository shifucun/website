# Copyright 2023 Google LLC
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

# Chart structure for the place comparison page.

import server.lib.explore.existence as exist
from server.lib.explore.page_type.builder import Builder
from server.lib.nl.config_builder import bar
import server.lib.nl.fulfillment.types as ftypes


def add_sv(sv: str, chart_vars: ftypes.ChartVars, state: ftypes.PopulateState,
           builder: Builder):
  sv_spec = {}
  places = state.uttr.places

  chart_vars.include_percapita = False

  # Main SV existence checks.
  exist_places = [
      p for p in places if exist.svs4place(state, p, [sv]).exist_svs
  ]
  # Main existence check
  if len(exist_places) <= 1:
    return {}
  sv_spec.update(
      bar.multiple_place_bar_block(column=builder.new_column(chart_vars),
                                   places=exist_places,
                                   svs=[sv],
                                   sv2thing=builder.sv2thing,
                                   cv=chart_vars,
                                   nopc_vars=builder.nopc()))

  return sv_spec


def add_svpg(chart_vars: ftypes.ChartVars, state: ftypes.PopulateState,
             builder: Builder):
  places = state.uttr.places
  sv_spec = {}

  chart_vars.include_percapita = False
  # Pick SVs that satisfy all places.
  exist_svs = []
  for sv in chart_vars.svs:
    if all([bool(exist.svs4place(state, p, [sv]).exist_svs) for p in places]):
      exist_svs.append(sv)
  if len(exist_svs) <= 1:
    return {}
  sv_spec.update(
      bar.multiple_place_bar_block(column=builder.new_column(chart_vars),
                                   places=places,
                                   svs=exist_svs,
                                   sv2thing=builder.sv2thing,
                                   cv=chart_vars,
                                   nopc_vars=builder.nopc()))
  return sv_spec
