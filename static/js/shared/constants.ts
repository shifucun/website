/**
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { NamedTypedPlace } from "../tools/map/context";

export const USA_PLACE_DCID = "country/USA";
export const INDIA_PLACE_DCID = "country/IND";
export const EUROPE_PLACE_DCID = "europe";

export const EARTH_NAMED_TYPED_PLACE: NamedTypedPlace = {
  dcid: "Earth",
  name: "Earth",
  types: ["Planet"],
};

export const MAX_YEAR = "2050";
export const MAX_DATE = "2050-06";
