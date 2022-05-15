## Brian Blaylock
## July 3, 2018
## Revised June 17, 2020

"""
=================
Landuse Colormaps
=================

Custom landuse colormaps.
"""

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import matplotlib as mpl

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
    cmap = colors.LinearSegmentedColormap.from_list(
        "MODIS_Land_Use", COLORS, N=len(ticks) - 1
    )
    norm = colors.BoundaryNorm(boundaries=ticks, ncolors=len(ticks))

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
    cmap = colors.LinearSegmentedColormap.from_list(
        "USGS_Land_Use", COLORS, N=len(ticks) - 1
    )
    norm = colors.BoundaryNorm(boundaries=ticks, ncolors=len(ticks))

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


if __name__ == "__main__":

    # Make colorbars for docs

    cm_modis21(display_cmap=True)
    plt.savefig("../docs/_static/BB_cmap/cm_modis21", bbox_inches="tight")

    cm_usgs24(display_cmap=True)
    plt.savefig("../docs/_static/BB_cmap/cm_usgs24", bbox_inches="tight")
