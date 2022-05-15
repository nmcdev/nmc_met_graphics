## Brian Blaylock
## May 2, 2018

"""
====================
Air Quality Colormap
====================

Air quality colormaps

"""

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import matplotlib as mpl


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
    cmap = colors.LinearSegmentedColormap.from_list(
        "airquality", COLORS, N=len(ticks) - 1
    )
    norm = colors.BoundaryNorm(boundaries=ticks, ncolors=len(ticks))

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


if __name__ == "__main__":
    # Make colorbars for docs

    cm_aqi("pm25", display_cmap=True)
    plt.savefig("../docs/_static/BB_cmap/cm_aqi-pm25", bbox_inches="tight")

    cm_aqi("o3", display_cmap=True)
    plt.savefig("../docs/_static/BB_cmap/cm_aqi-o3", bbox_inches="tight")
