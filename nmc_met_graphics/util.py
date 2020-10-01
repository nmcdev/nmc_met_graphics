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

    if key not in kwargs:
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
        '中国及周边': [50, 160, 0, 70], '东部海域': [115, 135, 20, 42],
        '南部海域': [103, 125, 3, 28], '华北': [103, 129, 30, 50],
        '东北': [103, 140, 32, 58], '华东': [107, 130, 20, 41],
        '华中': [100, 123, 22, 42], '华南': [100, 126, 12, 30],
        '西南': [90, 113, 18, 38], '西北': [89, 115, 27, 47],
        '新疆': [70, 101, 30, 52], '青藏': [68, 105, 18, 46]}
    return map_region


def get_map_global_regions():
    """
    Get the map region lon/lat limits.

    Returns:
        Dictionary: the region limits, 'name': [lonmin, lonmax, latmin, latmax]
    """
    map_region = get_map_regions()
    map_region.update({
        '全球': [-180, 180, -90, 90], '亚洲': [35, 140, 5, 80],
        '东亚': [90, 160, 5, 70], '南亚': [65, 135, -10, 35],
        '中亚': [25, 80, 10, 55], '欧洲': [-15, 35, 28, 72],
        '非洲': [-20, 55, -40, 40], '北美': [-140, -55, 10, 65],
        '南美': [-90, -30, -58, 14], '澳洲': [110, 180, -50, 0]})
    return map_region


def get_map_region(name):
    """
    Get the map region lon/lat limit with the given name.
    """
    if not isinstance(name, str):
        return check_map_region(name)
    map_regions = get_map_regions()
    if name in map_regions:
        return map_regions[name]
    else:
        print('{} is not a valid region name. Select from {}.'.format(
            name, ','.join(map_regions.keys())))
        return map_regions[1]


def check_map_region(map_region):
    """
    Check the map_region format, [lonmin, lonmax, latmin, latmax].
    """
    default_map_region = [73., 136, 15, 56]
    if len(map_region) != 4:
        print("The map_region length should be 4, [lonmin, lonmax, latmin, latmax].")
        return default_map_region
    if (not (-360 <= map_region[0] <= 360)) or \
       (not (-360 <= map_region[1] <= 360)) or \
       (map_region[0] >= map_region[1]):
       print("The map_region longitude range is not valid.")
       return default_map_region
    if (not (-90 <= map_region[2] <= 90)) or \
       (not (-90 <= map_region[3] <= 90)) or \
       (map_region[2] >= map_region[3]):
       print("The map_region latitude range is not valid.")
       return default_map_region
    return map_region


def check_region_to_contour(map_region, cnt1, cnt2, thred=600):
    """
    根据区域范围的大小来判断等值线的间隔.
    if map_region area >= thred, return cnt1
    if map_region area < thred, return cnt2

    Args:
        map_region (list): [lonmin, lonmax, latmin, latmax]
    """
    
    if map_region is None:
        return cnt1
    map_area = abs(map_region[1] - map_region[0]) * abs(map_region[3] - map_region[2])
    if map_area >= thred:
        return cnt1
    else:
        return cnt2
