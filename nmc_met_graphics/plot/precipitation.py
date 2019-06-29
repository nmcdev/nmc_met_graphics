# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Draw rain analysis map.
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from nmc_met_graphics.cmap.ctables import cm_precipitation_nws
from nmc_met_graphics.plot.china_map import add_china_map_2cartopy
from nmc_met_graphics.plot.util import add_gridlines


def draw_precipitation_nws(ax, prep, map_extent=(73, 136, 17, 54),
                           gridlines=True):
    """
    Draw NWS-style precipitation map.
    http://jjhelmus.github.io/blog/2013/09/17/plotting-nsw-precipitation-data/

    :param ax: `matplotlib.axes.Axes`, the `Axes` instance used for plotting.
    :param prep: precipitation, dictionary:
                 {'lon': 1D array, 'lat': 1D array, 'data': 2D array}
    :param map_extent: (lonmin, lonmax, latmin, latmax),
                       longitude and latitude range.
    :param gridlines: bool, draw grid lines or not.
    :return: plots dictionary.

    :Example:
    >>> plt.ioff()
    >>> fig = plt.figure(figsize=(8.6, 6.2))
    >>> fig.clf()
    >>> ax = plt.axes((0.1, 0.08, 0.85, 0.92), projection=ccrs.PlateCarree())
    >>> prep = {'lon': lon, 'lat': lat, 'data': rain}
    >>> plots = draw_precipitation_nws(ax, prep, map_extent=[73, 136, 17, 54])
    >>> ax.set_title('24h Accumulated Precipitation', fontsize=18, loc='left')
    >>> cax = fig.add_axes([0.16, 0.08, 0.7, 0.03])
    >>> cb = plt.colorbar(plots['prep'], cax=cax, orientation='horizontal',
    >>>                   ticks=plots['prep'].norm.boundaries)
    >>> cb.set_label('Precipitation (mm)', fontsize=10)
    >>> cb.ax.tick_params(labelsize=10)
    >>> plt.savefig('D:/plot.png')
    """

    # set data projection
    datacrs = ccrs.PlateCarree()

    # plot map background
    ax.set_extent(map_extent, crs=datacrs)
    add_china_map_2cartopy(ax, name='province', edgecolor='k', lw=1)
    add_china_map_2cartopy(ax, name='river', edgecolor='blue', lw=1)

    # plots container
    plots = {}

    # draw precipitation map
    x, y = np.meshgrid(prep['lon'], prep['lat'])
    cmap, norm = cm_precipitation_nws()
    plots['prep'] = ax.pcolormesh(x, y, np.squeeze(prep['data']), norm=norm,
                                  cmap=cmap, transform=datacrs)

    # add grid lines
    if gridlines:
        add_gridlines(ax)

    # return
    return plots


def draw_qpf_nmc(ax, prep, stations=None, map_extent=(107., 123, 28, 43.)):
    """
    Draw filled-contour QPF.

    :param ax: ax: `matplotlib.axes.Axes`, the `Axes` instance.
    :param prep: precipitation, dictionary:
                 necessary, {'lon': 1D array, 'lat': 1D array,
                             'data': 2D array}
                 optional, {'clevs': 1D array}
    :param stations: station locations, dictionary:
                 necessary, {'lon': 1D array, 'lat': 1D array}
    :param map_extent: [lonmin, lonmax, latmin, latmax],
                       longitude and latitude range.
    :return: plots dictionary.
    """

    # set data projection
    datacrs = ccrs.PlateCarree()

    # plot map background
    ax.set_extent(map_extent, crs=datacrs)
    add_china_map_2cartopy(ax, name='province', edgecolor='k', lw=1)
    add_china_map_2cartopy(ax, name='river', edgecolor='blue', lw=1)

    # plots container
    plots = {}

    # draw precipitation map
    x, y = np.meshgrid(prep['lon'], prep['lat'])
    if prep.get('clevs') is None:
        clevs = [0.1, 10, 25, 50, 100, 250, 600]
    cmap = plt.get_cmap("YlGnBu")
    norm = mpl.colors.BoundaryNorm(clevs, cmap.N)
    plots['prep'] = ax.contourf(
        x, y, np.squeeze(prep['data']), clevs, norm=norm,
        cmap=cmap, transform=datacrs)

    # add station points
    if stations is not None:
        plots['stations'] = ax.scatter(stations['lon'], stations['lat'],
                                       transform=ccrs.PlateCarree())

    # add grid lines
    add_gridlines(ax)

    # return
    return plots
