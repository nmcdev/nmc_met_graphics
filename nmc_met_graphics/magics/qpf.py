# _*_ coding: utf-8 _*_

# Copyright (c) 2020 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Quatitative precipitation forecast.
"""

import numpy as np
import xarray as xr
from nmc_met_graphics.magics import util, map_set, common
from nmc_met_graphics.util import check_region_to_contour, check_kwargs
from Magics import macro as magics


def draw_qpf(prep, lon, lat, mslp=None, map_region=None, atime=24,
             title_kwargs={}, outfile=None):
    """
    Draw precipitable water.

    Args:
        prep (np.array): precipitation, 2D array, [nlat, nlon]
        lon (np.array): longitude, 1D array, [nlon]
        lat (np.array): latitude, 1D array, [nlat]
        mslp (np.array, optional), mean sea level data, 2D array, [nlat, nlon]
        map_region (list or tuple): the map region limit, [lonmin, lonmax, latmin, latmax]
        title_kwargs (dictionaly, optional): keyword arguments for _get_title function.
    """

    # put data into fields
    prep_field = util.minput_2d(prep, lon, lat, {'long_name': 'precipitation', 'units': 'mm'}, map_region=map_region)
    mslp_field = util.minput_2d(mslp, lon, lat, {'long_name': 'height', 'units': 'gpm'}, map_region=map_region)

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

    # Define the shading for precipitation water.
    if atime == 24:
        level_list = [0.1, 2.5, 5, 7.5] + [3*i+10 for i in range(5)] + [5*i+25 for i in range(5)] + \
                     [5*i+50 for i in range(10)] + [30*i+100 for i in range(5)] + [50*i+250 for i in range(5)] + \
                     [100*i+500 for i in range(6)]
    elif (atime == 12) or (atime == 6):
        level_list = [0.1, 0.5] + [i+1 for i in range(3)] + [1.5*i + 4 for i in range(6)] + \
                     [2*i+13 for i in range(6)] + [5*i+25 for i in range(14)] + [10*i+100 for i in range(9)]
    else:
        level_list = [0.01, 0.1] + [0.5*i+0.5 for i in range(3)] + [i + 2 for i in range(6)] + \
                     [2*i+8 for i in range(8)] + [4*i+24 for i in range(12)] + [8*i+76 for i in range(9)]
    prep_contour = magics.mcont(
        legend= 'on',
        contour_shade= "on",
        contour_hilo= "off",
        contour= "off",
        contour_label= "off",
        #contour_shade_method= "area_fill",
        contour_shade_technique= "grid_shading",
        contour_level_selection_type= "level_list",
        contour_level_list =  level_list,
        contour_shade_colour_method = "list",
        contour_shade_colour_list = [
            '#BABABA', '#A6A1A1', '#7E7E7E', '#6C6C6C', 
            '#B2F8B0', '#94F397', '#56EE6C', '#2EB045', '#249C3B', 
            '#2562C6', '#347EE4', '#54A1EB', '#94CEF4', '#B2EEF6', 
            '#FDF8B2', '#FDE688', '#FDBC5C', '#FD9E42', '#FB6234', 
            '#FB3D2D', '#DD2826', '#BA1B21', '#9F1A1D', '#821519', 
            '#624038', '#88645C', '#B08880', '#C49C94', '#F0DAD1', 
            '#CBC4D9', '#A99CC1', '#9687B6', '#715C99', '#65538B', 
            '#73146F', '#881682', '#AA19A4', '#BB1BB5', '#C61CC0', '#D71ECF'])
    plots.extend([prep_field, prep_contour])

    # Define the simple contouring for gh
    if mslp_field is not None:
        mslp_contour = common._get_mslp_contour()
        plots.extend([mslp_field, mslp_contour])

    # Add a legend
    legend = common._get_legend(china_map, title="Precipitation [mm]", frequency=1)
    plots.append(legend)

    # Add the title
    title_kwargs = check_kwargs(title_kwargs, 'head', "Precipitation | MSLP")
    title = common._get_title(**title_kwargs)
    plots.append(title)

    # Add china province
    china_coastlines = map_set.get_mcoast(name='PROVINCE')
    plots.append(china_coastlines)

    # final plot
    return util.magics_plot(plots, outfile)

