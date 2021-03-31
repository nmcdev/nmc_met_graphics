# _*_ coding: utf-8 _*_

# Copyright (c) 2021 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Perform sounding analysis with R libraries.
"""

import os
import sys
import tempfile
from PIL import Image

try:
    import rpy2.robjects as ro
    from rpy2.robjects.packages import importr
    from rpy2.robjects import pandas2ri
    from rpy2.robjects.conversion import localconverter
except ImportError:
    print("rpy2 is not installed (pip install rpy2)")
    sys.exit(1)


def draw_sounding(pressure, altitude, temp, dpt, wd, ws, title="", parcel="MU",
                  max_speed=25, hazards=False, outfile=None):
    """
    Plot a composite of skew-T, hodograph and selected convective parameters
    on as single layout, by calling the sounding_plot of thunder packages with
    rp2 functions.

    thundeR - Rapid computation and visualisation of convective parameters
              from rawinsonde and NWP data.
              refer to https://github.com/bczernecki/thundeR

    Args:
        pressure (pd.Series): pressure [hPa]
        altitude (pd.Series): altitude [m] (can be above sea level or above ground level
                              as function always consider first level as surface, i.e h = 0 m) -
                              altitude [meters]
        temp (pd.Series): temperature [degree Celsius]
        dpt (pd.Series): dew point temperature [degree Celsius]
        wd (pd.Series): wind direction [azimuth in degrees]
        ws (pd.Series): wind speed [m/s], this function will convert ws units to knots.
        title (str, optional): title to be added in the layout's header. Defaults to "".
        parcel (str, optional): parcel tracing on Skew-T for "MU", "ML" or "SB" parcel. Defaults to "MU".
        max_speed (int, optional): range of the hodograph to be drawn, 25 m/s used as default. Defaults to 25.
        hazards (bool, optional): logical, whether to add extra information about possibility of convective
                                  hazards given convective initiation (default = FALSE). Defaults to False.
    """

    # try load thunder packages
    try:
        _ = importr("thunder")
    except ImportError:
        print("thunder package is not installed in R environment.")
        return None

    # check outfile name
    if outfile is None:
        f, outfile = tempfile.mkstemp(".png")
        os.close(f)
        remove_flag = True

    # produce sounding maps by calling the sounding_save function in thunder.
    with localconverter(ro.default_converter + pandas2ri.converter):
        ro.r['sounding_save'](
            pressure, altitude, temp, dpt, wd, ws*1.9438445, filename=outfile,
            title=title, parcel=parcel, max_speed=max_speed, hazards=hazards)
    
    # read image from outfile
    image = Image.open(outfile)
    if remove_flag:
        os.unlink(outfile)
    return image


def draw_hodograph(ws, wd, altitude, max_hght = 12000,
                   max_speed = 25, title="", outfile=None):
    """[summary]

    Args:
        ws ([type]): [description]
        wd ([type]): [description]
        altitude ([type]): [description]
        max_hght (int, optional): [description]. Defaults to 12000.
        max_speed (int, optional): [description]. Defaults to 25.
        outfile ([type], optional): [description]. Defaults to None.
    """

    # try load thunder packages
    try:
        _ = importr("thunder")
        grdevices = importr('grDevices')
    except ImportError:
        print("thunder package is not installed in R environment.")
        return None

    # check outfile name
    if outfile is None:
        f, outfile = tempfile.mkstemp(".png")
        os.close(f)
        remove_flag = True

    # produce sounding maps by calling the sounding_save function in thunder.
    with localconverter(ro.default_converter + pandas2ri.converter):
        grdevices.png(file=outfile, width=800, height=800)
        ro.r['sounding_hodograph'](
            ws*1.9438445, wd, altitude, max_hght=max_hght)
        ro.r['title'](title)
        grdevices.dev_off()
    
    # read image from outfile
    image = Image.open(outfile)
    if remove_flag:
        os.unlink(outfile)
    return image


def draw_wind_profile(ws, wd, pressure, altitude, ptop = 100, title="", outfile=None):
    """[summary]

    Args:
        ws ([type]): [description]
        wd ([type]): [description]
        altitude ([type]): [description]
        max_hght (int, optional): [description]. Defaults to 12000.
        max_speed (int, optional): [description]. Defaults to 25.
        outfile ([type], optional): [description]. Defaults to None.
    """

    # try load thunder packages
    try:
        _ = importr("thunder")
        grdevices = importr('grDevices')
    except ImportError:
        print("thunder package is not installed in R environment.")
        return None

    # check outfile name
    if outfile is None:
        f, outfile = tempfile.mkstemp(".png")
        os.close(f)
        remove_flag = True

    # produce sounding maps by calling the sounding_save function in thunder.
    with localconverter(ro.default_converter + pandas2ri.converter):
        grdevices.png(file=outfile, width=800, height=800)
        ro.r('par(fig = c(0.1, 0.75, 0.15, 0.9), new = TRUE, mar = c(1, 1, 1, 1), oma = c(0, 0, 0, 0))')
        ro.r['sounding_wind'](pressure, ws*1.9438445, ptop=ptop)
        ro.r['title'](title)
        ro.r('par(fig = c(0.65, 0.95, 0.15, 0.9), new = TRUE, mar = c(1, 1, 1, 1), oma = c(0, 0, 0, 0))')
        ro.r['sounding_barbs'](pressure, ws*1.9438445, wd, altitude, ptop=ptop)
        grdevices.dev_off()
    
    # read image from outfile
    image = Image.open(outfile)
    if remove_flag:
        os.unlink(outfile)
    return image