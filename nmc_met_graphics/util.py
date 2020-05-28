# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Some Utility functions.
"""

import math

def check_kwargs(kwargs, key, default):
    """
    Check the key is in kwargs or not. If not, =default.

    Args:
        kwargs (dictionary): kwargs dictionary.
        key (string): key name.
        default (object): python object.
    """

    if not key in kwargs.keys():
            kwargs[key] = default

    return kwargs


def get_map_regions():
    """
    Get the map region lon/lat limits.

    Returns:
        Dictionary: the region limits, 'name': [lonmin, lonmax, latmin, latmax]
    """

    map_region = {
        '中国': [70, 140, 8, 60], '中国陆地': [73, 136, 15, 56],
        '中国及周边': [50, 160, 0, 70], '华北': [103, 129, 30, 50],
        '东北': [103, 140, 32, 58], '华东': [107, 130, 20, 41],
        '华中': [100, 123, 22, 42], '华南': [100, 126, 12, 30],
        '西南': [90, 113, 18, 38], '西北': [89, 115, 27, 47],
        '新疆': [70, 101, 30, 52], '青藏': [68, 105, 18, 46]}

    return map_region
