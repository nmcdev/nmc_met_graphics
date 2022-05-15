## Brian Blaylock
## June 1, 2020

"""
================
Terrain Colormap
================
"""

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

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


def cm_terrain(
    water=True,
    water_threshold=-99,
    ocean_bottom=-500,
    land_top=3650,
    display_cmap=False,
):
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
    >>> import matplotlib.pyplot as plt
    >>> import numpy as np
    >>> cm_cmap, cm_label = cm_terrain()
    >>> plt.pcolormesh(np.random.rand(10,10)*3000, **cm_cmap)
    >>> plt.colorbar(**cm_label)

    """
    if water:
        oceancolors = ["mediumblue", "deepskyblue", np.array([151, 182, 225]) / 255]
        nodes = [0.0, 0.8, 1.0]
        colors_ocean = mcolors.LinearSegmentedColormap.from_list(
            "ocean_cmap", list(zip(nodes, oceancolors))
        )
        colors_ocean = colors_ocean(np.linspace(0, 1, 256))

    landcolors = [
        "yellowgreen",
        "darkgreen",
        "forestgreen",
        "wheat",
        "tan",
        "sienna",
        "snow",
    ]
    nodes = [0.0, 0.03, 0.08, 0.45, 0.60, 0.95, 1.0]
    colors_land = mcolors.LinearSegmentedColormap.from_list(
        "land_cmap", list(zip(nodes, landcolors))
    )
    colors_land = colors_land(np.linspace(0, 1, 256))

    if water:
        all_colors = np.vstack((colors_ocean, colors_land))
    else:
        all_colors = colors_land
    cmap = mcolors.LinearSegmentedColormap.from_list("BKB_terrain_cmap", all_colors)

    if water:
        norm = MidpointNormalize(
            vmin=ocean_bottom, vcenter=water_threshold, vmax=land_top
        )
    else:
        norm = mcolors.Normalize(vmax=land_top, vmin=water_threshold)

    label = "Terrain Height (m)"

    if display_cmap:
        fig = plt.figure(figsize=(8, 3))
        ax = fig.add_axes([0.05, 0.80, 0.9, 0.15])
        cb = mpl.colorbar.ColorbarBase(
            ax, orientation="horizontal", cmap=cmap, norm=norm, label=label
        )

    return {"cmap": cmap, "norm": norm}, {"label": label}


if __name__ == "__main__":

    cm_terrain(display_cmap=True)
    plt.savefig("../docs/_static/BB_cmap/cm_terrain", bbox_inches="tight")
