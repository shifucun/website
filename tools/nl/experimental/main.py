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

import pandas as pd
import os
import json
import collections
import torch
from flask import Flask

from stat_config_pb2 import PopObsSpecList
from google.protobuf import text_format
from sentence_transformers import SentenceTransformer
from torch.nn.functional import cosine_similarity


app = Flask(__name__)

def get_dpv_spec_list():
  all_dpv_spec_list = []
  for root, _, files in os.walk('dpv'):
    for file in files:
      if file.endswith('.textproto'):
        with open(os.path.join(root, file), 'r') as f:
          data = f.read()
          spec_list = PopObsSpecList()
          text_format.Parse(data, spec_list)
          all_dpv_spec_list.extend(spec_list.spec)
  return all_dpv_spec_list


def build_dpv_lookup_table():
  dpv_spec_list = get_dpv_spec_list()
  result = {}
  for s in dpv_spec_list:
    dpv_dict = {x.prop: x.val for x in s.dpv}
    cprops = s.cprop
    dprops = dpv_dict.keys()
    all_props = sorted(list(cprops) + list(dprops))

    if not s.obs_props:
      key = (s.pop_type,) + tuple(all_props)
      result[key] = {
        'dpv': dpv_dict,
        'cprops': s.cprop
      }
    else:
      for obs_prop in s.obs_props:
        key = (s.pop_type, obs_prop.mprop) + tuple(all_props)
        result[key] = {
          'dpv': dpv_dict,
          'cprops': s.cprop
        }
  return result


def read_sv_info():
  dpv_lookup_table = build_dpv_lookup_table()
  result = {}
  with open('nl_sv_info.json') as f:
    sv_info = json.load(f)
    for info in sv_info:
      id = info['id']
      item = {
        'population_type': info['population_type'],
        'measured_prop': info['measured_prop'],
        'pv': {}
      }
      for i in range(1, 9):
        pname = 'p' + str(i)
        vname = 'v' + str(i)
        if info[pname]:
          item['pv'][info[pname]] = info[vname]
      all_props = sorted(item['pv'].keys())
      item['cprops'] = all_props

      # Add dpv info
      key1 = (info['population_type'], ) + tuple(all_props)
      key2 = (info['population_type'], info['measured_prop']) + tuple(all_props)
      if key1 in dpv_lookup_table or key2 in dpv_lookup_table:
        has_dpv = True
        dpv = dpv_lookup_table.get(key1, {}) or dpv_lookup_table.get(key2, {})
        for dp, dv in dpv['dpv'].items():
          if item['pv'][dp] != dv:
            has_dpv = False
            break
        if has_dpv:
          item['cprops'] = dpv['cprops']
      result[id] = item
  return result


def has_dpv(sv_info, dpv_lookup_table):
  all_props = sorted(sv_info['pv'].keys())
  key1 = (sv_info['population_type'], ) + tuple(all_props)
  key2 = (sv_info['population_type'], sv_info['measured_prop']) + tuple(all_props)
  if key1 not in dpv_lookup_table and key2 not in dpv_lookup_table:
    dpv = dpv_lookup_table.get(key1, {}) or dpv_lookup_table.get(key2, {})
    for dp, dv in dpv.items():
      if sv_info['pv'][dp] == dv:
        return False

def generate_json():
  sv_info_map = read_sv_info()
  pop_type_map = collections.defaultdict(list)
  mprop_map = collections.defaultdict(list)
  cprop_map = collections.defaultdict(list)
  for id, info in sv_info_map.items():
    pop_type_map[info['population_type']].append(id)
    mprop_map[info['measured_prop']].append(id)
    for prop in info['cprops']:
      cprop_map[info['pv'][prop]].append(id)

  with open('pop_type_map.json', 'w') as f:
    json.dump(pop_type_map, f)
  with open('mprop_map.json', 'w') as f:
    json.dump(mprop_map, f)
  with open('cprop_map.json', 'w') as f:
    json.dump(cprop_map, f)


def build_embddings_df():
  model = SentenceTransformer('ft_final_v20230717230459.all-MiniLM-L6-v2')
  with open('concept.json') as f:
    all_concept = json.load(f)
    concept_list = []
    type_list = []
    description_list = []
    for item in all_concept:
      for desc in item['descriptions']:
        concept_list.append(item['concept'])
        type_list.append(item['type'])
        description_list.append(desc)
    df = pd.DataFrame({
      'concept': concept_list,
      'type': type_list,
      'description': description_list
      })
    embeddings = model.encode(df['description'].values)

    df = pd.concat([df, pd.DataFrame(embeddings)], axis=1)
    df.to_csv('embeddings.csv')


model = SentenceTransformer('ft_final_v20230717230459.all-MiniLM-L6-v2')
df = pd.read_csv('embeddings.csv')

def pick_and_rank(query, k):
  score = cosine_similarity(
    torch.tensor(model.encode(query).reshape((1,-1)), dtype=torch.float32),
    torch.tensor(df.iloc[:, -384:].to_numpy(), dtype=torch.float32)
  )
  series = pd.Series(score.numpy())
  top_k = series.nlargest(k)
  result = df.loc[top_k.index, df.columns[:4]]
  return pd.concat([result, top_k.rename('score')], axis=1)


@app.route('/<query>')
def home(query):
  df = pick_and_rank(query, 40)
  return df.to_html()

if __name__ == "__main__":
  app.run(debug=True)
