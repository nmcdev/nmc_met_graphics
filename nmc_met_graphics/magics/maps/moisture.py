# _*_ coding: utf-8 _*_

# Copyright (c) 2020 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Atmospheric moisture analysis.
"""

import numpy as np
import xarray as xr

from nmc_met_base.grid import grid_smooth
from nmc_met_base.regridding import hinterp
from nmc_met_base.moisture import cal_ivt
from nmc_met_io.retrieve_micaps_server import get_latest_initTime
from nmc_met_io.retrieve_micaps_server import get_model_3D_grid, get_model_grid
from nmc_met_graphics.util import get_map_region, check_initTime, check_model
from nmc_met_graphics.magics.moisture import draw_ivt
from nmc_met_graphics.magics.maps import util


def ivt_compare(initTime=None, fhour=0, frange=None,
                region='中国陆地', width=500, models=None):
    """
    对比显示多个模式的预报结果.

    Args:
        models (str list, optional): give the model names for comparison.
    """
    kwargs = locals().copy()
    return util.display_compare_plots(ivt, kwargs)

def ivt_trend(initTime=None, fhour=0, frange=None, model='ECMWF', 
              region='中国陆地', width=500, runBack=4, runStep=12):
    """
    分析模式不同起报时间, 同一预报时间的预报结果.
    Args:
        runBack (int, optional): how many model runs will be showed. Defaults to 4.
        runStep (int, optional): the model run time in every 'runStep' hours. Defaults to 12.
    """
    kwargs = locals().copy()
    util.display_trend_plots(ivt, kwargs)

def ivt(initTime=None, fhour=0, frange=None, model='ECMWF', region='中国陆地', 
        show='list', width=500, getModels=False, getInitTime=False, noshow=False):
    """
    分析水汽传输垂直积分场.

    Args:
        initTime (string, optional): model initial time YYYYmmddHH, like 2020061320. 
                                     Defaults to None, = the model latest run time. 
        fhour (int, optional): model forecast hour. Defaults to 0.
        frange (list, optional): model forecast hour range, [start, end, step] or [start, end] which step=6.
                                 if frange is set, fhour is ignored.
        model (str, optional): model name. Defaults to 'ECMWF'.
                               You can use "getModels=True" return all model names.
        region (str or list, optional): Predifined region name, like '中国', '中国陆地', '华北', '东北', '华东', '华中', '华南', 
                                        '西南', '西北', '新疆', '青藏'. Defaults to '中国陆地'. Or [lonmin, lonmax, latmin, latmax]
        show (str, optional): 'list', show all plots in one cell.
                              'tab', show one plot in each tab page. 
                              'animation', show gif animation.
        width (int, optional): Width of the displayed image. Defaults to 500.
        noshow (bool, optional): just return the plots.
    """

    # get function arguments
    kwargs = locals().copy()

    # set and check model directory
    model_dirs = {'ECMWF': ["ECMWF_HR/SPFH/", "ECMWF_HR/UGRD/", "ECMWF_HR/VGRD/",
                            "ECMWF_HR/PRES/SURFACE/", "ECMWF_HR/PRMSL/"],
                  'GRAPES': ['GRAPES_GFS/SPFH/', 'GRAPES_GFS/UGRD/', 'GRAPES_GFS/VGRD/', 
                             'GRAPES_GFS/PRES/SURFACE/', 'GRAPES_GFS/PRMSL/']}
    if getModels: return list(model_dirs.keys())
    model_dir = check_model(model, model_dirs)
    if model_dir is None: return None

    # check initTime
    if initTime is None:
        initTime = get_latest_initTime(model_dir[0] + '1000')
    initTime = check_initTime(initTime)
    if getInitTime: return initTime
    
    # check frange
    if frange is not None:
        return util.draw_multiple_plots(ivt, kwargs)
    
    # prepare data
    filename = initTime.strftime("%y%m%d%H") + '.' + str(int(fhour)).zfill(3)
    levels = [1000,950,925,900,850,800,700,600,500,400,300]
    qData = get_model_3D_grid(model_dir[0], filename, levels=levels)
    if qData is None: return None
    uData = get_model_3D_grid(model_dir[1], filename, levels=levels)
    if uData is None: return None
    vData = get_model_3D_grid(model_dir[2], filename, levels=levels)
    if vData is None: return None
    sPres = get_model_grid(model_dir[3], filename)
    if sPres is None: return None
    mslp  = get_model_grid(model_dir[4], filename)
    if mslp  is None: return None

    # get the coordinates
    lon   = qData.lon.values
    lat   = qData.lat.values
    lev   = qData.level.values
    time  = qData.forecast_reference_time.values
    fhour = qData.forecast_period.values[0]

    # comform surface and high variables
    sPres = hinterp(sPres.data.values.squeeze(), sPres.lon.values, sPres.lat.values, lon, lat)
    mslp  = hinterp(mslp.data.values.squeeze(), mslp.lon.values, mslp.lat.values, lon, lat)
    mslp  = grid_smooth(mslp, radius=4, method='CRES')
    qData = qData.data.values.squeeze()
    uData = uData.data.values.squeeze()
    vData = vData.data.values.squeeze()

    # compute IVT
    iquData, iqvData = cal_ivt(qData, uData, vData, lon, lat, lev, surf_pres=sPres)

    # draw the figure
    plot = draw_ivt(
        iquData, iqvData, lon, lat, mslp=mslp, map_region=get_map_region(region),
        title_kwargs={'name':model.upper(), 'time': time, 'fhour': fhour, 'tzone': 'BJT'})
    if noshow:
        return plot, str(int(fhour)).zfill(3)
    else:
        return plot

