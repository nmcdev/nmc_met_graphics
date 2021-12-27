# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Utilities for use in making plots.
"""

import os
import itertools
import string
import pkg_resources
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from scipy.ndimage.filters import minimum_filter, maximum_filter

import matplotlib.pyplot as plt
import matplotlib.patheffects as mpatheffects
import matplotlib.ticker as mticker
from matplotlib import collections
from matplotlib.lines import Line2D
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER



def get_mplstyle(name):
    """
    Return matplotlib style filepath.

    Args:
        name (str): mplstyle name.
    """
    
    file = pkg_resources.resource_filename(
            'nmc_met_graphics', "resources/mplstyle/{}.mplstyle".format(name))
    if os.path.isfile(file):
        return file
    else:
        raise ValueError('Cannot find the {} sytle file.'.format(file))


def add_gridlines(ax, draw_labels=True, linewidth=2, color='gray', alpha=0.5,
                  linestyle='--', xlabels_top=False, ylabels_right=False,
                  xlabel_style={'size': 16}, ylabel_style={'size': 16},
                  xlocator=None, ylocator=None, xlines=True, ylines=True):
    """
    Add grid line to cartopy map.
    http://scitools.org.uk/cartopy/docs/v0.13/matplotlib/gridliner.html

    :param ax: matplotlib axis instance.
    :param draw_labels: Toggle whether to draw labels.
    :param linewidth: grid line width.
    :param color: grid line color.
    :param alpha: grid line alpha.
    :param linestyle: grid line style.
    :param xlabels_top: whether to draw labels on the top of the map.
    :param ylabels_right: whether to draw labels on the right of the map.
    :param xlabel_style: A dictionary passed through to ax.text on x label
                         creation for styling of the text labels.
    :param ylabel_style: A dictionary passed through to ax.text on y label
                         creation for styling of the text labels.
    :param xlocator: determine the locations of the gridlines in the
                     x-coordinate of the given CRS.
    :param ylocator: determine the locations of the gridlines in the
                     y-coordinate of the given CRS.
    :param xlines: Whether to draw the x gridlines.
    :param ylines: Whether to draw the y gridlines.
    :return: None
    """

    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=draw_labels,
                      linewidth=linewidth, color=color, alpha=alpha,
                      linestyle=linestyle)
    gl.xlabels_top = xlabels_top
    gl.ylabels_right = ylabels_right
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlines = xlines
    gl.ylines = ylines
    if xlocator is not None:
        mticker.FixedLocator(xlocator)
    if ylocator is not None:
        mticker.FixedLocator(ylocator)
    gl.xlabel_style = xlabel_style
    gl.ylabel_style = ylabel_style


def add_logo(fig, x=10, y=10, zorder=100,
             which='nmc', size='medium', **kwargs):
    """

    :param fig: `matplotlib.figure`, The `figure` instance used for plotting
    :param x: x position padding in pixels
    :param y: y position padding in pixels
    :param zorder: The zorder of the logo
    :param which: Which logo to plot 'nmc', 'cmc'
    :param size: Size of logo to be used. Can be:
                 'small' for 40 px square
                 'medium' for 75 px square
                 'large' for 150 px square.
    :param kwargs:
    :return: `matplotlib.image.FigureImage`
             The `matplotlib.image.FigureImage` instance created.
    """
    fname_suffix = {
        'small': '_small.png', 'medium': '_medium.png',
        'large': '_large.png'}
    fname_prefix = {'nmc': 'nmc', 'cma': 'cma'}
    try:
        fname = fname_prefix[which] + fname_suffix[size]
        fpath = os.path.join("resources/logo/", fname)
    except KeyError:
        raise ValueError('Unknown logo size or selection')

    logo = plt.imread(pkg_resources.resource_filename(
        'nmc_met_graphics', fpath))
    return fig.figimage(logo, x, y, zorder=zorder, **kwargs)


def add_timestamp(ax, time=None, x=0.99, y=-0.04, ha='right',
                  high_contrast=False, pretext='Created: ',
                  time_format='%Y-%m-%dT%H:%M:%SZ', **kwargs):
    """
    Adds a timestamp to a plot, defaulting to the time of
    plot creation in ISO format.

    :param ax: `matplotlib.axes.Axes`, the `Axes` instance used for plotting.
    :param time: `datetime.datetime`, Specific time to be plotted -
                datetime.utcnow will be use if not specified
    :param x: Specific time to be plotted - datetime.utcnow will be use
              if not specified
    :param y: Relative y position on the axes of the timestamp
    :param ha: str, Horizontal alignment of the time stamp string
    :param high_contrast: bool, Outline text for increased contrast
    :param pretext: str, Text to appear before the timestamp, optional.
                    Defaults to 'Created: '
    :param time_format: str, Display format of time, optional.
                        Defaults to ISO format.
    :param kwargs: keyword arguments.
    :return: `matplotlib.text.Text`
             The `matplotlib.text.Text` instance created
    """
    if high_contrast:
        text_args = {
            'color': 'white', 'path_effects':
            [mpatheffects.withStroke(linewidth=2, foreground='black')]}
    else:
        text_args = {}
    text_args.update(**kwargs)
    if not time:
        time = datetime.utcnow()
    timestr = pretext + datetime.strftime(time, time_format)
    return ax.text(x, y, timestr, ha=ha, transform=ax.transAxes, **text_args)


def add_model_title(title, initial_time, model='',
                    fhour=0, fontsize=20, multilines=False, atime=0):
    """
    Add the title information to the plot.

    :param title: str, the plot content information.
    :param initial_time: model initial time.
    :param model: model name.
    :param fhour: forecast hour.
    :param fontsize: font size.
    :param multilines: multilines for title.
    :param atime: accumulating time.
    :return: None.
    """
    if isinstance(initial_time, np.datetime64):
        initial_time = pd.to_datetime(
            str(initial_time)).replace(tzinfo=None).to_pydatetime()
    valid_time = initial_time + timedelta(hours=fhour)
    initial_str = initial_time.strftime("Initial: %Y/%m/%dT%H")
    fhour_str = "FHour: {:03d}".format(fhour)
    if atime == 0:
        valid_str = valid_time.strftime('Valid: %m/%dT%H')
    else:
        valid_str = (
            (valid_time-timedelta(hours=atime)).strftime('Valid: %m/%dT%H') +
            valid_time.strftime(' to %dT%H'))
    if multilines:
        title = title + '\n' + initial_str + ' ' + \
            fhour_str + 'h; ' + valid_str
        if model != '':
            title = '[' + model + '] ' + title
        plt.title(title, loc='left', fontsize=fontsize)
    else:
        time_str = initial_str + '\n' + fhour_str + 'h; ' + valid_str
        if model != '':
            title = '[' + model + '] ' + title
        plt.title(title, loc='left', fontsize=fontsize)
        plt.title(time_str, loc='right', fontsize=fontsize-2)


def get_model_time_stamp(initial_time, fhour=0, atime=0):
    """
    Construct the time information string.
    Return inital time string like "Initial: 2018/08/20T08"
           forecast hour like "FHour: 024"
           forecast valid time "Valid: 08/20T08"
    
    Arguments:
        initial_time {[type]} -- model initial time.
    
    Keyword Arguments:
        fhour {int} -- forecast hour (default: {0})
        atime {int} -- accumulated time (default: {0})
    """
    if isinstance(initial_time, np.datetime64):
        initial_time = pd.to_datetime(
            str(initial_time)).replace(tzinfo=None).to_pydatetime()
    valid_time = initial_time + timedelta(hours=fhour)
    initial_str = initial_time.strftime("Initial: %Y/%m/%dT%H")
    fhour_str = "FHour: {:03d}".format(fhour)
    if atime == 0:
        valid_str = valid_time.strftime('Valid: %m/%dT%H')
    else:
        valid_str = (
            (valid_time-timedelta(hours=atime)).strftime('Valid: %m/%dT%H') +
            valid_time.strftime(' to %dT%H'))
    return initial_str, fhour_str, valid_str


def center_colorbar(cb):
    """Center a diverging colorbar around zero.
    Convenience function to adjust the color limits of a colorbar. The function
    multiplies the absolute maximum of the data range by ``(-1, 1)`` and uses
    this range as new color limits.
    Note:
        The colormap used should be continuous. Resetting the clim for discrete
        colormaps may produce strange artefacts.
    Parameters:
        cb (matplotlib.colorbar.Colorbar): Colorbar to center.
    Examples:
    .. plot::
        :include-source:
        import numpy as np
        import matplotlib.pyplot as plt
        from typhon.plots import center_colorbar
        fig, ax = plt.subplots()
        sm = ax.pcolormesh(np.random.randn(10, 10) + 0.75, cmap='difference')
        cb = fig.colorbar(sm)
        center_colorbar(cb)
        plt.show()
    """
    # Set color limits to +- the absolute maximum of the data range.
    cb.set_clim(np.multiply((-1, 1), np.max(np.abs(cb.get_clim()))))


def supcolorbar(mappable, fig=None, right=0.8, rect=(0.85, 0.15, 0.05, 0.7),
                **kwargs):
    """Create a common colorbar for all subplots in a figure.
    Parameters:
        mappable: A scalar mappable like to which the colorbar applies
            (e.g. :class:`~matplotlib.collections.QuadMesh`,
            :class:`~matplotlib.contour.ContourSet`, etc.).
        fig (:class:`~matplotlib.figure.Figure`):
            Figure to add the colorbar into.
        right (float): Fraction of figure to use for the colorbar (0-1).
        rect (array-like): Add an axes at postion
            ``rect = [left, bottom, width, height]`` where all quantities are
            in fraction of figure.
        **kwargs: Additional keyword arguments are passed to
            :func:`matplotlib.figure.Figure.colorbar`.
    Returns:
        matplotlib.colorbar.Colorbar: Colorbar.
    Note:
        In order to properly scale the value range of the colorbar the ``vmin``
        and ``vmax`` property should be set manually.
    Examples:
        .. plot::
            :include-source:
            import matplotlib.pyplot as plt
            import numpy as np
            from typhon.plots import supcolorbar
            fig, axes = plt.subplots(2, 2, sharex=True, sharey=True)
            for ax in axes.flat:
                sm = ax.pcolormesh(np.random.random((10,10)), vmin=0, vmax=1)
            supcolorbar(sm, label='Test label')
    """
    if fig is None:
        fig = plt.gcf()

    fig.subplots_adjust(right=right)
    cbar_ax = fig.add_axes(rect)

    return fig.colorbar(mappable, cax=cbar_ax, **kwargs)


def figsize(w, portrait=False):
    """Return a figure size matching the golden ratio.
    This function takes a figure width and returns a tuple
    representing width and height in the golden ratio.
    Results can be returned for portrait orientation.
    Parameters:
        w (float): Figure width.
        portrait (bool): Return size for portrait format.
    Return:
        tuple: Figure width and size.
    Examples:
        >>> import typhon.plots
        >>> typhon.plots.figsize(1)
        (1, 0.61803398874989479)
        >>> typhon.plots.figsize(1, portrait=True)
        (1, 1.6180339887498949)
    """
    phi = (1 + np.sqrt(5)) / 2
    return (w, w * phi) if portrait else (w, w / phi)


def autosize(fig=None, figsize=None):
    """
    It's a thin wrapper around matplotlib that automatically adjusts font sizes,
    scatter point sizes, line widths, etc. according the figure size.
    
    refer to: https://github.com/andrewcharlesjones/plottify

    Args:
        fig (ojbect, optional): matplotlib figure object. Defaults to current figure.
        figsize (list, optional): figure size. Defaults is got from current figure.
    
    Examples:
        from plottify import autosize
        import matplotlib.pyplot as plt

        plt.scatter(x, y)
        autosize()
        plt.show()
        
        # If you have a matplotlib figure object, you can pass it as an argument to autosize:
        autosize(fig)
    """

    ## Take current figure if no figure provided
    if fig is None:
        fig = plt.gcf()

    if figsize is None:

        ## Get size of figure
        figsize = fig.get_size_inches()
    else:

        ## Set size of figure
        fig.set_size_inches(figsize)

    ## Make font sizes proportional to figure size
    fontsize_labels = figsize[0] * 5
    fontsize_ticks = fontsize_labels / 2
    scatter_size = (figsize[0] * 1.5) ** 2
    linewidth = figsize[0]
    axes = fig.get_axes()
    for ax in axes:

        ## Set label font sizes
        for item in [ax.title, ax.xaxis.label, ax.yaxis.label]:
            item.set_fontsize(fontsize_labels)

        ## Set tick font sizes
        for item in ax.get_xticklabels() + ax.get_yticklabels():
            item.set_fontsize(fontsize_ticks)

        ## Set line widths
        plot_objs = [child for child in ax.get_children() if isinstance(child, Line2D)]
        for plot_obj in plot_objs:
            plot_obj.set_linewidth(linewidth)

        ## Set scatter point sizes
        plot_objs = [
            child
            for child in ax.get_children()
            if isinstance(child, collections.PathCollection)
        ]
        for plot_obj in plot_objs:
            plot_obj.set_sizes([scatter_size])

    ## Set tight layout
    plt.tight_layout()


def get_subplot_arrangement(n):
    """Get efficient (nrow, ncol) for n subplots
    If we want to put `n` subplots in a square-ish/rectangular
    arrangement, how should we arrange them?
    Returns (⌈√n⌉, ‖√n‖)
    """
    return (int(np.ceil(np.sqrt(n))),
            int(np.round(np.sqrt(n))))


def label_axes(axes=None, labels=None, loc=(.02, .9), **kwargs):
    """Walks through axes and labels each.
    Parameters:
        axes (iterable): An iterable container of :class:`AxesSubplot`.
        labels (iterable): Iterable of strings to use to label the axes.
            If ``None``, first upper and then lower case letters are used.
        loc (tuple of floats): Where to put the label in axes-fraction units.
        **kwargs: Additional keyword arguments are collected and
            passed to :func:`~matplotlib.pyplot.annotate`.
    Examples:
        .. plot::
            :include-source:
            import matplotlib.pyplot as plt
            from typhon.plots import label_axes, styles
            plt.style.use(styles('typhon'))
            # Automatic labeling of axes.
            fig, axes = plt.subplots(ncols=2, nrows=2)
            label_axes()
            # Manually specify the axes to label.
            fig, axes = plt.subplots(ncols=2, nrows=2)
            label_axes(axes[:, 0])  # label each row.
            # Pass explicit labels (and additional arguments).
            fig, axes = plt.subplots(ncols=2, nrows=2)
            label_axes(labels=map(str, range(axes.size)), weight='bold')
    .. Based on https://stackoverflow.com/a/22509497
    """

    # This code, or an earlier version, was posted by user 'tacaswell' on Stack
    # https://stackoverflow.com/a/22509497/974555 and is licensed under
    # CC-BY-SA 3.0.  This notice may not be removed.
    if axes is None:
        axes = plt.gcf().axes

    if labels is None:
        labels = string.ascii_uppercase + string.ascii_lowercase

    labels = itertools.cycle(labels)  # re-use labels rather than stop labeling

    for ax, lab in zip(axes, labels):
        ax.annotate(lab, xy=loc, xycoords='axes fraction', **kwargs)


def sorted_legend_handles_labels(ax=None, key=None, reverse=True):
    """Sort legend labels and handles.
    Returns legend handles and labels in descending order of y data peak
    values.
    Parameters:
        ax: Matplotlib axis.
        key (Callable): Function that takes :class:`~matplotlib.lines.Line2D`
                        object. See example below.
        reverse (bool): Default: True
    Returns:
        Tuple(handles, labels): Sorted legend handles and labels
    Example:
        >>> # Sort by maximum y value
        >>> ax.legend(*sorted_legend_handles_labels())
        >>> # Sort by minimum y value
        >>> ax.legend(*sorted_legend_handles_labels(
        ...           key=lambda line: np.min(line.get_ydata())))
    """
    if ax is None:
        ax = plt.gca()

    if key is None:
        def key(line):
            return np.max(line.get_ydata())

    # Sort legend entries by their cross section peak values
    return zip(*((h, l) for _, h, l in
                 sorted(
                     zip([key(h) for h in
                          ax.get_legend_handles_labels()[0]],
                         *ax.get_legend_handles_labels()),
                     reverse=reverse)))


def add_titlebox(ax, text, x=0.05, y=0.9, alignment='left', fontsize=12.5):
    """
    add title text box.
    
    Arguments:
        ax {`matplotlib.axes.Axes`} -- the `Axes` instance used for plotting.
        text {string} -- title text
    
    Keyword Arguments:
        x {float} -- title x position (default: {0.05})
        y {float} -- title y position (default: {0.9})
        alignment {str} -- horizontal alignment (default: {'left'})
        fontsize {float} -- text font size (default: {12.5})
    
    Returns:
        `matplotlib.axes.Axes` -- the `Axes` instance used for plotting.
    """

    ax.text(
        x, y, text, horizontalalignment=alignment, transform=ax.transAxes,
        bbox=dict(facecolor='white'), fontsize=fontsize)

    return ax


def add_mslp_label(ax, proj_ccrs, mslp, lat, lon):
    """
    Add mslp low and high label

    Args:
        ax (matplotlib.axes.Axes):  the `Axes` instance used for plotting.
        proj_ccrs (cartopy projection): cartopy projection object.
        mslp (np.array): numpy array.
        lat (np.array): latitude
        lon (np.array): longitdue
    """

    #Label MSLP extrema
    def _extrema(mat, mode='wrap', window=50):
        mn = minimum_filter(mat, size=window, mode=mode)
        mx = maximum_filter(mat, size=window, mode=mode)
        return np.nonzero(mat == mn), np.nonzero(mat == mx)
    
    #Determine an appropriate window given the lat/lon grid resolution
    res = np.abs(lat[1] - lat[0])
    nwindow = int(9.5 / res)
    mslp = np.ma.masked_invalid(mslp)
    local_min, local_max = _extrema(mslp, mode='wrap', window=nwindow)
    
    #Determine axis boundaries
    xmin, xmax, ymin, ymax = ax.get_extent()
    lons2d, lats2d = np.meshgrid(lon, lat)
    transformed = proj_ccrs.transform_points(proj_ccrs, lons2d, lats2d)
    x = transformed[..., 0]
    y = transformed[..., 1]
    
    #Get location of extrema on grid
    xlows = x[local_min]; xhighs = x[local_max]
    ylows = y[local_min]; yhighs = y[local_max]
    lowvals = mslp[local_min]; highvals = mslp[local_max]
    yoffset = 0.022*(ymax-ymin)
    dmin = yoffset
    
    #Plot low pressures
    xyplotted = []
    for x,y,p in zip(xlows, ylows, lowvals):
        if x < xmax-yoffset and x > xmin+yoffset and y < ymax-yoffset and y > ymin+yoffset:
            dist = [np.sqrt((x-x0)**2+(y-y0)**2) for x0,y0 in xyplotted]
            if not dist or min(dist) > dmin: #,fontweight='bold'
                a = ax.text(x,y,'L',fontsize=28,
                        ha='center',va='center',color='r',fontweight='normal')
                b = ax.text(x,y-yoffset,repr(int(p)),fontsize=14,
                        ha='center',va='top',color='r',fontweight='normal')
                a.set_path_effects([mpatheffects.Stroke(linewidth=1.5, foreground='black'),
                       mpatheffects.SimpleLineShadow(),mpatheffects.Normal()])
                b.set_path_effects([mpatheffects.Stroke(linewidth=1.0, foreground='black'),
                       mpatheffects.SimpleLineShadow(),mpatheffects.Normal()])
                xyplotted.append((x,y))
                
    #Plot high pressures
    xyplotted = []
    for x,y,p in zip(xhighs, yhighs, highvals):
        if x < xmax-yoffset and x > xmin+yoffset and y < ymax-yoffset and y > ymin+yoffset:
            dist = [np.sqrt((x-x0)**2+(y-y0)**2) for x0,y0 in xyplotted]
            if not dist or min(dist) > dmin:
                a = ax.text(x,y,'H',fontsize=28,
                        ha='center',va='center',color='b',fontweight='normal')
                b = ax.text(x,y-yoffset,repr(int(p)),fontsize=14,
                        ha='center',va='top',color='b',fontweight='normal')
                a.set_path_effects([mpatheffects.Stroke(linewidth=1.5, foreground='black'),
                       mpatheffects.SimpleLineShadow(),mpatheffects.Normal()])
                b.set_path_effects([mpatheffects.Stroke(linewidth=1.0, foreground='black'),
                       mpatheffects.SimpleLineShadow(),mpatheffects.Normal()])
                xyplotted.append((x,y))


