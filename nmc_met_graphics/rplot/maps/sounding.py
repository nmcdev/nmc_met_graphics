# _*_ coding: utf-8 _*_

# Copyright (c) 2021 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Perform sounding analysis.
"""

from nmc_met_io.retrieve_micaps_server import get_tlogp
from nmc_met_graphics.rplot.sounding import draw_sounding, draw_hodograph, draw_wind_profile


def sounding(time_str="", ID="54511", plot_type='all'):
    """

    Args:
        time_str (str, optional): [description]. Defaults to "".
        ID (str, optional): [description]. Defaults to "54511".
        plot_type (str, optional): ploting type, all / hodograph, Defaults to "all".
    """

    # load data
    if time_str == "":
        data = get_tlogp("UPPER_AIR/TLOGP/", remove_duplicate=True, remove_na=True)
    else:
        data = get_tlogp(
            "UPPER_AIR/TLOGP/", filename=time_str + "0000.000", 
            remove_duplicate=True, remove_na=True)
    if data is None:
        return None

    # get the station ID records and plot sounding analysis.
    data = data[data.ID == ID]
    title = ID + " [" + data.time.iloc[0].strftime("%Y-%m-%d, %H:%M") + "]"
    if plot_type.lower() == 'hodograph':
        image = draw_hodograph(
            data['ws'], data['wd'], data['h'], title=title)
    elif plot_type.lower() == 'wind_profile':
        image = draw_wind_profile(
            data['ws'], data['wd'], data['p'], data['h'], title=title)
    else:
        image = draw_sounding(
            data['p'], data['h'], data['t'], data['td'], data['wd'], data['ws'],
            title = title)
    return image
