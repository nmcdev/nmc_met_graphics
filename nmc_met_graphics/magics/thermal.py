# _*_ coding: utf-8 _*_

# Copyright (c) 2020 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Plot atmospheric thermal maps.
"""

import numpy as np
import xarray as xr
import Magics.macro as magics
from nmc_met_graphics.magics import util, map_set


# global variables
out_png_width = 1200


def draw_temp_high(temp, lon, lat, gh=None, map_region=None, 
                   head_info=None, date_obj=None, outfile=None):
    """
    Draw high temperature field.

    Args:
        temperature (np.array): temperature, 2D array, [nlat, nlon]
        lon (np.array): longitude, 1D array, [nlon]
        lat (np.array): latitude, 1D array, [nlat]
        gh (np.array): geopotential height, 2D array, [nlat, nlon]
        map_region (list or tuple): the map region limit, [lonmin, lonmax, latmin, latmax]
        head_info (string, optional): head information string. Defaults to None.
        date_obj (datetime, optional): datetime object, like 
            date_obj = dt.datetime.strptime('2016071912','%Y%m%d%H'). Defaults to None.
    """

    # put data into fields
    temp_field = util.minput_2d(temp, lon, lat, {'long_name': 'Temperature', 'units': 'degree'})
    if gh is not None:
        gh_field = util.minput_2d(gh, lon, lat, {'long_name': 'height', 'units': 'gpm'})

    #
    # set up visual parameters
    #

    plots = []

    # draw the figure
    if outfile is not None:
        output = magics.output(
            output_formats= ['png'],
            output_name_first_page_number= 'off',
            output_width= out_png_width,
            output_name= outfile)
        plots.append(output)

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
    if gh is not None:
        gh_contour = magics.mcont(
            legend= 'off', 
            contour_level_selection_type= 'interval',
            contour_interval= 20.,
            contour_reference_level= 5880.,
            contour_line_colour= 'black',
            contour_line_thickness= 2,
            contour_label= 'on',
            contour_label_height= 0.5,
            contour_highlight_colour= 'black',
            contour_highlight_thickness= 4)
        plots.extend([gh_field, gh_contour])

    # Add a legend
    legend = magics.mlegend(
        legend= 'on',
        legend_text_colour= 'black',
        legend_box_mode= 'legend_box_mode',
        legend_automatic_position= 'top',
        legend_border= 'off',
        legend_border_colour= 'black',
        legend_box_blanking= 'on',
        legend_display_type= 'continuous',
        legend_title = "on",
        legend_title_text= "Temperature",
        legend_title_font_size= 0.6,
        legend_text_font_size = 0.5)
    plots.append(legend)

    # Add the title
    text_lines = []
    if head_info is not None:
        text_lines.append("<font size='1'>{}</font>".format(head_info))
    else:
        text_lines.append("<font size='1'>850hPa Temperature[Degree] and 500hPa Height[gpm]</font>")
    if date_obj is not None:
        text_lines.append("<font size='0.8' colour='red'>{}</font>".format(date_obj.strftime("%Y/%m/%d %H:%M(UTC)")))
    title = magics.mtext(
        text_lines = text_lines,
        text_justification = 'left',
        text_font_size = 0.6,
        text_mode = "title",
        text_colour = 'charcoal')
    plots.append(title)

    # Add china province
    china_coastlines = map_set.get_mcoast(name='PROVINCE')
    plots.append(china_coastlines)

    # final plot
    return magics.plot(*plots)
