# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Retrieve resource dataset.
"""

import pkg_resources
import pandas as pd
import numpy as np
import shapefile
from netCDF4 import Dataset


def get_nation_station_info(limit=None):
    """
    Get the national surface weather station information.

    :param limit: region limit, (lon0, lon1, lat0, lat1)

    :return: pandas data frame, weather station information, column names:
    ['province', 'ID', 'name', 'grade', 'lat', 'lon', 'alt', 'pressureAlt']
    """

    file = pkg_resources.resource_filename(
        "nmc_met_graphics", "resources/stations/cma_national_station_info.dat")

    sta_info = pd.read_csv(file, dtype={"ID": np.str})

    if limit is None:
        sta_info = sta_info.loc[
            (sta_info['lon'] >= limit[0]) & (sta_info['lon'] <= limit[1]) &
            (sta_info['lat'] >= limit[2]) & (sta_info['lat'] <= limit[3])]

    return sta_info


def get_county_station_info(limit=None):
    """
    Get the county surface weather station information.
    return pandas data frame.

    Keyword Arguments:
        limit {tuple} -- region limit, (lon0, lon1, lat0, lat1)
    """

    file = pkg_resources.resource_filename(
        "nmc_met_graphics", "resources/stations/cma_county_station_info.dat")

    sta_info = pd.read_csv(
        file, delim_whitespace=True, header=None,
        names=['ID', 'lat', 'lon', 'county', 'city', 'province'],
        dtype={"ID": np.str})

    if limit is None:
        sta_info = sta_info.loc[
            (sta_info['lon'] >= limit[0]) & (sta_info['lon'] <= limit[1]) &
            (sta_info['lat'] >= limit[2]) & (sta_info['lat'] <= limit[3])]

    return sta_info


def get_china_city(limit=None, grade="province"):
    """
    Get china city information.
    Return pandas dataframe.

    Keyword Arguments:
        limit {[type]} -- [description] (default: {None})
        grade {str} -- [description] (default: {"province"})
    """

    if grade == "province":
        file = pkg_resources.resource_filename(
            "nmc_met_graphics", "resources/stations/res1_4m.shp")
    else:
        file = pkg_resources.resource_filename(
            "nmc_met_graphics", "resources/stations/res2_4m.shp")

    shape = shapefile.Reader(file)
    srs = shape.shapeRecords()
    city_info = pd.DataFrame(columns=['name', 'lon', 'lat'])
    for isr, sr in enumerate(srs):
        city_info.loc[isr] = [
            sr.record[9], sr.shape.points[0][0], sr.shape.points[0][1]]

    if limit is None:
        city_info = city_info.loc[
            (city_info['lon'] >= limit[0]) & (city_info['lon'] <= limit[1]) &
            (city_info['lat'] >= limit[2]) & (city_info['lat'] <= limit[3])]

    return city_info


def get_world_city(limit=None):
    """
    Get the world station information.
    return pandas data frame.

    Keyword Arguments:
        limit {tuple} -- region limit, (lon0, lon1, lat0, lat1)
    """

    file = pkg_resources.resource_filename(
        "nmc_met_graphics", "resources/stations/cma_world_city_station_info.dat")

    sta_info = pd.read_csv(
        file, delim_whitespace=True, header=None,
        names=['ID', 'lat', 'lon', 'alt', 'grade1', 'grade2', 'name'],
        dtype={"ID": np.str})

    sta_info['lat'] /= 100.
    sat_info['lon'] /= 100.

    if limit is None:
        sta_info = sta_info.loc[
            (sta_info['lon'] >= limit[0]) & (sta_info['lon'] <= limit[1]) &
            (sta_info['lat'] >= limit[2]) & (sta_info['lat'] <= limit[3])]

    return sta_info


def read_china_topo():
    """
    read china topography data and lon, lat topography.

    :return: {lon, lat, topo} dictionary.
    """

    # get topography filename
    filename = pkg_resources.resource_filename(
        'nmc_met_graphics', "resources/topo/topo_china.nc")

    # read topo data
    fio = Dataset(filename, 'r')
    lon = fio.variables['Longitude'][:]
    lat = fio.variables['Latitude'][:]
    topo = fio.variables['topo'][:]

    # return
    return {'lon': lon, 'lat': lat, 'topo': topo}


def get_mpl_style(name):
    """Get the matplotlib style file path.
    Matplotlib stylesheets can be passed via their full path. This function
    takes a style name and returns the absolute path to the typhon stylesheet.

    refer to:
      https://github.com/nirum/mplstyle
      https://github.com/tonysyu/matplotlib-style-gallery
      http://tonysyu.github.io/raw_content/matplotlib-style-gallery/gallery.html

    Arguments:
        name {string} -- style file name.
    """

    return pkg_resources.resource_filename(
        'nmc_met_graphics', 'resources/stylelib/'+name+'.mplstyle')
