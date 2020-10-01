# _*_ coding: utf-8 _*_

# Copyright (c) 2020 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Moisture analysis maps.
"""

import numpy as np
import xarray as xr
from nmc_met_graphics.magics import util, map_set, common
from nmc_met_graphics.util import check_region_to_contour, check_kwargs
from Magics import macro as magics


def draw_rh_high(uwind, vwind, rh, lon, lat, gh=None, skip_vector=None, 
                 map_region=None, title_kwargs={}, outfile=None):
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
        title_kwargs (dictionaly, optional): keyword arguments for _get_title function.
    """

    # check default parameters
    if skip_vector is None:
        skip_vector = util.get_skip_vector(lon, lat, map_region)

    # put data into fields
    wind_field = util.minput_2d_vector(uwind, vwind, lon, lat, skip=skip_vector)
    rh_field = util.minput_2d(rh, lon, lat, {'long_name': 'Relative Humidity', 'units': '%'})
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

    # Define the shading for the specific humidity
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
    wind_vector = common._get_wind_flags()
    plots.extend([wind_field, wind_vector])

    # Define the simple contouring for gh
    if gh is not None:
        gh_contour = common._get_gh_contour()
        plots.extend([gh_field, gh_contour])

    # Add a legend
    legend = common._get_legend(china_map, title="Relative Humidity[%]")
    plots.append(legend)

    # Add the title
    title_kwargs = check_kwargs(title_kwargs, 'head', "Relative Humidity | Wind | 500hPa GH")
    title = common._get_title(**title_kwargs)
    plots.append(title)

    # Add china province
    china_coastlines = map_set.get_mcoast(name='PROVINCE')
    plots.append(china_coastlines)

    # final plot
    return util.magics_plot(plots, outfile)


def draw_sp_high(uwind, vwind, sp, lon, lat, gh=None, skip_vector=None, 
                 map_region=None, title_kwargs={}, outfile=None):
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
        title_kwargs (dictionaly, optional): keyword arguments for _get_title function.
    """

    # check default parameters
    if skip_vector is None:
        skip_vector = util.get_skip_vector(lon, lat, map_region)

    # put data into fields
    wind_field = util.minput_2d_vector(uwind, vwind, lon, lat, skip=skip_vector)
    sp_field = util.minput_2d(sp, lon, lat, {'long_name': 'Specific humidity', 'units': 'g kg^-1'})
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
    wind_vector = common._get_wind_flags()
    plots.extend([wind_field, wind_vector])

    # Define the simple contouring for gh
    if gh_field is not None:
        gh_contour = common._get_gh_contour()
        plots.extend([gh_field, gh_contour])

    # Add a legend
    legend = common._get_legend(china_map, title="Specific Humidity [g/kg]")
    plots.append(legend)

    # Add the title
    title_kwargs = check_kwargs(title_kwargs, 'head', "Specific Humidity | 500hPa GH")
    title = common._get_title(**title_kwargs)
    plots.append(title)

    # Add china province
    china_coastlines = map_set.get_mcoast(name='PROVINCE')
    plots.append(china_coastlines)

    # final plot
    return util.magics_plot(plots, outfile)


def draw_pwat(pwat, lon, lat, gh=None, map_region=None, 
              title_kwargs={}, outfile=None):
    """
    Draw precipitable water.

    Args:
        pwat (np.array): pressure, 2D array, [nlat, nlon]
        lon (np.array): longitude, 1D array, [nlon]
        lat (np.array): latitude, 1D array, [nlat]
        gh (np.array, optional), geopotential height, 2D array, [nlat, nlon]
        map_region (list or tuple): the map region limit, [lonmin, lonmax, latmin, latmax]
        title_kwargs (dictionaly, optional): keyword arguments for _get_title function.
    """

    # put data into fields
    pwat_field = util.minput_2d(pwat, lon, lat, {'long_name': 'precipitable water', 'units': 'mm'})
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

    # Define the shading for precipitation water.
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
    if gh_field is not None:
        gh_contour = common._get_gh_contour()
        plots.extend([gh_field, gh_contour])

    # Add a legend
    legend = common._get_legend(china_map, title="Precipitable water [mm]", frequency=2)
    plots.append(legend)

    # Add the title
    title_kwargs = check_kwargs(title_kwargs, 'head', "Precipitable water | 500hPa GH")
    title = common._get_title(**title_kwargs)
    plots.append(title)

    # Add china province
    china_coastlines = map_set.get_mcoast(name='PROVINCE')
    plots.append(china_coastlines)

    # final plot
    return util.magics_plot(plots, outfile)


def draw_ivt(iqu, iqv, lon, lat, mslp=None, skip_vector=None, 
             map_region=None, title_kwargs={}, outfile=None):
    """
    Draw integrated Water Vapor Transport (IVT) .

    Args:
        iqu (np.array): u * q transport, 2D array, [nlat, nlon]
        iqv (np.array): v * q transport, 2D array, [nlat, nlon]
        lon (np.array): longitude, 1D array, [nlon]
        lat (np.array): latitude, 1D array, [nlat]
        mslp (np.array): mean sea level pressure, 2D array, [nlat, nlon]
        skip_vector (integer): skip grid number for vector plot
        map_region (list or tuple): the map region limit, [lonmin, lonmax, latmin, latmax]
        title_kwargs (dictionaly, optional): keyword arguments for _get_title function.
    """

    # check default parameters
    if skip_vector is None:
        skip_vector = util.get_skip_vector(lon, lat, map_region)

    # put data into fields
    ivt_field = util.minput_2d_vector(iqu, iqv, lon, lat, skip=skip_vector)
    ivt_mag_field = util.minput_2d(
        np.sqrt(iqu*iqu + iqv*iqv), lon, lat, 
        {'long_name': 'Integrated Water Vapor Transport', 'units': 'kg/m/s'})
    mslp_field = util.minput_2d(
        mslp, lon, lat, {'long_name': 'mean sea level pressure', 'units': 'mb'})

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

    # Define the shading for the wind speed
    ivt_mag_contour = magics.mcont(
        legend= 'on',
        contour= "off",
        contour_level_selection_type= "level_list",
        contour_level_list =  [i*50.0+150 for i in range(3)] + [i*100.0 + 300 for i in range(17)],
        contour_shade= 'on', 
        contour_shade_method= 'area_fill', 
        contour_shade_colour_method = "list",
        contour_shade_colour_list = [
            '#fdd6c4', '#fcae92', '#fc8363', '#f6573e', '#de2b25', '#b81419', '#840711',
            '#fbb1ba', '#f98cae', '#f25e9f', '#dc3296', '#b40781', '#890179', '#600070',
            '#787878', '#8c8c8c', '#a0a0a0', '#b4b4b4', '#c8c8c8', '#dcdcdc'],
        contour_highlight= 'off', 
        contour_hilo= 'off', 
        contour_label= 'off')
    plots.extend([ivt_mag_field, ivt_mag_contour])

    # Define the wind vector
    if ivt_field is not None:
        ivt_vector = magics.mwind(
            legend= 'off',
            wind_field_type= 'arrows',
            wind_arrow_head_shape= 1,
            wind_arrow_head_ratio= 0.5,
            wind_arrow_thickness= 2,
            wind_arrow_unit_velocity= 1000.0,
            wind_arrow_min_speed= 150.0,
            wind_arrow_calm_below = 150,
            wind_arrow_colour= '#31043a')
        plots.extend([ivt_field, ivt_vector])

    # Define the simple contouring for gh
    if mslp_field is not None:
        interval = check_region_to_contour(map_region, 4, 2, thred=600)
        mslp_contour = common._get_mslp_contour(interval=interval)
        plots.extend([mslp_field, mslp_contour])

    # Add a legend
    legend = common._get_legend(china_map, title="Integrated Water Vapor Transport [kg/m/s]")
    plots.append(legend)

    # Add the title
    title_kwargs = check_kwargs(title_kwargs, 'head', "Integrated Water Vapor Transport | MSLP")
    title = common._get_title(**title_kwargs)
    plots.append(title)

    # Add china province
    china_province_coastlines = map_set.get_mcoast(
        name='PROVINCE', map_user_layer_thickness=2,
        map_user_layer_colour='black')
    plots.append(china_province_coastlines)
    china_river_coastlines = map_set.get_mcoast(
        name='RIVER', map_user_layer_thickness=2,
        map_user_layer_colour='#71b2fd')
    plots.append(china_river_coastlines)

    # final plot
    return util.magics_plot(plots, outfile)
