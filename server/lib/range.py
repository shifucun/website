# Copyright 2020 Google LLC
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

from collections import defaultdict
import math
import re

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(lineno)d : %(message)s')

NUM_RANGE = 9

STAT_VAR_RANGE = {
    "age": (re.compile("Count_Person_(.*)Years"), "Count_Person_{}Years")
}


class Range(object):
    """Represents a range object with low and high."""

    def __init__(self, low, high):
        self.low = low
        self.high = high
        self.children = [self]

    def __hash__(self):
        return hash('{}^{}'.format(self.low, self.high))

    def __eq__(self, other):
        return self.low == other.low and self.high == other.high

    def __repr__(self):
        return '({}, {})'.format(self.low, self.high)

    def add_child(self, child):
        """Add a child and grow the range.

        The child range must be connected with the current range.
        """
        if child.low != self.high + 1:
            return False
        self.high = child.high
        self.children.append(child)
        return True

    def span(self):
        return self.high - self.low

    def to_stat_var(self, format_str):
        """Convert a range to stat var string."""
        if self.low == 0:
            part = 'Upto' + str(self.high)
        elif self.high == math.inf:
            part = str(self.low) + 'OrMore'
        else:
            part = '{}To{}'.format(self.low, self.high)
        return format_str.format(part)


def from_string(s):
    """Construct a range from string"""
    if len(s.split('To')) == 2:
        return Range(int(r.split('To')[0]), int(r.split('To')[1]))
    if s.startswith('Upto'):
        return Range(0, int(r.replace('Upto', '')))
    if s.endswith('OrMore'):
        return Range(int(r.replace('OrMore', '')), math.inf)
    return Range(int(r), int(r))


def from_stat_var(stat_var, regex):
    """Convert a stat var to a range tuple with low and high value."""
    p = regex.search(stat_var)
    if p:
        return from_string(p.group(1))
    raise ValueError("Invalid stat_var %s", stat_var)


def expand(range_lists, next_range_map):
    result = []
    complete = True
    for l in range_lists:
        last_item = l[-1]
        if last_item in next_range_map:
            complete = False
            for next_item in next_range_map[last_item]:
                result.append(l + [next_item])
        else:
            result.append(l)
    return result, complete


def build_range_list(ranges):
    """Build list of continous range list from input ranges.

    Args:
        ranges: a list of range in the form of a two value tuple, ex:
            [(0, 5), (6, 10), (21, 40), (11, 20), (21, math.inf)]
    Returns:
        A list of list of ranges.
    """
    ranges = sorted(ranges, key=lambda r: (r.low, r.high))

    # A map from the low value to a list of ranges.
    low_to_range = defaultdict(list)
    for r in ranges:
        low_to_range[r.low].append(r)

    # Find the connected ranges.
    next_range_map = defaultdict(list)
    for r in ranges:
        if r.high + 1 in low_to_range:
            next_range_map[r] = low_to_range[r.high + 1]

    # Build linked range groups.
    range_lists = [[ranges[0]]]
    while True:
        range_lists, complete = expand(range_lists, next_range_map)
        if complete:
            break
    range_lists.sort(key=lambda x: len(x))
    return range_lists


def aggregate_range(range_list):
    # Aggregate range if needed
    span = range_list[-1].low - range_list[0].low
    average_span = span / NUM_RANGE
    result = [range_list[0]]
    for r in range_list[1:]:
        current_span = result[-1].span()
        item_span = r.span()
        if (item_span < average_span and current_span < average_span and
                item_span + current_span < 1.5 * average_span):
            result[-1].add_child(r)
        else:
            result.append(r)
    for r in result:
        logging.info("%s, %s", r, r.children)
    return result


# def find_common_aggregated_stat_var(stat_vars_list, range_type):
#     """Build a continous and better ranged quantity range stat var.

#     Argument:
#         stat_vars_list: A list of list of stat vars. Each inner list represents
#         a cohort of stat vars of quantity range to be concatenated and
#         aggregated. The final result should be a common aggregation for all
#         the cohort.
#     Returns:
#         A map from computed stat var to input stat var list.

#     """
#     regex, fmt = STAT_VAR_RANGE[range_type]
#     for stat_vars in stat_vars_list:
#         range_list = [
#             stat_var_to_range(stat_var, regex) for stat_var in stat_vars
#         ]
#     range_groups = concat_aggregate_range(ranges)
#     result = {}
#     for group in range_groups:
#         if len(group) == 1:
#             sv = range_to_stat_var(group[0], fmt)
#             result[sv] = [sv]
#         else:
#             low = group[0][0]
#             high = group[-1][1]
#             key = range_to_stat_var((low, high), fmt)
#             result[key] = [range_to_stat_var(item, fmt) for item in group]
#     return result