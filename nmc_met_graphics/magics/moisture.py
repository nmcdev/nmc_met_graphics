# _*_ coding: utf-8 _*_

# Copyright (c) 2020 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Moisture analysis maps.
"""

import math
import numpy as np
import xarray as xr
import Magics.macro as magics
from nmc_met_graphics.magics import util, map_set


# global variables
out_png_width = 1200


def draw_rh_high(uwind, vwind, rh, lon, lat, gh=None, skip_vector=None, 
                 map_region=None, head_info=None, date_obj=None, outfile=None):
    """
    Draw high relative humidity.

    Args:
        uwind (np.array): u wind component, 2D array, [nlat, nlon]
        vwind (np.array): v wind component, 2D array, [nlat, nlon]
        rh (np.array): relative humidity wind component, 2D array, [nlat, nlon]
        lon (np.array): longitude, 1D array, [nlon]
        lat (np.array): latitude, 1D array, [nlat]
        gh (np.array): geopotential height, 2D array, [nlat, nlon]
        skip_vector (integer): skip grid number for vector plot
        map_region (list or tuple): the map region limit, [lonmin, lonmax, latmin, latmax]
        head_info (string, optional): head information string. Defaults to None.
        date_obj (datetime, optional): datetime object, like 
            date_obj = dt.datetime.strptime('2016071912','%Y%m%d%H'). Defaults to None.
    """

    # check default parameters
    if skip_vector is None:
        skip_vector = max(math.ceil(len(lon)/70), math.ceil(len(lat)/35))

    # put data into fields
    wind_field = util.minput_2d_vector(uwind, vwind, lon, lat, skip=skip_vector)
    rh_field = util.minput_2d(rh, lon, lat, {'long_name': 'Relative Humidity', 'units': '%'})
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

    # Define the shading for the wind speed
    rh_contour = magics.mcont(
        legend= 'on',
        contour_level_selection_type= 'level_list', 
        contour_level_list= [0,1.,5.,10,20,30,40,50,60,65,70,75,80,85,90,99,100.],
        contour_shade= 'on', 
        contour= "off",
        contour_shade_method= 'area_fill', 
        contour_shade_colour_method = 'list',
        contour_shade_colour_list = [
            '#644228', '#7f5330', '#9b6238', '#ab754b', '#b78a60', '#d0b494', '#decab2', '#e0dac8',
            '#bdcbab', '#adc59c', '#88bd89', '#6ba48d', '#506c93', '#4d6393', '#5c5692', '#6b4b92',
            '#7a3e94'],
        contour_reference_level= 60., 
        contour_highlight= 'off', 
        contour_hilo= 'hi', 
        contour_hilo_format= '(F3.0)', 
        contour_hilo_height= 0.6, 
        contour_hilo_type= 'number', 
        contour_hilo_window_size=10,
        contour_label= 'off')
    plots.extend([rh_field, rh_contour])

    # Define the wind vector
    wind_vector = magics.mwind(
        legend= 'off',
        wind_field_type= 'flags',
        wind_flag_length = 0.6,
        wind_thinning_factor= 2.,
        wind_flag_style= 'solid', 
        wind_flag_thickness= 1,
        wind_flag_origin_marker = 'dot',
        wind_flag_min_speed = 0.0,
        wind_flag_colour = 'charcoal')
    plots.extend([wind_field, wind_vector])

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
        legend_title_text= "Relative Humidity",
        legend_title_font_size= 0.6,
        legend_text_font_size = 0.5)
    plots.append(legend)

    # Add the title
    text_lines = []
    if head_info is not None:
        text_lines.append("<font size='1'>{}</font>".format(head_info))
    else:
        text_lines.append("<font size='1'>850hPa Wind[m/s], Relative Humidity[%] and 500hPa Height[gpm]</font>")
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


def draw_sp_high(uwind, vwind, sp, lon, lat, gh=None, skip_vector=None, 
                 map_region=None, head_info=None, date_obj=None, outfile=None):
    """
    Draw high specific  humidity.

    Args:
        uwind (np.array): u wind component, 2D array, [nlat, nlon]
        vwind (np.array): v wind component, 2D array, [nlat, nlon]
        sp (np.array): specific humidity wind component, 2D array, [nlat, nlon]
        lon (np.array): longitude, 1D array, [nlon]
        lat (np.array): latitude, 1D array, [nlat]
        gh (np.array): geopotential height, 2D array, [nlat, nlon]
        skip_vector (integer): skip grid number for vector plot
        map_region (list or tuple): the map region limit, [lonmin, lonmax, latmin, latmax]
        head_info (string, optional): head information string. Defaults to None.
        date_obj (datetime, optional): datetime object, like 
            date_obj = dt.datetime.strptime('2016071912','%Y%m%d%H'). Defaults to None.
    """

    # check default parameters
    if skip_vector is None:
        skip_vector = max(math.ceil(len(lon)/70), math.ceil(len(lat)/35))

    # put data into fields
    wind_field = util.minput_2d_vector(uwind, vwind, lon, lat, skip=skip_vector)
    sp_field = util.minput_2d(sp, lon, lat, {'long_name': 'Specific humidity', 'units': 'g kg^-1'})
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

    # Define the shading for the wind speed
    sp_contour = magics.mcont(
        legend= 'on',
        contour_level_selection_type= 'level_list', 
        contour_level_list= [4.0+2*i for i in range(9)] + [24.0+i*4 for i in range(4)],
        contour_shade= 'on', 
        contour= "off",
        contour_shade_method= 'area_fill',
        contour_shade_colour_method = 'palette',
        contour_shade_palette_name = 'eccharts_green_blue_13',
        contour_reference_level= 6., 
        contour_highlight= 'off', 
        contour_hilo= 'hi', 
        contour_hilo_format= '(F3.0)', 
        contour_hilo_height= 0.6, 
        contour_hilo_type= 'number', 
        contour_hilo_window_size=10,
        contour_label= 'off')
    plots.extend([sp_field, sp_contour])

    # Define the wind vector
    wind_vector = magics.mwind(
        legend= 'off',
        wind_field_type= 'flags',
        wind_flag_length = 0.6,
        wind_thinning_factor= 2.,
        wind_flag_style= 'solid', 
        wind_flag_thickness= 1,
        wind_flag_origin_marker = 'dot',
        wind_flag_min_speed = 0.0,
        wind_flag_colour = 'charcoal')
    plots.extend([wind_field, wind_vector])

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
        legend_title_text= "Specific Humidity",
        legend_title_font_size= 0.6,
        legend_text_font_size = 0.5)
    plots.append(legend)

    # Add the title
    text_lines = []
    if head_info is not None:
        text_lines.append("<font size='1'>{}</font>".format(head_info))
    else:
        text_lines.append("<font size='1'>850hPa Wind[m/s], Specific Humidity[g/Kg] and 500hPa Height[gpm]</font>")
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


def draw_pwat(pwat, lon, lat, gh=None, map_region=None, 
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
    plots.extend([pwat_field, pwat_contour])

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
        legend_label_frequency= 2,
        legend_title = "on",
        legend_title_text= "Precipitable Water",
        legend_title_font_size= 0.6,
        legend_text_font_size = 0.5)
    plots.append(legend)

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
    plots.append(title)

    # Add china province
    china_coastlines = map_set.get_mcoast(name='PROVINCE')
    plots.append(china_coastlines)

    # final plot
    return magics.plot(*plots)
