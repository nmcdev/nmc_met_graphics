## Brian Blaylock
## March 31, 2021

"""
=====================
Colomap for Vorticity
=====================

Based on the colormap in the MetPy example:
https://unidata.github.io/python-training/gallery/500hpa_absolute_vorticity_winds/
"""

import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from paint.standard2 import _display_cmap


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
