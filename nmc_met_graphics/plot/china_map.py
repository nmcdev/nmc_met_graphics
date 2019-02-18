# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Draw china map.
"""

import pkg_resources
import cartopy.crs as ccrs
from matplotlib.patches import Polygon
from cartopy.io.shapereader import Reader


def add_china_map_2basemap(mp, ax, name='province', facecolor='none',
                           edgecolor='c', lw=2, **kwargs):
    """
    Add china province boundary to basemap instance.

    :param mp: basemap instance.
    :param ax: matplotlib axes instance.
    :param name: map name.
    :param facecolor: fill color, default is none.
    :param edgecolor: edge color.
    :param lw: line width.
    :param kwargs: keywords passing to Polygon.
    :return: None.
    """

    # map name
    names = {'nation': "bou1_4p", 'province': "bou2_4p",
             'county': "BOUNT_poly", 'river': "hyd1_4p",
             'river_high': "hyd2_4p"}

    # get shape file and information
    shpfile = pkg_resources.resource_filename(
        'nmc_met_graphics', "resources\\maps\\"+names[name])
    _ = mp.readshapefile(shpfile, 'states', drawbounds=True)

    for info, shp in zip(mp.states_info, mp.states):
        poly = Polygon(
            shp, facecolor=facecolor, edgecolor=edgecolor, lw=lw, **kwargs)
        ax.add_patch(poly)


def add_china_map_2cartopy(ax, name='province', facecolor='none',
                           edgecolor='c', lw=2, **kwargs):
    """
    Draw china boundary on cartopy map.

    :param ax: matplotlib axes instance.
    :param name: map name.
    :param facecolor: fill color, default is none.
    :param edgecolor: edge color.
    :param lw: line width.
    :return: None
    """

    # map name
    names = {'nation': "bou1_4p", 'province': "bou2_4p",
             'county': "BOUNT_poly", 'river': "hyd1_4l",
             'river_high': "hyd2_4l"}

    # get shape filename
    shpfile = pkg_resources.resource_filename(
        'nmc_met_graphics', "resources\\maps\\" + names[name] + ".shp")

    # add map
    ax.add_geometries(
        Reader(shpfile).geometries(), ccrs.PlateCarree(),
        facecolor=facecolor, edgecolor=edgecolor, lw=lw, **kwargs)
