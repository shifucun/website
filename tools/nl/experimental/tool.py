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


import json
import re

def camel_case_to_spaces(input_str):
    # Insert a space before all caps and convert the whole string to lowercase
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', input_str).lower()


def generate_output_json():
  with open('cprop_map.json') as f:
    pop_type_map = json.load(f)
    output = {}
    for item, dcids in pop_type_map.items():
      value = item
      if "drug/dea" in value:
        value = dcids[0].split('_')[-1]
      output[item] = [
        camel_case_to_spaces(value)
      ]
    with open('output.json', 'w') as out:
      json.dump(output, out)

def convert_output_json():
  result = []
  with open('tmp.json') as f:
    input = json.load(f)
    for concept, values in input.items():
      item = {
        'concept': concept,
        'type': 'property_value',
        'descriptions': values
      }
      result.append(item)
  with open('result.json', 'w') as out:
    json.dump(result, out)


if __name__ == '__main__':
  convert_output_json()