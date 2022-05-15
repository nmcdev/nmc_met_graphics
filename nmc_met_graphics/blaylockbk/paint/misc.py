## Brian Blaylock
## June 10, 2020    COVID-19 Era

"""
=======================
Miscellaneous Colormaps
=======================

A set of colormaps that don't fit in any other category.

"""

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import matplotlib as mpl


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
    top = mpl.cm.get_cmap("Greens_r")
    middle = colors.to_rgba("#fffcf2")
    bottom = mpl.cm.get_cmap("RdPu")

    newcolors = np.vstack(
        (
            top(np.linspace(0, 0.8, 128)),
            middle,
            middle,
            middle,
            bottom(np.linspace(0.2, 1, 127)),
        )
    )

    cmap = colors.ListedColormap(newcolors, name="OBIMP")

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

    cmap = colors.LinearSegmentedColormap.from_list(
        "Ensemble Probability", COLORS, N=len(COLORS) * 2
    )

    norm = colors.BoundaryNorm(boundaries=bounds, ncolors=len(bounds))
    # norm = colors.Normalize(0, 1)

    if display_cmap:
        fig = plt.figure(figsize=(8, 3))
        ax = fig.add_axes([0.05, 0.80, 0.9, 0.1])
        cb = mpl.colorbar.ColorbarBase(
            ax, orientation="horizontal", cmap=cmap, norm=norm, label=label, ticks=ticks
        )

    return {"cmap": cmap, "norm": norm}, {"label": label, "ticks": ticks}


if __name__ == "__main__":
    # Save a copy of the colorbar for the docs

    cm_obimp(display_cmap=True)
    plt.savefig("../docs/_static/BB_cmap/cm_obimp", bbox_inches="tight")

    cm_prob(display_cmap=True)
    plt.savefig("../docs/_static/BB_cmap/cm_prob", bbox_inches="tight")
