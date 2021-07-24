# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Draw synoptic analysis graphics.
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from nmc_met_graphics.plot.mapview import add_china_map_2cartopy
from nmc_met_graphics.cmap.cm import guide_cmaps


def draw_gh500_uv850_mslp(ax, gh500=None, uv850=None, mslp=None,
                          map_extent=(50, 150, 0, 65), add_china=True,
                          regrid_shape=20):
    """
    Draw 500-hPa geopotential height contours, 850-hPa wind barbs
    and mean sea level pressure filled contours.

    :param ax: `matplotlib.axes.Axes`, the `Axes` instance used for plotting.
    :param gh500: 500-hPa gh, dictionary:
                  necessary, {'lon': 1D array, 'lat': 1D array,
                              'data': 2D array}
                  optional, {'clevs': 1D array}
    :param uv850: 850-hPa u-component and v-component wind, dictionary:
                  necessary, {'lon': 1D array, 'lat': 1D array,
                              'udata': 2D array, 'vdata': 2D array}
    :param mslp: MSLP, dictionary:
                 necessary, {'lon': 1D array, 'lat': 1D array,
                             'data': 2D array}
                 optional, {'clevs': 1D array}
    :param map_extent: [lonmin, lonmax, latmin, latmax],
                       longitude and latitude range.
    :param add_china: add china map or not.
    :param regrid_shape: control the wind barbs density.
    :return: plots dictionary.

    :Examples:
    See dk_tool_weather_map.synoptic.gh500_uv850_mslp
    """

    # set data projection
    datacrs = ccrs.PlateCarree()

    # plot map background
    ax.set_extent(map_extent, crs=datacrs)
    ax.add_feature(cfeature.LAND, facecolor='0.6')
    ax.coastlines('50m', edgecolor='black', linewidth=0.75, zorder=100)
    if add_china:
        add_china_map_2cartopy(
            ax, name='province', edgecolor='darkcyan', lw=1, zorder=100)

    # define return plots
    plots = {}

    # draw mean sea level pressure
    if mslp is not None:
        x, y = np.meshgrid(mslp['lon'], mslp['lat'])
        clevs = mslp.get('clevs')
        if clevs is None:
            clevs = np.arange(960, 1065, 5)
        cmap = guide_cmaps(26)
        plots['mslp'] = ax.contourf(
            x, y, np.squeeze(mslp['data']), clevs,
            cmap=cmap, alpha=0.8, zorder=10, transform=datacrs)

    # draw 850-hPa wind bards
    if uv850 is not None:
        x, y = np.meshgrid(uv850['lon'], uv850['lat'])
        u = np.squeeze(uv850['udata']) * 2.5
        v = np.squeeze(uv850['vdata']) * 2.5
        plots['uv850'] = ax.barbs(
            x, y, u, v, length=6, regrid_shape=regrid_shape,
            transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.05),
            zorder=20)

    # draw 500-hPa geopotential height
    if gh500 is not None:
        x, y = np.meshgrid(gh500['lon'], gh500['lat'])
        clevs = gh500.get('clevs')
        if clevs is None:
            clevs = np.append(np.arange(480, 584, 8), np.arange(580, 604, 4))
        plots['gh500'] = ax.contour(
            x, y, np.squeeze(gh500['data']), clevs, colors='purple',
            linewidths=2, transform=datacrs, zorder=30)
        plt.clabel(plots['gh500'], inline=1, fontsize=16, fmt='%.0f')

    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--')
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

    # return plots
    return plots


def draw_uv850(ax, uv850=None, gh850=None, map_extent=(73, 136, 18, 54),
               add_china=True, regrid_shape=15):
    """
    Draw 850-hPa wind field.

    :param ax: `matplotlib.axes.Axes`, the `Axes` instance used for plotting.
    :param uv850: 850-hPa u-component and v-component wind, dictionary:
                  necessary, {'lon': 1D array, 'lat': 1D array,
                              'udata': 2D array, 'vdata': 2D array}
                  optional, {'clevs': 1D array speed contour levels}
    :param gh850: optional, {'clevs': 1D array}
    :param map_extent: [lonmin, lonmax, latmin, latmax],
                       longitude and latitude range.
    :param add_china: add china map or not.
    :param regrid_shape: control the wind barbs density.
    :return: plots dictionary.
    """

    # set data projection
    datacrs = ccrs.PlateCarree()

    # plot map background
    ax.set_extent(map_extent, crs=datacrs)
    ax.add_feature(cfeature.LAND, facecolor='0.6')
    ax.coastlines('50m', edgecolor='black', linewidth=0.75, zorder=100)
    if add_china:
        add_china_map_2cartopy(
            ax, name='province', edgecolor='darkcyan', lw=1, zorder=100)

    # define return plots
    plots = {}

    # draw 850hPa wind speed and barbs
    if uv850 is not None:
        x, y = np.meshgrid(uv850['lon'], uv850['lat'])
        u = np.squeeze(uv850['udata'])
        v = np.squeeze(uv850['vdata'])
        clevs = uv850.get('clevs')
        if clevs is None:
            clevs = np.arange(4, 40, 4)
        cmaps = guide_cmaps("2")
        plots['uv850_cf'] = ax.contourf(
            x, y, np.sqrt(u * u + v * v), clevs, cmap=cmaps, transform=datacrs)
        plots['uv850_bb'] = ax.barbs(
            x, y, u*2.5, v*2.5, length=7, regrid_shape=regrid_shape,
            transform=datacrs, sizes=dict(emptybarb=0.05))

    # draw 850hPa geopotential height
    if gh850 is not None:
        x, y = np.meshgrid(gh850['lon'], gh850['lat'])
        clevs = gh850.get('clevs')
        if clevs is None:
            clevs = np.arange(80, 180, 4)
        plots['gh850'] = ax.contour(
            x, y, np.squeeze(gh850['data']), clevs, colors='purple',
            linewidths=2, transform=datacrs, zorder=30)
        plt.clabel(plots['gh850'], inline=1, fontsize=16, fmt='%.0f')

    # add grid lines
    gl = ax.gridlines(
        crs=ccrs.PlateCarree(), draw_labels=True, linewidth=2,
        color='gray', alpha=0.5, linestyle='--')
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xlabel_style = {'size': 16}
    gl.ylabel_style = {'size': 16}

    # return
    return plots


def draw_wind850(ax, lon, lat, u, v, mslp=None, gh500=None,
                 thetae850=None, map_extent=(73, 136, 18, 54),
                 wspeed_clev=np.arange(4, 40, 4),
                 mslp_clev=np.arange(960, 1060, 4), wind_cmap=None,
                 gh500_clev=np.arange(480, 600, 2),
                 thetae850_clev=np.arange(280, 360, 4),
                 draw_barbs=True, left_title="850hPa wind", right_title=None,
                 add_china=True, coastline_color='black', title_font=None,
                 cax=None, cb_title='850hPa wind speed (m/s)', cb_font=None):
    """
    Draw 850hPa wind field.

    :param ax: matplotlib axes.
    :param lon: longitude coordinates.
    :param lat: latitude coordinates.
    :param u: u wind.
    :param v: v wind.
    :param mslp: mean sea level pressure, [lon, lat, mslp_data]
    :param gh500: 500hPa geopotential height, [lon, lat, gh500_data]
    :param thetae850: 850hPa equivalent potential temperature,
                      [lon, lat, thetae850_data]
    :param map_extent: map extent
    :param wspeed_clev: wind speed filled contour levels.
    :param mslp_clev: mean sea level contour levels.
    :param wind_cmap: wind filled contour color map.
    :param gh500_clev: geopotential height 500 contour levels.
    :param thetae850_clev: 850hPa theta contour levels.
    :param draw_barbs: flag for drawing wind barbs.
    :param cax: color bar axes, if None, no color bar will be draw.
    :param left_title: left title.
    :param right_title: right title.
    :param add_china: draw china province boundary or not.
    :param coastline_color: coast line color.
    :param title_font: title font properties, like:
                       title_font = mpl.font_manager.FontProperties(
                           fname='C:/Windows/Fonts/SIMYOU.TTF')
    :param cb_title: color bar title
    :param cb_font: color bar title font properties
    :return: wind filled contour cf and barbs bb object.

    """

    # set data projection, should be longitude and latitude.
    datacrs = ccrs.PlateCarree()

    # clear figure
    ax.clear

    # set map extent
    ax.set_extent(map_extent)

    # add map boundary
    ax.coastlines('50m', edgecolor=coastline_color)
    if add_china:
        add_china_map_2cartopy(ax, name='province', edgecolor='darkcyan')

    # draw 850hPa wind speed
    x, y = np.meshgrid(lon, lat)
    if wind_cmap is None:
        wind_cmap = guide_cmaps("2")
    cf = ax.contourf(
        x, y, np.sqrt(u*u + v*v), wspeed_clev,
        cmap=wind_cmap, transform=datacrs)
    if cax is not None:
        cb = plt.colorbar(
            cf, cax=cax, orientation='horizontal',
            extendrect=True, ticks=wspeed_clev)
        cb.set_label(
            cb_title, size='large', fontsize=16, fontproperties=cb_font)
        cb.ax.tick_params(labelsize=16)

    # draw wind barbs
    if draw_barbs:
        bb = ax.barbs(
            x, y, u, v, length=7, regrid_shape=15, transform=datacrs,
            sizes=dict(emptybarb=0.05))

    # draw mean sea level pressure
    if mslp is not None:
        x, y = np.meshgrid(mslp[0], mslp[1])
        cs1 = ax.contour(
            x, y, mslp[2], mslp_clev, colors='k',
            linewidth=1.0, linestyles='solid', transform=datacrs)
        plt.clabel(
            cs1, fontsize=10, inline=1, inline_spacing=10, fmt='%i',
            rightside_up=True, use_clabeltext=True)

    # draw 500hPa geopotential height
    if gh500 is not None:
        x, y = np.meshgrid(gh500[0], gh500[1])
        cs2 = ax.contour(
            x, y, gh500[2], gh500_clev, colors='w',
            linewidth=1.0, linestyles='dashed', transform=datacrs)
        plt.clabel(
            cs2, fontsize=10, inline=1, inline_spacing=10,
            fmt='%i', rightside_up=True, use_clabeltext=True)

    # draw 850hPa equivalent potential temperature
    if thetae850 is not None:
        x, y = np.meshgrid(thetae850[0], thetae850[1])
        cmap = plt.get_cmap("hsv")
        cs3 = ax.contour(
            x, y, thetae850[2], thetae850_clev, cmap=cmap,
            linewidth=0.8, linestyles='solid', transform=datacrs)
        plt.clabel(
            cs3, fontsize=10, inline=1, inline_spacing=10, fmt='%i',
            rightside_up=True, use_clabeltext=True)

    # add grid lines
    gl = ax.gridlines(
        crs=ccrs.PlateCarree(), draw_labels=True, linewidth=2,
        color='gray', alpha=0.5, linestyle='--')
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xlabel_style = {'size': 16}
    gl.ylabel_style = {'size': 16}

    # add title
    ax.set_title(
        left_title, loc='left', fontsize=18, fontproperties=title_font)
    if right_title is not None:
        ax.set_title(
            right_title, loc='right', fontsize=18, fontproperties=title_font)

    # return plot
    if draw_barbs:
        return cf, bb
    else:
        return cf


def draw_theta_on_pv(ax, lon, lat, theta, mslp=None, gh500=None,
                     map_extent=(73, 136, 18, 54),
                     theta_clev=np.arange(300, 400, 4), alpha=0,
                     mslp_clev=np.arange(960, 1060, 4),
                     gh500_clev=np.arange(480, 600, 2),
                     cax=None, left_title="850hPa wind", right_title=None,
                     add_china=True, coastline_color='black'):
    """
    Draw potential temperature on pv surface.

    :param ax: matplotlib axes.
    :param lon: longitude coordinates.
    :param lat: latitude coordinates.
    :param theta: potential temperature.
    :param mslp: mean sea level pressure.
    :param gh500: geopotential height 500hpa.
    :param map_extent: map extent.
    :param theta_clev: potential temperature.
    :param alpha: theta contour transparency.
    :param mslp_clev: mean sea level contour levels.
    :param gh500_clev: geopotential height 500 contour levels.
    :param cax: color bar axes.
    :param left_title: left title.
    :param right_title: right title.
    :param add_china: draw china province map or not.
    :param coastline_color: coast lines color.
    :return: potential temperature filled contour cf object.
    """

    # set data projection, should be longitude and latitude.
    datacrs = ccrs.PlateCarree()

    # clear figure
    ax.clear

    # set map extent
    ax.set_extent(map_extent)

    # add map boundary
    ax.coastlines('50m', edgecolor=coastline_color)
    if add_china:
        add_china_map_2cartopy(
            ax, name='province', edgecolor='darkcyan', lw=4)

    # draw potential temperature
    x, y = np.meshgrid(lon, lat)
    cmap = guide_cmaps("27")
    cf = ax.contourf(
        x, y, theta, theta_clev, cmap=cmap, alpha=alpha,
        antialiased=True, transform=datacrs)
    if cax is not None:
        cb = plt.colorbar(
            cf, cax=cax, orientation='horizontal',
            extendrect=True, ticks=theta_clev)
        cb.set_label(
            'Potential Temperature [K]', size='large', fontsize=16)
        cb.ax.tick_params(labelsize=16)

    # draw mean sea level pressure
    if mslp is not None:
        x, y = np.meshgrid(mslp[0], mslp[1])
        cs1 = ax.contour(
            x, y, mslp[2], mslp_clev, colors='k', linewidth=1.0,
            linestyles='solid', transform=datacrs)
        plt.clabel(
            cs1, fontsize=10, inline=1, inline_spacing=10,
            fmt='%i', rightside_up=True, use_clabeltext=True)

    # draw 500hPa geopotential height
    if gh500 is not None:
        x, y = np.meshgrid(gh500[0], gh500[1])
        cs2 = ax.contour(
            x, y, gh500[2], gh500_clev, colors='w', linewidth=1.0,
            linestyles='dashed', transform=datacrs)
        plt.clabel(
            cs2, fontsize=10, inline=1, inline_spacing=10, fmt='%i',
            rightside_up=True, use_clabeltext=True)

    # add grid lines
    gl = ax.gridlines(
        crs=ccrs.PlateCarree(), draw_labels=True, linewidth=2,
        color='gray', alpha=0.5, linestyle='--')
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xlabel_style = {'size': 16}
    gl.ylabel_style = {'size': 16}

    # add title
    ax.set_title(left_title, loc='left', fontsize=18)
    if right_title is not None:
        ax.set_title(right_title, loc='right', fontsize=18)

    # return plot
    return cf
