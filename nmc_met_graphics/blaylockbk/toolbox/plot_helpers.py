## Brian Blaylock
## March 23, 2020    COVID-19 Era

"""
==================
Matplotlib Helpers
==================

Some helpers for plotting

This was a good primer on Matplotlib:
https://dev.to/skotaro/artist-in-matplotlib---something-i-wanted-to-know-before-spending-tremendous-hours-on-googling-how-tos--31oo

"""
import pickle

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

# Sometimes it is useful to put this at the top of your scripts to
# format the date axis formatting.
# - plt.rcParams['date.autoformatter.day'] = '%b %d\n%H:%M'
# - plt.rcParams['date.autoformatter.hour'] = '%b %d\n%H:%M'


def copy_fig(fig):
    """
    Copy a figure

    See comment by jmetz: https://stackoverflow.com/a/45812071/2383070
    """
    return pickle.loads(pickle.dumps(fig))


def date_axis_ticks(ax=None, locator="day", major=3, minor=1, fmt=None, minor_fmt=None):
    """
    Set tick intervals for a date axis.

    I always forget how to do this, so I hope this will jog my memory.
    For reference: https://matplotlib.org/stable/api/dates_api.html

    Parameters
    ----------
    locator : {'day', 'hour'}
        Place ticks on every day or every hour.
    major, minor : int
        Tick interval for major and minor ticks.
    fmt : str
        String format for the dates. Default is None.
        A popular dateformat is ``"%b %d\n%H:%M"``.
    """
    if ax is None:
        ax = plt.gca()

    # Where ticks should be placed
    if locator.lower() == "day":
        if major is not None:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=major))
        if minor is not None:
            ax.xaxis.set_minor_locator(mdates.DayLocator(interval=minor))
    elif locator.lower() == "hour":
        if major is not None:
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=major))
        if minor is not None:
            ax.xaxis.set_minor_locator(mdates.HourLocator(interval=minor))

    # Format Date Tick String
    if fmt is not None:
        ax.xaxis.set_major_formatter(mdates.DateFormatter(fmt))
    if minor_fmt is not None:
        ax.xaxis.set_minor_formatter(mdates.DateFormatter(minor_fmt))


def scatter_density(x, y, ax=None, **kwargs):
    """
    Plot a scatter density plot

    See example here: https://gist.github.com/blaylockbk/3190e0c21e11b5a25e09731c7ae46ad3
    """
    if ax is None:
        ax = plt.gca()

    kwargs.setdefault("c", "tab:blue")
    kwargs.setdefault("lw", 0)
    kwargs.setdefault("alpha", 0.25)
    kwargs.setdefault("s", 40)
    kwargs.setdefault("zorder", 10)

    ax.scatter(
        x, y, s=kwargs["s"], zorder=kwargs["zorder"] - 1, color="0.2", lw=1
    )  # dark grey outline
    ax.scatter(
        x, y, s=kwargs["s"], zorder=kwargs["zorder"] - 1, color="1.0", lw=0
    )  # cover overlapping edges
    ax.scatter(x, y, **kwargs)  # fill color


def _infer_interval_breaks(coord):
    """
    Infer grid spacing interval for plotting pcolormesh as center points.

    Adapted from xarray: (github/pydata/xarray/plot/utils)

    If you want to plot with pcolormesh, it will chop off the last
    row/column because pcolormesh uses the box edges as the vertices,
    and not the center of the box. This function infers the gridpoints
    to position the dat points in the center of the plotted box pixel.

    This is slightly different from the xarray code in that this
    performs the infering on both axes (if available) before returning
    the final product.

    Parameters
    ----------
    coord : array_like
        Array of x or y coordinate values.

    Returns
    -------
    Array of coordinates that allow pcolormesh to show box centered on
    the data point.


    Examples
    --------
    >>> LON, LAT = np.meshgrid(np.arange(-120, -110), np.arange(30, 40))
    >>> DATA = LON*LAT
    >>> pLON = utils.gridded_data._infer_interval_breaks(LON)
    >>> pLAT = utils.gridded_data._infer_interval_breaks(LAT)
    >>> plt.pcolormesh(LON, LAT, DATA, alpha=.5)   # grid color data at bottom-left corner
    >>> plt.pcolormesh(pLON, pLAT, DATA, alpha=.5) # grid color data at center
    """
    axis = 0
    deltas = 0.5 * np.diff(coord, axis=axis)
    first = np.take(coord, [0], axis=axis) - np.take(deltas, [0], axis=axis)
    last = np.take(coord, [-1], axis=axis) + np.take(deltas, [-1], axis=axis)
    trim_last = tuple(
        slice(None, -1) if n == axis else slice(None) for n in range(coord.ndim)
    )

    coord = np.concatenate([first, coord[trim_last] + deltas, last], axis=axis)

    if coord.ndim == 1:
        return coord

    axis = 1
    deltas = 0.5 * np.diff(coord, axis=axis)
    first = np.take(coord, [0], axis=axis) - np.take(deltas, [0], axis=axis)
    last = np.take(coord, [-1], axis=axis) + np.take(deltas, [-1], axis=axis)
    trim_last = tuple(
        slice(None, -1) if n == axis else slice(None) for n in range(coord.ndim)
    )

    coord = np.concatenate([first, coord[trim_last] + deltas, last], axis=axis)

    return coord


def center_axis_on_zero(x=True, y=False, ax=None):
    """
    Center a plot on zero along the x and/or y axis.

    Parameters
    ----------
    x, y: bool
        Center the figure for the x and/or y axis.
    """
    if ax is None:
        ax = plt.gca()

    if x:
        left, right = ax.get_xlim()
        lr_max = np.maximum(np.abs(left), np.abs(right))
        ax.set_xlim(-lr_max, lr_max)

    if y:
        down, up = ax.get_ylim()
        du_max = np.maximum(np.abs(down), np.abs(up))
        ax.set_ylim(-du_max, du_max)


def add_fig_letters(axes, offset=0.03, facecolor="#f9ecd2", labels=None, **kwargs):
    """
    Add a figure letter to top-left corner for all axes

    Like is done in a publication figure, all axes are labeled with a
    letter so individual axes can be referred to from the text.

    Parameters
    ----------
    axes : list of matplotlib axes
        maplotlib axes to label
    offset : float or tuple of float
        Either a float or tuple of floats (x-offset, y-offset)
    facecolor : color
        a color
    labels : None or str
        If none, the default is to cycle the axes with lables, 'a', 'b', 'c', etc.

    Example
    -------

    .. code-block: python

        fig, axes = plt.subplots(4,4)
        add_fig_letters(axes)

    """
    if not hasattr(offset, "__len__"):
        offset = (offset, offset)

    if not hasattr(axes, "__len__"):
        axes = [axes]

    assert len(offset) == 2, "Offset must be a number or tuple"

    if not hasattr(axes, "flat"):
        np.array(axes)

    ### Add letters to plots
    if labels is None:
        import string

        labels = string.ascii_letters

    try:
        axes = axes.flat
    except:
        pass

    for i, (ax, letter) in enumerate(zip(axes, labels)):
        plt.sca(ax)

        # Add figure letter
        box_prop = dict(boxstyle="round", facecolor=facecolor, alpha=1, linewidth=0.5)

        plt.text(
            0 + offset[0],
            1 - offset[1],
            f"{letter}",
            transform=ax.transAxes,
            fontfamily="monospace",
            va="top",
            ha="left",
            bbox=box_prop,
            zorder=100_000,
            **kwargs,
        )
