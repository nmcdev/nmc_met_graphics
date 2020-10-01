# _*_ coding: utf-8 _*_

# Copyright (c) 2020 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Provide the map background.
"""

import pkg_resources
import numpy as np
from nmc_met_graphics.util import check_kwargs
from Magics import macro as magics


def get_page_setup(kwargs, map_region=None):
    """
    设置Magics的默认页面大小和绘图范围大小.
    """

    if map_region is not None:
        super_page_x_length = 29.7
        page_ratio = (map_region[3]-map_region[2])*1.0/(map_region[1]-map_region[0])
        # make sure the page will show all figure contents
        kwargs = check_kwargs(kwargs, 'super_page_x_length', super_page_x_length)
        kwargs = check_kwargs(kwargs, 'super_page_y_length', super_page_x_length * page_ratio)
        # Set subpage_x_length and subpage_y_length, the small one is working
        subpage_x_length = 25.0
        kwargs = check_kwargs(kwargs, 'subpage_x_length', subpage_x_length)
        kwargs = check_kwargs(kwargs, 'subpage_y_length', subpage_x_length * page_ratio)
        # make sure the axis lable will show
        kwargs = check_kwargs(kwargs, 'subpage_x_position', 1.2)
        kwargs = check_kwargs(kwargs, 'subpage_y_position', 1)
    else:
        kwargs = check_kwargs(kwargs, 'super_page_x_length', 29.7)
        kwargs = check_kwargs(kwargs, 'subpage_x_length', 25.0)
        kwargs = check_kwargs(kwargs, 'subpage_y_length', 25.0)
        kwargs = check_kwargs(kwargs, 'subpage_x_position', 1)
        kwargs = check_kwargs(kwargs, 'subpage_y_position', 1)

    return kwargs


def get_logo():
    """
    Get the logo image.
    """
    imagefile = pkg_resources.resource_filename(
        'nmc_met_graphics', 'resources/logo/nmc_large.png')
    logo = magics.mimport(
        import_file_name=imagefile, import_x_position=1.2, import_y_position=1)
    return logo


def get_mmap(name='CHINA_LAND_CYLINDRICAL', **kwargs):
    """Get magics map background.

    refer to https://confluence.ecmwf.int/display/MAGP/Subpage+-+Projection
             https://confluence.ecmwf.int/display/MAGP/Subpage+examples
    
    Args:
        name (str, optional): map region name. Defaults to 'CHINA_LAND_CYLINDRICAL'.
            if 'CHINA_REGION_CYLINDRICAL', set map_region=[lonmin, lonmax, latmin, latmax]

    Return:
        map background project object.
    """

    # genderal kwargs
    kwargs = check_kwargs(kwargs, 'subpage_clipping', 'on')
    kwargs = check_kwargs(kwargs, 'page_id_line', 'off')

    if name.upper() == 'CHINA_CYLINDRICAL':                                                  # 中国陆地和海洋范围
        map_region = [70.0, 140.0, 8.0, 60.0]
        kwargs = get_page_setup(kwargs, map_region=map_region)
        kwargs['subpage_lower_left_longitude'] = map_region[0]
        kwargs['subpage_upper_right_longitude'] = map_region[1]
        kwargs['subpage_lower_left_latitude'] = map_region[2]
        kwargs['subpage_upper_right_latitude'] = map_region[3]
        project = magics.mmap(
            subpage_map_projection="cylindrical",
            **kwargs)
    elif name.upper() == 'CHINA_LAND_CYLINDRICAL':
        map_region = [73.0, 136.0, 16.0, 55.0]
        kwargs = get_page_setup(kwargs, map_region=map_region)
        kwargs['subpage_lower_left_longitude'] = map_region[0]
        kwargs['subpage_upper_right_longitude'] = map_region[1]
        kwargs['subpage_lower_left_latitude'] = map_region[2]
        kwargs['subpage_upper_right_latitude'] = map_region[3]
        project = magics.mmap(
            subpage_map_projection="cylindrical",
            **kwargs)
    elif name.upper() == 'CHINA_REGION_CYLINDRICAL':
        if 'map_region' in kwargs.keys():
            map_region = kwargs['map_region']
            del kwargs['map_region']
        else:
            map_region = [70, 140, 8, 60]
        kwargs = get_page_setup(kwargs, map_region=map_region)
        kwargs['subpage_lower_left_longitude'] = map_region[0]
        kwargs['subpage_upper_right_longitude'] = map_region[1]
        kwargs['subpage_lower_left_latitude'] = map_region[2]
        kwargs['subpage_upper_right_latitude'] = map_region[3]
        project = magics.mmap(
            subpage_map_projection="cylindrical",
            **kwargs)
    elif name.upper() == "CHINA_POLAR_STEREOGRAPHIC":
        kwargs = get_page_setup(kwargs)
        kwargs = check_kwargs(kwargs, 'subpage_map_area_definition_polar', 'center')
        kwargs = check_kwargs(kwargs, 'subpage_map_vertical_longitude', 105)
        kwargs = check_kwargs(kwargs, 'subpage_map_centre_latitude', 35)
        kwargs = check_kwargs(kwargs, 'subpage_map_centre_longitude', 105)
        kwargs = check_kwargs(kwargs, 'subpage_map_scale', 32.e6)
        project = magics.mmap(
            subpage_map_projection = "polar_stereographic",
            **kwargs)
    elif name.upper() == "WORLD_mollweide":
        project = magics.mmap(
            subpage_map_projection = "mollweide",
            subpage_map_area_definition = "full",
            subpage_frame = "off",
            page_frame = "off",
            **kwargs)
    else:
        project = None

    return project


def get_mcoast(name='PROVINCE', **kwargs):
    """
    Project coastlines and latitude/longitude grid lines onto

    Args:
        name (str, optional): [description]. Defaults to 'PROVINCE'.

    Return:
        map coastlines object.
    """

    if name.upper() == 'COAST':
        kwargs = check_kwargs(kwargs, 'map_coastline_colour', "grey")
        kwargs = check_kwargs(kwargs, 'map_label', "on")
        kwargs = check_kwargs(kwargs, 'map_label_height', 0.6)
        kwargs = check_kwargs(kwargs, 'map_label_right', 'off')
        kwargs = check_kwargs(kwargs, 'map_label_top', 'off')
        kwargs = check_kwargs(kwargs, 'map_grid', "on")
        kwargs = check_kwargs(kwargs, 'map_grid_thickness', 0.2)
        kwargs = check_kwargs(kwargs, 'map_grid_line_style', "dot")
        kwargs = check_kwargs(kwargs, 'map_grid_latitude_increment', 10)
        kwargs = check_kwargs(kwargs, 'map_grid_longitude_increment', 10)
        coast = magics.mcoast(**kwargs)
    elif name.upper() == 'COAST_FILL':
        kwargs = check_kwargs(kwargs, 'map_coastline_colour', "grey")
        kwargs = check_kwargs(kwargs, 'map_coastline_land_shade', "on")
        kwargs = check_kwargs(kwargs, 'map_coastline_sea_shade', "on")
        kwargs = check_kwargs(kwargs, 'map_coastline_land_shade_colour', "cream")
        kwargs = check_kwargs(kwargs, 'map_coastline_sea_shade_colour', "white")
        kwargs = check_kwargs(kwargs, 'map_label', "on")
        kwargs = check_kwargs(kwargs, 'map_label_height', 0.6)
        kwargs = check_kwargs(kwargs, 'map_label_right', 'off')
        kwargs = check_kwargs(kwargs, 'map_label_top', 'off')
        kwargs = check_kwargs(kwargs, 'map_grid', "on")
        kwargs = check_kwargs(kwargs, 'map_grid_thickness', 0.2)
        kwargs = check_kwargs(kwargs, 'map_grid_line_style', "dot")
        kwargs = check_kwargs(kwargs, 'map_grid_latitude_increment', 10)
        kwargs = check_kwargs(kwargs, 'map_grid_longitude_increment', 10)
        coast = magics.mcoast(**kwargs)
    elif name.upper() == 'PROVINCE':
        shpfile = pkg_resources.resource_filename('nmc_met_graphics', 'resources/maps/bou2_4l')
        kwargs = check_kwargs(kwargs, 'map_user_layer_colour', "navy")
        kwargs = check_kwargs(kwargs, 'map_user_layer_thickness', 1)
        kwargs = check_kwargs(kwargs, 'map_label', "off")
        kwargs = check_kwargs(kwargs, 'map_grid', "off")
        coast = magics.mcoast(
            map_user_layer="on",
            map_user_layer_name = shpfile,
            **kwargs)
    elif name.upper() == 'RIVER':
        shpfile = pkg_resources.resource_filename('nmc_met_graphics', 'resources/maps/hyd1_4l')
        kwargs = check_kwargs(kwargs, 'map_user_layer_colour', "blue")
        kwargs = check_kwargs(kwargs, 'map_user_layer_thickness', 1)
        kwargs = check_kwargs(kwargs, 'map_label', "off")
        kwargs = check_kwargs(kwargs, 'map_grid', "off")
        coast = magics.mcoast(
            map_user_layer="on",
            map_user_layer_name = shpfile,
            **kwargs)
    else:
        coast = None

    return coast
