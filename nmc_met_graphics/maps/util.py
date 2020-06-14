# _*_ coding: utf-8 _*_

# Copyright (c) 2020 NMC Developers.
# Distributed under the terms of the GPL V3 License.

import io
import os
from datetime import datetime, timedelta
import tempfile
import numpy as np
from IPython.display import Image, display, HTML
import nmc_met_graphics.web.ipyplot as ipyplot


def check_initTime(initTime):
    """
    Check the initTime format, return a datetime object.
    """
    if initTime is None: return initTime
    if isinstance(initTime, datetime):
        return initTime
    if isinstance(initTime, str):
        try:
            initTime = datetime.strptime(initTime, "%y%m%d%H")
            return initTime
        except Exception:
            pass
        try:
            initTime = datetime.strptime("%Y%m%d%H")
            return initTime
        except Exception:
            pass
    print('The initTime should be like "2020061230" and format is YYYYmmddHH.')
    return None


def check_model(model, model_dirs):
    """
    Check the given model dose supported or not.
    """
    model = model.upper()
    if model in model_dirs:
        return model_dirs[model]
    else:
        print('{} dose not supported. Please select {}'.format(
            model, ','.join(model_dirs.keys())))
        return None


def check_frange(frange):
    """
    Check the forecast hour range.
    """
    if frange is None: return None
    # check the length
    if (len(frange) < 2) or (len(frange) > 3):
        print("frange should be [start, end(, step)]. If step doesn't given, step=6.")
        return None
    # check the order
    if frange[0] > frange[1]:
        print("frange[0] should be less than frange[1].")
        return None
    step = 6 if len(frange) < 3 else frange[2]
    fhours = list(range(frange[0], frange[1]+1, step))
    return fhours


def draw_multiple_plots(func, kwargs):
    """
    调用func绘图函数绘制多个预报时效的图形, 并根据运行环境显示为
    动画或列出每张图形.
    """

    # generate forecast hours
    fhours = check_frange(kwargs['frange'])
    if fhours is None:
        return None
    
    # call funcation
    plots  = [] ; fhourLabels = []
    for fhour in fhours:
        kwargs['fhour'] = fhour
        kwargs['frange'] = None
        noshow = kwargs['noshow']            # force the plot function return tuple.
        kwargs['noshow'] = True
        plot, fhourLabel = func(**kwargs)
        kwargs['noshow'] = noshow            # retore the noshow keyword parameter.
        if plot is None: continue
        fhourLabels.append(fhourLabel)
        plots.append(plot)
    
    # don't show in the jupyter
    if kwargs['noshow']:
        return plots, fhourLabels
    
    try:
        # code run in jupyter notebook or not
        get_ipython()

        if kwargs['show'].upper() == 'ANIMATION':
            # generate the gif figure
            # bf = io.BytesIO()
            # return Image(bf.getvalue())
            f, outfile = tempfile.mkstemp(".gif")
            os.close(f)
            plots[0].save(outfile, format='GIF', append_images=plots[1:],
                          save_all=True, duration=400, loop=0)
            image = Image(outfile)
            os.unlink(outfile)
            return image
        else:
            # show all plot figure
            plots = np.asarray(plots, dtype=np.object)
            fhourLabels = np.asarray(fhourLabels)
            if kwargs['show'].upper() == 'TAB':
                ipyplot.plot_class_tabs(plots, fhourLabels, max_imgs_per_tab=3, img_width=plots[0].width)
            else:
                ipyplot.plot_images(plots, fhourLabels, img_width=kwargs['width'])
    except Exception:
        return plots, fhourLabels


def display_compare_plots(func, kwargs):
    """
    调用func绘图函数绘制多个模式, 多个预报时效的预报图形.
    """
    # prepare function keyword
    models = kwargs.pop('models')
    kwargs['noshow'] = True

    # get all model names
    allModels = func(getModels=True)

    # get all model plots
    allPlots  = []
    allLabels = []
    for model in allModels:
        if models is not None:
            if model not in models: continue
        kwargs['model'] = model
        plots, labels = func(**kwargs)
        allPlots.append(plots)
        allLabels.append(labels)
    allPlots  = [item for sublist in allPlots for item in sublist]
    allLabels = [item for sublist in allLabels for item in sublist]

    # display in jupyter
    try:
        # code run in jupyter notebook or not
        get_ipython()

        allPlots  = np.asarray(allPlots, dtype=np.object)
        allLabels = np.asarray(allLabels)
        ipyplot.plot_class_tabs(allPlots, allLabels, max_imgs_per_tab=15, img_width=kwargs['width'])
    except Exception:
        return allPlots, allLabels


def display_trend_plots(func, kwargs):
    """
    调用func函数绘制单个模式不同起报时间, 同一预报时刻的对比.
    """

    # prepare function keyword
    initTime = kwargs.pop('initTime')
    fhour    = kwargs.pop('fhour')
    frange   = kwargs.pop('frange')
    runBack  = kwargs.pop('runBack')
    runStep  = kwargs.pop('runStep')

    # prepare initTime and forecast hours
    initTime = func(getInitTime=True)
    fhours = check_frange(frange)
    if fhours is None:
        fhours = [fhour]

    # get the plots
    allPlots  = []
    allLabels = []
    for fh in fhours:
        validTime = initTime + timedelta(hours=fh)
        for irun in range(runBack):
            kwargs['initTime'] = initTime - timedelta(hours=runStep*irun)
            kwargs['fhour'] = fh + runStep*irun
            plot = func(**kwargs)
            if plot is None: continue
            allPlots.append(plot)
            allLabels.append(validTime.strftime('%y%m%d%H'))

    # display in jupyter
    try:
        # code run in jupyter notebook or not
        get_ipython()

        allPlots  = np.asarray(allPlots, dtype=np.object)
        allLabels = np.asarray(allLabels)
        ipyplot.plot_class_tabs(allPlots, allLabels, max_imgs_per_tab=15, img_width=kwargs['width'])
    except Exception:
        return allPlots, allLabels
