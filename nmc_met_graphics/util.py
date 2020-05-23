# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Some Utility functions.
"""

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


def get_map_region(name='CHINA'):

    map_region = {
        'CHINA': [70, 140, 8, 60],
        'CHINA_LAND': [73, 136, 16, 55],
        'CHINA_LARGE': [50, 160, 6, 60],
        'HUABEI': [103, 129, 31, 47],
        'DONGBEI': [103, 34, 140, 55]
    }
