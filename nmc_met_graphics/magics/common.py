# _*_ coding: utf-8 _*_

# Copyright (c) 2020 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Some common plot elements.
"""

import datetime
import numpy as np
from Magics import macro as magics


def get_title(head=None, name='', time=None, fhour=None, tzone='UTC'):
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
            <font size='1'><b>{} </b></font>
            <font size='1'>{}</font>
            """.format(name, head))
    
    # the model time stamp
    if time is not None:
        # convert numpy.datetime64 to datetime
        if isinstance(time, np.datetime64):
            time = time.astype('M8[ms]').astype('O')
            
        if fhour is not None:
            validtime = time + datetime.timedelta(hours = fhour)
            text_lines.append(
                """
                <font size='0.8' colour='black'>Init: {}({}) -- </font>
                <font size='0.8' colour='red'><b>[{}]</b></font>
                <font size='0.8' colour='black'> --> Valid: </font>
                <font size='0.8' colour='blue'><b>{}({})</b></font>
                """.format(
                    time.strftime("%Y/%m/%d %H:%M"), tzone, str(int(fhour)).zfill(3),
                    validtime.strftime("%Y/%m/%d %H:%M"), tzone))
        else:
            text_lines.append("<font size='0.8' colour='red'>{}({})</font>".format(
                time.strftime("%Y/%m/%d %H:%M"), tzone))
    else:
        text_lines.append(" ")
    
    title = magics.mtext(
        text_lines = text_lines,
        text_justification = 'left')

    return title
