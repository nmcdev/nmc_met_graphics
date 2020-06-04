# _*_ coding: utf-8 _*_

# Copyright (c) 2020 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Plot atmospheric dynamics maps.
"""

import math
import numpy as np
import xarray as xr
import scipy.ndimage as ndimage
import metpy.calc as calc
from metpy.units import units
import Magics.macro as magics
from nmc_met_graphics.magics import util, map_set


# global variables
out_png_width = 1200


def draw_wind_upper(uwind, vwind, lon, lat, gh=None, skip_vector=None, 
                    map_region=None, head_info=None, date_obj=None, outfile=None):
    """
    Draw 200hPa wind speed and vector field.

    Args:
        uwind (np.array): u wind component, 2D array, [nlat, nlon]
        vwind (np.array): v wind component, 2D array, [nlat, nlon]
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
    wspeed = np.sqrt(uwind*uwind + vwind*vwind)
    wspeed_field = util.minput_2d(wspeed, lon, lat, {'long_name': 'Wind Speed', 'units': 'm/s'})
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
    if wspeed.max() > 30.:
        wspeed_contour = magics.mcont(
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
        plots.extend([wspeed_field, wspeed_contour])

    # Define the wind vector
    wind_vector = magics.mwind(
        legend= 'on',
        wind_field_type= 'arrows',
        wind_arrow_head_shape=1,
        wind_arrow_thickness= 0.5,
        wind_arrow_unit_velocity=50,
        wind_arrow_colour= 'evergreen')
    plots.extend([wind_field, wind_vector])

    # Define the simple contouring for gh
    if gh is not None:
        gh_contour = magics.mcont(
            legend= 'off', 
            contour_level_selection_type= 'interval',
            contour_interval= 50.,
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
        legend_title_text= "Wind Speed",
        legend_title_font_size= 0.6,
        legend_text_font_size = 0.5)
    plots.append(legend)

    # Add the title
    text_lines = []
    if head_info is not None:
        text_lines.append("<font size='1'>{}</font>".format(head_info))
    else:
        text_lines.append("<font size='1'>200hPa Wind[m/s] and Height[gpm]</font>")
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


def draw_height_temp(gh, temp, lon, lat, map_region=None, 
                     head_info=None, date_obj=None, outfile=None):
    """
    Draw geopotential height and temperature.

    Args:
        gh (np.array): geopotential height, 2D array, [nlat, nlon]
        temp (np.array): temperature, 2D array, [nlat, nlon]
        lon (np.array): longitude, 1D array, [nlon]
        lat (np.array): latitude, 1D array, [nlat]
        skip_vector (integer): skip grid number for vector plot
        map_region (list or tuple): the map region limit, [lonmin, lonmax, latmin, latmax]
        head_info (string, optional): head information string. Defaults to None.
        date_obj (datetime, optional): datetime object, like 
            date_obj = dt.datetime.strptime('2016071912','%Y%m%d%H'). Defaults to None.
    """

    # put data into fields
    gh_field = util.minput_2d(gh, lon, lat, {'long_name': 'Geopotential Height', 'units': 'gpm'})
    temp_field = util.minput_2d(temp, lon, lat, {'long_name': 'Temperature', 'units': 'm/s'})

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

    # Define the simple contouring for temperature
    if temp.min() < -2.0:
        temp_contour1 = magics.mcont(
            legend= 'off', 
            contour_level_selection_type= 'interval',
            contour_interval= 2.0,
            contour_reference_level= 0.,
            contour_line_colour= 'red',
            contour_line_thickness= 2,
            contour_line_style = "dash",
            contour_label= 'on',
            contour_label_height= 0.5,
            contour_max_level= -2.0,
            contour_highlight = 'off')
        plots.extend([temp_field, temp_contour1])

    if temp.min() < 0.0 and temp.max() > 0.0:
        temp_contour2 = magics.mcont(
            legend= 'off', 
            contour_level_selection_type= 'level_list',
            contour_level_list = [0.00],
            contour_line_colour= 'red',
            contour_line_thickness= 4,
            contour_label= 'on',
            contour_label_height= 0.5,
            contour_highlight = 'off')
        plots.extend([temp_field, temp_contour2])

    if temp.max() > 2.0:
        temp_contour3 = magics.mcont(
            legend= 'off', 
            contour_level_selection_type= 'interval',
            contour_interval= 2.0,
            contour_reference_level= 0.,
            contour_line_colour= 'red',
            contour_line_thickness= 2,
            contour_label= 'on',
            contour_label_height= 0.5,
            contour_min_level=2.0,
            contour_highlight = 'off')
        plots.extend([temp_field, temp_contour3])

    # Define the simple contouring for gh
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

    # Add the title
    text_lines = []
    if head_info is not None:
        text_lines.append("<font size='1'>{}</font>".format(head_info))
    else:
        text_lines.append("<font size='1'>500hPa Height[gpm] and Temperature[DegC]</font>")
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


def draw_wind_high(uwind, vwind, lon, lat, gh=None, skip_vector=None, 
                   map_region=None, head_info=None, date_obj=None, outfile=None):
    """
    Draw high wind speed and flags.

    Args:
        uwind (np.array): u wind component, 2D array, [nlat, nlon]
        vwind (np.array): v wind component, 2D array, [nlat, nlon]
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
    wspeed_field = util.minput_2d(np.sqrt(uwind*uwind + vwind*vwind), lon, lat, {'long_name': 'Wind Speed', 'units': 'm/s'})
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
    wspeed_contour = magics.mcont(
        legend= 'on',
        contour_level_selection_type= 'interval', 
        contour_shade_max_level= 44.,
        contour_shade_min_level= 8., 
        contour_interval= 4.,
        contour_shade= 'on', 
        contour= "off",
        contour_shade_method= 'area_fill', 
        contour_shade_colour_method = 'palette',
        contour_shade_palette_name = 'eccharts_rainbow_blue_purple_9',
        contour_reference_level= 8., 
        contour_highlight= 'off', 
        contour_hilo= 'hi', 
        contour_hilo_format= '(F3.0)', 
        contour_hilo_height= 0.6, 
        contour_hilo_type= 'number', 
        contour_hilo_window_size=10,
        contour_label= 'off')
    plots.extend([wspeed_field, wspeed_contour])

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
        legend_title_text= "Wind Speed",
        legend_title_font_size= 0.6,
        legend_text_font_size = 0.5)
    plots.append(legend)

    # Add the title
    text_lines = []
    if head_info is not None:
        text_lines.append("<font size='1'>{}</font>".format(head_info))
    else:
        text_lines.append("<font size='1'>850hPa Wind[m/s] and 500hPa Height[gpm]</font>")
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


def draw_vort_high(uwind, vwind, lon, lat, vort=None, gh=None, skip_vector=None, smooth_factor=1.0,
                   map_region=None, head_info=None, date_obj=None, outfile=None):
    """
    Draw high vorticity.

    Args:
        uwind (np.array): u wind component, 2D array, [nlat, nlon]
        vwind (np.array): v wind component, 2D array, [nlat, nlon]
        lon (np.array): longitude, 1D array, [nlon]
        lat (np.array): latitude, 1D array, [nlat]
        vort (np.array, optional): vorticity component, 2D array, [nlat, nlon]
        gh (np.array): geopotential height, 2D array, [nlat, nlon]
        skip_vector (integer): skip grid number for vector plot
        smooth_factor (float): smooth factor for vorticity, larger for smoother.
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
    if vort is None:
        dx, dy = calc.lat_lon_grid_deltas(lon, lat)
        vort = calc.vorticity(uwind * units.meter/units.second, vwind * units.meter/units.second, dx, dy)
        vort = ndimage.gaussian_filter(vort,sigma=smooth_factor, order=0)* 10**5
    vort_field = util.minput_2d(vort, lon, lat, {'long_name': 'vorticity', 'units': 's-1'})
    if gh is not None:
        gh_feild = util.minput_2d(gh, lon, lat, {'long_name': 'height', 'units': 'gpm'})

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


    # Define the shading contour
    vort_contour = magics.mcont(
        legend= 'on',
        contour_level_selection_type= 'level_list', 
        contour_level_list= [-200.0, -100.0, -75.0, -50.0, -30.0, -20.0, -15.0, -13.0, -11.0, -9.0, -7.0, 
                             -5.0, -3.0, -1.0, 1.0, 3.0, 5.0, 7.0, 9.0, 11.0, 13.0, 15.0, 20.0, 30.0, 50.0,
                             75.0, 100.0, 200.0],
        contour_shade= 'on', 
        contour= "off",
        contour_shade_method= 'area_fill', 
        contour_shade_colour_method = 'list',
        contour_shade_colour_list = [
            "rgb(0,0,0.3)","rgb(0,0,0.5)","rgb(0,0,0.7)","rgb(0,0,0.9)","rgb(0,0.15,1)","rgb(0,0.3,1)",
            "rgb(0,0.45,1)","rgb(0,0.6,1)","rgb(0,0.75,1)","rgb(0,0.85,1)","rgb(0.2,0.95,1)","rgb(0.45,1,1)",
            "rgb(0.75,1,1)","none","rgb(1,1,0)","rgb(1,0.9,0)","rgb(1,0.8,0)","rgb(1,0.7,0)","rgb(1,0.6,0)",
            "rgb(1,0.5,0)","rgb(1,0.4,0)","rgb(1,0.3,0)","rgb(1,0.15,0)","rgb(0.9,0,0)","rgb(0.7,0,0)",
            "rgb(0.5,0,0)","rgb(0.3,0,0)"],
        contour_reference_level= 8., 
        contour_highlight= 'off', 
        contour_hilo= 'off', 
        contour_label= 'off')
    plots.extend([vort_field, vort_contour])

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
        plots.extend([gh_feild, gh_contour])

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
        legend_title_text= "Vorticity",
        legend_title_font_size= 0.6,
        legend_text_font_size = 0.5)
    plots.append(legend)

    # Add the title
    text_lines = []
    if head_info is not None:
        text_lines.append("<font size='1'>{}</font>".format(head_info))
    else:
        text_lines.append("<font size='1'>500hPa Wind, Vorticity and Height[gpm]</font>")
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


def draw_vvel_high(uwind, vwind, wwind, lon, lat, vort=None, gh=None, skip_vector=None,
                   smooth_factor=1.0, map_region=None, head_info=None, date_obj=None, outfile=None):
    """
    Draw high vertical velocity.

    Args:
        uwind (np.array): u wind component, 2D array, [nlat, nlon]
        vwind (np.array): v wind component, 2D array, [nlat, nlon]
        wwind (np.array): w wind component, 2D array, [nlat, nlon]
        lon (np.array): longitude, 1D array, [nlon]
        lat (np.array): latitude, 1D array, [nlat]
        vort (np.array, optional): vorticity component, 2D array, [nlat, nlon]
        gh (np.array): geopotential height, 2D array, [nlat, nlon]
        skip_vector (integer): skip grid number for vector plot
        smooth_factor (float): smooth factor for vorticity, larger for smoother.
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
    vvel_field = util.minput_2d(wwind, lon, lat, {'long_name': 'vertical velocity', 'units': 'Pa/s'})
    if gh is not None:
        gh_feild = util.minput_2d(gh, lon, lat, {'long_name': 'height', 'units': 'gpm'})

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

    # Define the shading contour
    vvel_contour = magics.mcont(
        legend= 'on',
        contour_level_selection_type= 'level_list', 
        contour_level_list= [-60,-30,-10,-5,-2.5,-1,-0.5,-0.2,0.2,0.5,1,2.5,5,10,30],
        contour_shade= 'on', 
        contour= "off",
        contour_shade_method= 'area_fill', 
        contour_shade_colour_method = 'list',
        contour_shade_colour_list = [
            '#9D0001','#C90101','#F10202','#FF3333','#FF8585','#FFBABA','#FEDDDD','#FFFFFF', 
            '#E1E1FF','#BABAFF','#8484FF','#2C2CF7','#0404F1','#0101C8','#020299'],
        contour_reference_level= 0, 
        contour_highlight= 'off', 
        contour_hilo= 'off', 
        contour_label= 'off')
    plots.extend([vvel_field, vvel_contour])

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
        plots.extend([gh_feild, gh_contour])

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
        legend_title_text= "Vertical Velocity",
        legend_title_font_size= 0.6, 
        legend_text_font_size= 0.5)
    plots.append(legend)

    # Add the title
    text_lines = []
    if head_info is not None:
        text_lines.append("<font size='1'>{}</font>".format(head_info))
    else:
        text_lines.append("<font size='1'>700hPa Wind, Vertical Velocity and Height[gpm]</font>")
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


def draw_mslp(mslp, lon, lat, gh=None, map_region=None, 
              head_info=None, date_obj=None, outfile=None):
    """
    Draw mean sea level pressure field.

    Args:
        mslp (np.array): sea level pressure field (mb), 2D array, [nlat, nlon]
        lon (np.array): longitude, 1D array, [nlon]
        lat (np.array): latitude, 1D array, [nlat]
        gh (np.array): geopotential height, 2D array, [nlat, nlon]
        map_region (list or tuple): the map region limit, [lonmin, lonmax, latmin, latmax]
        head_info (string, optional): head information string. Defaults to None.
        date_obj (datetime, optional): datetime object, like 
            date_obj = dt.datetime.strptime('2016071912','%Y%m%d%H'). Defaults to None.
    """

    # put data into fields
    mslp_field = util.minput_2d(mslp, lon, lat, {'long_name': 'Sea level pressure', 'units': 'mb'})
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
    mslp_contour = magics.mcont(
        legend= 'on',
        contour_shade= "on",
        contour_hilo= "on",
        contour_hilo_height= 0.6,
        contour_hi_colour= 'blue',
        contour_lo_colour= 'red',
        contour_hilo_window_size= 5,
        contour= "off",
        contour_label= "off",
        contour_shade_method= "area_fill",
        contour_level_selection_type= "level_list",
        contour_level_list=  [940.+i*2.5 for i in range(51)],
        contour_shade_colour_method= "list",
        contour_shade_colour_list= [
            '#FD90EB', '#EB78E5', '#EF53E0', '#F11FD3', '#F11FD3', '#A20E9B', '#880576', '#6D0258', '#5F0853', 
            '#2A0DA8', '#2F1AA7', '#3D27B4', '#3F3CB6', '#6D5CDE', '#A28CF9', '#C1B3FF', '#DDDCFE', '#1861DB',
            '#206CE5', '#2484F4', '#52A5EE', '#91D4FF', '#B2EFF8', '#DEFEFF', '#C9FDBD', '#91F78B', '#53ED54',
            '#1DB31E', '#0CA104', '#FFF9A4', '#FFE27F', '#FAC235', '#FF9D04', '#FF5E00', '#F83302', '#E01304',
            '#A20200', '#603329', '#8C6653', '#B18981', '#DDC0B3', '#F8A3A2', '#DD6663', '#CA3C3B', '#A1241D', 
            '#6C6F6D', '#8A8A8A', '#AAAAAA', '#C5C5C5', '#D5D5D5', '#E7E3E4'])
    plots.extend([mslp_field, mslp_contour])

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
        legend_title_text= "Pressure",
        legend_label_frequency= 2,
        legend_title_font_size= 0.6,
        legend_text_font_size = 0.5)
    plots.append(legend)

    # Add the title
    text_lines = []
    if head_info is not None:
        text_lines.append("<font size='1'>{}</font>".format(head_info))
    else:
        text_lines.append("<font size='1'>Mean sea level pressure[mb] and 500hPa Height[gpm]</font>")
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
