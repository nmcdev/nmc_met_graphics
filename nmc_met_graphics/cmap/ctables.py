# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Define customer color maps.
"""

import numpy as np
import matplotlib as mpl
from nmc_met_graphics.cmap.cm import make_cmap


def cm_precipitation_metpy():
    """
    https://unidata.github.io/python-gallery/examples/Precipitation_Map.html
    :return:
    """
    colors = [
        (1.0, 1.0, 1.0),
        (0.3137255012989044, 0.8156862854957581, 0.8156862854957581),
        (0.0, 1.0, 1.0), (0.0, 0.8784313797950745, 0.501960813999176),
        (0.0, 0.7529411911964417, 0.0),
        (0.501960813999176, 0.8784313797950745, 0.0), (1.0, 1.0, 0.0),
        (1.0, 0.6274510025978088, 0.0),
        (1.0, 0.0, 0.0), (1.0, 0.125490203499794, 0.501960813999176),
        (0.9411764740943909, 0.250980406999588, 1.0),
        (0.501960813999176, 0.125490203499794, 1.0),
        (0.250980406999588, 0.250980406999588, 1.0),
        (0.125490203499794, 0.125490203499794, 0.501960813999176),
        (0.125490203499794, 0.125490203499794, 0.125490203499794),
        (0.501960813999176, 0.501960813999176, 0.501960813999176),
        (0.8784313797950745, 0.8784313797950745, 0.8784313797950745),
        (0.9333333373069763, 0.8313725590705872, 0.7372549176216125),
        (0.8549019694328308, 0.6509804129600525, 0.47058823704719543),
        (0.6274510025978088, 0.42352941632270813, 0.23529411852359772),
        (0.4000000059604645, 0.20000000298023224, 0.0)]
    return mpl.colors.ListedColormap(colors, 'precipitation')


def cm_precipitation_nws(atime=24):
    """
    http://jjhelmus.github.io/blog/2013/09/17/plotting-nsw-precipitation-data/

    :param atime: accumulative time period.
    :return: colormap function, normalization boundary.
    """

    if atime == 1:
        clevs = [0.01, 1, 2, 3, 4, 6, 8, 10, 15, 20, 30, 40, 60, 80, 100]
    elif atime == 3:
        clevs = [0.01, 1, 2, 3, 4, 6, 8, 10, 15, 20, 30, 40, 60, 80, 100]
    elif atime == 6:
        clevs = [0.01, 1, 3, 5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100, 120]
    else:
        clevs = [0.1, 2.5, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 250]
    colors = ["#04e9e7", "#019ff4", "#0300f4", "#02fd02",
              "#01c501", "#008e00", "#fdf802", "#e5bc00",
              "#fd9500", "#fd0000", "#d40000", "#bc0000",
              "#f800fd", "#dd1c77", "#9854c6"]
    cmap, norm = mpl.colors.from_levels_and_colors(clevs, colors, extend='max')
    return cmap, norm


def cm_rain_nws(atime=24, pos=None):
    """
    Rainfall color map.

    Keyword Arguments:
        atime {int} -- [description] (default: {24})
        pos {[type]} -- specify the color position (default: {None})
    """

    # set colors
    _colors = [
        [144, 238, 144], [0, 127, 0], [135, 206, 250],
        [0, 0, 255], [255, 0, 255], [127, 0, 0]
    ]
    _colors = np.array(_colors)/255.0
    if pos is None:
        if atime == 24:
            _pos = [0.1, 10, 25, 50, 100, 250, 800]
        elif atime == 6:
            _pos = [0.1, 4, 13, 25, 60, 120, 800]
        else:
            _pos = [0.01, 2, 7, 13, 30, 60, 800]
    else:
        _pos = pos
    cmap, norm = mpl.colors.from_levels_and_colors(_pos, _colors, extend='neither')
    return cmap, norm


def cm_qpf_nws(atime=24, pos=None):
    """
    Quantitative Precipitation Forecasts color map.

    Keyword Arguments:
        atime {int} -- [description] (default: {24})
        pos {[type]} -- specify the color position (default: {None})
    """

    # set colors
    _colors = ["#FFFFFF", "#BABABA", "#A6A1A1", "#7E7E7E", "#6C6C6C",
               "#B2F8B0", "#94F397", "#56EE6C", "#2EB045", "#249C3B", 
               "#2562C6", "#347EE4", "#54A1EB", "#94CEF4", "#B2EEF6", 
               "#FDF8B2", "#FDE688", "#FDBC5C", "#FD9E42", "#FB6234",
               "#FB3D2D", "#DD2826", "#BA1B21", "#9F1A1D", "#821519",
               "#624038", "#88645C", "#B08880", "#C49C94", "#F0DAD1",
               "#CBC4D9", "#A99CC1", "#9687B6", "#715C99", "#65538B",
               "#73146F", "#881682", "#AA19A4", "#BB1BB5", "#C61CC0",
               "#D71ECF"]

    # set precipitation accumultated time
    if pos is None:
        if atime == 24:
            _pos = np.concatenate((
                np.array([0, 0.1, 0.5, 1]), np.arange(2.5, 25, 2.5),
                np.arange(25, 50, 5), np.arange(50, 150, 10),
                np.arange(150, 475, 25)))
        elif atime == 6:
            _pos = np.concatenate(
                (np.array([0, 0.1, 0.5]), np.arange(1, 4, 1),
                 np.arange(4, 13, 1.5), np.arange(13, 25, 2),
                 np.arange(25, 60, 2.5), np.arange(60, 105, 5)))
        else:
            _pos = np.concatenate(
                (np.array([0, 0.01, 0.1]), np.arange(0.5, 2, 0.5),
                 np.arange(2, 8, 1), np.arange(8, 20, 2),
                 np.arange(20, 55, 2.5), np.arange(55, 100, 5)))
    else:
        _pos = pos

    # construct color map and normalized boundary
    cmap, norm = mpl.colors.from_levels_and_colors(_pos, _colors, extend='max')
    return cmap, norm


def cm_precip():
    """
    Standardized colormaps from National Weather Service
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/NWS_standard_cmap.py

    Range of values:
        metric: 0 to 762 millimeters
        english: 0 to 30 inches
    """
    # The amount of precipitation in inches
    a = [0,.01,.1,.25,.5,1,1.5,2,3,4,6,8,10,15,20,30]

    # Normalize the bin between 0 and 1 (uneven bins are important here)
    norm = [(float(i)-min(a))/(max(a)-min(a)) for i in a]

    # Color tuple for every bin
    C = np.array(
        [[255,255,255], [199,233,192], [161,217,155], [116,196,118], [49,163,83], 
        [0,109,44], [255,250,138], [255,204,79], [254,141,60], [252,78,42], 
        [214,26,28], [173,0,38], [112,0,38], [59,0,48], [76,0,115], [255,219,255]])

    # Create a tuple for every color indicating the normalized 
    # position on the colormap and the assigned color.
    COLORS = []
    for i, n in enumerate(norm):
        COLORS.append((n, np.array(C[i])/255.))

    # Create the colormap
    cmap = mpl.colors.LinearSegmentedColormap.from_list("precipitation", COLORS)

    return cmap


def cm_precip1():
    """
    generate maps from wrfout netCDF files
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/LukeM_colormap.py
    """

    precip_cdict ={
        'red':    ((0.000, 1.000, 1.000),
                (0.004, 0.914, 0.914),
                (0.012, 0.812, 0.812),
                (0.020, 0.514, 0.514),
                (0.040, 0.227, 0.227),
                (0.060, 0.114, 0.114),
                (0.080, 0.000, 0.000),
                (0.100, 0.012, 0.012),
                (0.120, 0.020, 0.020),
                (0.160, 0.031, 0.031),
                (0.200, 0.518, 0.518),
                (0.240, 1.000, 1.000),
                (0.280, 1.000, 1.000),
                (0.320, 1.000, 1.000),
                (0.360, 1.000, 1.000),
                (0.400, 0.702, 0.702),
                (0.500, 0.490, 0.490),
                (0.600, 0.294, 0.294),
                (0.700, 0.196, 0.196),
                (0.800, 0.980, 0.980),
                (1.000, 1.000, 1.000)),
        'green':    ((0.000, 1.000, 0.000),
                (0.004, 0.800, 0.800),
                (0.012, 0.502, 0.502),
                (0.020, 0.200, 0.200),
                (0.040, 0.000, 0.000),
                (0.060, 0.000, 0.000),
                (0.080, 0.000, 0.000),
                (0.100, 0.235, 0.235),
                (0.120, 0.467, 0.467),
                (0.160, 0.702, 0.702),
                (0.200, 0.851, 0.851),
                (0.240, 1.000, 1.000),
                (0.280, 0.667, 0.667),
                (0.320, 0.227, 0.227),
                (0.360, 0.000, 0.000),
                (0.400, 0.000, 0.000),
                (0.500, 0.000, 0.000),
                (0.600, 0.000, 0.000),
                (0.700, 0.000, 0.000),
                (0.800, 0.773, 0.773),
                (1.000, 1.000, 1.000)),
        'blue':        ((0.000, 1.000, 1.000),
                (0.004, 0.976, 0.976),
                (0.012, 0.875, 0.875),
                (0.020, 0.576, 0.576),
                (0.040, 0.690, 0.690),
                (0.060, 0.843, 0.843),
                (0.080, 1.000, 1.000),
                (0.100, 0.686, 0.686),
                (0.120, 0.372, 0.372),
                (0.160, 0.059, 0.059),
                (0.200, 0.031, 0.031),
                (0.240, 0.000, 0.000),
                (0.280, 0.000, 0.000),
                (0.320, 0.000, 0.000),
                (0.360, 0.000, 0.000),
                (0.400, 0.000, 0.000),
                (0.500, 0.000, 0.000),
                (0.600, 0.000, 0.000),
                (0.700, 0.000, 0.000),
                (0.800, 0.980, 0.980),
                (1.000, 1.000, 1.000))}
    precip_coltbl = mpl.colors.LinearSegmentedColormap('PRECIP_COLTBL',precip_cdict)
    return precip_coltbl


def cm_sleet_nws(atime=24, pos=None):
    """
    Sleet color map.

    Keyword Arguments:
        atime {int} -- [description] (default: {24})
        pos {[type]} -- specify the color position (default: {None})
    """

    # set colors
    _colors = [
        [253, 216, 213], [251, 174, 185], [247, 109, 163],
        [211, 41, 146], [146, 1, 122], [81, 0, 108]
    ]
    _colors = np.array(_colors)/255.0
    if pos is None:
        if atime == 24:
            _pos = [0.1, 10, 25, 50, 100, 250]
        elif atime == 6:
            _pos = [0.1, 4, 13, 25, 60, 120]
        else:
            _pos = [0.1, 2, 7, 13, 30, 60]
    else:
        _pos = pos
    cmap, norm = mpl.colors.from_levels_and_colors(_pos, _colors, extend='max')
    return cmap, norm


def cm_snow_nws(atime=24, pos=None):
    """
    Snowfall color map.

    Keyword Arguments:
        atime {int} -- [description] (default: {24})
        pos {[type]} -- specify the color position (default: {None})
    """

    # set colors
    _colors = [
        [234, 234, 234], [200, 200, 200], [154, 154, 154],
        [108, 108, 108], [58, 58, 58], [6, 6, 6]
    ]
    _colors = np.array(_colors)/255.0
    if pos is None:
        if atime == 24:
            _pos = [0.1, 2.5, 5, 10, 20, 30]
        elif atime == 6:
            _pos = [0.1, 1, 3, 5, 10, 15]
        else:
            _pos = [0.1, 1, 2, 4, 8, 12]
    else:
        _pos = pos
    cmap, norm = mpl.colors.from_levels_and_colors(_pos, _colors, extend='max')
    return cmap, norm


def cm_snow2():
    """
    generate maps from wrfout netCDF files
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/LukeM_colormap.py
    """

    snowf_cdict ={
        'red':  ((0.00, 0.91, 0.91),
                (0.06, 0.81, 0.81),
                (0.12, 0.51, 0.51),
                (0.18, 0.23, 0.23),
                (0.24, 0.11, 0.11),
                (0.30, 0.00, 0.00),
                (0.36, 0.02, 0.02),
                (0.42, 0.02, 0.02),
                (0.48, 0.03, 0.03),
                (0.54, 0.52, 0.52),
                (0.60, 1.00, 1.00),
                (0.66, 1.00, 1.00),
                (0.72, 1.00, 1.00),
                (0.78, 1.00, 1.00),
                (0.84, 0.70, 0.70),
                (0.90, 0.40, 0.40),
                (1.00, 0.20, 0.20)),
        'green':((0.00, 0.80, 0.80),
                (0.06, 0.50, 0.50),
                (0.12, 0.20, 0.20),
                (0.18, 0.00, 0.00),
                (0.24, 0.00, 0.00),
                (0.30, 0.00, 0.00),
                (0.36, 0.24, 0.24),
                (0.42, 0.47, 0.47),
                (0.48, 0.70, 0.70),
                (0.54, 0.85, 0.85),
                (0.60, 1.00, 1.00),
                (0.66, 0.67, 0.67),
                (0.72, 0.33, 0.33),
                (0.78, 0.00, 0.00),
                (0.84, 0.00, 0.00),    
                (0.90, 0.00, 0.00),
                (1.00, 0.00, 0.00)),
        'blue': ((0.00, 0.98, 0.98),
                (0.06, 0.87, 0.87),
                (0.12, 0.58, 0.58),
                (0.18, 0.69, 0.69),
                (0.24, 0.84, 0.84),
                (0.30, 1.00, 1.00),
                (0.36, 0.69, 0.69),
                (0.42, 0.37, 0.37),
                (0.48, 0.06, 0.06),
                (0.54, 0.03, 0.03),
                (0.60, 0.00, 0.00),
                (0.66, 0.00, 0.00),
                (0.72, 0.00, 0.00),
                (0.78, 0.00, 0.00),
                (0.84, 0.00, 0.00),
                (0.90, 0.00, 0.00),
                (1.00, 0.00, 0.00))}
    snowf_coltbl = mpl.colors.LinearSegmentedColormap('SNOWF_COLTBL',snowf_cdict)
    return snowf_coltbl


def cm_precipitation_type_nws(pos=None):
    """
    Precipitation type color map.

    Keyword Arguments:
        pos {[type]} -- specify the color position (default: {None})
    """
    _colors = [
        '#FFFFFF', '#4169E1', '#DC143C', '#708090', '#228B22',
        '#EE82EE', '#FFD700']
    # '无降水', '雨', '冻雨', '纯雪', '湿的雪', '雨夹雪', '冰粒'
    if pos is None:
        _pos = [0, 1, 3, 5, 6, 7, 8]
    else:
        _pos = pos
    cmap, norm = mpl.colors.from_levels_and_colors(_pos, _colors, extend='max')
    return cmap, norm


def cm_qsf_nws(atime=24, pos=None):
    """
    Quantitative Snow Forecasts color map.

    Keyword Arguments:
        atime {int} -- [description] (default: {24})
        pos {[type]} -- specify the color position (default: {None})
    """

    # set colors
    _colors = [
        '#BBBBBB', '#949494', '#6D6D6D', '4F4F52', '#97D0F6',
        '#76B5FA', '#50A5F1', '#4097EC', '2F7FE4', '#256AE5',
        '#1C64CA', '#155BBB', '#400A80', '4F0687', '#5A0888',
        '#6A0785', '#860C83', '#9F0F81', 'C9117C', '#C9117C',
        '#E31B73', '#E31B73', '#F33E96', 'FC5DAD', '#FD6CB1',
        '#F883BA', '#ED8EBF', '#EC93C5', 'EA9ACA', '#D7A8D1',
        '#D3B0D3', '#BFC6DC', '#B3D4E8', 'A5E4E9', '#9BEFF0',
        '#92F9F7', '#90F2F0', '#7ED9D8', '76B5C6', '#6FBBC3',
        '#7DB5C4', '#7FB2C6', '#89B1CB', '88ABC8', '#8CA8CB',
        '#91A8D3', '#92A8CF', '#95A0DB', '98A3D4', '#A19DDE',
        '#A39CD9', '#A99CD2', '#AB95E7', 'AF95ED', '#B394E3',
        '#BA8DE8', '#BA90E8', '#BF8DEC']

    # set precipitation accumultated time
    if pos is None:
        if atime == 24:
            _pos = np.concatenate((
                np.array([0.1]), np.arange(0.5, 15, 0.5),
                np.arange(15, 43, 1)))
        elif atime == 6:
            _pos = np.concatenate((
                np.array([0.1]), np.arange(0.5, 20, 0.5),
                np.arange(20, 38, 1)))
        else:
            _pos = np.concatenate((
                np.array([0.01]), np.arange(0.5, 25, 0.5),
                np.arange(25, 33, 1)))
    else:
        _pos = pos

    # construct color map and normalized boundary
    cmap, norm = mpl.colors.from_levels_and_colors(_pos, _colors, extend='max')
    return cmap, norm


def cm_snow_depth_nws(pos=None):
    """
    Snow depth color map.

    Keyword Arguments:
        pos {[type]} -- specify the color position (default: {None})
    """
    _colors = [
        '#FFFFFF', '#E0E0E0', '#C6C6C6', '#ADADAD', '#949494',
        '#A8E6F0', '#72BDD4', '#3F96B7', '#126F9C', '#0C47AA',
        '#2D63B6', '#4F80C3', '#749ECF', '#99BCDC', '#BFDAE9',
        '#C7ABD7', '#BF93CE', '#B77DC4', '#AE66BC', '#A650B2',
        '#9E3AA9', '#851547', '#942359', '#A4326C', '#B3427E',
        '#C35191', '#D462A4', '#E9A5B5', '#E69A9F', '#E48E8A',
        '#E18175', '#DF7660', '#DC6A4D', '#DA8056', '#DF946C',
        '#E4A781', '#EABB98', '#F0CFB0', '#F5E4C6', '#FAF8DE']
    if pos is None:
        _pos = np.concatenate((
            np.array([0, 0.1, 0.5]), np.arange(1, 12, 1),
            np.arange(12, 60, 4), np.arange(60, 100, 10),
            np.arange(100, 1100, 100)))

    # construct color map and normalized boundary
    cmap, norm = mpl.colors.from_levels_and_colors(_pos, _colors, extend='max')
    return cmap, norm


def cm_snow_density_nws(pos=None):
    """
    Snow density color map.

    Keyword Arguments:
        pos {[type]} -- specify the color position (default: {None})
    """
    _colors = [
        '#FFFFFF', '#E0E0E0', '#C6C6C6', '#ADADAD', '#949494',
        '#A8E6F0', '#72BDD4', '#3F96B7', '#126F9C', '#0C47AA',
        '#2D63B6', '#4F80C3', '#749ECF', '#99BCDC', '#BFDAE9',
        '#C7ABD7', '#BF93CE', '#B77DC4', '#AE66BC', '#A650B2',
        '#9E3AA9', '#851547', '#942359', '#A4326C', '#B3427E',
        '#C35191', '#D462A4', '#E9A5B5', '#E69A9F', '#E48E8A',
        '#E18175', '#DF7660', '#DC6A4D', '#DA8056', '#DF946C',
        '#E4A781', '#EABB98', '#F0CFB0', '#F5E4C6', '#FAF8DE']
    if pos is None:
        _pos = np.concatenate((
            np.array([0, 0.1, 0.5]), np.arange(1, 12, 1),
            np.arange(12, 60, 4), np.arange(60, 100, 10),
            np.arange(100, 1100, 100)))

    # construct color map and normalized boundary
    cmap, norm = mpl.colors.from_levels_and_colors(_pos, _colors, extend='max')
    return cmap, norm


def cm_temperature_nws(pos=None):
    """
    Construct 2m temperature color maps.

    Keyword Arguments:
        pos {[type]} -- specify the color position (default: {None})

    >>> ax.pcolormesh(x, y, data, cmap=cm_temperature_nws(), vmin=-45, vmax=45)
    """
    _colors = [
        [61, 2, 57], [250, 0, 252], [9, 0, 121], [94, 157, 248], 
        [46, 94, 127], [6, 249, 251], [254, 254, 254], [32, 178, 170],
        [11, 244, 11], [0, 97, 3], [173, 255, 47], [254, 254, 0],
        [255, 140, 0], [255, 99, 61], [90, 3, 3], [253, 253, 253]]
    if pos is None:
        _pos = np.array([
            -45, -30, -20, -10, -5, 0, 0, 5, 5, 10, 20, 20, 30, 30, 40, 45])
    else:
        _pos = pos
    return make_cmap(_colors, position=_pos, rgb=True)


def cm_temp():
    """
    Standardized colormaps from National Weather Service
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/NWS_standard_cmap.py

    F: vmax=120, vmin=-60
    C: vmax=50, vmin=-50
    """
    # The range of temperature bins in Fahrenheit
    a = np.arange(-60,121,5)

    # Bins normalized between 0 and 1
    norm = [(float(i)-min(a))/(max(a)-min(a)) for i in a]

    # Color tuple for every bin
    C = np.array(
        [[145,0,63], [206,18,86], [231,41,138], [223,101,176], [255,115,223], 
        [255,190,232], [255,255,255], [218,218,235], [188,189,220], 
        [158,154,200], [117,107,177], [84,39,143], [13,0,125], [13,61,156], 
        [0,102,194], [41,158,255], [74,199,255], [115,215,255], [173,255,255], 
        [48,207,194], [0,153,150], [18,87,87], [6,109,44], [49,163,84], 
        [116,196,118], [161,217,155], [211,255,190], [255,255,179], 
        [255,237,160], [254,209,118], [254,174,42], [253,141,60], [252,78,42], 
        [227,26,28], [177,0,38], [128,0,38], [89,0,66], [40,0,40]])/255.

    # Create a tuple for every color indicating the 
    # normalized position on the colormap and the assigned color.
    COLORS = []
    for i, n in enumerate(norm):
        COLORS.append((n, C[i]))

    cmap = mpl.colors.LinearSegmentedColormap.from_list("Temperature", COLORS)

    return cmap


def cm_sftemp():
    """
    generate maps from wrfout netCDF files
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/LukeM_colormap.py
    """

    sfc_cdict ={
        'red':    ((0.00, 0.20, 0.20),
                (0.08, 0.40, 0.40),
                (0.17, 0.27, 0.27),
                (0.25, 0.80, 0.80),
                (0.33, 0.20, 0.20),
                (0.42, 0.20, 0.20),
                (0.50, 0.00, 0.00),
                (0.58, 0.99, 0.99),
                (0.67, 1.00, 1.00),
                (0.75, 0.82, 0.82),
                (0.83, 0.53, 0.53),
                (0.92, 0.95, 0.95),
                (1.00, 1.00, 1.00)),

        'green':    ((0.00, 0.20, 0.20),
                (0.08, 0.40, 0.40),
                (0.17, 0.00, 0.00),
                (0.25, 0.60, 0.60),
                (0.33, 0.40, 0.40),
                (0.42, 0.60, 0.60),
                (0.50, 0.39, 0.39),
                (0.58, 0.76, 0.76),
                (0.67, 0.36, 0.36),
                (0.75, 0.02, 0.02),
                (0.83, 0.00, 0.00),
                (0.92, 0.03, 0.03),
                (1.00, 0.60, 0.60)),

        'blue':        ((0.00, 0.60, 0.60),
                (0.08, 0.60, 0.60),
                (0.17, 0.65, 0.65),
                (0.25, 1.00, 1.00),
                (0.33, 1.00, 1.00),
                (0.42, 0.40, 0.40),
                (0.50, 0.07, 0.07),
                (0.58, 0.02, 0.02),
                (0.67, 0.00, 0.00),
                (0.75, 0.01, 0.01),
                (0.83, 0.00, 0.00),
                (0.92, 0.52, 0.52),
                (1.00, 0.80, 0.80))}

     
    sfc_coltbl = mpl.colors.LinearSegmentedColormap('SFC_COLTBL',sfc_cdict)
    return sfc_coltbl 


def cm_temperature_trend_nws(pos=None):
    """
    Construct temperature trend color map.
    
    Keyword Arguments:
        pos {[type]} -- specify the color position (default: {None})
    """
    
    _colors = [
        '#Fcdcf7', '#F795E7', '#F378E0', '#F059D8', '#EC2ACE',
        '#C022A8', '#A01F8C', '#811C70', '#6B195E', '#54154B',
        '#342799', '#402FA8', '#4A40BB', '#6E60D0', '#7E6EDF',
        '#9D89F3', '#BCB0F7', '#DDDDFE', '#DDDDFE', '#B2F8B0',
        '#94F397', '#78F384', '#56EE6C', '#42CE5A', '#2EB045',
        '#249C3B', '#2562C6', '#2C6CDF', '#4492EB', '#54A1EB',
        '#78B5F2', '#94CEF4', '#B2EEF6', '#FFFFFF', '#FDFCFC',
        '#FDFFB1', '#FDE099', '#FDC083', '#FDA56D', '#FD8858',
        '#FC6D46', '#FB5337', '#E5372A', '#CD3126', '#B72B22',
        '#A0251F', '#8C1F1B', '#761A18', '#621215', '#4E0F12',
        '#624039', '#74524A', '#88645C', '#9C766E', '#B08880',
        '#C49C94', '#DDBAB2', '#EEDAD0', '#F8EEE4', '#FDE4E4',
        '#FDC4C6', '#F29E9E', '#E28082', '#DD6466', '#DD6466',
        '#BF4345', '#AE3335']
    if pos is None:
        _pos = np.concatenate((
            np.arange(-42, -18, 2), np.arange(-18, -3, 1),
            np.arange(-3, 0, 0.5),  np.arange(0.5, 3, 0.5),
            np.arange(3, 18, 1), np.arange(18, 43, 2)))

    # construct color map and normalized boundary
    cmap, norm = mpl.colors.from_levels_and_colors(
        _pos, _colors, extend='both')
    return cmap, norm


def cm_thetae():
    """
    generate maps from wrfout netCDF files
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/LukeM_colormap.py
    """

    thte_cdict ={
        'red': ((0.00, 0.20, 0.20),
                (0.08, 0.40, 0.40),
                (0.17, 0.27, 0.27),
                (0.25, 0.80, 0.80),
                (0.33, 0.20, 0.20),
                (0.42, 0.20, 0.20),
                (0.50, 0.00, 0.00),
                (0.58, 0.99, 0.99),
                (0.67, 1.00, 1.00),
                (0.75, 0.82, 0.82),
                (0.83, 0.53, 0.53),
                (0.92, 0.95, 0.95),
                (1.00, 1.00, 1.00)),

        'green':((0.00, 0.20, 0.20),
                (0.08, 0.40, 0.40),
                (0.17, 0.00, 0.00),
                (0.25, 0.60, 0.60),
                (0.33, 0.40, 0.40),
                (0.42, 0.60, 0.60),
                (0.50, 0.39, 0.39),
                (0.58, 0.76, 0.76),
                (0.67, 0.36, 0.36),
                (0.75, 0.02, 0.02),
                (0.83, 0.00, 0.00),
                (0.92, 0.03, 0.03),
                (1.00, 0.60, 0.60)),

        'blue': ((0.00, 0.60, 0.60),
                (0.08, 0.60, 0.60),
                (0.17, 0.65, 0.65),
                (0.25, 1.00, 1.00),
                (0.33, 1.00, 1.00),
                (0.42, 0.40, 0.40),
                (0.50, 0.07, 0.07),
                (0.58, 0.02, 0.02),
                (0.67, 0.00, 0.00),
                (0.75, 0.01, 0.01),
                (0.83, 0.00, 0.00),
                (0.92, 0.52, 0.52),
                (1.00, 0.80, 0.80))}

    thte_coltbl = mpl.colors.LinearSegmentedColormap('THTE_COLTBL',thte_cdict)
    return thte_coltbl


def cm_irsat():
    """
    generate maps from wrfout netCDF files
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/LukeM_colormap.py
    """

    irsat_cdict ={
        'red':    ((0.000, 1.000, 0.294),
                (0.067, 1.000, 1.000),
                (0.133, 0.804, 0.804),
                (0.200, 0.369, 0.369),
                (0.267, 0.627, 0.627),
                (0.333, 0.804, 0.804),
                (0.400, 1.000, 1.000),
                (0.567, 0.000, 0.000),
                (0.667, 0.400, 0.400),
                (0.700, 0.596, 0.596),
                (0.800, 0.000, 0.000),
                (0.867, 0.416, 0.416),
                (0.933, 0.804, 0.804),
                (1.000, 0.294, 0.294)),
        'green':    ((0.000, 1.000, 0.000),
                (0.067, 0.000, 0.000),
                (0.133, 0.361, 0.361),
                (0.200, 0.149, 0.149),
                (0.267, 0.322, 0.322),
                (0.333, 0.584, 0.584),
                (0.400, 0.757, 0.757),
                (0.567, 0.392, 0.392),
                (0.667, 0.804, 0.804),
                (0.700, 0.961, 0.961),
                (0.800, 0.000, 0.000),
                (0.867, 0.353, 0.353),
                (0.933, 0.000, 0.000),
                (1.000, 0.000, 0.000)),
        'blue':        ((0.000, 1.000, 1.000),
                (0.067, 0.000, 0.000),
                (0.133, 0.360, 0.360),
                (0.200, 0.070, 0.070),
                (0.267, 0.176, 0.176),
                (0.333, 0.047, 0.047),
                (0.400, 0.145, 0.145),
                (0.567, 0.000, 0.000),
                (0.667, 0.667, 0.667),
                (0.700, 1.000, 1.000),
                (0.800, 0.502, 0.502),
                (0.867, 0.804, 0.804),
                (0.933, 0.804, 0.804),
                (1.000, 0.510, 0.510))}
    irsat_coltbl = mpl.colors.LinearSegmentedColormap('IRSAT_COLTBL',irsat_cdict)
    return irsat_coltbl


def cm_wind_speed_nws(pos=None):
    """
    Construct 10m wind speed color maps.

    Keyword Arguments:
        pos {[type]} -- specify the color position (default: {None})
    """
    _colors = [
        [255, 255, 255], [99, 99, 99], [28, 99, 207], [177, 238, 239],
        [60, 206, 77], [197, 254, 189], [251, 249, 173], [163, 14, 19],
        [95, 61, 54], [221, 186, 177], [241, 218, 209], [209, 83, 80]
    ]
    if pos is None:
        _pos = np.array(
            [0, 3.6, 3.6, 10.8, 10.8, 17.2, 17.2, 24.5, 24.5, 32.7, 32.7, 42])
    else:
        _pos = pos
    return make_cmap(_colors, position=_pos, rgb=True)


def cm_wind():
    """
    Standardized colormaps from National Weather Service
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/NWS_standard_cmap.py

    MPH: vmin=0, vmax=140
    m/s: vmin=0, vmax=60
    """
    # The wind speed bins in miles per hour (MPH)
    a = [0,5,10,15,20,25,30,35,40,45,50,60,70,80,100,120,140]

    # Normalize the bin between 0 and 1 (uneven bins are important here)
    norm = [(float(i)-min(a))/(max(a)-min(a)) for i in a]

    # Color tuple for every bin
    C = np.array(
        [[16,63,120], [34,94,168], [29,145,192], [65,182,196], [127,205,187], 
        [180,215,158], [223,255,158], [255,255,166], [255,232,115], 
        [255,196,0], [255,170,0], [255,89,0], [255,0,0], [168,0,0], [110,0,0], 
        [255,190,232], [255,115,223]])

    # Create a tuple for every color indicating the normalized 
    # position on the colormap and the assigned color.
    COLORS = []
    for i, n in enumerate(norm):
        COLORS.append((n, np.array(C[i])/255.))

    # Create the colormap
    cmap = mpl.colors.LinearSegmentedColormap.from_list("wind", COLORS)

    return cmap


def cm_high_wind_speed_nws(start=6, step=1.5, pos=None):
    """
    Construct high wind speed color map (32 colors).
    
    Keyword Arguments:
        start {int} -- start value (default: {24})
        step {int} -- step value (default: {2})
        pos {numpy array} -- specify the color position (default: {None})
            like pos = np.concatenate((np.arange(4,22,1), np.arange(22,38,2),
                                       np.arange(38,62,4)))  # 925
                 pos = np.concatenate((np.arange(6,24,1), np.arange(24,40,2),
                                       np.arange(40,64,4)))  # 850
                 pos = np.concatenate((np.arange(8,26,1), np.arange(26,42,2),
                                       np.arange(42,68,4)))  # 700
                 pos = np.concatenate((np.arange(18,36,1), np.arange(36,50,2),
                                       np.arange(50,85,5)))  # 500
                 pos = np.concatenate((np.arange(24,48,2),
                                       np.arange(48,128,4)))  # 200
    
    Returns:
        matplotlib.colors.ListedColormap -- color map.
    """

    _colors = [
        '#DEEBF7', '#B7EBFA', '#91D1F5', '#52A2EF', '#2F80E2',
        '#1F61D0', '#41AB5D', '#3ECE4D', '#54EE60', '#76F678',
        '#B4F8B1', '#C6FDBC', '#FDF6B2', '#FDE687', '#F7BD50',
        '#FC6123', '#FB5E24', '#F73A1E', '#E21D19', '#C11015',
        '#9D0E11', '#633B33', '#785144', '#8C645A', '#B48A82',
        '#DFBDB5', '#F1DBD4', '#FDC4C5', '#F0A1A4', '#E67F81',
        '#DB6464', '#D75052']
    if pos is not None:
        _pos = pos
    else:
        _pos = np.arange(len(_colors)) * step + start

    # construct color map and normalized boundary
    cmap, norm = mpl.colors.from_levels_and_colors(
        
        _pos, _colors, extend='max')
    return cmap, norm


def cm_gust():
    """"
    Suggested ranges: vmin=0, vmax=35 [m/s]
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/my_cmap.py

    """
    num_sections = 4
    sections = np.linspace(0, 1, num_sections)
    cdict = {'red': ((sections[0], 1.0, 1.0),
                    (sections[1], 75/256., 75/256.),
                    (sections[2], 134/256., 134/256.),
                    (sections[3], 184/256., 184/256.)),
            'green': ((sections[0], 1.0, 1.0),
                    (sections[1], 132/256., 132/256.),
                    (sections[2], 1/256., 1/256.),
                    (sections[3], 134/256., 134/256.)),
            'blue': ((sections[0], 1.0, 1.0),
                    (sections[1], 181/256., 181/256.),
                    (sections[2], 124/256., 124/256.),
                    (sections[3], 11/256., 11/256.))}
    cmap_gusts = mpl.colors.LinearSegmentedColormap('gust_colormap_COD', cdict, 256)
    return cmap_gusts


def cm_dewpoint1():
    """
    generate maps from wrfout netCDF files
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/LukeM_colormap.py
    """ 

    dwp_cdict ={
        'red':    ((0.00, 0.60, 0.60),
                (0.35, 0.70, 0.70),
                (0.40, 0.80, 0.80),
                (0.45, 0.90, 0.90),
                (0.50, 1.00, 1.00),
                (0.55, 0.90, 0.90),
                (0.60, 0.76, 0.76),
                (0.70, 0.64, 0.64),
                (0.75, 0.52, 0.52),
                (0.85, 0.42, 0.42),
                (1.00, 0.32, 0.32)),
        'green':    ((0.00, 0.33, 0.33),
                (0.35, 0.44, 0.44),
                (0.40, 0.56, 0.56),
                (0.45, 0.69, 0.69),
                (0.50, 0.85, 0.85),
                (0.55, 1.00, 1.00),
                (0.60, 0.90, 0.90),
                (0.70, 0.80, 0.80),
                (0.75, 0.70, 0.70),
                (0.85, 0.60, 0.60),
                (1.00, 0.50, 0.50)),
        'blue':        ((0.00, 0.06, 0.06),
                (0.35, 0.17, 0.17),
                (0.40, 0.32, 0.32),
                (0.45, 0.49, 0.49),
                (0.50, 0.70, 0.70),
                (0.55, 0.70, 0.70),
                (0.60, 0.49, 0.49),
                (0.70, 0.32, 0.32),
                (0.75, 0.17, 0.17),
                (0.85, 0.06, 0.06),
                (1.00, 0.05, 0.05))}
     
    dwp_coltbl = mpl.colors.LinearSegmentedColormap('DWP_COLTBL',dwp_cdict)
    return dwp_coltbl 


def cm_dpt():
    """
    Standardized colormaps from National Weather Service
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/NWS_standard_cmap.py

    Range of values:
        Celsius: -18 to 27 C
        Fahrenheit: 0 to 80 F
    """
    # The dew point temperature bins in Celsius (C)
    a = np.array([0,10,20,30,40,45,50,55,60,65,70,75,80])

    # Normalize the bin between 0 and 1 (uneven bins are important here)
    norm = [(float(i)-min(a))/(max(a)-min(a)) for i in a]

    # Color tuple for every bin
    C = np.array(
        [[59,34,4], [84,48,5], [140,82,10], [191,129,45], [204,168,84], 
        [223,194,125], [230,217,181], [211,235,231], [169,219,211], 
        [114,184,173], [49,140,133], [1,102,95], [0,60,48], [0,41,33]])

    # Create a tuple for every color indicating the 
    # normalized position on the colormap and the assigned color.
    COLORS = []
    for i, n in enumerate(norm):
        COLORS.append((n, np.array(C[i])/255.))

    # Create the colormap
    cmap = mpl.colors.LinearSegmentedColormap.from_list("dewpoint", COLORS)

    return cmap


def cm_relative_humidity_nws(pos=None):
    """
    Construct 10m relative humidity color maps.
    
    Keyword Arguments:
        pos {[type]} -- specify the color position (default: {None})
    """
    _colors = [
        [99, 68, 46], [125, 84, 54], [153, 98, 62], [168, 115, 79],
        [181, 137, 99], [206, 178, 148], [218, 198, 178], [221, 215, 198],
        [185, 199, 170], [170, 193, 156], [135, 187, 138], [108, 165, 145],
        [79, 105, 143], [79, 98, 143], [157, 24, 177], [121, 20, 97]
    ]
    _colors = np.array(_colors)/255.0
    if pos is None:
        _pos = [0, 1, 5, 10, 20, 30, 40, 50, 60, 65, 70, 75, 80, 85, 90, 99]
    else:
        _pos = pos

    # construct color map and normalized boundary
    cmap, norm = mpl.colors.from_levels_and_colors(
        _pos, _colors, extend='max')
    return cmap, norm


def cm_rh():
    """
    Standardized colormaps from National Weather Service
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/NWS_standard_cmap.py

    Range of values:
        5 to 90 %
    """
    # The relative humidity bins in percent (%)
    a = [5,10,15,20,25,30,35,40,50,60,70,80,90]

    # Normalize the bin between 0 and 1 (uneven bins are important here)
    norm = [(float(i)-min(a))/(max(a)-min(a)) for i in a]

    # Color tuple for every bin
    C = np.array(
        [[145,0,34], [166,17,34], [189,46,36], [212,78,51], [227,109,66], 
        [250,143,67], [252,173,88], [254,216,132], [255,242,170], 
        [230,244,157], [188,227,120], [113,181,92], [38,145,75], [0,87,46]])

    # Create a tuple for every color indicating the normalized 
    # position on the colormap and the assigned color.
    COLORS = []
    for i, n in enumerate(norm):
        COLORS.append((n, np.array(C[i])/255.))

    # Create the colormap
    cmap = mpl.colors.LinearSegmentedColormap.from_list("rh", COLORS)

    return cmap


def cm_cloud_cover_nws(pos=None):
    """
    Construct total cloud cover color maps.

    Keyword Arguments:
        pos {[type]} -- specify the color position (default: {None})
    """
    _colors = [
        '#000000', '#3C3C3C', '#7C7C7C', '#BFBFBF', '#E3E3E3', '#FFFFFF']
    if pos is None:
        _pos = [0, 25, 50, 75, 90, 100]
    else:
        _pos = pos

    return make_cmap(_colors, position=_pos, hex=True)


def cm_sky():
    """
    Standardized colormaps from National Weather Service
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/NWS_standard_cmap.py

    Range of Values:
        0 to 90 %
    """
    # The sky covered by clouds in percent (%)
    a = range(0,91,10)

    # Normalize the bin between 0 and 1 (uneven bins are important here)
    norm = [(float(i)-min(a))/(max(a)-min(a)) for i in a]

    # Color tuple for every bin
    C = np.array(
        [[36, 160, 242], [78, 176, 242], [128, 183, 248], [160, 200, 255], 
        [210, 225, 255], [225, 225, 225], [201, 201, 201], [165, 165, 165], 
        [110, 110, 110], [80, 80, 80]])

    # Create a tuple for every color indicating the normalized 
    # position on the colormap and the assigned color.
    COLORS = []
    for i, n in enumerate(norm):
        COLORS.append((n, np.array(C[i])/255.))

    # Create the colormap
    cmap = mpl.colors.LinearSegmentedColormap.from_list("cloudcover", COLORS)

    return cmap


def cm_visibility_nws(pos=None):
    """
    Construct visibility color map.

    Keyword Arguments:
        pos {[type]} -- specify the color position (default: {None})
    """
    _colors = [
        '#31007E', '#0032B3', '#007DFF', '#00BDFF', 
        '#FF2290', '#FFAED7', '#FFFF00', '#FF9800', 
        '#17D78B', '2AA92A', '53FF00']
    if pos is None:
        _pos = [0, 0.05, 0.2, 0.5, 1, 2.5, 5, 10, 20, 30, 40]
    else:
        _pos = pos

    # construct color map and normalized boundary
    cmap, norm = mpl.colors.from_levels_and_colors(
        _pos, _colors, extend='max')
    return cmap, norm


def cm_mslp_nws(pos=None):
    """
    Constrcut mean sea level pressure color map.

    Keyword Arguments:
        pos {[type]} -- specify the color position (default: {None})
    """
    _colors = [
        '#FD90EB', '#EB78E5', '#EF53E0', '#F11FD3', '#F11FD3', '#A20E9B',
        '#880576', '#6D0258', '#5F0853', '#2A0DA8', '#2F1AA7', '#3D27B4',
        '#3F3CB6', '#6D5CDE', '#A28CF9', '#C1B3FF', '#DDDCFE', '#1861DB',
        '#206CE5', '#2484F4', '#52A5EE', '#91D4FF', '#B2EFF8', '#DEFEFF',
        '#C9FDBD', '#91F78B', '#53ED54', '#1DB31E', '#0CA104', '#FFF9A4',
        '#FFE27F', '#FAC235', '#FF9D04', '#FF5E00', '#F83302', '#E01304',
        '#A20200', '#603329', '#8C6653', '#B18981', '#DDC0B3', '#F8A3A2',
        '#DD6663', '#CA3C3B', '#A1241D', '#6C6F6D', '#8A8A8A', '#AAAAAA',
        '#C5C5C5', '#D5D5D5', '#E7E3E4']
    if pos is None:
        _pos = np.arange(940, 1067.5, 2.5)
    else:
        _pos = pos

    # construct color map and normalized boundary
    cmap, norm = mpl.colors.from_levels_and_colors(
        _pos, _colors, extend='max')
    return cmap, norm


def cm_height_nws(start=488, step=2.5, pos=None):
    """
    Construct geopotential height color map (44 colors).
    
    Keyword Arguments:
    start {int} -- start value (default: {24})
    step {int} -- step value (default: {2})
    pos {numpy array} -- specify the color position (default: {None})
    
    Returns:
        matplotlib.colors.ListedColormap -- color map.
    """
    
    _colors = [
        '#333637', '#50514C', '#676467', '#888888', '#9F9F9F',
        '#B3ADB3', '#C5C5C3', '#DBDBE6', '#B2AEE5', '#7C70D2',
        '#6E60CF', '#483FB8', '#32289A', '#2C6CDF', '#347DE2',
        '#4493EB', '#54A1EB', '#95CFF5', '#B2F8B0', '#95F398',
        '#56EC6B', '#2EB146', '#249D3B', '#624039', '#74524A',
        '#89645C', '#9A736A', '#AE8781', '#C49C94', '#DDBBB3',
        '#FDF9B3', '#FDE788', '#FDBD5C', '#FD9F43', '#FB6234',
        '#FB3D2D', '#DD2826', '#BB1B21', '#9F181D', '#F29F9F',
        '#E38183', '#D55B58', '#CF5251', '#C54043']
    if pos is not None:
        _pos = pos
    else:
        _pos = np.arange(len(_colors)) * step + start

    # construct color map and normalized boundary
    cmap, norm = mpl.colors.from_levels_and_colors(
        _pos, _colors, extend='max')
    return cmap, norm


def cm_vertical_velocity_nws(pos=None):
    """
    Construct vertical velocity color map.

    Keyword Arguments:
        pos {numpy array} -- specify the color position (default: {None})
    """

    _colors = [
        '#9D0001', '#C90101', '#F10202', '#FF3333', '#FF8585',
        '#FFBABA', '#FEDDDD', '#FFFFFF', '#E1E1FF', '#BABAFF',
        '#8484FF', '#2C2CF7', '#0404F1', '#0101C8', '#020299']
    if pos is not None:
        _pos = pos
    else:
        _pos = [
            -30, -20, -10, -5, -2.5, -1, -0.5,
            0.5, 1, 2.5, 5, 10, 20, 30]
    
    # construct color map and normalized boundary
    cmap, norm = mpl.colors.from_levels_and_colors(
        _pos, _colors, extend='both')
    return cmap, norm


def cm_precipitable_water_nws(pos=None):
    """
    Construct precipitable water color map.
    
    Keyword Arguments:
        pos {[type]} -- specify the color position (default: {None})
    """

    _colors = [
        '#C5C5C5', '#B5B5B5', '#A1A1A1', '#8B8B8B', '#787878',
        '#636363', '#505050', '#3B3B3B', '#5B431F', '#6D583B',
        '#866441', '#9C7B46', '#B28C5D', '#CA9D64', '#D8AC7D',
        '#B9B5FF', '#A7A8E1', '#989ACD', '#8686C6', '#6B6CA4',
        '#5A5B91', '#474880', '#016362', '#1D6C59', '#2C774E',
        '#398545', '#589A39', '#6FA720', '#8BB41A', '#A29E54',
        '#AEAD43', '#C4C732', '#D9DB18', '#F0EC11', '#E96F57',
        '#C55645', '#B04035', '#9D2527', '#8A121C', '#7B0007',
        '#7A0076', '#8E0096', '#AE00B8', '#C300C0', '#E200E1',
        '#A002DB', '#7901DD', '#6201DE', '#3C00DC', '#2500D9',
        '#0028DD', '#004ED6', '#0571E0', '#0C98E7', '#02B8DD']
    if pos is not None:
        _pos = pos
    else:
        _pos = np.concatenate((np.arange(25), np.arange(26, 86, 2)))
   
    # construct color map and normalized boundary
    cmap, norm = mpl.colors.from_levels_and_colors(
        _pos, _colors, extend='both')
    return cmap, norm


def cm_specific_humidity_nws(pos=None):
    """
    Construct specific humidity color map.

    Keyword Arguments:
        pos {[type]} -- specify the color position (default: {None})
    """

    _colors = [
        '#FFFFB3', '#463F35', '#F3F1D7', '#E5F4E6', '#124E19',
        '#62A1AC', '#1A2F2E', '#656596', '#302361', '#D3B8DA',
        '#845574']
    if pos is not None:
        _pos = pos
    else:
        _pos = [0, 4, 8, 8, 12, 12, 16, 16, 20, 20, 24]

    return make_cmap(_colors, position=_pos, hex=True)


def cm_high_temperature_nws(pos=None):
    """
    Construct high temperature color map.

    Keyword Arguments:
        pos {[type]} -- specify the color position (default: {None})
    """

    _colors = [
        '#EDC4EF', '#F25AB1', '#F31E83', '#EA2283', '#C6478D',
        '#BD68B4', '#6C429B', '#CACEEB', '#484BB0', '#387DF0',
        '#1FFBFD', '#66EAAE', '#159929', '#FDFE89', '#F09450',
        '#BF231B', '#A83750', '#E27185', '#F5B3F0', '#9550AA']
    if pos is not None:
        _pos = pos
    else:
        _pos = [-60, -50, -40, -35, -30, -25, -20, -15, -10, -5, 0,
                0, 5, 10, 15, 20, 25, 30, 35, 40]

    return make_cmap(_colors, position=_pos, hex=True)


def cm_high_thermal_temperature_nws(pos=None):
    """
    Construct high thermal temperature color map.

    Keyword Arguments:
        pos {[type]} -- specify the color position (default: {None})
    """

    _colors = [
        '#996035', '#F2DACD', '#1E6EC8', '#AAFFFF', '#01F6E2',
        '#00FF00', '#03E19F', '#26BC0D', '#88DB07', '#FFFF13',
        '#FFE100', '#264CFF', '#FF7F00', '#FF0000', '#B5003C',
        '#7F0067', '#9868B4', '#F2EBF5', '#ED00ED']
    if pos is not None:
        _pos = pos
    else:
        _pos = [270, 280, 285, 290, 295, 300, 305,
                310, 315, 320, 330, 335, 340, 345, 350,
                355, 360]

    # construct color map and normalized boundary
    cmap, norm = mpl.colors.from_levels_and_colors(
        _pos, _colors, extend='both')
    return cmap, norm


def cm_cape_nws(pos=None):
    """
    Construct CAPSE color map.

    Keyword Arguments:
        pos {[type]} -- specify the color position (default: {None})
    """

    _colors = [
        '#FFFFFF', '#1E68E4', '#479BEC', '#22FBFB', '#1CD78B',
        '#1CAE30', '#52C636', '#BAEA41', '#FEFF4A', '#FA8D2C',
        '#FD3B4B', '#A40F4D', '#5A0B76', '#F1EBF5']
    if pos is not None:
        _pos = pos
    else:
        _pos = np.array([
            0, 100, 150, 500, 900, 1300, 1500, 1800,
            2000, 2850, 3600, 3900, 4200, 4950])
    
    return make_cmap(_colors, position=_pos, hex=True)


def cm_terrain_256():
    """Custom terrain colormap with 256 distinct colors.
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/terrain_colormap.py

    """

    C = np.array([[0, 125, 255], 
                  [2, 97, 0],  # Alternativley [0, 0, 255], for blue at sealevel
                  [2, 97, 0], [3, 97, 0], [4, 97, 0], [5, 97, 0], [6, 98, 0], [7, 98, 0], [8, 98, 0], [9, 98, 0],
                  [10, 98, 0], [11, 98, 0], [11, 99, 0], [12, 99, 0], [13, 99, 0], [14, 99, 0], [15, 99, 0], 
                  [16, 99, 0], [17, 100, 0], [18, 100, 0], [19, 100, 0], [19, 100, 0],
                  [20, 100, 0], [21, 101, 0], [22, 101, 0], [23, 101, 0], [24, 101, 0], [25, 101, 0], [26, 102, 0], 
                  [27, 102, 0], [28, 102, 0], [28, 102, 0], [29, 102, 0], [30, 102, 0], [31, 103, 0], [32, 103, 0], 
                  [33, 103, 0], [34, 103, 0], [35, 103, 0], [36, 104, 0], [37, 104, 0], [37, 104, 0], [38, 104, 0], 
                  [39, 104, 0], [40, 104, 0], [41, 105, 0], [42, 105, 0], [43, 105, 0], [44, 105, 0], [45, 105, 0], 
                  [45, 106, 0], [46, 106, 0], [47, 106, 0], [48, 106, 0], [49, 106, 0], [50, 106, 0], [51, 107, 0], 
                  [52, 107, 0], [53, 107, 0], [54, 107, 0], [54, 107, 0], [55, 108, 0], [56, 108, 0], [57, 108, 0], 
                  [58, 108, 0], [59, 108, 0], [60, 108, 1], [61, 109, 1], [62, 109, 2], [63, 109, 2], [64, 109, 3], 
                  [65, 109, 3], [66, 110, 4], [67, 110, 4], [68, 110, 4], [69, 110, 5], [70, 110, 5], [71, 110, 6], 
                  [72, 111, 6], [73, 111, 7], [74, 111, 7], [75, 111, 8], [76, 111, 8], [77, 112, 9], [78, 112, 9], 
                  [79, 112, 10], [80, 112, 10], [81, 112, 11], [82, 112, 11], [83, 113, 12], [84, 113, 12], 
                  [85, 113, 13], [85, 113, 13], [86, 113, 14], [87, 114, 14], [88, 114, 15], [89, 114, 15], 
                  [90, 114, 16], [91, 114, 16], [92, 114, 17], [93, 115, 17], [94, 115, 18], [95, 115, 18], 
                  [96, 115, 19], [97, 115, 19], [98, 115, 20], [99, 116, 20], [100, 116, 20], [101, 116, 21], 
                  [102, 116, 21], [103, 116, 22], [104, 117, 22], [105, 117, 23], [106, 117, 23], [107, 117, 24], 
                  [108, 117, 24], [109, 118, 25], [110, 118, 25], [111, 118, 26], [112, 118, 26], [113, 118, 27], 
                  [114, 118, 27], [115, 119, 28], [116, 119, 28], [117, 119, 29], [118, 119, 29], [119, 119, 30], 
                  [120, 120, 30], [121, 120, 31], [122, 120, 31], [123, 120, 32], [124, 121, 32], [125, 121, 32], 
                  [126, 121, 33], [127, 122, 33], [128, 122, 34], [129, 122, 34], [130, 123, 35], [131, 123, 35], 
                  [132, 123, 36], [133, 124, 36], [134, 124, 37], [135, 124, 37], [136, 125, 37], [137, 125, 38], 
                  [138, 125, 38], [139, 126, 39], [139, 126, 39], [140, 126, 40], [141, 126, 40], [142, 127, 41], 
                  [143, 127, 41], [144, 127, 41], [145, 128, 42], [146, 128, 42], [147, 128, 43], [148, 129, 43], 
                  [149, 129, 44], [150, 129, 44], [151, 130, 45], [152, 130, 45], [153, 130, 45], [154, 131, 46], 
                  [155, 131, 46], [156, 131, 47], [157, 132, 47], [158, 132, 48], [159, 132, 48], [160, 133, 49], 
                  [161, 133, 49], [162, 133, 50], [163, 134, 50], [164, 134, 50], [165, 134, 51], [166, 135, 51], 
                  [167, 135, 52], [168, 135, 52], [169, 136, 53], [170, 136, 53], [171, 136, 54], [172, 137, 54], 
                  [173, 137, 54], [174, 137, 55], [175, 138, 55], [176, 138, 56], [177, 138, 56], [178, 139, 57], 
                  [179, 139, 57], [180, 139, 58], [181, 140, 58], [182, 140, 58], [183, 140, 59], [184, 141, 59], 
                  [185, 142, 62], [186, 144, 65], [187, 146, 68], [188, 147, 71], [189, 149, 74], [190, 151, 77], 
                  [192, 153, 80], [193, 155, 83], [194, 156, 86], [195, 158, 90], [196, 160, 93], [197, 162, 96], 
                  [198, 164, 99], [199, 165, 102], [201, 167, 105], [202, 169, 108], [203, 171, 111], 
                  [204, 173, 114], [205, 174, 117], [206, 176, 120], [207, 178, 123], [208, 180, 126], 
                  [210, 182, 130], [211, 184, 133], [212, 185, 136], [213, 187, 139], [214, 189, 142], 
                  [215, 191, 145], [216, 193, 148], [217, 194, 151], [219, 196, 154], [220, 198, 157], 
                  [221, 200, 160], [222, 202, 163], [223, 203, 166], [224, 205, 170], [225, 207, 173], 
                  [226, 209, 176], [228, 211, 179], [229, 212, 182], [230, 214, 185], [231, 216, 188], 
                  [232, 218, 191], [233, 220, 194], [234, 221, 197], [235, 223, 200], [237, 225, 203], 
                  [238, 227, 207], [239, 229, 210], [240, 230, 213], [241, 232, 216], [242, 234, 219], 
                  [243, 236, 222], [245, 238, 225], [246, 240, 228], [247, 241, 231], [248, 243, 234], 
                  [249, 245, 237], [250, 247, 240], [251, 249, 243], [252, 250, 247], [254, 252, 250], 
                  [255, 254, 253], [255, 255, 255]])

    cm = mpl.colors.ListedColormap(C/255.)
    return cm


def cm_terrain_50():
    """
     Custom terrain colormap with 50 distinct colors
    """
    C = np.array([
        [2, 97, 0], [6, 98, 0], [11, 98, 0], [16, 99, 0], [20, 100, 0], [25, 101, 0], 
        [30, 102, 0], [34, 103, 0], [39, 104, 0], [44, 105, 0], [48, 106, 0], 
        [53, 107, 0], [58, 108, 0], [63, 109, 2], [68, 110, 4], [73, 111, 7], 
        [78, 112, 9], [83, 113, 12], [88, 114, 15], [93, 115, 17], [98, 116, 20], 
        [103, 116, 22], [109, 117, 25], [114, 118, 27], [119, 119, 30], 
        [124, 121, 32], [129, 122, 34], [134, 124, 37], [139, 126, 39], 
        [144, 127, 41], [149, 129, 44], [155, 131, 46], [160, 133, 48], 
        [165, 134, 51], [170, 136, 53], [175, 138, 55], [180, 139, 58], 
        [185, 143, 64], [191, 152, 80], [197, 162, 96], [203, 171, 112], 
        [209, 181, 128], [215, 190, 144], [221, 199, 160], [226, 209, 176], 
        [232, 218, 192], [238, 228, 208], [244, 237, 224], [250, 246, 240], 
        [255, 255, 255]])

    cm = mpl.colors.ListedColormap(C/255.)
    return cm


def cm_reflect_ncdc():
    """NCAR Reflectivity Colormap
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/reflectivity_colormap.py
    
    Returns:
        [type] -- [description]
    """

    reflect_ncdc_cdict = {
        'red':(
            (0.0000, 0.000, 0.000), (0.0714, 0.000, 0.000), (0.1429, 0.000, 0.000), 
            (0.2143, 0.000, 0.000), (0.2857, 0.000, 0.000), (0.3571, 0.000, 0.000), 
            (0.4286, 1.000, 1.000), (0.5000, 0.906, 0.906), (0.5714, 1.000, 1.000), 
            (0.6429, 1.000, 1.000), (0.7143, 0.839, 0.839), (0.7857, 0.753, 0.753), 
            (0.8571, 1.000, 1.000), (0.9286, 0.600, 0.600), (1.000, 0.923, 0.923)),
        'green':(
            (0.0000, 0.925, 0.925), (0.0714, 0.627, 0.627), (0.1429, 0.000, 0.000), 
            (0.2143, 1.000, 1.000), (0.2857, 0.784, 0.784), (0.3571, 0.565, 0.565), 
            (0.4286, 1.000, 1.000), (0.5000, 0.753, 0.753), (0.5714, 0.565, 0.565), 
            (0.6429, 0.000, 0.000), (0.7143, 0.000, 0.000), (0.7857, 0.000, 0.000), 
            (0.8571, 0.000, 0.000), (0.9286, 0.333, 0.333), (1.000, 0.923, 0.923)),
        'blue':(
            (0.0000, 0.925, 0.925), (0.0714, 0.965, 0.965), (0.1429, 0.965, 0.965), 
            (0.2143, 0.000, 0.000), (0.2857, 0.000, 0.000), (0.3571, 0.000, 0.000), 
            (0.4286, 0.000, 0.000), (0.5000, 0.000, 0.000), (0.5714, 0.000, 0.000), 
            (0.6429, 0.000, 0.000), (0.7143, 0.000, 0.000), (0.7857, 0.000, 0.000), 
            (0.8571, 1.000, 1.000), (0.9286, 0.788, 0.788), (1.000, 0.923, 0.923))}

    reflect_ncdc_coltbl = mpl.colors.LinearSegmentedColormap(
        'REFLECT_NCDC_COLTBL', reflect_ncdc_cdict)
    
    return reflect_ncdc_coltbl


def cm_LU_MODIS21():
    """Land use colormap (includes lake category).
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/landuse_colormap.py

      # MUST SET VMAX AND VMIN LIKE THIS TO SCALE COLOR RANGE CORRECTLY
      cm, labels = LU_MODIS21()
      plt.pcolormesh(LU_INDEX, cmap=cm, vmin=1, vmax=len(labels) + 1)
    """

    C = np.array([[0, .4, 0],           # 1 Evergreen Needleleaf Forest
                  [0, .4, .2],          # 2 Evergreen Broadleaf Forest
                  [.2, .8, .2],         # 3 Deciduous Needleleaf Forest
                  [.2, .8, .4],         # 4 Deciduous Broadleaf Forest
                  [.2, .6, .2],         # 5 Mixed Forests
                  [.3, .7, 0],          # 6 Closed Shrublands
                  [.82, .41, .12],      # 7 Open Shurblands
                  [.74, .71, .41],      # 8 Woody Savannas
                  [1, .84, .0],         # 9 Savannas
                  [0, 1, 0],            # 10 Grasslands
                  [0, 1, 1],            # 11 Permanant Wetlands
                  [1, 1, 0],            # 12 Croplands
                  [1, 0, 0],            # 13 Urban and Built-up
                  [.7, .9, .3],         # 14 Cropland/Natural Vegetation Mosaic
                  [1, 1, 1],            # 15 Snow and Ice
                  [.914, .914, .7],     # 16 Barren or Sparsely Vegetated
                  [.5, .7, 1],          # 17 Water (like oceans)
                  [1, 0, .74],          # 18 Wooded Tundra
                  [.97, .5, .31],       # 19 Mixed Tundra
                  [.91, .59, .48],      # 20 Barren Tundra
                  [0, 0, .88]           # 21 Lake
                 ])

    cm = mpl.colors.ListedColormap(C)

    labels = ['Evergreen Needleleaf Forest',
              'Evergreen Broadleaf Forest',
              'Deciduous Needleleaf Forest',
              'Deciduous Broadleaf Forest',
              'Mixed Forests',
              'Closed Shrublands',
              'Open Shrublands',
              'Woody Savannas',
              'Savannas',
              'Grasslands',
              'Permanent Wetlands',
              'Croplands',
              'Urban and Built-Up',
              'Cropland/Natural Vegetation Mosaic',
              'Snow and Ice',
              'Barren or Sparsely Vegetated',
              'Water',
              'Wooded Tundra',
              'Mixed Tundra',
              'Barren Tundra',
              'Lake']

    return cm, labels


def cm_LU_MODIS20():
    """Land use colormap.
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/landuse_colormap.py

      # MUST SET VMAX AND VMIN LIKE THIS TO SCALE COLOR RANGE CORRECTLY
      cm, labels = LU_MODIS21()
      plt.pcolormesh(LU_INDEX, cmap=cm, vmin=1, vmax=len(labels) + 1)
    """

    C = np.array([[0, .4, 0],       # 1 Evergreen Needleleaf Forest
                  [0, .4, .2],      # 2 Evergreen Broadleaf Forest
                  [.2, .8, .2],     # 3 Deciduous Needleleaf Forest
                  [.2, .8, .4],     # 4 Deciduous Broadleaf Forest
                  [.2, .6, .2],     # 5 Mixed Forests
                  [.3, .7, 0],      # 6 Closed Shrublands
                  [.82, .41, .12],  # 7 Open Shurblands
                  [.74, .71, .41],  # 8 Woody Savannas
                  [1, .84, .0],     # 9 Savannas
                  [0, 1, 0],        # 10 Grasslands
                  [0, 1, 1],        # 11 Permanant Wetlands
                  [1, 1, 0],        # 12 Croplands
                  [1, 0, 0],        # 13 Urban and Built-up
                  [.7, .9, .3],     # 14 Cropland/Natual Vegation Mosaic
                  [1, 1, 1],        # 15 Snow and Ice
                  [.914, .914, .7], # 16 Barren or Sparsely Vegetated
                  [0, 0, .88],      # 17 Water
                  [.86, .08, .23],  # 18 Wooded Tundra
                  [.97, .5, .31],   # 19 Mixed Tundra
                  [.91, .59, .48]   # 20 Barren Tundra
                 ])

    cm = mpl.colors.ListedColormap(C)

    labels = ['Evergreen Needleleaf Forest',
              'Evergreen Broadleaf Forest',
              'Deciduous Needleleaf Forest',
              'Deciduous Broadleaf Forest',
              'Mixed Forests',
              'Closed Shrublands',
              'Open Shrublands',
              'Woody Savannas',
              'Savannas',
              'Grasslands',
              'Permanent Wetlands',
              'Croplands',
              'Urban and Built-Up',
              'Cropland/Natural Vegetation Mosaic',
              'Snow and Ice',
              'Barren or Sparsely Vegetated',
              'Water',
              'Wooded Tundra',
              'Mixed Tundra',
              'Barren Tundra']

    return cm, labels


def cm_LU_USGS24():
    """Land use colormap.
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/landuse_colormap.py

      # MUST SET VMAX AND VMIN LIKE THIS TO SCALE COLOR RANGE CORRECTLY
      cm, labels = LU_MODIS21()
      plt.pcolormesh(LU_INDEX, cmap=cm, vmin=1, vmax=len(labels) + 1)
    """

    C = np.array([[1, 0, 0],  # 1 Urban and Built-up Land
                  [1, 1, 0],  # 2 Dryland Cropland and Pasture
                  [1, 1, .2],  # 3 Irrigated Cropland and Pasture
                  [1, 1, .3],  # 4 Mixed Dryland/Irrigated Cropland and Pasture
                  [.7, .9, .3],  # 5 Cropland/Grassland Mosaic
                  [.7, .9, .3],  # 6 Cropland/Woodland Mosaic
                  [0, 1, 0],  # 7 Grassland
                  [.3, .7, 0],  # 8 Shrubland
                  [.82, .41, .12],  # 9 Mixed Shrubland/Grassland
                  [1, .84, .0],  # 10 Savanna
                  [.2, .8, .4],  # 11 Deciduous Broadleaf Forest
                  [.2, .8, .2],  # 12 Deciduous Needleleaf Forest
                  [0, .4, .2],  # 13 Evergreen Broadleaf Forest
                  [0, .4, 0],  # 14 Evergreen Needleleaf Forest
                  [.2, .6, .2],  # 15 Mixed Forests
                  [0, 0, .88],  # 16 Water Bodies
                  [0, 1, 1],  # 17 Herbaceous Wetlands
                  [.2, 1, 1],  # 18 Wooden Wetlands
                  [.914, .914, .7],  # 19 Barren or Sparsely Vegetated
                  [.86, .08, .23],  # 20 Herbaceous Tundraa
                  [.86, .08, .23],  # 21 Wooded Tundra
                  [.97, .5, .31],  # 22 Mixed Tundra
                  [.91, .59, .48],  # 23 Barren Tundra
                  [1, 1, 1]])  # 24 Snow and Ice

    cm = mpl.colors.ListedColormap(C)

    labels = ['Urban and Built-up Land',
              'Dryland Cropland and Pasture',
              'Irrigated Cropland and Pasture',
              'Mixed Dryland/Irrigated Cropland and Pasture',
              'Cropland/Grassland Mosaic',
              'Cropland/Woodland Mosaic',
              'Grassland',
              'Shrubland',
              'Mixed Shrubland/Grassland',
              'Savanna',
              'Deciduous Broadleaf Forest',
              'Deciduous Needleleaf Forest',
              'Evergreen Broadleaf',
              'Evergreen Needleleaf',
              'Mixed Forest',
              'Water Bodies',
              'Herbaceous Wetland',
              'Wooden Wetland',
              'Barren or Sparsely Vegetated',
              'Herbaceous Tundra',
              'Wooded Tundra',
              'Mixed Tundra',
              'Bare Ground Tundra',
              'Snow or Ice']

    return cm, labels


def cm_LU_NLCD_chris():
    """Land use colormap.
    https://github.com/blaylockbk/pyBKB_v2/blob/master/BB_cmap/landuse_colormap.py

      # MUST SET VMAX AND VMIN LIKE THIS TO SCALE COLOR RANGE CORRECTLY
      cm, labels = LU_MODIS21()
      plt.pcolormesh(LU_INDEX, cmap=cm, vmin=1, vmax=len(labels) + 1)
    """

    # Provided by Chris Foster
    C = np.array([[0.0, 0.0, 1.0],
                  [0.0, 1.0, 1.0],
                  [0.3, 0.3, 0.3],
                  [0.4, 0.4, 0.4],
                  [0.5, 0.5, 0.5],
                  [0.6, 0.6, 0.6],
                  [0.0, 0.4, 0.2],
                  [0.2, 0.6, 0.2],
                  [0.3, 0.7, 0.0],
                  [0.8, 1.0, 0.2],
                  [0.0, 1.0, 0.0],
                  [0.8, 0.4, 0.2],
                  [0.6, 0.4, 0.0]])

    cm = mpl.colors.ListedColormap(C)

    labels = ['Water',
              'Wetland',
              'Developed High Intensity',
              'Developed Medium Intensity',
              'Developed Low Intensity',
              'Developed Open Space',
              'Evergreen Forest',
              'Deciduous Forest',
              'Cultivated Crops',
              'Pasture/Hay',
              'Grassland',
              'Shrubland',
              'Barren Land']

    return cm, labels


def cm_ir_enhancement():
    """for the AWIPS IR enhancement
    This is assuming that the data you are plotting are actual brightness temps,
    not indexed 0-255 like the old GOES products.

    :Example:
    im = ax.imshow(a[:], extent=(xa[0],xa[-1],ya[-1],ya[0]), origin='upper', cmap=my_cmap, vmin=162., vmax=330.0)
    """

    cdict = {
        'red':  ((0.0, 0.1, 0.1),
                 (.052, 0.07, 0.07),
                 (.055, 0.004, 0.004),
                 (.113, 0.004, 0.004),
                 (.116, 0.85, 0.85),
                 (.162, 0.02, 0.2),
                 (0.165, 0.0, 0.0),
                 (0.229, 0.047, 0.047),
                 (0.232, 0.0, 0.0),
                 (0.297, 0.0, 0.0),
                 (0.30, 0.55, 0.55),
                 (0.355, 0.95, 0.95),
                 (0.358, 0.93, 0.93),
                 (0.416, 0.565, 0.565),
                 (0.419, .373, .373),
                 (0.483, 0.97, 0.97),
                 (0.485, 0.98, 0.98),
                 (1.0, 0.0, 0.0)),
         'green': ((0.0, 0.0, 0.0),
                   (.052, 0.0, 0.0),
                   (.055, 0.0, 0.0),
                   (.113, 0.0, 0.0),
                   (.116, 0.85, 0.85),
                   (.162, 0.0, 0.0),
                   (0.165, .435, .435),
                   (0.229, .97, .97),
                   (0.232, 0.37, 0.37),
                   (0.297, 0.78, 0.78),
                   (0.30, 0.0, 0.0),
                   (0.355, 0.0, 0.0),
                   (0.358, 0.0, 0.0),
                   (0.416, 0.0, 0.0),
                   (0.419, .357, .357),
                   (0.483, 0.95, 0.95),
                   (0.485, 0.98, 0.98),
                   (1.0, 0.0, 0.0)),
         'blue': ((0.0, 0.04, 0.04),
                  (.052, 0.467, 0.467),
                  (.055, 0.4, 0.4),
                  (.113, 0.97, 0.97),
                  (.116, 0.85, 0.85),
                  (.162, 0.0, 0.0),
                  (0.165, 0.0, 0.0),
                  (0.229, 0.0, 0.0),
                  (0.232,0.816, 0.816),
                  (0.297, 0.565, 0.565),
                  (0.30, .55, .55),
                  (0.355, .97, .97),
                  (0.358, 0.0, 0.0),
                  (0.416, 0., 0.),
                  (0.419, 0., 0.),
                  (0.483, 0., 0.),
                  (0.486, 0.98, 0.98),
                  (1.0, 0.0, 0.0))}

    cmap = mpl.colors.LinearSegmentedColormap('IR_enhancement', cdict)
    return cmap


def cm_ir_enhancement1():
    """for the McIDAS IR enhancement
    This is assuming that the data you are plotting are actual brightness temps,
    not indexed 0-255 like the old GOES products.
    
    :Example:
    im = ax.imshow(a[:], extent=(xa[0],xa[-1],ya[-1],ya[0]), origin='upper', cmap=my_cmap, vmin=162., vmax=330.0)
    """

    cdict  = {
        'red': ((0.0, 0.0, 0.0),
                 (.001, 1.00, 1.00),
                 (.107, 1.00, 1.00),
                 (.113, 0.498, 0.498),
                 (.173, 1.00, 1.00),
                 (.179, 0.902, 0.902),
                 (.227, 0.102, 0.102),
                 (.233, 0.00, 0.00),
                 (.287, 0.902, 0.902),
                 (.293, 1.00, 1.00),
                 (.346, 1.00, 1.00),
                 (.352, 1.00, 1.00),
                 (.406, 0.101, 0.101),
                 (.412, 0.00, 0.00),
                 (.481, 0.00, 0.00),
                 (.484, 0.00, 0.00),
                 (.543, 0.00, 0.00),
                 (.546, 0.773, 0.773),
                 (.994, 0.012, 0.012),
                 (.997, 0.004, 0.004),
                 (1.0, 0.0, 0.0)),
         'green': ((0.0, 0.0, 0.0),
                 (.001, 1.00, 1.00),
                 (.107, 1.00, 1.00),
                 (.113, 0.00, 0.00),
                 (.173, 0.498, 0.498),
                 (.179, 0.902, 0.902),
                 (.227, 0.102, 0.102),
                 (.233, 0.00, 0.00),
                 (.287, 0.00, 0.00),
                 (.293, 0.00, 0.00),
                 (.346, 0.902, 0.902),
                 (.352, 1.00, 1.00),
                 (.406, 1.00, 1.00),
                 (.412, 1.00, 1.00),
                 (.481, 0.00, 0.00),
                 (.484, 0.00, 0.00),
                 (.543, 1.00, 1.00),
                 (.546, 0.773, 0.773),
                 (.994, 0.012, 0.012),
                 (.997, 0.004, 0.004),
                   (1.0, 0.0, 0.0)),
         'blue': ((0.0, 0.00, 0.00),
                 (.001, 1.00, 1.00),
                 (.107, 0.00, 0.00),
                 (.113, 0.498, 0.498),
                 (.173, 0.786, 0.786),
                 (.179, 0.902, 0.902),
                 (.227, 0.102, 0.102),
                 (.233, 0.00, 0.00),
                 (.287, 0.00, 0.00),
                 (.293, 0.00, 0.00),
                 (.346, 0.00, 0.00),
                 (.352, 0.00, 0.00),
                 (.406, 0.00, 0.00),
                 (.412, 0.00, 0.00),
                 (.481, 0.451, 0.451),
                 (.484, 0.451, 0.451),
                 (.543, 1.00, 1.00),
                 (.546, 0.773, 0.773),
                 (.994, 0.012, 0.012),
                 (.997, 0.004, 0.004),
                  (1.0, 0.0, 0.0))}

    cmap = mpl.colors.LinearSegmentedColormap('IR_enhancement', cdict)
    return cmap


def cm_ir_enhancement2():
    """for the Shortwave IR enhancement
    This is assuming that the data you are plotting are actual brightness temps,
    not indexed 0-255 like the old GOES products.
    
    :Example:
    im = ax.imshow(a[:], extent=(xa[0],xa[-1],ya[-1],ya[0]), origin='upper', cmap=my_cmap, vmin=162., vmax=330.0)
    """

    cdict  = {
        'red': ((0.0, 0.0, 0.0),
                 (.001, 1.00, 1.00),
                 (.107, 1.00, 1.00),
                 (.113, 0.498, 0.498),
                 (.173, 1.00, 1.00),
                 (.179, 0.902, 0.902),
                 (.227, 0.102, 0.102),
                 (.233, 0.00, 0.00),
                 (.287, 0.902, 0.902),
                 (.293, 1.00, 1.00),
                 (.346, 1.00, 1.00),
                 (.352, 1.00, 1.00),
                 (.406, 0.101, 0.101),
                 (.412, 0.00, 0.00),
                 (.481, 0.00, 0.00),
                 (.484, 0.00, 0.00),
                 (.543, 0.00, 0.00),
                 (.546, 0.773, 0.773),
                 (.994, 0.012, 0.012),
                 (.997, 0.004, 0.004),
                 (1.0, 0.0, 0.0)),
         'green': ((0.0, 0.0, 0.0),
                 (.001, 1.00, 1.00),
                 (.107, 1.00, 1.00),
                 (.113, 0.00, 0.00),
                 (.173, 0.498, 0.498),
                 (.179, 0.902, 0.902),
                 (.227, 0.102, 0.102),
                 (.233, 0.00, 0.00),
                 (.287, 0.00, 0.00),
                 (.293, 0.00, 0.00),
                 (.346, 0.902, 0.902),
                 (.352, 1.00, 1.00),
                 (.406, 1.00, 1.00),
                 (.412, 1.00, 1.00),
                 (.481, 0.00, 0.00),
                 (.484, 0.00, 0.00),
                 (.543, 1.00, 1.00),
                 (.546, 0.773, 0.773),
                 (.994, 0.012, 0.012),
                 (.997, 0.004, 0.004),
                   (1.0, 0.0, 0.0)),
         'blue': ((0.0, 0.00, 0.00),
                 (.001, 1.00, 1.00),
                 (.107, 0.00, 0.00),
                 (.113, 0.498, 0.498),
                 (.173, 0.786, 0.786),
                 (.179, 0.902, 0.902),
                 (.227, 0.102, 0.102),
                 (.233, 0.00, 0.00),
                 (.287, 0.00, 0.00),
                 (.293, 0.00, 0.00),
                 (.346, 0.00, 0.00),
                 (.352, 0.00, 0.00),
                 (.406, 0.00, 0.00),
                 (.412, 0.00, 0.00),
                 (.481, 0.451, 0.451),
                 (.484, 0.451, 0.451),
                 (.543, 1.00, 1.00),
                 (.546, 0.773, 0.773),
                 (.994, 0.012, 0.012),
                 (.997, 0.004, 0.004),
                  (1.0, 0.0, 0.0))}

    cmap = mpl.colors.LinearSegmentedColormap('IR_enhancement', cdict)
    return cmap


def cm_wv_enhancement():
    """for the Water Vapor channels enhancement
    This is assuming that the data you are plotting are actual brightness temps,
    not indexed 0-255 like the old GOES products.
    
    :Example:
    im = ax.imshow(a[:], extent=(xa[0],xa[-1],ya[-1],ya[0]), origin='upper', cmap=my_cmap, vmin=162., vmax=330.0)
    """

    cdict  = {
        'red': ((0.0, 0.0, 0.0),
                 (0.290, 0.263, .263),
                 (0.385, 1.0, 1.0),
                 (0.475, 0.443, .443),
                 (0.515, 0.0, 0.0),
                 (0.575, 1.0, 1.0),
                 (0.664, 1.0, 1.0),
                 (1.0, 0.0, 0.0)),
         'green': ((0.0, 0.0, 0.0),
                   (0.290, .513, .513),
                   (0.385, 1.0, 1.0),
                   (0.475, .443, .443),
                   (0.515, 0., 0.0),
                   (0.575, 1.0, 1.0),
                   (0.664, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),
         'blue': ((0.0, 0.0, 0.0),
                  (0.290, .137, .137),
                  (0.385, 1.0, 1.0),
                  (0.475,0.694, 0.694),
                  (0.515, .451, .451),
                  (0.552, 0.0, 0.0),
                  (0.664, 0.0, 0.0),
                  (1.0, 0.0, 0.0))}

    cmap = mpl.colors.LinearSegmentedColormap('WV_enhancement', cdict)
    return cmap


def cm_RdBufloat(valrange):
    # https://github.com/lmadaus/old_wrf_plotting_scripts/blob/master/coltbls.py
    # Will define a colortable that keeps zero as white
    length = max(valrange)-min(valrange)
    distance = 0 - min(valrange)
    pct = float(distance)/float(length)
            
    RdBufloat_cdict ={'red':((0.00, 0.00, 0.00),
			             	 (pct, 1.00, 1.00),
				             (1.00, 1.00, 1.00)),
		              'green':((0.00, 0.00, 0.00),
				              (pct, 1.00, 1.00),
			              	  (1.00, 0.00, 0.00)),
		              'blue': ((0.00, 1.00, 1.00),
				               (pct, 1.00, 1.00),
				               (1.00, 0.00, 0.00))}
    RdBufloat_coltbl = mpl.colors.LinearSegmentedColormap('RdBufloat_COLTBL',RdBufloat_cdict)
    return RdBufloat_coltbl


def cm_rain1():
    # https://github.com/lmadaus/old_wrf_plotting_scripts/blob/master/coltbls.py
	rain_cdict ={'red':	((0.00, 0.00, 0.00),
				(1.00, 0.00, 0.00)),
		'green':	((0.00, 1.00, 1.00),
				(1.00, 0.20, 0.20)),
		'blue':		((0.00, 0.00, 0.00),
				(1.00, 0.00, 0.00))}
	rain_coltbl = mpl.colors.LinearSegmentedColormap('RAIN_COLTBL',rain_cdict)
	return rain_coltbl


def cm_snow1():
    # https://github.com/lmadaus/old_wrf_plotting_scripts/blob/master/coltbls.py
	snow_cdict ={'red':	((0.00, 0.00, 0.00),
				(1.00, 0.00, 0.00)),
		'green':	((0.00, 0.00, 0.00),
				(1.00, 0.00, 0.00)),
		'blue':		((0.00, 1.00, 1.00),
				(1.00, 0.20, 0.20))}
	snow_coltbl = mpl.colors.LinearSegmentedColormap('SNOW_COLTBL',snow_cdict)
	return snow_coltbl


def mixprecip1():
    # https://github.com/lmadaus/old_wrf_plotting_scripts/blob/master/coltbls.py
	mix_cdict ={'red':	((0.00, 0.20, 0.20),
				(1.00, 1.00, 1.00)),
		'green':	((0.00, 0.00, 0.00),
				(1.00, 0.00, 0.00)),
		'blue':		((0.00, 0.00, 0.00),
				(1.00, 0.00, 0.00))}
	mix_coltbl = mpl.colors.LinearSegmentedColormap('MIX_COLTBL',mix_cdict)
	return mix_coltbl


def cm_grays():
    # https://github.com/lmadaus/old_wrf_plotting_scripts/blob/master/coltbls.py
	grays_cdict ={'red':	((0.00, 1.00, 1.00),
				(1.00, 0.05, 0.05)),
		'green':	((0.00, 1.00, 1.00),
				(1.00, 0.05, 0.05)),
		'blue':		((0.00, 1.00, 1.00),
				(1.00, 0.05, 0.05))}
	grays_coltbl = mpl.colors.LinearSegmentedColormap('GRAYS_COLTBL',grays_cdict)
	return grays_coltbl


def cm_reflect():
    # https://github.com/lmadaus/old_wrf_plotting_scripts/blob/master/coltbls.py
    reflect_cdict ={'red':	((0.000, 0.40, 0.40),
				(0.067, 0.20, 0.20),
				(0.133, 0.00, 0.00),
				(0.200, 0.00, 0.00),
				(0.267, 0.00, 0.00),
				(0.333, 0.00, 0.00),
				(0.400, 1.00, 1.00),
				(0.467, 1.00, 1.00),
				(0.533, 1.00, 1.00),
				(0.600, 1.00, 1.00),
				(0.667, 0.80, 0.80),
				(0.733, 0.60, 0.60),
				(0.800, 1.00, 1.00),
				(0.867, 0.60, 0.60),
				(0.933, 1.00, 1.00),
				(1.000, 0.00, 0.00)),
		'green':	((0.000, 1.00, 1.00),
				(0.067, 0.60, 0.60),
				(0.133, 0.00, 0.00),
				(0.200, 1.00, 1.00),
				(0.267, 0.80, 0.80),
				(0.333, 0.60, 0.60),
				(0.400, 1.00, 1.00),
				(0.467, 0.80, 0.80),
				(0.533, 0.40, 0.40),
				(0.600, 0.00, 0.00),
				(0.667, 0.20, 0.20),
				(0.733, 0.00, 0.00),
				(0.800, 0.00, 0.00),
				(0.867, 0.20, 0.20),
				(0.933, 1.00, 1.00),
				(1.000, 1.00, 1.00)),
		'blue':		((0.000, 1.00, 1.00),
				(0.067, 1.00, 1.00),
				(0.133, 1.00, 1.00),
				(0.200, 0.00, 0.00),
				(0.267, 0.00, 0.00),
				(0.333, 0.00, 0.00),
				(0.400, 0.00, 0.00),
				(0.467, 0.00, 0.00),
				(0.533, 0.00, 0.00),
				(0.600, 0.00, 0.00),
				(0.667, 0.00, 0.00),
				(0.733, 0.00, 0.00),
				(0.800, 1.00, 1.00),
				(0.867, 0.80, 0.80),
				(0.933, 1.00, 1.00),
				(1.000, 1.00, 1.00))}
    reflect_coltbl = mpl.colors.LinearSegmentedColormap('REFLECT_COLTBL',reflect_cdict)
    return reflect_coltbl


def cm_bw_irsat():
    # https://github.com/lmadaus/old_wrf_plotting_scripts/blob/master/coltbls.py
	bw_irsat_cdict ={'red':	((0.000, 1.000, 1.000),
				(1.000, 0.000, 0.000)),
		'green':	((0.000, 1.000, 1.000),
				(1.000, 0.000, 0.000)),
		'blue':		((0.000, 1.000, 1.000),
				(1.000, 0.000, 0.000))}
	bw_irsat_coltbl = mpl.colors.LinearSegmentedColormap('BW_IRSAT_COLTBL',bw_irsat_cdict)
	return bw_irsat_coltbl


def cm_PkBlfloat(datarange):
   distance = max(datarange)-min(datarange)
   zeroloc = 0-min(datarange)
   pct = float(zeroloc)/float(distance)

   # Now, rescale the colormap so each value
   # is scaled to equal that
   PkBl_data = {'red':   [(0.*pct, 0.1178, 0.1178),(0.015873*pct, 0.195857, 0.195857),
                        (0.031746*pct, 0.250661, 0.250661),(0.047619*pct, 0.295468, 0.295468),
                        (0.063492*pct, 0.334324, 0.334324),(0.079365*pct, 0.369112, 0.369112),
                        (0.095238*pct, 0.400892, 0.400892),(0.111111*pct, 0.430331, 0.430331),
                        (0.126984*pct, 0.457882, 0.457882),(0.142857*pct, 0.483867, 0.483867),
                        (0.158730*pct, 0.508525, 0.508525),(0.174603*pct, 0.532042, 0.532042),
                        (0.190476*pct, 0.554563, 0.554563),(0.206349*pct, 0.576204, 0.576204),
                        (0.222222*pct, 0.597061, 0.597061),(0.238095*pct, 0.617213, 0.617213),
                        (0.253968*pct, 0.636729, 0.636729),(0.269841*pct, 0.655663, 0.655663),
                        (0.285714*pct, 0.674066, 0.674066),(0.301587*pct, 0.691980, 0.691980),
                        (0.317460*pct, 0.709441, 0.709441),(0.333333*pct, 0.726483, 0.726483),
                        (0.349206*pct, 0.743134, 0.743134),(0.365079*pct, 0.759421, 0.759421),
                        (0.380952*pct, 0.766356, 0.766356),(0.396825*pct, 0.773229, 0.773229),
                        (0.412698*pct, 0.780042, 0.780042),(0.428571*pct, 0.786796, 0.786796),
                        (0.444444*pct, 0.793492, 0.793492),(0.460317*pct, 0.800132, 0.800132),
                        (0.476190*pct, 0.806718, 0.806718),(0.492063*pct, 0.813250, 0.813250),
                        (0.507937*pct, 0.819730, 0.819730),(0.523810*pct, 0.826160, 0.826160),
                        (0.539683*pct, 0.832539, 0.832539),(0.555556*pct, 0.838870, 0.838870),
                        (0.571429*pct, 0.845154, 0.845154),(0.587302*pct, 0.851392, 0.851392),
                        (0.603175*pct, 0.857584, 0.857584),(0.619048*pct, 0.863731, 0.863731),
                        (0.634921*pct, 0.869835, 0.869835),(0.650794*pct, 0.875897, 0.875897),
                        (0.666667*pct, 0.881917, 0.881917),(0.682540*pct, 0.887896, 0.887896),
                        (0.698413*pct, 0.893835, 0.893835),(0.714286*pct, 0.899735, 0.899735),
                        (0.730159*pct, 0.905597, 0.905597),(0.746032*pct, 0.911421, 0.911421),
                        (0.761905*pct, 0.917208, 0.917208),(0.777778*pct, 0.922958, 0.922958),
                        (0.793651*pct, 0.928673, 0.928673),(0.809524*pct, 0.934353, 0.934353),
                        (0.825397*pct, 0.939999, 0.939999),(0.841270*pct, 0.945611, 0.945611),
                        (0.857143*pct, 0.951190, 0.951190),(0.873016*pct, 0.956736, 0.956736),
                        (0.888889*pct, 0.962250, 0.962250),(0.904762*pct, 0.967733, 0.967733),
                        (0.920635*pct, 0.973185, 0.973185),(0.936508*pct, 0.978607, 0.978607),
                        (0.952381*pct, 0.983999, 0.983999),(0.968254*pct, 0.989361, 0.989361),
                        (0.984127*pct, 0.994695, 0.994695),(1.0*pct, 1.0, 1.0),
                        ((1-pct)*0.125+pct, 0.87058824300765991, 0.87058824300765991), 
                        ((1-pct)*0.25+pct,0.7764706015586853, 0.7764706015586853), 
                        ((1-pct)*0.375+pct, 0.61960786581039429, 0.61960786581039429), 
                        ((1-pct)*0.5+pct, 0.41960784792900085, 0.41960784792900085), 
                        ((1-pct)*0.625+pct,	0.25882354378700256, 0.25882354378700256), 
                        ((1-pct)*0.75+pct, 0.12941177189350128, 0.12941177189350128),
                        ((1-pct)*0.875+pct,	0.031372550874948502, 0.031372550874948502),
                        (1.0, 0.031372550874948502, 0.031372550874948502)],

              'green': [(0., 0., 0.),(0.015873*pct, 0.102869, 0.102869),
                        (0.031746*pct, 0.145479, 0.145479),(0.047619*pct, 0.178174, 0.178174),
                        (0.063492*pct, 0.205738, 0.205738),(0.079365*pct, 0.230022, 0.230022),
                        (0.095238*pct, 0.251976, 0.251976),(0.111111*pct, 0.272166, 0.272166),
                        (0.126984*pct, 0.290957, 0.290957),(0.142857*pct, 0.308607, 0.308607),
                        (0.158730*pct, 0.325300, 0.325300),(0.174603*pct, 0.341178, 0.341178),
                        (0.190476*pct, 0.356348, 0.356348),(0.206349*pct, 0.370899, 0.370899),
                        (0.222222*pct, 0.384900, 0.384900),(0.238095*pct, 0.398410, 0.398410),
                        (0.253968*pct, 0.411476, 0.411476),(0.269841*pct, 0.424139, 0.424139),
                        (0.285714*pct, 0.436436, 0.436436),(0.301587*pct, 0.448395, 0.448395),
                        (0.317460*pct, 0.460044, 0.460044),(0.333333*pct, 0.471405, 0.471405),
                        (0.349206*pct, 0.482498, 0.482498),(0.365079*pct, 0.493342, 0.493342),
                        (0.380952*pct, 0.517549, 0.517549),(0.396825*pct, 0.540674, 0.540674),
                        (0.412698*pct, 0.562849, 0.562849),(0.428571*pct, 0.584183, 0.584183),
                        (0.444444*pct, 0.604765, 0.604765),(0.460317*pct, 0.624669, 0.624669),
                        (0.476190*pct, 0.643958, 0.643958),(0.492063*pct, 0.662687, 0.662687),
                        (0.507937*pct, 0.680900, 0.680900),(0.523810*pct, 0.698638, 0.698638),
                        (0.539683*pct, 0.715937, 0.715937),(0.555556*pct, 0.732828, 0.732828),
                        (0.571429*pct, 0.749338, 0.749338),(0.587302*pct, 0.765493, 0.765493),
                        (0.603175*pct, 0.781313, 0.781313),(0.619048*pct, 0.796819, 0.796819),
                        (0.634921*pct, 0.812029, 0.812029),(0.650794*pct, 0.826960, 0.826960),
                        (0.666667*pct, 0.841625, 0.841625),(0.682540*pct, 0.856040, 0.856040),
                        (0.698413*pct, 0.870216, 0.870216),(0.714286*pct, 0.884164, 0.884164),
                        (0.730159*pct, 0.897896, 0.897896),(0.746032*pct, 0.911421, 0.911421),
                        (0.761905*pct, 0.917208, 0.917208),(0.777778*pct, 0.922958, 0.922958),
                        (0.793651*pct, 0.928673, 0.928673),(0.809524*pct, 0.934353, 0.934353),
                        (0.825397*pct, 0.939999, 0.939999),(0.841270*pct, 0.945611, 0.945611),
                        (0.857143*pct, 0.951190, 0.951190),(0.873016*pct, 0.956736, 0.956736),
                        (0.888889*pct, 0.962250, 0.962250),(0.904762*pct, 0.967733, 0.967733),
                        (0.920635*pct, 0.973185, 0.973185),(0.936508*pct, 0.978607, 0.978607),
                        (0.952381*pct, 0.983999, 0.983999),(0.968254*pct, 0.989361, 0.989361),
                        (0.984127*pct, 0.994695, 0.994695),(1.0*pct, 1.0, 1.0), 
                        ((1-pct)*0.125+pct,	0.92156863212585449, 0.92156863212585449), 
                        ((1-pct)*0.25+pct, 0.85882353782653809, 0.85882353782653809), 
                        ((1-pct)*0.375+pct,	0.7921568751335144, 0.7921568751335144), 
                        ((1-pct)*0.5+pct, 0.68235296010971069, 0.68235296010971069), 
                        ((1-pct)*0.625+pct,	0.57254904508590698, 0.57254904508590698), 
                        ((1-pct)*0.75+pct, 0.44313725829124451, 0.44313725829124451), 
                        ((1-pct)*0.875+pct,	0.31764706969261169, 0.31764706969261169), 
                        ((1-pct)*1.0+pct, 0.18823529779911041, 0.18823529779911041)],

              'blue':  [(0.*pct, 0., 0.),(0.015873*pct, 0.102869, 0.102869),
                        (0.031746*pct, 0.145479, 0.145479),(0.047619*pct, 0.178174, 0.178174),
                        (0.063492*pct, 0.205738, 0.205738),(0.079365*pct, 0.230022, 0.230022),
                        (0.095238*pct, 0.251976, 0.251976),(0.111111*pct, 0.272166, 0.272166),
                        (0.126984*pct, 0.290957, 0.290957),(0.142857*pct, 0.308607, 0.308607),
                        (0.158730*pct, 0.325300, 0.325300),(0.174603*pct, 0.341178, 0.341178),
                        (0.190476*pct, 0.356348, 0.356348),(0.206349*pct, 0.370899, 0.370899),
                        (0.222222*pct, 0.384900, 0.384900),(0.238095*pct, 0.398410, 0.398410),
                        (0.253968*pct, 0.411476, 0.411476),(0.269841*pct, 0.424139, 0.424139),
                        (0.285714*pct, 0.436436, 0.436436),(0.301587*pct, 0.448395, 0.448395),
                        (0.317460*pct, 0.460044, 0.460044),(0.333333*pct, 0.471405, 0.471405),
                        (0.349206*pct, 0.482498, 0.482498),(0.365079*pct, 0.493342, 0.493342),
                        (0.380952*pct, 0.503953, 0.503953),(0.396825*pct, 0.514344, 0.514344),
                        (0.412698*pct, 0.524531, 0.524531),(0.428571*pct, 0.534522, 0.534522),
                        (0.444444*pct, 0.544331, 0.544331),(0.460317*pct, 0.553966, 0.553966),
                        (0.476190*pct, 0.563436, 0.563436),(0.492063*pct, 0.572750, 0.572750),
                        (0.507937*pct, 0.581914, 0.581914),(0.523810*pct, 0.590937, 0.590937),
                        (0.539683*pct, 0.599824, 0.599824),(0.555556*pct, 0.608581, 0.608581),
                        (0.571429*pct, 0.617213, 0.617213),(0.587302*pct, 0.625727, 0.625727),
                        (0.603175*pct, 0.634126, 0.634126),(0.619048*pct, 0.642416, 0.642416),
                        (0.634921*pct, 0.650600, 0.650600),(0.650794*pct, 0.658682, 0.658682),
                        (0.666667*pct, 0.666667, 0.666667),(0.682540*pct, 0.674556, 0.674556),
                        (0.698413*pct, 0.682355, 0.682355),(0.714286*pct, 0.690066, 0.690066),
                        (0.730159*pct, 0.697691, 0.697691),(0.746032*pct, 0.705234, 0.705234),
                        (0.761905*pct, 0.727166, 0.727166),(0.777778*pct, 0.748455, 0.748455),
                        (0.793651*pct, 0.769156, 0.769156),(0.809524*pct, 0.789314, 0.789314),
                        (0.825397*pct, 0.808969, 0.808969),(0.841270*pct, 0.828159, 0.828159),
                        (0.857143*pct, 0.846913, 0.846913),(0.873016*pct, 0.865261, 0.865261),
                        (0.888889*pct, 0.883229, 0.883229),(0.904762*pct, 0.900837, 0.900837),
                        (0.920635*pct, 0.918109, 0.918109),(0.936508*pct, 0.935061, 0.935061),
                        (0.952381*pct, 0.951711, 0.951711),(0.968254*pct, 0.968075, 0.968075),
                        (0.984127*pct, 0.984167, 0.984167),(1.0*pct, 1.0, 1.0),
                        ((1-pct)*0.125+pct, 0.9686274528503418, 0.9686274528503418), 
                        ((1-pct)*0.25+pct, 0.93725490570068359, 0.93725490570068359),
                        ((1-pct)*0.375+pct, 0.88235294818878174, 0.88235294818878174),
                        ((1-pct)*0.5+pct, 0.83921569585800171, 0.83921569585800171),
                        ((1-pct)*0.625+pct, 0.7764706015586853,	0.7764706015586853),
                        ((1-pct)*0.75+pct, 0.70980393886566162, 0.70980393886566162),
                        ((1-pct)*0.875+pct, 0.61176472902297974, 0.61176472902297974),
                        (1.0, 0.41960784792900085, 0.41960784792900085)]}

   PkBl_coltbl = mpl.colors.LinearSegmentedColormap('PKBL_COLTBL',PkBl_data)
   return PkBl_coltbl


def cm_PuRdBlfloat(datarange):
   distance = max(datarange)-min(datarange)
   zeroloc = 0-min(datarange)
   pct = float(zeroloc)/float(distance)

   PuRdBl_data = {'blue': [
			(0.0*pct, 0.12156862765550613,0.12156862765550613),
			(0.125*pct,0.26274511218070984, 0.26274511218070984), 
			(0.25*pct,0.33725491166114807, 0.33725491166114807), 
			(0.375*pct, 0.54117649793624878, 0.54117649793624878), 
			(0.5*pct, 0.69019609689712524, 0.69019609689712524),
			(0.625*pct, 0.78039216995239258,0.78039216995239258), 
			(0.75*pct, 0.85490196943283081,0.85490196943283081), 
			(0.875*pct, 0.93725490570068359,0.93725490570068359), 
			(1.0*pct, 0.97647058963775635,0.97647058963775635), 
			((1-pct)*0.125+pct, 0.9686274528503418,
			0.9686274528503418), ((1-pct)*0.25+pct, 0.93725490570068359, 0.93725490570068359),
			((1-pct)*0.375+pct, 0.88235294818878174, 0.88235294818878174), ((1-pct)*0.5+pct,
			0.83921569585800171, 0.83921569585800171), ((1-pct)*0.625+pct, 0.7764706015586853,
			0.7764706015586853), ((1-pct)*0.75+pct, 0.70980393886566162, 0.70980393886566162),
			((1-pct)*0.875+pct, 0.61176472902297974, 0.61176472902297974), (1.0,
			0.41960784792900085, 0.41960784792900085)],

    		'green': [
			(0.0*pct, 0.0, 0.0),
			(0.125*pct, 0.0, 0.0),
			(0.25*pct, 0.070588238537311554, 0.070588238537311554), 
			(0.375*pct, 0.16078431904315948, 0.16078431904315948), 
			(0.5*pct, 0.3960784375667572, 0.3960784375667572), 
			(0.625*pct, 0.58039218187332153, 0.58039218187332153), 
			(0.75*pct, 0.72549021244049072, 0.72549021244049072), 
			(0.875*pct,0.88235294818878174, 0.88235294818878174), 
			(1.0*pct, 0.95686274766921997, 0.95686274766921997), 
			((1-pct)*0.125+pct,	0.92156863212585449, 0.92156863212585449), ((1-pct)*0.25+pct,
    			0.85882353782653809, 0.85882353782653809), ((1-pct)*0.375+pct,
    			0.7921568751335144, 0.7921568751335144), ((1-pct)*0.5+pct,
    			0.68235296010971069, 0.68235296010971069), ((1-pct)*0.625+pct,
    			0.57254904508590698, 0.57254904508590698), ((1-pct)*0.75+pct,
    			0.44313725829124451, 0.44313725829124451), ((1-pct)*0.875+pct,
    			0.31764706969261169, 0.31764706969261169), ((1-pct)*1.0+pct,
    			0.18823529779911041, 0.18823529779911041)],

    		'red': [
			(0.0*pct, 0.40392157435417175, 0.40392157435417175),
			(0.125*pct, 0.59607845544815063, 0.59607845544815063), 
			(0.25*pct, 0.80784314870834351, 0.80784314870834351), 
			(0.375*pct, 0.90588235855102539, 0.90588235855102539), 
			(0.5*pct, 0.87450981140136719, 0.87450981140136719), 
			(0.625*pct, 0.78823530673980713, 0.78823530673980713), 
			(0.75*pct, 0.83137255907058716, 0.83137255907058716), 
			(0.875*pct, 0.90588235855102539, 0.90588235855102539), 
			(1.0*pct, 0.9686274528503418, 0.9686274528503418), 
			((1-pct)*0.125+pct,
    			0.87058824300765991, 0.87058824300765991), ((1-pct)*0.25+pct,
    			0.7764706015586853, 0.7764706015586853), ((1-pct)*0.375+pct,
    			0.61960786581039429, 0.61960786581039429), ((1-pct)*0.5+pct,
    			0.41960784792900085, 0.41960784792900085), ((1-pct)*0.625+pct,
    			0.25882354378700256, 0.25882354378700256), ((1-pct)*0.75+pct,
    			0.12941177189350128, 0.12941177189350128), ((1-pct)*0.875+pct,
    			0.031372550874948502, 0.031372550874948502), (1.0,
    			0.031372550874948502, 0.031372550874948502)]}

   #print PuRdBl_data
   PuRdBl_coltbl = mpl.colors.LinearSegmentedColormap('PURDBL_COLTBL',PuRdBl_data)
   return PuRdBl_coltbl


def cm_RdBuWH():
   RdBuWH_data = {'blue': [(0.0, 0.3803921639919281, 0.3803921639919281),
                           (0.10000000000000002, 0.67450982332229614,
                            0.67450982332229614),
                           (0.20000000000000004, 0.76470589637756348,
                            0.76470589637756348),
                           (0.29999999999999996, 0.87058824300765991,
                            0.87058824300765991),
                           (0.39999999999999998, 0.94117647409439087,
                            0.94117647409439087),
                           (0.45, 1.0, 1.0),
                           (0.55, 1.0, 1.0),
                           (0.60000000000000002, 0.78039216995239258,
                            0.78039216995239258),
                           (0.69999999999999999, 0.50980395078659058,
                            0.50980395078659058),
                           (0.80000000000000001, 0.30196079611778259,
                            0.30196079611778259),
                           (0.90000000000000001, 0.16862745583057404,
                            0.16862745583057404),
                           (1.0, 0.12156862765550613, 0.12156862765550613)],

                  'green': [(0.0, 0.18823529779911041, 0.18823529779911041),
                            (0.10000000000000002, 0.40000000596046448,
                             0.40000000596046448),
                            (0.20000000000000004, 0.57647061347961426,
                             0.57647061347961426),
                            (0.29999999999999996, 0.77254903316497803,
                             0.77254903316497803),
                            (0.39999999999999998, 0.89803922176361084,
                             0.89803922176361084),
                            (0.45, 1.0, 1.0),
                            (0.55, 1.0, 1.0),
                            (0.60000000000000002, 0.85882353782653809,
                             0.85882353782653809),
                            (0.69999999999999999, 0.64705884456634521,
                             0.64705884456634521),
                            (0.80000000000000001, 0.37647059559822083,
                             0.37647059559822083),
                            (0.90000000000000001, 0.094117648899555206,
                             0.094117648899555206),
                            (1.0, 0.0, 0.0)],

                  'red': [(0.0, 0.019607843831181526, 0.019607843831181526),
                          (0.10000000000000002, 0.12941177189350128,
                           0.12941177189350128),
                          (0.20000000000000004, 0.26274511218070984,
                           0.26274511218070984),
                          (0.29999999999999996, 0.57254904508590698,
                           0.57254904508590698),
                          (0.39999999999999998, 0.81960785388946533,
                           0.81960785388946533),
                          (0.45, 1.0, 1.0),
                          (0.55, 1.0, 1.0),
                          (0.60000000000000002, 0.99215686321258545,
                           0.99215686321258545),
                          (0.69999999999999999, 0.95686274766921997,
                           0.95686274766921997),
                          (0.80000000000000001, 0.83921569585800171,
                           0.83921569585800171),
                          (0.90000000000000001, 0.69803923368453979,
                           0.69803923368453979),
                          (1.0, 0.40392157435417175, 0.40392157435417175)]}
   RdBuWH_coltbl = mpl.colors.LinearSegmentedColormap(
       'RDBUWH_COLTBL', RdBuWH_data)
   return RdBuWH_coltbl
