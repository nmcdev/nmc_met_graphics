# Brian Blaylock
# November 11, 2017

"""
===============
Radar Colormaps
===============

Consider using colorbars from PyART. They include colorblind-friendly color maps.

"""

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import matplotlib as mpl


def cm_reflectivity(display_cmap=False, levels=40):
    """
    Colormap for radar reflectivity in dBZ.

    Based on `PyART NWSref colorbar <https://github.com/ARM-DOE/pyart/blob/master/pyart/graph/_cm.py>`_

    .. image:: _static/BB_cmap/cm_reflectivity.png

    Parameters
    ----------
    display_cmap : bool
        Show the cmap only
    levels : int
        Number of color segments. If None, will be continuous.

    Returns
    -------
    - First dict for colormapping
    - Second dict for colorbar

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> import numpy as np
    >>> cm_cmap, cm_label = cm_reflect()
    >>> plt.pcolormesh(np.random.rand(10,10)*80, **cm_cmap)
    >>> plt.colorbar(**cm_label)

    """
    label = r"Reflectivity (dBZ)"

    COLORS = [
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

    # Create the colormap
    if levels is None:
        cmap = colors.LinearSegmentedColormap.from_list("NWS Reflectivity", COLORS)
    else:
        cmap = colors.LinearSegmentedColormap.from_list(
            "NWS Reflectivity", COLORS, N=levels
        )
    norm = colors.Normalize(0, 80)
    ticks = range(0, 81, 10)

    if display_cmap:
        fig = plt.figure(figsize=(8, 3))
        ax = fig.add_axes([0.05, 0.80, 0.9, 0.12])
        cb = mpl.colorbar.ColorbarBase(
            ax, orientation="horizontal", cmap=cmap, norm=norm, label=label, ticks=ticks
        )

    return {"cmap": cmap, "norm": norm}, {"label": label, "ticks": ticks}


def cm_radialvelocity(display_cmap=False, levels=16):
    """
    Colormap for radar radial velocity (m/s).

    Based on `PyART NWSref colorbar <https://github.com/ARM-DOE/pyart/blob/master/pyart/graph/_cm.py>`_

    .. image:: _static/BB_cmap/cm_radialvelocity.png

    Parameters
    ----------
    display_cmap : bool
        Show the cmap only
    levels : int
        Number of color segments. If None, will be continuous.

    Returns
    -------
    - First dict for colormapping
    - Second dict for colorbar

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> import numpy as np
    >>> cm_cmap, cm_label = cm_reflect()
    >>> plt.pcolormesh(np.random.rand(10,10)*80, **cm_cmap)
    >>> plt.colorbar(**cm_label)

    """
    label = r"Radial Velocity (m s$\mathregular{^{-1}}$)"

    COLORS = [
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

    # Create the colormap
    if levels is None:
        cmap = colors.LinearSegmentedColormap.from_list("NWS Radial Velocity", COLORS)
    else:
        cmap = colors.LinearSegmentedColormap.from_list(
            "NWS Radial Velocity", COLORS, N=levels
        )
    norm = colors.Normalize(-20, 20)
    ticks = range(-20, 21, 5)

    if display_cmap:
        fig = plt.figure(figsize=(8, 3))
        ax = fig.add_axes([0.05, 0.80, 0.9, 0.12])
        cb = mpl.colorbar.ColorbarBase(
            ax, orientation="horizontal", cmap=cmap, norm=norm, label=label, ticks=ticks
        )

    return {"cmap": cmap, "norm": norm}, {"label": label, "ticks": ticks}


if __name__ == "__main__":

    cm_reflectivity(display_cmap=True)
    plt.savefig("../docs/_static/BB_cmap/cm_reflectivity", bbox_inches="tight")

    cm_radialvelocity(display_cmap=True)
    plt.savefig("../docs/_static/BB_cmap/cm_radialvelocity", bbox_inches="tight")
