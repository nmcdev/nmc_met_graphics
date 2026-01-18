"""
Brian Blaylock, https://github.com/blaylockbk/Carpenter_Workshop
March 13, 2021
refer to: 
    * https://github.com/blaylockbk/Carpenter_Workshop/blob/main/paint/standard2.py
    
"""


"""
=========================
NWS Standard Color Curves
=========================
Custom colormaps for standard meteorological variables with the necessary
bounds, ticks, and labels for building the colorbar.

Standardized colormaps from National Weather Service

- Source: Joseph Moore <joseph.moore@noaa.gov>
- Document: ./NWS Standard Color Curve Summary.pdf

TODO
- [ ] Truncated colormap doesn't work as expected yet.
- [ ] General clean-up. These are far from perfect. They need some clean up and organization.
"""

import numpy as np
from cycler import cycler
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


#======================================
#
# https://github.com/blaylockbk/Carpenter_Workshop/blob/main/paint/standard2.py

# Inspired by the Matplotlib docs
# https://matplotlib.org/3.2.0/tutorials/colors/colormapnorms.html#custom-normalization-manually-implement-two-linear-ranges
class MidpointNormalize(mcolors.Normalize):
    def __init__(self, vmin=None, vmax=None, vcenter=None, clip=False):
        self.vcenter = vcenter
        mcolors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.vcenter, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))


def _display_cmap(
    ax=None, ticks=None, ticklabels=None, cbar_shape=None, fig_kw={}, **kwargs
):
    """
    Display a colormap by itself.

    https://matplotlib.org/stable/api/colorbar_api.html?highlight=colorbarbase#matplotlib.colorbar.ColorbarBase

        The main application of using a ColorbarBase explicitly is drawing
        colorbars that are not associated with other elements in the figure,
        e.g. when showing a colormap by itself.
        --- Matplotlib Docs

    Parameters
    ----------
    ax : axes
    ticks : ticks locations
    ticklabels : labels for the tick locations
    cbar_shape : shape of a colorbar to create [x-pos, y-pos, width, height]
    fig_kw : figure kwargs
    kwargs : kwargs for ColorbarBase
    """
    kwargs.setdefault("orientation", "horizontal")
    fig_kw.setdefault("figsize", (8, 3))
    fig_kw.setdefault("dpi", 150)

    if ax is None:
        # Display Colorbar as Standalone. Create new figure.
        fig = plt.figure(**fig_kw)
        if kwargs["orientation"] == "horizontal":
            ax = fig.add_axes([0.05, 0.80, 0.9, 0.1])  # [x-pos, y-pos, width, height]
        else:
            ax = fig.add_axes([0.05, 0.80, 0.05, 2])
    elif ax is not None and cbar_shape is None:
        # Auto create a colorbar to an axis
        if kwargs["orientation"] == "horizontal":
            ax = ax.get_figure().add_axes([0.1, 0.05, 0.8, 0.05])
        else:
            ax = ax.get_figure().add_axes([0.91, 0.1, 0.05, 0.8])
    else:
        # Use the values specified by cbar_shape to add the colorbar to a figure
        ax = ax.get_figure().add_axes(cbar_shape)

    cbar = mpl.colorbar.ColorbarBase(ax, **kwargs)

    if ticks is not None:
        cbar.set_ticks(ticks)
    if ticklabels is not None:
        cbar.set_ticklabels(ticklabels)

    return cbar


def _continuous_cmap(name, colors, vmin, vmax):
    cmap = mcolors.LinearSegmentedColormap.from_list(name, colors)
    norm = mcolors.Normalize(vmin, vmax)
    return cmap, norm


def _segmented_cmap(name, colors, bounds, extend="neither"):
    cmap = mcolors.LinearSegmentedColormap.from_list(name, colors, N=len(bounds) + 1)
    norm = mcolors.BoundaryNorm(bounds, cmap.N, extend=extend)
    return cmap, norm


def _normalize(value, lower_limit, upper_limit, clip=True):
    """
    Normalize values between 0 and 1.

    Parameters
    ----------
    value :
        The original value. A single value, vector, or array.
    upper_limit :
        The upper limit.
    lower_limit :
        The lower limit.
    clip : bool
        - True: Clips values between 0 and 1.
        - False: Retain the numbers that extends outside 0-1 range.
    Output:
        Values normalized between the upper and lower limit.
    """
    norm = (value - lower_limit) / (upper_limit - lower_limit)
    if clip:
        norm = np.clip(norm, 0, 1)
    return norm


class cm_tmp:
    """
    Color map for Temperature
    """

    def __init__(self, levels=-1, vmin=None, vmax=None, units="C", tick_interval=5):
        """
        tick_interval : int
            put a tick label every X number of bins
        clip_cmap : None or tuple
        """
        units = units.upper()
        _units = {"C", "F", "K"}
        assert units in _units, f"units must be one of {_units}"

        self.vmin = vmin
        self.vmax = vmax
        self.levels = levels
        self.name = "Temperature"
        self.tick_interval = tick_interval

        if units == "C":
            self.units = f"$\degree${units}"
            if vmin is None:
                self.vmin = -50
            if vmax is None:
                self.vmax = 50
            self.bounds = np.linspace(self.vmin, self.vmax, 51)
        elif units == "F":
            self.units = f"$\degree${units}"
            if vmin is None:
                self.vmin = -60
            if vmax is None:
                self.vmax = 120
            self.bounds = np.linspace(self.vmin, self.vmax, 37)
        elif units == "K":
            self.units = f"{units}"
            if vmin is None:
                self.vmin = -50 + 273  # Don't need to be exact for a color scale
            if vmax is None:
                self.vmax = 50 + 273
            self.bounds = np.linspace(self.vmin, self.vmax, 51)

        self.label = f"{self.name} ({self.units})"

        self.COLORS = np.array(
            [
                "#91003f",
                "#ce1256",
                "#e7298a",
                "#df65b0",
                "#ff73df",
                "#ffbee8",
                "#ffffff",
                "#dadaeb",
                "#bcbddc",
                "#9e9ac8",
                "#756bb1",
                "#54278f",
                "#0d007d",
                "#0d3d9c",
                "#0066c2",
                "#299eff",
                "#4ac7ff",
                "#73d7ff",
                "#adffff",
                "#30cfc2",
                "#009996",
                "#125757",
                "#066d2c",
                "#31a354",
                "#74c476",
                "#a1d99b",
                "#d3ffbe",
                "#ffffb3",
                "#ffeda0",
                "#fed176",
                "#feae2a",
                "#fd8d3c",
                "#fc4e2a",
                "#e31a1c",
                "#b10026",
                "#800026",
                "#590042",
                "#280028",
            ]
        )

        self.extend = "both"

        if self.levels is None:
            self.cmap, self.norm = _continuous_cmap(
                self.name, self.COLORS, self.vmin, self.vmax
            )
        else:
            self.cmap, self.norm = _segmented_cmap(
                self.name, self.COLORS, self.bounds, extend=self.extend
            )

        self.cmap_kwargs = dict(cmap=self.cmap, norm=self.norm)
        self.cbar_kwargs = dict(
            label=self.label,
            extend=self.extend,
            extendfrac="auto",
            ticks=self.bounds[:: self.tick_interval],
        )

    def truncate(self, cmin, cmax):
        normalized = _normalize(self.bounds, self.bounds.min(), self.bounds.max())
        logic = np.all([self.bounds >= cmin, self.bounds <= cmax], axis=0)
        bounds2 = self.bounds[logic]
        normalized2 = normalized[logic]
        new_colors = self.cmap(
            np.linspace(normalized2.min(), normalized2.max(), len(normalized2))
        )
        over = self.cmap(normalized2.max() + 0.01)
        under = self.cmap(normalized2.min() - 0.01)
        new_cmap = mcolors.ListedColormap(new_colors)
        new_cmap.set_over(over)
        new_cmap.set_under(under)
        new_norm = mcolors.BoundaryNorm(bounds2, len(bounds2))
        self.bounds = bounds2
        self.cmap = new_cmap
        self.norm = new_norm
        self.cmap_kwargs = dict(cmap=self.cmap, norm=self.norm)
        self.cbar_kwargs = dict(
            label=self.label,
            extend=self.extend,
            extendfrac="auto",
            ticks=self.bounds[:: self.tick_interval],
        )
        return self

    def display(self, ax=None, ticklabels=None, fig_kw={}, **kwargs):
        cbar = _display_cmap(
            ax,
            ticklabels=ticklabels,
            fig_kw=fig_kw,
            **kwargs,
            **self.cmap_kwargs,
            **self.cbar_kwargs,
        )
        return cbar

    def colors_to_rgb(self, mpl_rgb=False):
        """
        Parameters
        ----------
        mpl_rgb : bool
            If True, return colors as a matplotlib RGB, range [0-1]
            if False, return colors as a regular RGB, range [0-255]
        """
        if mpl_rgb:
            return [np.array(mcolors.to_rgb(i)) * 255 for i in self.COLORS]
        else:
            return [np.array(mcolors.to_rgb(i)) * 255 for i in self.COLORS]


class cm_dpt:
    def __init__(
        self,
        levels=14,
        vmin=None,
        vmax=None,
        units="C",
        tick_interval=1,
        convert="approximate",
    ):
        units = units.upper()
        _units = {"C", "F", "K"}
        assert units in _units, f"units must be one of {_units}"

        self.vmin = vmin
        self.vmax = vmax
        self.levels = levels
        self.name = "Dew Point Temperature"

        if units == "C":
            self.units = f"$\degree${units}"
            if vmin is None:
                self.vmin = -18
            if vmax is None:
                self.vmax = 28
            self.bounds = [-18, -13, -8, -3, 2, 7, 10, 13, 16, 19, 22, 25, 28]
        elif units == "F":
            self.units = f"$\degree${units}"
            if vmin is None:
                self.vmin = 0
            if vmax is None:
                self.vmax = 80
            self.bounds = np.array([0, 10, 20, 30, 40, 45, 50, 55, 60, 65, 70, 75, 80])
        elif units == "K":
            self.units = f"{units}"
            if vmin is None:
                self.vmin = -18 + 273  # Don't need to be exact for a color scale
            if vmax is None:
                self.vmax = 28 + 273
            self.bounds = (
                np.array([-18, -13, -8, -3, 2, 7, 10, 13, 16, 19, 22, 25, 28]) + 273
            )

        self.label = f"{self.name} ({self.units})"

        self.COLORS = np.array(
            [
                "#3b2204",
                "#543005",
                "#8c520a",
                "#bf812d",
                "#cca854",
                "#dfc27d",
                "#e6d9b5",
                "#d3ebe7",
                "#a9dbd3",
                "#72b8ad",
                "#318c85",
                "#01665f",
                "#003c30",
                "#002921",
            ]
        )

        if self.levels is None:
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS
            )
            self.norm = mcolors.Normalize(self.vmin, self.vmax)
        else:
            self.levels = np.maximum(self.levels, len(self.bounds) + 1)
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS, N=self.levels
            )
            self.norm = mcolors.BoundaryNorm(
                boundaries=self.bounds, ncolors=self.cmap.N, extend="both"
            )

        self.cmap_kwargs = dict(cmap=self.cmap, norm=self.norm)
        self.cbar_kwargs = dict(
            label=self.label,
            extend="both",
            spacing="proportional",
            ticks=self.bounds[::tick_interval],
        )

    def display(self, ax=None, ticklabels=None, fig_kw={}, **kwargs):
        cbar = _display_cmap(
            ax,
            ticklabels=ticklabels,
            fig_kw=fig_kw,
            **kwargs,
            **self.cmap_kwargs,
            **self.cbar_kwargs,
        )
        return cbar

    def colors_to_rgb(self, mpl_rgb=False):
        """
        Parameters
        ----------
        mpl_rgb : bool
            If True, return colors as a matplotlib RGB, range [0-1]
            if False, return colors as a regular RGB, range [0-255]
        """
        if mpl_rgb:
            return [np.array(mcolors.to_rgb(i)) for i in self.COLORS]
        else:
            return [np.array(mcolors.to_rgb(i)) * 255 for i in self.COLORS]


class cm_rh:
    def __init__(self, vmin=0, vmax=100, levels=14):
        self.levels = levels
        self.vmin = vmin
        self.vmax = vmax
        self.name = "Relative Humidity"
        self.units = "%"
        self.label = f"{self.name} ({self.units})"
        self.COLORS = np.array(
            [
                "#910022",
                "#a61122",
                "#bd2e24",
                "#d44e33",
                "#e36d42",
                "#fa8f43",
                "#fcad58",
                "#fed884",
                "#fff2aa",
                "#e6f49d",
                "#bce378",
                "#71b55c",
                "#26914b",
                "#00572e",
            ]
        )
        self.bounds = np.array(
            [0, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100]
        )

        if levels is None:
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS
            )
            self.norm = mcolors.Normalize(self.vmin, self.vmax)
        else:
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS, N=len(self.COLORS)
            )
            self.norm = mcolors.BoundaryNorm(
                boundaries=self.bounds, ncolors=self.cmap.N
            )

        self.cmap_kwargs = dict(cmap=self.cmap, norm=self.norm)
        self.cbar_kwargs = dict(
            label=self.label, ticks=self.bounds, spacing="proportional"
        )

    def display(self, ax=None, ticklabels=None, fig_kw={}, **kwargs):
        cbar = _display_cmap(
            ax,
            ticklabels=ticklabels,
            fig_kw=fig_kw,
            **kwargs,
            **self.cmap_kwargs,
            **self.cbar_kwargs,
        )
        return cbar

    def colors_to_rgb(self, mpl_rgb=False):
        """
        Parameters
        ----------
        mpl_rgb : bool
            If True, return colors as a matplotlib RGB, range [0-1]
            if False, return colors as a regular RGB, range [0-255]
        """
        if mpl_rgb:
            return [np.array(mcolors.to_rgb(i)) * 255 for i in self.COLORS]
        else:
            return [np.array(mcolors.to_rgb(i)) * 255 for i in self.COLORS]


class cm_wind:
    """Wind Speed/Gust Colormap"""

    def __init__(
        self,
        vmin=None,
        vmax=None,
        levels=18,
        units="m/s",
        convert="approximate",
        tick_interval=2,
    ):
        """
        Parameters
        ----------
        vmin, vmax : None or number
            lower and upper bounds of the colorbar in the units specified.
        levels : int
            Number of descrite levels. If None, will be a continuous color map.
        units : {'m/s', 'kn', 'km/h', 'mph'}
            Specify units of the wind speed to be used.
        convert : {'approximate', 'exact'}
            Specify how to convert the units bounds. Exact will result
            in many decimals (e.g., converting MPH to m/s). Approximate
            gives some nicer round numbers.
        tick_interval : int
            Interval for ticks labels
        """
        if units == "kph":
            units = "km/h"
        if units == "knots":
            units = "kn"

        _units = ["m/s", "kn", "km/h", "mph"]
        _convert = ["approximate", "exact"]
        assert units in _units, f"units must be one of {_units}"
        assert convert in _convert, f"unit_contert must be one of {_convert}"

        self.levels = levels
        self.vmin = vmin
        self.vmax = vmax
        self.tick_interval = tick_interval
        self.name = "Wind Speed"
        self.COLORS = np.array(
            [
                "#103f78",
                "#225ea8",
                "#1d91c0",
                "#41b6c4",
                "#7fcdbb",
                "#b4d79e",
                "#dfff9e",
                "#ffffa6",
                "#ffe873",
                "#ffc400",
                "#ffaa00",
                "#ff5900",
                "#ff0000",
                "#a80000",
                "#6e0000",
                "#ffbee8",
                "#ff73df",
            ]
        )

        # NWS bounds are in are in mph
        self.bounds = np.array(
            [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 100, 120, 140],
            dtype=float,
        )
        self.ticks = self.bounds[::tick_interval]

        if units == "m/s":
            if convert == "exact":
                scale = 0.44704
            else:
                scale = 0.5
            self.units = r"m s$\mathregular{^{-1}}$"
            if vmin is None:
                self.vmin = self.bounds.min() / scale
            if vmax is None:
                self.vmax = self.bounds.max() / scale
            self.bounds *= scale
        elif units == "mph":
            self.units = "mph"
            if vmin is None:
                self.vmin = self.bounds.min()
            if vmax is None:
                self.vmax = self.bounds.max()
            # self.bounds is already in mph. No scaling needed
        elif units == "km/h":
            if convert == "exact":
                scale = 1.609344
            else:
                scale = 1.5
            self.units = r"km h$\mathregular{^{-1}}$"
            if vmin is None:
                self.vmin = self.bounds.min() / scale
            if vmax is None:
                self.vmax = self.bounds.max() / scale
            self.bounds *= scale
        elif units == "kn":
            if convert == "exact":
                scale = 0.86897624
            else:
                scale = 1
            self.units = "kn"
            if vmin is None:
                self.vmin = self.bounds.min() / scale
            if vmax is None:
                self.vmax = self.bounds.max() / scale
            self.bounds *= scale

        self.label = f"{self.name} ({self.units})"

        self.extend = "max"

        if levels is None:
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS
            )
            self.norm = mcolors.Normalize(self.vmin, self.vmax)
        else:
            logic = np.logical_and(self.bounds >= self.vmin, self.bounds <= self.vmax)
            self.COLORS = self.COLORS[logic]
            self.bounds = self.bounds[logic]
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS, N=len(self.COLORS)
            )
            self.norm = mcolors.BoundaryNorm(
                boundaries=self.bounds, ncolors=self.cmap.N, extend=self.extend
            )

        self.cmap_kwargs = dict(cmap=self.cmap, norm=self.norm)
        self.cbar_kwargs = dict(
            label=self.label,
            extend=self.extend,
            ticks=self.ticks,
            spacing="proportional",
        )

    def display(self, ax=None, ticklabels=None, fig_kw={}, **kwargs):
        cbar = _display_cmap(
            ax,
            ticklabels=ticklabels,
            fig_kw=fig_kw,
            **kwargs,
            **self.cmap_kwargs,
            **self.cbar_kwargs,
        )
        return cbar

    def truncate(self, cmin, cmax):
        normalized = _normalize(self.bounds, self.bounds.min(), self.bounds.max())
        logic = np.all([self.bounds >= cmin, self.bounds <= cmax], axis=0)
        bounds2 = self.bounds[logic]
        normalized2 = normalized[logic]
        new_colors = self.cmap(
            np.linspace(normalized2.min(), normalized2.max(), len(normalized2))
        )
        over = self.cmap(normalized2.max() + 0.01)
        under = self.cmap(normalized2.min() - 0.01)
        new_cmap = mcolors.ListedColormap(new_colors)
        new_cmap.set_over(over)
        new_cmap.set_under(under)
        new_norm = mcolors.BoundaryNorm(bounds2, len(bounds2))
        self.bounds = bounds2
        self.cmap = new_cmap
        self.norm = new_norm
        self.cmap_kwargs = dict(cmap=self.cmap, norm=self.norm)
        self.cbar_kwargs = dict(
            label=self.label,
            extend=self.extend,
            extendfrac="auto",
            ticks=self.bounds[:: self.tick_interval],
        )
        return self

    def colors_to_rgb(self, mpl_rgb=False):
        """
        Parameters
        ----------
        mpl_rgb : bool
            If True, return colors as a matplotlib RGB, range [0-1]
            if False, return colors as a regular RGB, range [0-255]
        """
        if mpl_rgb:
            return [np.array(mcolors.to_rgb(i)) * 255 for i in self.COLORS]
        else:
            return [np.array(mcolors.to_rgb(i)) * 255 for i in self.COLORS]


class cm_cloud:
    def __init__(self, vmin=0, vmax=100, levels=15):
        self.levels = levels
        self.vmin = vmin
        self.vmax = vmax
        self.name = "Cloud Cover"
        self.units = "%"
        self.label = f"{self.name} ({self.units})"
        self.COLORS = np.array(
            [
                "#24a0f2",
                "#4eb0f2",
                "#80b7f8",
                "#a0c8ff",
                "#d2e1ff",
                "#e1e1e1",
                "#c9c9c9",
                "#a5a5a5",
                "#6e6e6e",
                "#505050",
            ]
        )
        self.bounds = np.arange(0, 101, 10)

        if levels is None:
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS
            )
            self.norm = mcolors.Normalize(self.vmin, self.vmax)
        else:
            # logic = np.logical_and(self.bounds >=vmin, self.bounds <= vmax)
            # self.COLORS = self.COLORS[logic]
            # self.bounds = self.bounds[logic]
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS, N=len(self.COLORS)
            )
            self.norm = mcolors.BoundaryNorm(
                boundaries=self.bounds, ncolors=self.cmap.N
            )
        self.cmap_kwargs = dict(cmap=self.cmap, norm=self.norm)
        self.cbar_kwargs = dict(
            label=self.label, ticks=self.bounds, spacing="proportional"
        )

    def display(self, ax=None, ticklabels=None, fig_kw={}, **kwargs):
        cbar = _display_cmap(
            ax,
            ticklabels=ticklabels,
            fig_kw=fig_kw,
            **kwargs,
            **self.cmap_kwargs,
            **self.cbar_kwargs,
        )
        return cbar


class cm_pcp:
    def __init__(self, vmin=0, vmax=762, levels=15, units="mm"):
        assert units in ["mm", "in"], 'units must be "mm" or "in"'
        self.levels = levels
        self.vmin = vmin
        self.vmax = vmax
        self.name = "Precipitation"
        self.units = units
        self.label = f"{self.name} ({self.units})"
        self.COLORS = np.array(
            [
                "#ffffff",
                "#c7e9c0",
                "#a1d99b",
                "#74c476",
                "#31a353",
                "#006d2c",
                "#fffa8a",
                "#ffcc4f",
                "#fe8d3c",
                "#fc4e2a",
                "#d61a1c",
                "#ad0026",
                "#700026",
                "#3b0030",
                "#4c0073",
                "#ffdbff",
            ]
        )

        # These are in inches
        self.bounds = np.array(
            [0, 0.01, 0.1, 0.25, 0.5, 1, 1.5, 2, 3, 4, 6, 8, 10, 15, 20, 30]
        )

        if units == "mm":
            self.bounds *= 25.4
            self.vmin *= 25.4
            self.vmax *= 25.4

        if levels is None:
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS
            )
            self.norm = mcolors.Normalize(self.vmin, self.vmax)
        else:
            logic = np.logical_and(self.bounds >= vmin, self.bounds <= vmax)
            self.COLORS = self.COLORS[logic]
            self.bounds = self.bounds[logic]
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS, N=len(self.COLORS)
            )
            self.norm = mcolors.BoundaryNorm(
                boundaries=self.bounds, ncolors=self.cmap.N, extend="max"
            )
        self.cmap_kwargs = dict(cmap=self.cmap, norm=self.norm)
        self.cbar_kwargs = dict(
            label=self.label, ticks=self.bounds, extend="max", spacing="uniform"
        )

    def display(self, ax=None, ticklabels=None, fig_kw={}, **kwargs):
        cbar = _display_cmap(
            ax,
            ticklabels=ticklabels,
            fig_kw=fig_kw,
            **kwargs,
            **self.cmap_kwargs,
            **self.cbar_kwargs,
        )
        return cbar


class cm_pop:
    """Colormap: Probability of Precipitation"""

    def __init__(self, ptype="rain", vmin=0, vmax=100, levels=10):
        self.levels = levels
        self.vmin = vmin
        self.vmax = vmax
        self.name = "Probability of Precipitation"
        self.units = "%"

        if ptype.lower() == "snow":
            self.name = "Probability of Snow"
            self.COLORS = np.array(
                [
                    "#f5f5f5",
                    "#e3ebff",
                    "#bdd6ff",
                    "#94b8ff",
                    "#66a3ff",
                    "#3690ff",
                    "#0a7afa",
                    "#006bd6",
                    "#004ead",
                    "#002487",
                ]
            )
        elif ptype.lower() == "ice":
            self.name = "Probability of Ice"
            self.COLORS = np.array(
                [
                    "#f5f5f5",
                    "#ffd9ed",
                    "#ffaafa",
                    "#ff83f9",
                    "#ff57f7",
                    "#ff37f5",
                    "#e619f9",
                    "#d500fd",
                    "#a200ad",
                    "#640087",
                ]
            )
        else:
            # Rain
            self.COLORS = np.array(
                [
                    "#f5f5f5",
                    "#e2f6da",
                    "#d5f2ca",
                    "#c0ebaf",
                    "#98df7b",
                    "#6fd349",
                    "#43c634",
                    "#23b70b",
                    "#139e07",
                    "#0b8403",
                ]
            )

        self.label = f"{self.name} ({self.units})"

        self.bounds = np.linspace(vmin, vmax, levels + 1)

        if levels is None:
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS
            )
            self.norm = mcolors.Normalize(self.vmin, self.vmax)
        else:
            logic = np.logical_and(self.bounds >= vmin, self.bounds <= vmax)
            self.bounds = self.bounds[logic]
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS, N=len(self.COLORS)
            )
            self.norm = mcolors.BoundaryNorm(
                boundaries=self.bounds, ncolors=self.cmap.N
            )
        self.cmap_kwargs = dict(cmap=self.cmap, norm=self.norm)
        self.cbar_kwargs = dict(
            label=self.label, ticks=self.bounds, spacing="proportional"
        )

    def display(self, ax=None, ticklabels=None, fig_kw={}, **kwargs):
        cbar = _display_cmap(
            ax,
            ticklabels=ticklabels,
            fig_kw=fig_kw,
            **kwargs,
            **self.cmap_kwargs,
            **self.cbar_kwargs,
        )
        return cbar


class cm_snow:
    def __init__(self, vmin=0, vmax=42, levels="default", units="in"):
        assert units in ["mm", "in"], 'units must be "mm" or "in"'
        self.levels = levels
        self.vmin = vmin
        self.vmax = vmax
        self.name = "Snow Amount"
        self.units = units
        self.label = f"{self.name} ({self.units})"
        self.COLORS = np.array(
            [
                "#ffffff",
                "#bdd7e7",
                "#6baed6",
                "#3182bd",
                "#08519c",
                "#082694",
                "#ffff96",
                "#ffc400",
                "#ff8700",
                "#db1400",
                "#9e0000",
                "#690000",
                "#360000",
            ]
        )

        # These are in inches
        self.bounds = np.array([0, 0.1, 1, 2, 3, 4, 6, 8, 12, 18, 24, 30, 36])

        if levels is None:
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS
            )
            # self.norm = mcolors.Normalize(self.vmin, self.vmax)
            self.norm = MidpointNormalize(vmin=self.vmin, vcenter=8, vmax=self.vmax)
        else:
            self.cmap = mcolors.ListedColormap(
                self.COLORS, self.name, N=len(self.COLORS)
            )
            self.norm = mcolors.BoundaryNorm(
                boundaries=self.bounds, ncolors=self.cmap.N, extend="max"
            )
        self.cmap_kwargs = dict(cmap=self.cmap, norm=self.norm)
        self.cbar_kwargs = dict(
            label=self.label, ticks=self.bounds, extend="max", spacing="uniform"
        )

    def display(self, ax=None, ticklabels=None, fig_kw={}, **kwargs):
        cbar = _display_cmap(
            ax,
            ticklabels=ticklabels,
            fig_kw=fig_kw,
            **kwargs,
            **self.cmap_kwargs,
            **self.cbar_kwargs,
        )
        return cbar


class cm_wave_height:
    """Colormap: Wave Height (ft)"""

    def __init__(self, vmin=0, vmax=60, levels="default", units="ft"):
        self.levels = levels
        self.vmin = vmin
        self.vmax = vmax
        self.name = "Wave Height"
        self.units = units
        self.label = f"{self.name} ({self.units})"
        self.COLORS = np.array(
            [
                "#ebfdff",
                "#abedf5",
                "#78cdd6",
                "#4bb8c4",
                "#55b59f",
                "#86d483",
                "#b0e890",
                "#ddff99",
                "#fed976",
                "#feb24c",
                "#fd8d3c",
                "#fc4e2a",
                "#e31a1c",
                "#bd0026",
                "#800026",
                "#5c002f",
                "#330023",
            ]
        )
        self.bounds = np.array(
            [0, 1, 2, 3, 4, 5, 7, 10, 12, 15, 20, 25, 30, 35, 40, 50, 60]
        )

        if levels is None:
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS
            )
            self.norm = mcolors.Normalize(self.vmin, self.vmax)
        else:
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS, N=len(self.COLORS)
            )
            self.norm = mcolors.BoundaryNorm(
                boundaries=self.bounds, ncolors=self.cmap.N, extend="max"
            )

        self.cmap_kwargs = dict(cmap=self.cmap, norm=self.norm)
        self.cbar_kwargs = dict(
            label=self.label, extend="max", ticks=self.bounds, spacing="proportional"
        )

    def display(self, ax=None, ticklabels=None, fig_kw={}, **kwargs):
        cbar = _display_cmap(
            ax,
            ticklabels=ticklabels,
            fig_kw=fig_kw,
            **kwargs,
            **self.cmap_kwargs,
            **self.cbar_kwargs,
        )
        return cbar

    def colors_to_rgb(self, mpl_rgb=False):
        """
        Parameters
        ----------
        mpl_rgb : bool
            If True, return colors as a matplotlib RGB, range [0-1]
            if False, return colors as a regular RGB, range [0-255]
        """
        if mpl_rgb:
            return [np.array(mcolors.to_rgb(i)) * 255 for i in self.COLORS]
        else:
            return [np.array(mcolors.to_rgb(i)) * 255 for i in self.COLORS]


#======================================
#
# https://github.com/blaylockbk/Carpenter_Workshop/blob/main/paint/radar2.py

class cm_reflectivity:
    def __init__(self, vmin=0, vmax=80, levels=40):
        self.levels = levels
        self.name = "Reflectivity"
        self.units = "dBZ"
        self.label = f"{self.name} ({self.units})"
        self.COLORS = np.array(
            [
                "#00ecec",
                "#01b5f3",
                "#0021f6",
                "#00de20",
                "#00cb00",
                "#079300",
                "#fdf900",
                "#ebb700",
                "#fd9500",
                "#ff0400",
                "#d50000",
                "#c80021",
                "#ea11f4",
                "#6e3d90",
                "#000000",
            ]
        )
        self.bounds = np.linspace(vmin, vmax, levels + 1)

        if levels is None:
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS
            )
            self.norm = mcolors.Normalize(self.vmin, self.vmax)
        else:
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS, N=levels
            )
            self.norm = mcolors.BoundaryNorm(
                boundaries=self.bounds, ncolors=self.cmap.N
            )

        self.cmap_kwargs = dict(cmap=self.cmap, norm=self.norm)
        self.cbar_kwargs = dict(label=self.label, spacing="proportional")

    def display(self, ax=None, ticklabels=None, fig_kw={}, **kwargs):
        cbar = _display_cmap(
            ax,
            ticklabels=ticklabels,
            fig_kw=fig_kw,
            **kwargs,
            **self.cmap_kwargs,
            **self.cbar_kwargs,
        )
        return cbar


class cm_radialvelocity:
    """
    Colormap for radar radial velocity (m/s).

    Based on `PyART NWSref colorbar <https://github.com/ARM-DOE/pyart/blob/master/pyart/graph/_cm.py>`_
    """

    def __init__(self, vmin=-20, vmax=20, levels=16):
        self.levels = levels
        self.name = "Radial Velocity"
        self.units = "m s$\mathregular{^{-1}}$"
        self.label = f"{self.name} ({self.units})"
        self.COLORS = np.array(
            [
                "#90009f",
                "#29b72d",
                "#00ed00",
                "#00cc00",
                "#00b100",
                "#008f00",
                "#0c740c",
                "#7d9177",
                "#947a77",
                "#810303",
                "#a10000",
                "#bc0000",
                "#dd0000",
                "#f30000",
                "#ff0000",
            ]
        )
        self.bounds = np.linspace(vmin, vmax, levels + 1)

        if levels is None:
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS
            )
            self.norm = mcolors.Normalize(self.vmin, self.vmax)
        else:
            self.cmap = mcolors.LinearSegmentedColormap.from_list(
                self.name, self.COLORS, N=levels
            )
            self.norm = mcolors.BoundaryNorm(
                boundaries=self.bounds, ncolors=self.cmap.N
            )

        self.cmap_kwargs = dict(cmap=self.cmap, norm=self.norm)
        self.cbar_kwargs = dict(label=self.label, spacing="proportional")

    def display(self, ax=None, ticklabels=None, fig_kw={}, **kwargs):
        cbar = _display_cmap(
            ax,
            ticklabels=ticklabels,
            fig_kw=fig_kw,
            **kwargs,
            **self.cmap_kwargs,
            **self.cbar_kwargs,
        )
        return cbar


#======================================
#
# https://github.com/blaylockbk/Carpenter_Workshop/blob/main/paint/airquality.py

def cm_aqi(pollutant="pm25", display_cmap=False):
    """
    Colormap for Air Quality Index for PM 2.5 and ozone pollutants.

    Based on AirNow `Air Quality Index <https://www.airnow.gov/aqi/aqi-basics/>`_
    and `Utah Division of Air Quality AQI <https://air.utah.gov/currentconditions.php>`_.

    .. image:: _static/BB_cmap/cm_aqi-pm25.png

    .. image:: _static/BB_cmap/cm_aqi-o3.png


    Parameters
    ----------
    pollutant : {'pm25', 'o3'}
        Color thresholds are dependent on the pollutant.
        - ``pm25`` is particulate matter smaller thatn 2.5 microns (micrograms/m3)
        - ``o3`` is ozone in parts per billion.
    display_cmap : bool
        Show the cmap object as a figure.

    Returns
    -------
    Two dictionaries, one for colormaping and the other for colorbar.

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> import numpy as np
    >>> cm_cmap, cm_label = cm_airquality()
    >>> plt.pcolormesh(np.random.rand(10,10)*300, **cm_cmap)
    >>> plt.colorbar(**cm_label)

    """
    _pollutant = {"pm25", "o3"}
    assert (
        pollutant in _pollutant
    ), f"Not a valid pollutant. Please specify one of {_pollutant}"

    if pollutant == "pm25":
        # The PM 2.5 Colorscale
        ticks = [0, 12.1, 35.5, 55.5, 150.5, 250.5, 300]  # micrograms/m3
        label = r"PM 2.5 ($\mu$g m$\mathregular{^{-3}}$)"

    elif pollutant == "o3":
        # The Ozone Colorscale
        ticks = [0, 55, 71, 86, 106, 201, 300]  # parts per billion
        label = "Ozone (ppb)"

    # Color tuple for every bin
    COLORS = np.array(
        [
            "#00e400",  # Green   - Good
            "#ffff00",  # Yellow  - Moderate
            "#ff7e00",  # Orange  - Sensitive Groups
            "#ff0000",  # Red     - Unhealthy
            "#99004c",  # Purple  - Hazardous
            "#4c0026",  # Maroon  - Very Unhealthy
        ]
    )

    # Create the colormap
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "airquality", COLORS, N=len(ticks) - 1
    )
    norm = mcolors.BoundaryNorm(boundaries=ticks, ncolors=len(ticks))

    if display_cmap:
        fig = plt.figure(figsize=(8, 3))
        ax = fig.add_axes([0.05, 0.80, 0.9, 0.15])
        mpl.colorbar.ColorbarBase(
            ax,
            orientation="horizontal",
            cmap=cmap,
            norm=norm,
            ticks=ticks,
            extend="max",
            label=label,
        )

    return {"cmap": cmap, "norm": norm}, {
        "ticks": ticks,
        "extend": "max",
        "label": label,
    }


#======================================
#
# https://github.com/blaylockbk/Carpenter_Workshop/blob/main/paint/landuse.py
# For the future, here is the NOAH 3.6 soil and vegetation typs
# https://inversion.nrlmry.navy.mil/confluence/display/COAMPSOPS/NOAH+3.6+soil+and+vegetation+types

def cm_modis21(display_cmap=False):
    """
    Colormap for 21-category MODIS Landuse.

    .. image:: _static/BB_cmap/cm_modis21.png

    Parameters
    ----------
    display_cmap : bool
        Show the cmap object as a figure.

    Returns
    -------
    Three dictionaries
    1. for colormapping
    2. for colorbar
    3. for colorbar tick labels

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> import numpy as np
    >>> cm_cmap, cm_colorbar, cm_labels = cm_modis21()
    >>> plt.pcolormesh(np.random.rand(10,10)*21, **cm_cmap)
    >>> cb = plt.colorbar(**cm_colorbar)
    >>> cb.ax.set_yticklabels(**cm_labels, rotation=0)
    >>> cb.ax.invert_yaxis()

    """
    CATEGORY = {
        1: {"color": "#006600", "label": "Evergreen Needleleaf Forest"},
        2: {"color": "#006633", "label": "Evergreen Broadleaf Forest"},
        3: {"color": "#33cc33", "label": "Deciduous Needleleaf Forest"},
        4: {"color": "#33cc66", "label": "Deciduous Broadleaf Forest"},
        5: {"color": "#339933", "label": "Mixed Forests"},
        6: {"color": "#4cb200", "label": "Closed Shrublands"},
        7: {"color": "#d1691f", "label": "Open Shrublands"},
        8: {"color": "#bdb569", "label": "Woody Savannas"},
        9: {"color": "#ffd600", "label": "Savannas"},
        10: {"color": "#00ff00", "label": "Grasslands"},
        11: {"color": "#00ffff", "label": "Permanent Wetlands"},
        12: {"color": "#ffff00", "label": "Croplands"},
        13: {"color": "#ff0000", "label": "Urban and Built-Up"},
        14: {"color": "#b2e64c", "label": "Cropland/Natural Vegetation Mosaic"},
        15: {"color": "#ffffff", "label": "Snow and Ice"},
        16: {"color": "#e9e9b2", "label": "Barren or Sparsely Vegetated"},
        17: {"color": "#80b2ff", "label": "Water"},
        18: {"color": "#ff00bd", "label": "Wooded Tundra"},
        19: {"color": "#f7804f", "label": "Mixed Tundra"},
        20: {"color": "#e8967a", "label": "Barren Tundra"},
        21: {"color": "#0000e0", "label": "Lake"},
    }

    COLORS = np.array([CATEGORY[i]["color"] for i in CATEGORY])
    ticks = np.array(list(CATEGORY) + [22])
    labels = np.array([str(i) + "  " + CATEGORY[i]["label"] for i in CATEGORY])

    # Create the colormap
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "MODIS_Land_Use", COLORS, N=len(ticks) - 1
    )
    norm = mcolors.BoundaryNorm(boundaries=ticks, ncolors=len(ticks))

    if display_cmap:
        fig = plt.figure(figsize=(3, 8))
        ax = fig.add_axes([0.05, 0.80, 0.12, 0.9])
        cb = mpl.colorbar.ColorbarBase(
            ax, orientation="vertical", cmap=cmap, norm=norm, ticks=ticks + 0.5
        )
        cb.ax.set_yticklabels(labels)
        cb.ax.invert_yaxis()

    return (
        {"cmap": cmap, "norm": norm},
        {"ticks": ticks + 0.5, "orientation": "vertical"},
        {"labels": labels},
    )


def cm_usgs24(display_cmap=False):
    """
    Colormap for 24-category USGS Landuse.

    .. image:: _static/BB_cmap/cm_usgs24.png

    Parameters
    ----------
    display_cmap : bool
        Show the cmap object as a figure.

    Returns
    -------
    Three dictionaries
    1. for colormapping
    2. for colorbar
    3. for colorbar tick labels

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> import numpy as np
    >>> cm_cmap, cm_colorbar, cm_labels = cm_usgs24()
    >>> plt.pcolormesh(np.random.rand(10,10)*21, **cm_cmap)
    >>> cb = plt.colorbar(**cm_colorbar)
    >>> cb.ax.set_yticklabels(**cm_labels, rotation=0)
    >>> cb.ax.invert_yaxis()

    """

    CATEGORY = {
        1: {"color": "#ff0000", "label": "Urban and Built-up Land"},
        2: {"color": "#ffff00", "label": "Dryland Cropland and Pasture"},
        3: {"color": "#ffff33", "label": "Irrigated Cropland and Pasture"},
        4: {
            "color": "#ffff4c",
            "label": "Mixed Dryland/Irrigated Cropland and Pasture",
        },
        5: {"color": "#b2e64c", "label": "Cropland/Grassland Mosaic"},
        6: {"color": "#b2e64c", "label": "Cropland/Woodland Mosaic"},
        7: {"color": "#00ff00", "label": "Grassland"},
        8: {"color": "#4cb200", "label": "Shrubland"},
        9: {"color": "#d1691f", "label": "Mixed Shrubland/Grassland"},
        10: {"color": "#ffd600", "label": "Savanna"},
        11: {"color": "#33cc66", "label": "Deciduous Broadleaf Forest"},
        12: {"color": "#33cc33", "label": "Deciduous Needleleaf Forest"},
        13: {"color": "#006633", "label": "Evergreen Broadleaf Forest"},
        14: {"color": "#006600", "label": "Evergreen Needleleaf Forest"},
        15: {"color": "#339933", "label": "Mixed Forests"},
        16: {"color": "#0000e0", "label": "Water Bodies"},
        17: {"color": "#00ffff", "label": "Herbaceous Wetlands"},
        18: {"color": "#33ffff", "label": "Wooden Wetlands"},
        19: {"color": "#e9e9b2", "label": "Barren or Sparsely Vegetated"},
        20: {"color": "#db143b", "label": "Herbaceous Tundraa"},
        21: {"color": "#db143b", "label": "Wooded Tundra"},
        22: {"color": "#f7804f", "label": "Mixed Tundra"},
        23: {"color": "#e8967a", "label": "Barren Tundra"},
        24: {"color": "#ffffff", "label": "Snow and Ice"},
    }

    COLORS = np.array([CATEGORY[i]["color"] for i in CATEGORY])
    ticks = np.array(list(CATEGORY) + [25])
    labels = np.array([str(i) + "  " + CATEGORY[i]["label"] for i in CATEGORY])

    # Create the colormap
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "USGS_Land_Use", COLORS, N=len(ticks) - 1
    )
    norm = mcolors.BoundaryNorm(boundaries=ticks, ncolors=len(ticks))

    if display_cmap:
        fig = plt.figure(figsize=(3, 8))
        ax = fig.add_axes([0.05, 0.80, 0.12, 0.9])
        cb = mpl.colorbar.ColorbarBase(
            ax, orientation="vertical", cmap=cmap, norm=norm, ticks=ticks + 0.5
        )
        cb.ax.set_yticklabels(labels)
        cb.ax.invert_yaxis()

    return (
        {"cmap": cmap, "norm": norm},
        {"ticks": ticks + 0.5, "orientation": "vertical"},
        {"labels": labels},
    )


#======================================
#
# https://github.com/blaylockbk/Carpenter_Workshop/blob/main/paint/misc.py

def cm_obimp(display_cmap=False):
    """
    Colormap for observation impact (OBIMP) from Forecast Sensitivity
    Observation Impact (FSOI).

    The user will need to manually set vmax and vmin to an appropriate range
    for the data.

    .. image:: _static/BB_cmap/cm_obimp.png

    Parameters
    ----------
    display_cmap : bool
        Show the only the colorbar.
    """
    top = mpl.colormaps["Greens_r"]
    middle = mcolors.to_rgba("#fffcf2")
    bottom = mpl.colormaps["RdPu"]

    newcolors = np.vstack(
        (
            top(np.linspace(0, 0.8, 128)),
            middle,
            middle,
            middle,
            bottom(np.linspace(0.2, 1, 127)),
        )
    )

    cmap = mcolors.ListedColormap(newcolors, name="OBIMP")

    label = "Observation Impact"

    if display_cmap:
        fig = plt.figure(figsize=(8, 3))
        ax = fig.add_axes([0.05, 0.80, 0.9, 0.1])
        cb = mpl.colorbar.ColorbarBase(
            ax, orientation="horizontal", cmap=cmap, label=label
        )

    return {"cmap": cmap}, {"label": label}


def cm_prob(display_cmap=False):
    """
    Colormap for ensemble probability.

    Based on the `NCAR Ensemble <https://www2.mmm.ucar.edu/projects/ncar_ensemble/legacy/>`_
    proability colorscale.

    .. image:: _static/BB_cmap/cm_prob.png

    Parameters
    ----------
    display_cmap : bool
        If True, show just the cmap
    """
    label = "Probability"

    # Color tuple for every bin
    COLORS = [
        "#ffffff",
        "#d7e3ee",
        "#b5caff",
        "#8fb3ff",
        "#7f97ff",
        "#abcf63",
        "#e8f59e",
        "#fffa14",
        "#ffd121",
        "#ffa30a",
        "#ff4c00",
    ]

    bounds = np.arange(0, 1.06, 0.05)
    ticks = bounds[::2]

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "Ensemble Probability", COLORS, N=len(COLORS) * 2
    )

    norm = mcolors.BoundaryNorm(boundaries=bounds, ncolors=len(bounds))
    # norm = colors.Normalize(0, 1)

    if display_cmap:
        fig = plt.figure(figsize=(8, 3))
        ax = fig.add_axes([0.05, 0.80, 0.9, 0.1])
        cb = mpl.colorbar.ColorbarBase(
            ax, orientation="horizontal", cmap=cmap, norm=norm, label=label, ticks=ticks
        )

    return {"cmap": cmap, "norm": norm}, {"label": label, "ticks": ticks}


#======================================
#
# https://github.com/blaylockbk/Carpenter_Workshop/blob/main/paint/simple_colors.py
#
# 20 simple, distinct colors from Sasha Trubetskoy
#   https://sashamaps.net/docs/resources/20-colors/
# If you want to use these colors as your matplotlib color cycle just do
#    from paint.simple_colors import simple_colors
#    simple_colors().set_rcParams

# 95% accessible colors
simple_colors_9500 = {
    "Red": "#e6194B",
    "Green": "#3cb44b",
    "Yellow": "#ffe119",
    "Blue": "#4363d8",
    "Orange": "#f58231",
    "Purple": "#911eb4",
    "Cyan": "#42d4f4",
    "Magenta": "#f032e6",
    "Lime": "#bfef45",
    "Pink": "#fabed4",
    "Teal": "#469990",
    "Lavender": "#dcbeff",
    "Brown": "#9A6324",
    "Beige": "#fffac8",
    "Maroon": "#800000",
    "Mint": "#aaffc3",
    "Olive": "#808000",
    "Apricot": "#ffd8b1",
    "Navy": "#000075",
    "Grey": "#a9a9a9",
    "White": "#ffffff",
    "Black": "#000000",}

# 99% accessible colors
simple_colors_9900 = {
    "Red": "#e6194B",
    "Green": "#3cb44b",
    "Yellow": "#ffe119",
    "Blue": "#4363d8",
    "Orange": "#f58231",
    "Cyan": "#42d4f4",
    "Magenta": "#f032e6",
    "Pink": "#fabed4",
    "Teal": "#469990",
    "Lavender": "#dcbeff",
    "Brown": "#9A6324",
    "Beige": "#fffac8",
    "Maroon": "#800000",
    "Mint": "#aaffc3",
    "Navy": "#000075",
    "Grey": "#a9a9a9",
    "White": "#ffffff",
    "Black": "#000000",}

# 99.99% accessible colors
simple_colors_9999 = {
    "Yellow": "#ffe119",
    "Blue": "#4363d8",
    "Orange": "#f58231",
    "Lavender": "#dcbeff",
    "Maroon": "#800000",
    "Navy": "#000075",
    "Grey": "#a9a9a9",
    "White": "#ffffff",
    "Black": "#000000",}

# 100% accessible colors
simple_colors_10000 = {
    "Yellow": "#ffe119",
    "Blue": "#4363d8",
    "Grey": "#a9a9a9",
    "White": "#ffffff",
    "Black": "#000000",}


class simple_colors:
    """
    Class for 20 simple, distinct colors (plus black and white).
    Examples
    --------
    To cycle through these colors with Matplotlib, do
    >>> from paint.simple_colors import simple_colors
    >>> simple_colors().set_rcParams
    """

    def __init__(self, accessibility=0.95):
        """
        Parameters
        ----------
        accessibility: float
            Get colors that are at a level of accessibility.
            Default 20 colors (plus black and white) is 95% accessible.
        """
        self.accessibility = accessibility

        if accessibility == 1:
            self.colors = simple_colors_10000
        elif accessibility >= 0.9999:
            self.colors = simple_colors_9999
        elif accessibility >= 0.99:
            self.colors = simple_colors_9900
        else:
            self.colors = simple_colors_9500

        self.color_list = [i for _, i in self.colors.items()]

    @property
    def cycler(self):
        """Create a cycler object with the color list"""
        return cycler(color=self.color_list)

    @property
    def set_rcParams(self):
        """Set the Matplotlib rcParams to cycle through the colors"""
        mpl.rcParams["axes.prop_cycle"] = self.cycler
        

#======================================
#
# https://github.com/blaylockbk/Carpenter_Workshop/blob/main/paint/simple_colors.py

class cm_terrain:
    """
    Colormap for terrain.

    .. image:: _static/BB_cmap/cm_terrain.png

    Parameters
    ----------
    water : bool
        Include water in the colormap.
    water_threshold : int or float
        The value where the colors for water values begin.
        Default is -99 because some land points are below sea level
        and we don't want to color those points as ocean.
        You might consider using a landsea mask to change water colors
        to some value below -99
    ocean_bottom, land_top : int or float
        The bottom of the ocean and top of land surface.
    display_cmap : bool
        Show the colorbar.

    Examples
    --------

    .. code-block:: python

        import matplotlib.pyplot as plt
        import numpy as np
        plt.pcolormesh(np.random.rand(10,10)*3000, **cm_terrain().cmap_kwargs)
        plt.colorbar(**cm_terrain().cbar_kwargs)

    """

    def __init__(
        self,
        water=True,
        water_threshold=-99,
        ocean_bottom=-500,
        land_top=3650,
        land_color_scheme=1,
    ):
        self.water = water
        self.water_threshold = water_threshold
        self.ocean_bottom = ocean_bottom
        self.land_top = land_top
        self.name = "Terrain Height"
        self.units = "m"
        self.label = f"{self.name} ({self.units})"

        if water:
            oceancolors = ["mediumblue", "deepskyblue", "#97b6e1"]
            nodes = [0.0, 0.8, 1.0]
            colors_ocean = mcolors.LinearSegmentedColormap.from_list(
                "ocean", list(zip(nodes, oceancolors))
            )
            colors_ocean = colors_ocean(np.linspace(0, 1, 256))

        if land_color_scheme == 1:
            landcolors = [
                (0.0, "yellowgreen"),
                (0.03, "darkgreen"),
                (0.08, "forestgreen"),
                (0.45, "wheat"),
                (0.60, "tan"),
                (0.95, "sienna"),
                (1.00, "snow"),
            ]
        elif land_color_scheme == 2:
            landcolors = [
                (0, "#ffad7d"),
                (0.5, "#b46f46"),
                (1, "#6b3d22"),
            ]
        elif land_color_scheme == 3:
            landcolors = [
                (0, "#f8b893"),
                (0.4, "#c0784f"),
                (0.6, "#97674c"),
                (.85, "#6b3d22"),
                (1, "#dadada"),
            ]
        else:
            landcolors = land_color_scheme

        colors_land = mcolors.LinearSegmentedColormap.from_list("land", landcolors)
        colors_land = colors_land(np.linspace(0, 1, 256))

        if water:
            all_colors = np.vstack((colors_ocean, colors_land))
        else:
            all_colors = colors_land

        self.cmap = mcolors.LinearSegmentedColormap.from_list("Terrain", all_colors)

        if water:
            self.norm = MidpointNormalize(
                vmin=ocean_bottom, vcenter=water_threshold, vmax=land_top
            )
        else:
            self.norm = mcolors.Normalize(vmax=land_top, vmin=water_threshold)

        self.cmap_kwargs = dict(cmap=self.cmap, norm=self.norm)
        self.cbar_kwargs = dict(label=self.label)

    def display(self, ax=None, ticklabels=None, fig_kw={}, **kwargs):
        cbar = _display_cmap(
            ax,
            ticklabels=ticklabels,
            fig_kw=fig_kw,
            **kwargs,
            **self.cmap_kwargs,
            **self.cbar_kwargs,
        )
        return cbar


#======================================
#
# https://github.com/blaylockbk/Carpenter_Workshop/blob/main/paint/simple_colors.py

class cm_vorticity:
    def __init__(self):

        self.name = "Absolute Vorticity"
        self.units = "$s^{-1}$"
        self.label = f"{self.name} ({self.units})"
        self.bounds = list(range(-8, 1, 1)) + list(range(8, 46, 1))
        colors1 = plt.cm.YlOrRd(np.linspace(0, 1, 48))
        colors2 = plt.cm.BuPu(np.linspace(0.5, 0.75, 8))
        self.COLORS = np.vstack((colors2, (1, 1, 1, 1), colors1))
        self.cmap = mcolors.ListedColormap(self.COLORS)
        self.norm = mcolors.BoundaryNorm(self.bounds, len(self.bounds))

        self.cmap_kwargs = dict(cmap=self.cmap, norm=self.norm)
        self.cbar_kwargs = dict(label=self.label)

    def display(self, ax=None, ticklabels=None, fig_kw={}, **kwargs):
        cbar = _display_cmap(
            ax,
            ticklabels=ticklabels,
            fig_kw=fig_kw,
            **kwargs,
            **self.cmap_kwargs,
            **self.cbar_kwargs,
        )
        return cbar