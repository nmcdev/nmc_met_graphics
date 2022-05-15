# Brian Blaylock
# July 3, 2018

"""
=================
Wind Calculations
=================

Functions related to wind vectors

- spddir_to_uv
- uv_to_spddir
- unit_vector
- angle_between

"""

import numpy as np


def spddir_to_uv(wspd, wdir):
    """
    Calculate the u and v wind components from wind speed and direction.

    See https://earthscience.stackexchange.com/a/11989/18840

    Parameters
    ----------
    wspd, wdir : array_like
        Arrays of wind speed and wind direction (in degrees)

    Returns
    -------
    u and v wind components
    """
    if isinstance(wspd, list) or isinstance(wdir, list):
        wspd = np.array(wspd, dtype=float)
        wdir = np.array(wdir, dtype=float)

    rad = np.pi / 180.0
    u = -wspd * np.sin(rad * wdir)
    v = -wspd * np.cos(rad * wdir)

    # If the speed is zero, then u and v should be set to zero (not NaN)
    if hasattr(u, "__len__"):
        u[np.where(wspd == 0)] = 0
        v[np.where(wspd == 0)] = 0
    elif wspd == 0:
        u = float(0)
        v = float(0)

    return np.round(u, 3), np.round(v, 3)


def uv_to_spddir(u, v):
    """
    Calculates the wind speed and direction from u and v components.

    Takes into account the wind direction coordinates is different than
    the trig unit circle coordinate.
    If the wind direction is 360, then return zero.

    Parameters
    ----------
    u, v: array_like
        u (west to east) and v (south to north) wind component.

    Returns
    -------
    Wind speed and direction
    """
    if isinstance(u, list) or isinstance(v, list):
        u = np.array(u)
        v = np.array(v)

    wdir = (270 - np.rad2deg(np.arctan2(v, u))) % 360
    wspd = np.sqrt(u * u + v * v)

    return wspd.round(3), wdir.round(3)


def unit_vector(i, j):
    """
    Return a unit vector for a 2D vector.
    """
    magnitude = np.sqrt(i ** 2 + j ** 2)
    unit_i = i / magnitude
    unit_j = j / magnitude

    return unit_i, unit_j


def angle_between(i1, j1, i2, j2):
    """
    Calculate the angle between two 2D vectors (i.e., 2 wind vectors).

    Utilizes the cos equation:
        $cos(theta) = (v1 dot v2) / (V1 x V2)$ where V1 and V2 are the magnitude of vector1 and vecto2.

    For a two-dimensional vector where v1 = <i1, j1> and v2 = <i2, j2>:

        cos(theta) = (i1*i2 + j1*j2) / (sqrt(i1**2 + j1**2) * sqrt(i2**2 + j2**2)

    Parameters
    ----------
    i1, j1 : array like
        i and j components representing the first vector
    i2, j2 : array like
        i and j components representing the second vector

    Returns
    -------
    The angle between vectors vector 1 and vector 2 in degrees.

    Examples
    --------

    >>> angle_between(0, 10, 30, 30)
    45.0

    >>> angle_between(1, 0, 0, 1)
    90.0

    >>> angle_between((1, 0), (-1, 0))
    180
    """

    dot_product = i1 * i2 + j1 * j2
    magnitude1 = np.sqrt(i1 ** 2 + j1 ** 2)
    magnitude2 = np.sqrt(i2 ** 2 + j2 ** 2)

    theta = np.arccos(dot_product / (magnitude1 * magnitude2))

    return np.rad2deg(theta).round(3)


def wind_degree_labels(res="m"):
    """Wind degree increment and direction labels

    This is useful for labeling a matplotlib wind direction axis ticks.

    .. code-block:: python

        plt.yticks(*wind_degree_labels())

    .. code-block:: python

        ticks, labels = wind_degree_labels()
        ax.set_yticks(ticks)
        ax.set_yticklabels(labels)

    ..image:: https://rechneronline.de/geo-coordinates/wind-rose.png

    Parameters
    ----------
    res : {'l', 'm', 'h'} or {90, 45, 22.5}
        Low, medium, and high increment resolution.
        - l : returns 4 cardinal directions [N, E, S, W, N]
        - m : returns 8 cardinal directions [N, NE, E, SE, ...]
        - h : returns 16 cardinal directions [N, NNE, NE, ENE, E, ...]
    """
    labels = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
        "N",
    ]
    degrees = np.arange(0, 361, 22.5)

    if res in ["l", 90]:
        return degrees[::4], labels[::4]
    elif res in ["m", 45]:
        return degrees[::2], labels[::2]
    elif res in ["h", 22.5]:
        return degrees, labels


def wind_profile_power_law(wind_speed_ref, z_ref, z=10, alpha=0.143):
    """
    Adjust a wind to a different height above ground with the power law.

    Parameters
    ----------
    wind_speed_ref : float or array-like
        The reference wind speed, wind u, or wind v (m/s) at height z_ref.
    z_ref : float or int
        The reference height of the given reference wind (m)
    z : float or int
        The height to adjust the wind. Default is 10 m.
    alpha : float or int, {'land', 'water'}
        The empirical alpha value for the power law relationship.
        Default is 0.143 (which is ~1/7), valid for neutral stability
        conditions over open land.
        - "land" is an alias for 0.143
        - "water" is an alias for 0.11

    References
    ----------

    - https://en.wikipedia.org/wiki/Wind_profile_power_law
    - https://doi.org/10.1175/1520-0450(1994)033%3C0757:DTPLWP%3E2.0.CO;2
    - https://github.com/ydeos/ydeos_aerodynamics/blob/8f42a4959f093f204228aff682ed40b0a9bd3a27/ydeos_aerodynamics/profiles.py

    """
    if alpha == "water":
        alpha = 0.11
    elif alpha == "land":
        alpha = 0.143

    wind_speed_z = wind_speed_ref * (z / z_ref) ** alpha
    return wind_speed_z


if __name__ == "__main__":

    # Examples
    u = np.array([1, 0, -5])
    v = np.array([-1, -2, 5])

    print("U component: ", u)
    print("V component: ", v)
    print("Wind Speed and Direction: ", uv_to_spddir(u, v))
    print("")

    print("Angle between vector 1 and 2: ", angle_between(u[0], v[0], u[1], v[1]))
    print("Angle between vector 2 and 3: ", angle_between(u[1], v[1], u[2], v[2]))
