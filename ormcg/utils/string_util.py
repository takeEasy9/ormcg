# -*- coding: utf-8 -*-

"""
@author: takeEasy9
@description: common methods for string
@version: 1.0.0
@since: 2024/4/30 19:31
"""

import string

from ormcg.utils.constant_util import ConstantUtil


def to_camel_case(column_name: string, abbr_replace=True):
    words = column_name.split('_')
    for i in range(1, len(words)):
        tmp = words[i].lower()
        if abbr_replace \
                and tmp in ConstantUtil.COLUMN_NAME_ABBREVIATION_REPLACE:
            tmp = ConstantUtil.COLUMN_NAME_ABBREVIATION_REPLACE.get(tmp)
        words[i] = tmp.capitalize()
    return words[0] + ''.join(words[1:])


def first_upper_case(s: str):
    if s:
        return s[:1].upper() + s[1:]
    else:
        return s


def first_lower_case(s: str):
    if s:
        return s[:1].lower() + s[1:]
    else:
        return s


def substr(s, t, alt):
    first = s.find(t)
    if first == -1:
        first = s.find(alt)
    return s[:first]
