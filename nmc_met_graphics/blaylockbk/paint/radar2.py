# Brian Blaylock
# November 11, 2017

"""
===============
Radar Colormaps
===============

Consider using colorbars from PyART. They include colorblind-friendly color maps.

"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import matplotlib as mpl

from paint.standard2 import _display_cmap


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
