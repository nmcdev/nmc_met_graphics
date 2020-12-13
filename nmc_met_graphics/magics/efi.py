# _*_ coding: utf-8 _*_

# Copyright (c) 2020 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Plot extreme forecast index maps.
"""

from nmc_met_graphics.magics import util, map_set, common
from nmc_met_graphics.util import check_kwargs
from Magics import macro as magics


def draw_efi(efi, lon, lat, sot90=None, sot10=None, gh=None,
             map_region=None, title_kwargs={}, outfile=None):
    """
    Draw extreme forecast index maps.

    Args:
        efi (np.array): extreme forecast index data, 2D array, [nlat, nlon]
        lon (np.array): longitude, 1D array, [nlon]
        lat (np.array): latitude, 1D array, [nlat]
        gh (np.array, optional), geopotential height, 2D array, [nlat, nlon]
        map_region (list or tuple): the map region limit, [lonmin, lonmax, latmin, latmax]
        title_kwargs (dictionaly, optional): keyword arguments for _get_title function.
    """

    # put data into fields
    efi_field = util.minput_2d(efi, lon, lat, {'long_name': 'extreme forecast index', 'units': ''})
    sot90_field = util.minput_2d(sot90, lon, lat, {'long_name': 'shift of tails', 'units': ''})
    sot10_field = util.minput_2d(sot10, lon, lat, {'long_name': 'shift of tails', 'units': ''})
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
    coastlines = map_set.get_mcoast(
        name='COAST_FILL',
        map_grid_latitude_increment=15,
        map_grid_longitude_increment=20)
    plots.append(coastlines)

    # Draw shaded contour
    efi_contour1 = magics.mcont(
        legend= 'on',
        contour_shade= "on",
        contour_hilo= "off",
        contour= "off",
        contour_label= "off",
        contour_shade_technique= "grid_shading",
        contour_level_selection_type= "level_list",
        contour_level_list =  [-1, -0.95, -0.9, -0.8, -0.7, -0.6, -0.5],
        contour_shade_colour_method = "list",
        contour_shade_colour_list = ['#ff32dd', '#1058b0', '#0066ff', '#00ccff', '#05fcaa', '#aafb02'])
    plots.extend([efi_field, efi_contour1])
    efi_contour2 = magics.mcont(
        legend= 'on',
        contour_shade= "on",
        contour_hilo= "off",
        contour= "off",
        contour_label= "off",
        contour_shade_technique= "grid_shading",
        contour_level_selection_type= "level_list",
        contour_level_list =  [0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0],
        contour_shade_colour_method = "list",
        contour_shade_colour_list = ['#fffc01', '#f8b420', '#f86c00', '#f82c00', '#c80800', '#a00000'])
    plots.extend([efi_field, efi_contour2])
    
    # Draw contour lines
    efi_contour3 = magics.mcont(
        contour_level_selection_type = "level_list",
        contour_level_list = [0.3],
        contour_line_colour = "red",
        contour_line_thickness = 1,
        contour_line_style = "dash",
        contour_highlight = "off",
        contour_label = "on",
        contour_label_colour = "red",
        contour_label_height = 0.50)
    plots.extend([efi_field, efi_contour3])
    efi_contour4 = magics.mcont(
        contour_level_selection_type = "level_list",
        contour_level_list = [-0.3],
        contour_line_colour = "blue",
        contour_line_thickness = 1,
        contour_line_style = "dash",
        contour_highlight = "off",
        contour_label = "on",
        contour_label_colour = "blue",
        contour_label_height = 0.50)
    plots.extend([efi_field, efi_contour4])

    # draw SOT (shift of tails) contours
    sot_contour = magics.mcont(
        contour_level_selection_type = "level_list",
        contour_level_list = [0, 1.0, 2.0, 5.0, 8.0],
        contour_line_colour = "black",
        contour_line_thickness = 2,
        contour_line_style = "solid",
        contour_highlight = "off",
        contour_label = "on",
        contour_label_colour = "red",
        contour_label_height = 0.50)
    if sot90_field is not None:
        plots.extend([sot90_field, sot_contour])
    if sot10_field is not None:
        plots.extend([sot10_field, sot_contour])

    # Define the simple contouring for gh
    if gh_field is not None:
        gh_contour = common._get_gh_contour()
        plots.extend([gh_field, gh_contour])

    # Add a legend
    legend = common._get_legend(china_map, title="Extreme Forecast Index", frequency=1)
    plots.append(legend)

    # Add the title
    title_kwargs = check_kwargs(title_kwargs, 'head', "Extreme Forecast Index | 500hPa GH")
    title = common._get_title(**title_kwargs)
    plots.append(title)

    # Add china province
    china_coastlines = map_set.get_mcoast(name='PROVINCE', map_boundaries='on')
    plots.append(china_coastlines)

    # final plot
    return util.magics_plot(plots, outfile)
