# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Some Utility functions.
"""


from datetime import datetime
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from nmc_met_graphics.cmap import cm


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


def check_initTime(initTime):
    """
    Check the initTime format, return a datetime object.
    """
    if initTime is None: return initTime
    if isinstance(initTime, datetime):
        return initTime
    if isinstance(initTime, str):
        try:
            initTime = datetime.strptime(initTime, "%y%m%d%H")
            return initTime
        except Exception:
            pass
        try:
            initTime = datetime.strptime(initTime, "%Y%m%d%H")
            return initTime
        except Exception:
            pass
    print('The initTime should be like "2020061208" and format is YYYYmmddHH.')
    return None


def check_model(model, model_dirs):
    """
    Check the given model dose supported or not.
    """
    model = model.upper()
    if model in model_dirs:
        return model_dirs[model]
    else:
        print('{} dose not supported. Please select {}'.format(
            model, ','.join(model_dirs.keys())))
        return None


def check_frange(frange):
    """
    Check the forecast hour range.
    """
    if frange is None: return None
    # check the length
    if (len(frange) < 2) or (len(frange) > 3):
        print("frange should be [start, end(, step)]. If step doesn't given, step=6.")
        return None
    # check the order
    if frange[0] > frange[1]:
        print("frange[0] should be less than frange[1].")
        return None
    step = 6 if len(frange) < 3 else frange[2]
    fhours = list(range(frange[0], frange[1]+1, step))
    return fhours


def get_map_regions():
    """
    Get the map region lon/lat limits.

    Returns:
        Dictionary: the region limits, 'name': (lonmin, lonmax, latmin, latmax)
    """
    map_region = {
        '中国': (70, 140, 8, 60), '中国陆地': (73, 136, 15, 56),
        '中国及周边': (50, 160, 0, 70), '东部海域': (115, 135, 20, 42),
        '南部海域': (103, 125, 3, 28), '华北': (103, 129, 30, 50), '冬奥': (114,118,39,42),
        '东北': (103, 140, 32, 58), '华东': (107, 130, 20, 41),
        '华中': (100, 123, 22, 42), '华南': (100, 126, 12, 30),
        '西南': (90, 113, 18, 38), '西北': (89, 115, 27, 47),
        '新疆': (70, 101, 30, 52), '青藏': (68, 105, 18, 46),
        '河南': (109.8, 117, 31, 37.5), '四川盆地': (102.5, 110, 27.5, 33)}
    return map_region


def get_map_global_regions():
    """
    Get the map region lon/lat limits.

    Returns:
        Dictionary: the region limits, 'name': (lonmin, lonmax, latmin, latmax)
    """
    map_region = get_map_regions()
    map_region.update({
        '全球': (-180, 180, -90, 90), '亚洲': (35, 140, 5, 80),
        '东亚': (90, 160, 5, 70), '南亚': (65, 135, -10, 35),
        '中亚': (25, 80, 10, 55), '欧洲': (-15, 35, 28, 72),
        '非洲': (-20, 55, -40, 40), '北美': (220, 305, 10, 65),
        '南美': (270, 330, -58, 14), '澳洲': (110, 180, -50, 0)})
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


def get_plot_attrs(name, clevs=None, min_lev=None, extend='max'):
    """
    获得预先设置的各种变量绘图属性.

    Args:
        name (str): the name of predefined plot attributes.

    Returns:
        dict: plot attribute dictionary.
    """

    # convert to lower
    name = name.lower()
    
    if name == 'z_500_contour':
        if clevs is None:
            clevs = np.concatenate((np.arange(480, 580, 4), np.arange(580, 604, 4)))
        clevs = np.asarray(clevs)
        linewidths = np.full(len(clevs), 1)
        linewidths[clevs == 588] = 2
        return {"levels":clevs, "linewidths":linewidths}
    
    elif name == 'qpf_1h_contourf_blues':
        if clevs is None:
            clevs = [0.1, 4, 13, 25, 60, 120, 250]
        clevs = np.asarray(clevs)
        cmap = cm.truncate_colormap('Blues', minval=0.1)
        norm = mpl.colors.BoundaryNorm(clevs, cmap.N, extend=extend)
        return {'clevs':clevs, 'cmap':cmap, 'norm':norm}
    
    elif name == 'nmc_accumulated_rainfall':
        if clevs is None:
            clevs = [0.1, 10, 25, 50, 100, 250, 400, 600, 800, 1000]
        clevs = np.asarray(clevs)
        _colors = [[161, 241, 141], [61, 186, 61], [96,  184, 255], [0,   0,   255],
                  [250, 0,   250], [128, 0,   64], [255, 170, 0], [255, 102, 0],
                  [230, 0,   0], [80,  45,  10]]
        _colors = np.asarray(_colors)/255.0
        if min_lev is not None:
            idx = np.where(clevs >= min_lev)
            clevs = clevs[idx]
            _colors = _colors[idx,]
        cmap, norm = mpl.colors.from_levels_and_colors(clevs, _colors, extend=extend)
        return {'clevs':clevs, 'cmap':cmap, 'norm':norm}
    
    elif name == 'ecmf_accumulated_rainfall':
        if clevs is None:
            clevs = [0.5, 10, 30, 50, 70, 100, 130, 160]
        clevs = np.asarray(clevs)
        _colors = np.array(['#a7aaaa', '#5cc8d7', '#3076bc', '#6aaa43',
                            '#f5832a', '#ee2f2d', '#8350a0', '#231f20'])
        if min_lev is not None:
            idx = np.where(clevs >= min_lev)
            clevs = clevs[idx]
            _colors = _colors[idx]
        cmap, norm = mpl.colors.from_levels_and_colors(clevs, _colors, extend=extend)
        return {'clevs':clevs, 'cmap':cmap, 'norm':norm}
    
    elif name == 'probability_forecast':
        if clevs is None:
            clevs = [1,5,10,20,30,40,50,60,70,80,90,95,100]
        clevs = np.asarray(clevs)
        cmap = cm.guide_cmaps(44)
        cmap = cm.truncate_colormap(cmap, maxval=0.95)
        norm = mpl.colors.BoundaryNorm(clevs, cmap.N, extend=extend)
        return {'clevs':clevs, 'cmap':cmap, 'norm':norm}
    
    elif name == 'ndfd_t_summer':
        if clevs is None:
            clevs = np.arange(0, 35, 2)
        clevs = np.asarray(clevs)
        cmap = cm.ndfd_cmaps('T_summer')
        norm = mpl.colors.BoundaryNorm(clevs, cmap.N, extend=extend)
        return {'clevs':clevs, 'cmap':cmap, 'norm':norm}
    
    elif name == '2m_temperature':
        if clevs is None:
            clevs = [-45, -30, -20, -10,  -5,   0,   0, 
                     5,   5,  10,  20,  20,  30,  30,  40 , 45]
        clevs = np.asarray(clevs)
        r = np.asarray([ 61, 250,  9,   94,  46,   6, 254, 32,   11,   0, 173, 254, 255, 255,  90, 253])
        g = np.asarray([  2,   0,  0,  157,  94, 249, 254, 178, 244,  97, 255, 254, 140,  99,   3, 253])
        b = np.asarray([ 57, 252, 121, 248, 127, 251, 254, 170,  11,   3,  47,   0,   0,  61,   3, 253])
        _colors = np.stack((r,g,b), axis=-1)
        _colors = np.asarray(_colors)/255.0
        if min_lev is not None:
            idx = np.where(clevs >= min_lev)
            clevs = clevs[idx]
            _colors = _colors[idx,]
        cmap, norm = mpl.colors.from_levels_and_colors(clevs, _colors, extend=extend)
        return {'clevs':clevs, 'cmap':cmap, 'norm':norm}
    
    else:
        raise ValueError('{} is not supported.'.format(name))

