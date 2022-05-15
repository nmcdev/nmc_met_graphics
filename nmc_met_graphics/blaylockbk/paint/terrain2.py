## Brian Blaylock
## June 1, 2020

"""
================
Terrain Colormap
================
Brian's custom terrain colormap.

"""
import matplotlib as mpl

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

from paint.standard2 import _display_cmap

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


if __name__ == "__main__":

    cm_terrain().display()
    plt.savefig("../docs/_static/BB_cmap/cm_terrain", bbox_inches="tight")
