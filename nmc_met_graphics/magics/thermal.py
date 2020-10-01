# _*_ coding: utf-8 _*_

# Copyright (c) 2020 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Plot atmospheric thermal maps.
"""

import numpy as np
import xarray as xr
from nmc_met_graphics.magics import util, map_set, common
from nmc_met_graphics.util import check_kwargs
from Magics import macro as magics


def draw_temp_high(temp, lon, lat, gh=None, map_region=None, 
                   title_kwargs={}, outfile=None):
    """
    Draw high temperature field.

    Args:
        temperature (np.array): temperature, 2D array, [nlat, nlon]
        lon (np.array): longitude, 1D array, [nlon]
        lat (np.array): latitude, 1D array, [nlat]
        gh (np.array): geopotential height, 2D array, [nlat, nlon]
        map_region (list or tuple): the map region limit, [lonmin, lonmax, latmin, latmax]
        title_kwargs (dictionaly, optional): keyword arguments for _get_title function.
    """

    # put data into fields
    temp_field = util.minput_2d(temp, lon, lat, {'long_name': 'Temperature', 'units': 'degree'})
    gh_field = util.minput_2d(gh, lon, lat, {'long_name': 'height', 'units': 'gpm'})

    #
    # set up visual parameters
    #

    plots = []

    # Setting the coordinates of the geographical area
    if map_region is None:
        china_map = map_set.get_mmap(
            name='CHINA_CYLINDRICAL',
            subpage_frame_thickness = 5)
    else:
        china_map = map_set.get_mmap(
            name='CHINA_REGION_CYLINDRICAL',
            map_region=map_region,
            subpage_frame_thickness = 5)
    plots.append(china_map)

    # Background Coaslines
    coastlines = map_set.get_mcoast(name='COAST_FILL')
    plots.append(coastlines)

    # Define the shading for teperature
    temp_contour = magics.mcont(
        legend= 'on',
        contour_shade= "on",
        contour_hilo= "off",
        contour= "off",
        contour_label= "off",
        contour_shade_method= "area_fill",
        contour_shade_max_level= 42.,
        contour_shade_min_level= -42.,
        contour_level_selection_type= "interval",
        contour_interval= 3.,
        contour_shade_colour_method= "palette",
        contour_shade_palette_name= "eccharts_rainbow_purple_magenta_31")
    plots.extend([temp_field, temp_contour])

    temp_contour_zero = magics.mcont(
        contour_level_selection_type = "level_list",
        contour_level_list = [0.00],
        contour_line_colour = "red",
        contour_line_thickness = 4,
        contour_highlight = "off",
        contour_label = "off",
        contour_min_level = -1.00,
        contour_max_level = 1.00,
        legend = "off")
    plots.extend([temp_field, temp_contour_zero])

    # Define the simple contouring for gh
    if gh_field is not None:
        gh_contour = common._get_gh_contour()
        plots.extend([gh_field, gh_contour])

    # Add a legend
    legend = common._get_legend(china_map, title="Temperature [Degree]")
    plots.append(legend)

    # Add the title
    title_kwargs = check_kwargs(title_kwargs, 'head', "850hPa T | 500hPa GH")
    title = common._get_title(**title_kwargs)
    plots.append(title)

    # Add china province
    china_coastlines = map_set.get_mcoast(name='PROVINCE')
    plots.append(china_coastlines)

    # final plot
    return util.magics_plot(plots, outfile)

