# _*_ coding: utf-8 _*_

# Copyright (c) 2020 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Some common magics plot elements.
"""

import datetime
import numpy as np
from Magics import macro as magics


def _get_title(head=None, name='', time=None, fhour=None,
               fhour_range=None, tzone='UTC', fontsize=1):
    """
    Construct the title string for magics.

    Args:
        head (str, optional): head information string. Defaults to None.
        name (str, optional): product or model name. Defaults to ''. 
        time (datetime, optional): datetime object, analysis or initial time, like 
            time = dt.datetime.strptime('2016071912','%Y%m%d%H'). Defaults to None.
        fhour (int, optional): forecast hour. Defaults to None.
        tzone (str, optional): time zone. Defaults to None.
    """

    text_lines = []

    # add the main title
    if head is not None:
        text_lines.append(
            """
            <font size='{fontsize}'><b>{name} </b></font>
            <font size='{fontsize}'>{head}</font>
            """.format(name=name, head=head, fontsize=str(fontsize)))
    
    # the model time stamp
    if time is not None:
        # convert numpy.datetime64 to datetime
        if isinstance(time, np.datetime64):
            time = time.astype('M8[ms]').astype('O')
            
        if fhour is not None:
            validtime = time + datetime.timedelta(hours = fhour)
            text_lines.append(
                """
                <font size='{fontsize}' colour='black'>Init: {time}({tzone}) -- </font>
                <font size='{fontsize}' colour='red'><b>[{fhour}]</b></font>
                <font size='{fontsize}' colour='black'> --> Valid: </font>
                <font size='{fontsize}' colour='blue'><b>{validtime}({tzone})</b></font>
                """.format(
                    time=time.strftime("%Y/%m/%d %H:%M"), tzone=tzone,
                    fhour=str(int(fhour)).zfill(3), fontsize=str(fontsize*0.8),
                    validtime=validtime.strftime("%Y/%m/%d %H:%M")))
        else:
            if fhour_range is not None:
                validtime1 = time + datetime.timedelta(hours = fhour_range[0])
                validtime2 = time + datetime.timedelta(hours = fhour_range[1])
                text_lines.append(
                    """
                    <font size='{fontsize}' colour='black'>Init: {time}({tzone}) -- </font>
                    <font size='{fontsize}' colour='red'><b>[{fhour}]</b></font>
                    <font size='{fontsize}' colour='black'> --> Valid: </font>
                    <font size='{fontsize}' colour='blue'><b>{validtime1}({tzone})</b></font>
                    <font size='{fontsize}' colour='black'> to </font>
                    <font size='{fontsize}' colour='blue'><b>{validtime2}({tzone})</b></font>
                    """.format(
                        time=time.strftime("%Y/%m/%d %H:%M"), tzone=tzone,
                        fhour=str(int(fhour_range[0])).zfill(3)+'-'+str(int(fhour_range[1])).zfill(3),
                        fontsize=str(fontsize*0.8),
                        validtime1=validtime1.strftime("%Y/%m/%d %H:%M"),
                        validtime2=validtime2.strftime("%Y/%m/%d %H:%M")))
            else:
                text_lines.append("<font size='{fontsize}' colour='red'>{time}({tzone})</font>".format(
                    time=time.strftime("%Y/%m/%d %H:%M"), tzone=tzone, fontsize=str(fontsize*0.8)))
    else:
        text_lines.append(" ")
    
    title = magics.mtext(
        text_lines = text_lines,
        text_justification = 'left')

    return title


def _get_legend(china_map, title='', frequency=1):
    """
    construct plot legend.
    """
    return magics.mlegend(
        legend= 'on',
        legend_text_colour= 'black',
        legend_box_mode= 'positional',
        legend_box_x_position= china_map.args['subpage_x_length']+1.6,
        legend_box_y_position= 1,
        legend_box_x_length= 2,
        legend_box_y_length= china_map.args['subpage_y_length']*1.0,
        legend_border= 'off',
        legend_border_colour= 'black',
        legend_box_blanking= 'on',
        legend_display_type= 'continuous',
        legend_title= "on",
        legend_title_position_ratio=0.6,
        legend_title_text= title,
        legend_title_font_size= 0.7,
        legend_text_font_size = 0.6,
        legend_label_frequency=frequency)


def _get_mslp_contour(interval=4, color='#399c9c'):
    """
    mean sea level contour plot.
    """
    return magics.mcont(
        legend= 'off', 
        contour_level_selection_type= 'interval',
        contour_interval= interval,
        contour_reference_level= 1000.,
        contour_line_colour= color,
        contour_line_thickness= 3,
        contour_label= 'on',
        contour_label_height= 0.5,
        contour_highlight_colour= color,
        contour_highlight_thickness= 4,
        contour_hilo= "on",
        contour_hilo_height= 0.6,
        contour_hi_colour= 'blue',
        contour_lo_colour= 'red',
        contour_hilo_window_size= 5)


def _get_gh_contour(interval=20, reference=5880, color='black'):
    """
    geopotential height contours.
    """
    return magics.mcont(
        legend= 'off', 
        contour_level_selection_type= 'interval',
        contour_interval= interval,
        contour_reference_level= reference,
        contour_line_colour= color,
        contour_line_thickness= 2,
        contour_label= 'on',
        contour_label_height= 0.5,
        contour_highlight_colour= 'black',
        contour_highlight_thickness= 4)


def _get_wind_flags(thick=1, min_speed=0.0, color='charcoal'):
    """
    wind flags.
    """
    return magics.mwind(
        legend= 'off',
        wind_field_type= 'flags',
        wind_flag_length = 0.6,
        wind_flag_style= 'solid', 
        wind_flag_thickness= 1,
        wind_flag_origin_marker = 'dot',
        wind_flag_min_speed = 0.0,
        wind_flag_colour = 'charcoal')

