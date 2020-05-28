# _*_ coding: utf-8 _*_

# Copyright (c) 2020 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Moisture analysis maps.
"""

import numpy as np
import xarray as xr
import Magics.macro as magics
from nmc_met_graphics.magics import util, map_set


# global variables
out_png_width = 1200


def draw_pwat(pwat, lon, lat, map_region=None, 
              head_info=None, date_obj=None, outfile=None):
    """
    Draw precipitable water.

    Args:
        pwat (np.array): pressure, 2D array, [nlat, nlon]
        lon (np.array): longitude, 1D array, [nlon]
        lat (np.array): latitude, 1D array, [nlat]
        map_region (list or tuple): the map region limit, [lonmin, lonmax, latmin, latmax]
        head_info (string, optional): head information string. Defaults to None.
        date_obj (datetime, optional): datetime object, like 
            date_obj = dt.datetime.strptime('2016071912','%Y%m%d%H'). Defaults to None.
    """

    # put data into fields
    pwat_field = util.minput_2d(pwat, lon, lat, {'long_name': 'precipitable water', 'units': 'mm'})

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
    pwat_contour = magics.mcont(
        legend= 'on',
        contour_shade= "on",
        contour_hilo= "off",
        contour= "off",
        contour_label= "off",
        contour_shade_method= "area_fill",
        contour_level_selection_type= "level_list",
        contour_level_list =  [i*1.0 for i in range(25)] + [i*2.0 + 26 for i in range(30)],
        contour_shade_colour_method = "list",
        contour_shade_colour_list = [
            '#C5C5C5', '#B5B5B5', '#A1A1A1', '#8B8B8B', '#787878', '#636363', '#505050', '#3B3B3B',
            '#5B431F', '#6D583B', '#866441', '#9C7B46', '#B28C5D', '#CA9D64', '#D8AC7D', '#B9B5FF',
            '#A7A8E1', '#989ACD', '#8686C6', '#6B6CA4', '#5A5B91', '#474880', '#016362', '#1D6C59',
            '#2C774E', '#398545', '#589A39', '#6FA720', '#8BB41A', '#A29E54', '#AEAD43', '#C4C732',
            '#D9DB18', '#F0EC11', '#E96F57', '#C55645', '#B04035', '#9D2527', '#8A121C', '#7B0007', 
            '#7A0076', '#8E0096', '#AE00B8', '#C300C0', '#E200E1', '#A002DB', '#7901DD', '#6201DE', 
            '#3C00DC', '#2500D9', '#0028DD', '#004ED6', '#0571E0', '#0C98E7', '#02B8DD'])

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
        legend_title_text= "Precipitable Water",
        legend_text_font_size = "0.5")

    # Add the title
    text_lines = []
    if head_info is not None:
        text_lines.append("<font size='1'>{}</font>".format(head_info))
    else:
        text_lines.append("<font size='1'>Precipitable Water (mm)</font>")
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
            output, china_map, coastlines, pwat_field, pwat_contour,
            legend, title, china_coastlines)
    else:
        return magics.plot(
            china_map, coastlines, pwat_field, pwat_contour,
            legend, title, china_coastlines)
