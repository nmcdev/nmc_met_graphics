# _*_ coding: utf-8 _*_

# Copyright (c) 2020 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Plot potential vorticity analysis maps.
"""

import numpy as np
import xarray as xr
from nmc_met_graphics.magics import util, map_set, common
from nmc_met_graphics.util import check_kwargs
from Magics import macro as magics


def draw_pres_pv2(pres, lon, lat, map_region=None, 
                  title_kwargs={}, outfile=None):
    """
    Draw pressure field on 2.0PVU surface.

    Args:
        pres (np.array): pressure, 2D array, [nlat, nlon]
        lon (np.array): longitude, 1D array, [nlon]
        lat (np.array): latitude, 1D array, [nlat]
        map_region (list or tuple): the map region limit, [lonmin, lonmax, latmin, latmax]
        title_kwargs (dictionaly, optional): keyword arguments for _get_title function.
    """

    # put data into fields
    pres_field = util.minput_2d(pres, lon, lat, {'long_name': 'pressure', 'units': 'hPa'})

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

    # Define the shading for pressure
    pres_contour = magics.mcont(
        legend= 'on',
        contour_shade= "on",
        contour_hilo= "off",
        contour= "off",
        contour_label= "off",
        contour_shade_method= "area_fill",
        contour_level_selection_type= "level_list",
        contour_level_list = [80., 190., 200., 310., 320., 430., 440., 550.],
        contour_shade_colour_method = "gradients",
        contour_gradients_colour_list = ['#440300','#e7d799','#dde2a4', '#145360', '#1450b2', '#ddecf3', '#d2e2e9', '#a33ab2'],
        contour_gradients_step_list = [11, 1, 11, 1, 11, 1, 11])
    plots.extend([pres_field, pres_contour])

    # Add a legend
    legend = common._get_legend(china_map, title="Pressure [mb]", frequency=2)
    plots.append(legend)

    # Add the title
    title_kwargs = check_kwargs(title_kwargs, 'head', "PVU Surface Pressure")
    title = common._get_title(**title_kwargs)
    plots.append(title)

    # Add china province
    china_coastlines = map_set.get_mcoast(name='PROVINCE')
    plots.append(china_coastlines)

    # final plot
    return util.magics_plot(plots, outfile)
