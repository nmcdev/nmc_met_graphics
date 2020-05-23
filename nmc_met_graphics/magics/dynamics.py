# _*_ coding: utf-8 _*_

# Copyright (c) 2020 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Plot atmospheric dynamics maps.
"""

import numpy as np
import xarray as xr
import Magics.macro as magics
from nmc_met_graphics.magics import util, map_set


def draw_wind_200(u200, v200, lon, lat, gh200=None, skip_vector=1, 
                  head=None, date_obj=None, outfile=None):
    """
    Draw 200hPa wind speed and vector field.

    Args:
        u200 (np.array): u wind component, 2D array, [nlat, nlon]
        v200 (np.array): v wind component, 2D array, [nlat, nlon]
        lon (np.array): longitude, 1D array, [nlon]
        lat (np.array): latitude, 1D array, [nlat]
        gh200 (np.array): geopotential height, 2D array, [nlat, nlon]
        skip_vector (integer): skip grid number for vector plot
        head (string, optional): head string. Defaults to None.
        date_obj (datetime, optional): datetime object, like 
            date_obj = dt.datetime.strptime('2016071912','%Y%m%d%H'). Defaults to None.
    """

    # put data into fields
    wind200_field = util.minput_2d_vector(u200, v200, lon, lat, skip=skip_vector)
    speed200_field = util.minput_2d(np.sqrt(u200*u200 + v200*v200), lon, lat, {'long_name': '200hPa Wind Speed', 'units': 'm/s'})
    if gh200 is not None:
        gh200_feild = util.minput_2d(gh200, lon, lat, {'long_name': 'height', 'units': 'gpm'})

    #
    # set up visual parameters
    #

    # Setting the coordinates of the geographical area
    china_map = map_set.get_mmap(
        name='CHINA_CYLINDRICAL',
        subpage_frame_thickness = 5)

    # Background Coaslines
    coastlines = map_set.get_mcoast(name='COAST_FILL')
    china_coastlines = map_set.get_mcoast(name='PROVINCE')

    # Define the simple contouring for gh
    gh200_contour = magics.mcont(
        legend= 'off', 
        contour_level_selection_type= 'interval',
        contour_interval= 50.,
        contour_line_colour= 'black',
        contour_line_thickness= 1,
        contour_label= 'on',
        contour_label_height= 0.5,
        contour_highlight_colour= 'black',
        contour_highlight_thickness= 2)

    # Define the shading for the wind speed
    speed200_contour = magics.mcont(
        legend= 'on',
        contour_level_selection_type= 'level_list', 
        contour_level_list= [30., 40., 50., 60., 70., 80., 90., 100.], 
        contour_shade= 'on', 
        contour_shade_max_level_colour= 'evergreen', 
        contour_shade_min_level_colour= 'yellow',
        contour_shade_method= 'area_fill', 
        contour_reference_level= 0., 
        contour_highlight= 'off', 
        contour_hilo= 'hi', 
        contour_hilo_format= '(F3.0)', 
        contour_hilo_height= 0.6, 
        contour_hilo_type= 'number', 
        contour_hilo_window_size=10,
        contour_label= 'off')

    # Define the wind vector
    uv200_wind = magics.mwind(
        legend= 'on',
        wind_field_type= 'arrows',
        wind_arrow_head_shape=1,
        wind_arrow_thickness= 0.5,
        wind_arrow_unit_velocity=50,
        wind_arrow_colour= 'evergreen')

    # Add a legend
    legend = magics.mlegend(
        legend= 'on',
        legend_text_colour= 'black',
        legend_box_mode= 'positional',
        legend_box_x_position= 26,
        legend_box_y_position= 3.,
        legend_box_x_length= 2.,
        legend_box_y_length= 16.,
        legend_border= 'off',
        legend_border_colour= 'black',
        legend_box_blanking= 'on',
        legend_display_type= 'continuous',
        legend_title = "on",
        legend_title_text= "Wind speed at 200 hPa",
        legend_text_font_size = "0.5")

    # Add the title
    text_lines = []
    if head is not None:
        text_lines.append("<font size='1'>{}</font>".format(head))
    else:
        text_lines.append("<font size='1'>200hPa Wind[m/s] and Height[gpm]</font>")
    if date_obj is not None:
        text_lines.append("<font size='0.8' colour='red'>{}</font>".format(date_obj.strftime("%Y/%m/%d %H:%M(UTC)")))
    title = magics.mtext(
        text_lines = text_lines,
        text_justification = 'left',
        text_font_size = 0.5,
        text_mode = "positional",
        text_box_x_position = 2.00,
        text_box_y_position = 19.0,
        text_colour = 'charcoal')

    # draw the figure
    if outfile is not None:
        output = magics.output(
            output_formats= ['png'],
            output_name_first_page_number= 'off',
            output_width= 1200,
            output_name= outfile)

        if gh200 is not None:
            magics.plot(
                output, china_map, coastlines, china_coastlines, speed200_field, speed200_contour,
                wind200_field, uv200_wind, gh200_feild, gh200_contour, legend, title)
        else:
            magics.plot(
                output, china_map, coastlines, china_coastlines, speed200_field, speed200_contour,
                wind200_field, uv200_wind, legend, title)
    else:
        if gh200 is not None:
            return magics.plot(
                china_map, coastlines, china_coastlines, speed200_field, speed200_contour,
                wind200_field, uv200_wind, gh200_feild, gh200_contour, legend, title)
        else:
            return magics.plot(
                china_map, coastlines, china_coastlines, speed200_field, speed200_contour,
                wind200_field, uv200_wind, legend, title)


