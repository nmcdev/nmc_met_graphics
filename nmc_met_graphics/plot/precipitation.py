# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Draw rain analysis map.
"""

import pkg_resources
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as path_effects
from matplotlib.font_manager import FontProperties
from matplotlib.transforms import offset_copy
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimg
from nmc_met_graphics.cmap.ctables import cm_precipitation_nws
from nmc_met_graphics.plot.mapview import add_china_map_2cartopy
from nmc_met_graphics.plot.util import add_gridlines


def draw_total_precipitation(prep, map_extent=(107., 112, 23.2, 26.5),
                             back_image='terrain-background', back_image_zoom=8, title="降水量实况图",
                             draw_station=True, station_info='cities', station_size=22, 
                             just_contourf=False):
    """
    该程序用于显示多日的累积降水量分布特征, 2020/6/7按业务要求制作.

    Args:
        ax (matplotlib.axes.Axes): the `Axes` instance used for plotting.
        prep (dictionary): precipitation, dictionary: {'lon': 1D array, 'lat': 1D array, 'data': 2D array}
        map_extent (tuple, optional): (lonmin, lonmax, latmin, latmax),. Defaults to (107., 112, 23.2, 26.5).
        back_image (str, opional): the background image name. Default is stamen 'terrain-background', else is
                                      arcgis map server 'World_Physical_Map' (max zoom level is 8)
        back_image_zoom (int, optional): the zoom level for background image. Defaults to 8.
        draw_station (bool, optional): draw station name. Defaults to True.
        station_info (str, optional): station information, 'cities' is 260 city names, or province captial shows.
        station_size (int, optional): station font size. Defaults to 22.
        title (str, optional): title string. Defaults to "降水量实况图".
    
    Example:
        import pandas as pd
        from nmc_met_graphics.plot.precipitation import draw_total_precipitation
        from nmc_met_io.retrieve_micaps_server import get_model_grids

        # read data
        times = pd.date_range(start = pd.to_datetime('2020-06-02 08:00'), end =  pd.to_datetime('2020-06-07 08:00'), freq='1H')
        dataset = get_model_grids("CLDAS/RAIN01_TRI_DATA_SOURCE", times.strftime("%y%m%d%H.000"))
        data = dataset.sum(dim="time")
        data['data'].values[data['data'].values > 2400.0] = np.nan
        prep = {'lon': data['lon'].values, 'lat': data['lat'].values, 'data': data['data'].values}

        # draw the figure
        draw_total_precipitation(prep);
    """

    # set figure size
    fig = plt.figure(figsize=(16, 14.5))

    # set map projection
    datacrs = ccrs.PlateCarree()
    mapcrs = ccrs.LambertConformal(
        central_longitude=np.mean(map_extent[0:1]), central_latitude=np.mean(map_extent[2:3]),
        standard_parallels=(30, 60))
    ax = plt.axes((0.1, 0.08, 0.85, 0.92), projection=mapcrs)
    ax.set_extent(map_extent, crs=datacrs)

    # add map background
    add_china_map_2cartopy(ax, name='province', edgecolor='k', lw=1)
    add_china_map_2cartopy(ax, name='river', edgecolor='cyan', lw=1)
    if back_image == 'terrain-background':
        stamen_terrain = cimg.Stamen('terrain-background')
        ax.add_image(stamen_terrain, back_image_zoom)
    else:
        image = cimg.GoogleTiles(url="https://server.arcgisonline.com/arcgis/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}.jpg")
        ax.add_image(image, back_image_zoom)

    # set colors and levels
    clevs = [50, 100, 200, 300, 400, 500, 600]
    colors = ['#6ab4f1', '#0001f6', '#f405ee', '#ffa900', '#fc6408', '#e80000', '#9a0001']
    linewidths = [1, 1, 2, 2, 3, 4, 4]
    cmap, norm = mpl.colors.from_levels_and_colors(clevs, colors, extend='max')

    # draw precipitation contour map
    x, y = np.meshgrid(prep['lon'], prep['lat'])
    if just_contourf:
        _ = ax.contourf(
            x, y, np.squeeze(prep['data']), clevs, norm=norm,
            cmap=cmap, transform=datacrs, extend='max', alpha=0.5)
    else:
        _ = ax.contourf(
            x, y, np.squeeze(prep['data']), clevs, norm=norm,
            cmap=cmap, transform=datacrs, extend='max', alpha=0.1)
        con2 = ax.contour(
            x, y, np.squeeze(prep['data']), clevs, norm=norm,
            cmap=cmap, transform=datacrs, linewidths=linewidths)
        # add path effects
        plt.setp(con2.collections, path_effects=[
            path_effects.SimpleLineShadow(), path_effects.Normal()])

    # add title and legend
    font = FontProperties(family='Microsoft YaHei', size=32)
    ax.set_title('降水量实况图(累计降水: 6月02日—6月06日)', loc='center', fontproperties=font)
    font = FontProperties(family='Microsoft YaHei', size=16)
    plt.legend([mpatches.Patch(color=b) for b in colors],[
        '50~100 毫米', '100~200 毫米', '200-300 毫米', '300~400 毫米', '400~500 毫米', '500~600 毫米', '>=600毫米'],
        prop=font)

    # add city information
    if draw_station:
        if station_info == 'cities':
            cities = pd.read_csv(pkg_resources.resource_filename(
                'nmc_met_graphics', "resources/stations/cma_city_station_info.dat"),  delimiter=r"\s+")
        else:
            cities = pd.read_csv(pkg_resources.resource_filename(
                'nmc_met_graphics', "resources/stations/provincial_capital.csv"))
        font = FontProperties(family='SimHei', size=22, weight='bold')
        geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
        for _, row in cities.iterrows():
            text_transform = offset_copy(geodetic_transform, units='dots', x=-5)
            ax.plot(row['lon'], row['lat'], marker='o', color='white', markersize=8,
                    alpha=0.7, transform=datacrs)
            ax.text(row['lon'], row['lat'], row['city_name'], clip_on=True,
                    verticalalignment='center', horizontalalignment='right',
                    transform=text_transform, fontproperties=font, color='white',
                    path_effects=[
                        path_effects.Stroke(linewidth=1, foreground='black'),path_effects.Normal()])
    
    return fig


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
