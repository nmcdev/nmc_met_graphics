# _*_ coding: utf-8 _*_

# Copyright (c) 2020 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Plot potential vorticity analysis maps.
"""

import numpy as np
import xarray as xr
import Magics.macro as magics
from nmc_met_graphics.magics import util, map_set


# global variables
out_png_width = 1200


def draw_pres_pv2(pres, lon, lat, map_region=None, 
                  head_info=None, date_obj=None, outfile=None):
    """
    Draw pressure field on 2.0PVU surface.

    Args:
        pres (np.array): pressure, 2D array, [nlat, nlon]
        lon (np.array): longitude, 1D array, [nlon]
        lat (np.array): latitude, 1D array, [nlat]
        map_region (list or tuple): the map region limit, [lonmin, lonmax, latmin, latmax]
        head_info (string, optional): head information string. Defaults to None.
        date_obj (datetime, optional): datetime object, like 
            date_obj = dt.datetime.strptime('2016071912','%Y%m%d%H'). Defaults to None.
    """

    # put data into fields
    pres_field = util.minput_2d(pres, lon, lat, {'long_name': 'pressure', 'units': 'hPa'})

    #
    # set up visual parameters
    #

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

    # Background Coaslines
    coastlines = map_set.get_mcoast(name='COAST_FILL')
    china_coastlines = map_set.get_mcoast(name='PROVINCE')

    # Define the shading for teperature
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

    # Add a legend
    legend = magics.mlegend(
        legend= 'on',
        legend_text_colour= 'black',
        legend_box_mode= 'legend_box_mode',
        legend_automatic_position= 'right',
        legend_border= 'off',
        legend_border_colour= 'black',
        legend_box_blanking= 'on',
        legend_display_type= 'continuous',
        legend_label_frequency= 2,
        legend_title = "on",
        legend_title_text= "Pressure",
        legend_text_font_size = "0.5")

    # Add the title
    text_lines = []
    if head_info is not None:
        text_lines.append("<font size='1'>{}</font>".format(head_info))
    else:
        text_lines.append("<font size='1'>2 PVU Surface Pressure (mb)</font>")
    if date_obj is not None:
        text_lines.append("<font size='0.8' colour='red'>{}</font>".format(date_obj.strftime("%Y/%m/%d %H:%M(UTC)")))
    title = magics.mtext(
        text_lines = text_lines,
        text_justification = 'left',
        text_font_size = 0.6,
        text_mode = "title",
        text_colour = 'charcoal')

    # draw the figure
    if outfile is not None:
        output = magics.output(
            output_formats= ['png'],
            output_name_first_page_number= 'off',
            output_width= out_png_width,
            output_name= outfile)

        magics.plot(
            output, china_map, coastlines, pres_field, pres_contour,
            legend, title, china_coastlines)
    else:
        return magics.plot(
            china_map, coastlines, pres_field, pres_contour,
            legend, title, china_coastlines)