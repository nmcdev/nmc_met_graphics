## Brian Blaylock
## November 22, 2019

"""
====================
Gridded Data Helpers
====================

Utilities for modifying gridded data

"""

import warnings

import numpy as np
import xarray as xr
from shapely.geometry import Polygon


def _infer_interval_breaks(coords):
    """Copied from `toolbox.plot_helpers`"""
    import toolbox.plot_helpers

    return toolbox.plot_helpers._infer_interval_breaks(coords)


def _to_180(lon):
    """
    Wrap longitude from degrees [0, 360] to degrees [-180, 180].

    An alternative method is
        lon[lon>180] -= 360

    Parameters
    ----------
    lon : array_like
        Longitude values
    """
    lon = np.array(lon)
    lon = (lon + 180) % 360 - 180
    return lon


def pluck_points(ds, points, names=None, dist_thresh=10_000, verbose=False):
    """
    Pluck values at point nearest a give list of latitudes and longitudes pairs.

    Uses a nearest neighbor approach to get the values. The general
    methodology is illustrated in this
    `GitHub Notebook <https://github.com/blaylockbk/pyBKB_v3/blob/master/demo/Nearest_lat-lon_Grid.ipynb>`_.

    Parameters
    ----------
    ds : xarray.Dataset
        The Dataset should include coordinates for both 'latitude' and
        'longitude'.
    points : tuple or list of tuples
        The longitude and latitude (lon, lat) coordinate pair (as a tuple)
        for the points you want to pluck from the gridded Dataset.
        A list of tuples may be given to return the values from multiple points.
    names : list
        A list of names for each point location (i.e., station name).
        None will not append any names. names should be the same
        length as points.
    dist_thresh: int or float
        The maximum distance (m) between a plucked point and a matched point.
        Default is 10,000 m. If the distance is larger than this, the point
        is disregarded.

    Returns
    -------
    The Dataset values at the points nearest the requested lat/lon points.
    """

    if len(points) > 8:
        warnings.warn(
            "If possible, use the herbie.tools.nearest_points method. It is *much* faster."
        )

    if "lat" in ds:
        ds = ds.rename(dict(lat="latitude", lon="longitude"))

    if isinstance(points, tuple):
        # If a tuple is give, turn into a one-item list.
        points = [points]

    if names is not None:
        assert len(points) == len(names), "`points` and `names` must be same length."

    # Find the index for the nearest points
    xs = []  # x index values
    ys = []  # y index values
    for point in points:
        assert (
            len(point) == 2
        ), "``points`` should be a tuple or list of tuples (lon, lat)"

        p_lon, p_lat = point

        # Force longitude values to range from -180 to 180 degrees.
        p_lon = _to_180(p_lon)
        ds["longitude"][:] = _to_180(ds.longitude)

        # Find absolute difference between requested point and the grid coordinates.
        abslat = np.abs(ds.latitude - p_lat)
        abslon = np.abs(ds.longitude - p_lon)

        # Create grid of the maximum values of the two absolute grids
        c = np.maximum(abslon, abslat)

        # Find location where lat/lon minimum absolute value intersects
        if ds.latitude.dims == ("y", "x"):
            y, x = np.where(c == np.min(c))
        elif ds.latitude.dims == ("x", "y"):
            x, y = np.where(c == np.min(c))
        else:
            raise ValueError(
                f"Sorry, I do not understand dimensions {ds.latitude.dims}. Expected ('y', 'x')"
            )

        xs.append(x[0])
        ys.append(y[0])

    # ===================================================================
    # Select Method 1:
    # This method works, but returns more data than you ask for.
    # It returns an NxN matrix where N is the number of points,
    # and matches each point with each point (not just the coordinate
    # pairs). The points you want will be along the diagonal.
    # I leave this here so I remember not to do this.
    #
    # ds = ds.isel(x=xs, y=ys)
    #
    # ===================================================================

    # ===================================================================
    # Select Method 2:
    # This is only *slightly* slower, but returns just the data at the
    # points you requested. Creates a new dimension, called 'point'
    ds = xr.concat([ds.isel(x=i, y=j) for i, j in zip(xs, ys)], dim="point")
    # ===================================================================

    # -------------------------------------------------------------------
    # 📐Approximate the Great Circle distance between matched point and
    # requested point.
    # Based on https://andrew.hedges.name/experiments/haversine/
    # -------------------------------------------------------------------
    lat1 = np.deg2rad([i[1] for i in points])
    lon1 = np.deg2rad([i[0] for i in points])

    lat2 = np.deg2rad(ds.latitude.data)
    lon2 = np.deg2rad(ds.longitude.data)

    R = 6373.0  # approximate radius of earth in km

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distance = R * c * 1000  # converted to meters

    # Add the distance values as a coordinate
    ds.coords["distance"] = ("point", distance)
    ds["distance"].attrs = dict(
        long_name="Distance between requested point and matched grid point", units="m"
    )

    # -------------------------------------------------------------------
    # -------------------------------------------------------------------

    # Add list of names as a coordinate
    if hasattr(names, "__len__"):
        # Assign the point dimension as the names.
        assert len(ds.point) == len(
            names
        ), f"`names` must be same length as `points` pairs."
        ds["point"] = names

    ## Print some info about each point:
    if verbose:
        p_lons = [i[0] for i in points]
        p_lats = [i[1] for i in points]
        g_lons = ds.longitude.data
        g_lats = ds.latitude.data
        distances = ds.distance.data
        p_names = ds.point.data
        zipped = zip(p_lons, p_lats, g_lons, g_lats, distances, p_names)
        for plon, plat, glon, glat, d, name in zipped:
            print(
                f"🔎 Matched requested point [{name}] ({plat:.3f}, {plon:.3f}) to grid point ({glat:.3f}, {glon:.3f}). Distance of {d/1000:,.2f} km."
            )
            if d > dist_thresh:
                print(f"   💀 Point [{name}] Failed distance threshold")

    ds.attrs["x_index"] = xs
    ds.attrs["y_index"] = ys

    # Drop points that do not meet the dist_thresh criteria
    failed = ds.distance > dist_thresh
    if np.sum(failed).data >= 1:
        warnings.warn(
            f" 💀 Dropped {np.sum(failed).data} point(s) that exceeded dist_thresh."
        )
        ds = ds.where(~failed, drop=True)

    return ds


def border(array, *, corner=0, direction="cw"):
    """
    Extract the values around the border of a 2d array.

    Default settings start from top left corner and move clockwise.
    Corners are only used once.

    This is handy to get the domain outline from arrays of latitude and
    longitude.

    .. figure:: _static/BB_utils/corners-border.png

    Parameters
    ----------
    array : array_like
        A 2d array
    corner : {0, 1, 2, 3}
        Specify the corner to start at.
        0 - start at top left corner (default)
        1 - start at top right corner
        2 - start at bottom right corner
        3 - start at bottom left corner
    direction : {'cw', 'ccw'}
        Specify the direction to walk around the array
        cw  - clockwise (default)
        ccw - counter-clockwise

    Returns
    -------
    border : ndarray
        Values around the border of `array`.

    Examples
    --------
    >>> x, y = np.meshgrid(range(1,6), range(5))
    >>> array=x*y
    >>> array[0,0]=999
    array([[999,   0,   0,   0,   0],
           [  1,   2,   3,   4,   5],
           [  2,   4,   6,   8,  10],
           [  3,   6,   9,  12,  15],
           [  4,   8,  12,  16,  20]])
    >>> border(array)
    array([999,   0,   0,   0,   0,   5,  10,  15,  20,  16,  12,   8,   4,
             3,   2,   1, 999])
    >> border(array, corner=2)
    array([ 20,  16,  12,   8,   4,   3,   2,   1, 999,   0,   0,   0,   0,
             5,  10,  15,  20])
    >>> border(array, direction='ccw')
    array([999,   1,   2,   3,   4,   8,  12,  16,  20,  15,  10,   5,   0,
             0,   0,   0, 999])
    >>> border(array, corner=2, direction='ccw')
    array([ 20,  15,  10,   5,   0,   0,   0,   0, 999,   1,   2,   3,   4,
             8,  12,  16,  20])
    """
    if corner > 0:
        # Rotate the array so we start on a different corner
        array = np.rot90(array, k=corner)
    if direction == "ccw":
        # Transpose the array so we march around counter-clockwise
        array = array.T

    border = []
    border += list(array[0, :-1])  # Top row (left to right), not the last element.
    border += list(
        array[:-1, -1]
    )  # Right column (top to bottom), not the last element.
    border += list(
        array[-1, :0:-1]
    )  # Bottom row (right to left), not the last element.
    border += list(array[::-1, 0])  # Left column (bottom to top), all elements element.
    # NOTE: in that last statement, we include the last element to close the path.

    return np.array(border)


def corners(array, *, corner=0, direction="cw"):
    """
    Get values at the four corners of a 2D array.

    Default settings start from top left corner and moves around the
    array clockwise. Corners are only used once.

    This is handy to get the domain corners from arrays of latitude and
    longitude. However, if you need the boundaries for a domain with
    a non-rectangular grid (e.g., lambert projection), you should
    use the ``border`` function instead.

    .. figure:: _static/BB_utils/corners-border.png

    Parameters
    ----------
    array : array_like
        A 2d array
    corner : {0, 1, 2, 3}
        Specify the corner to start at.
        0 - start at top left corner (default)
        1 - start at top right corner
        2 - start at bottom right corner
        3 - start at bottom left corner
    direction : {'cw', 'ccw'}
        Specify the direction to walk around the array
        cw  - clockwise (default)
        ccw - counter-clockwise

    Returns
    -------
    corners : numpy.ndarray
        Values at the corners of ``array``.

    Examples
    --------
    >>> a = np.array([[1,2],[3,4]])
    >>> corners(a)
    array([1, 2, 4, 3])
    >>> corners(a, direction='ccw')
    array([1, 3, 4, 2])
    >>> corners(a, corner=2, direction='ccw')
    array([4, 2, 1, 3])
    """
    if isinstance(array, xr.core.dataarray.DataArray):
        # Because indexing DataArrays behaves a bit different than numpy
        # arrays in this case, we convert the DataArray to a numpy array.
        array = array.data

    if corner > 0:
        # Rotate the array so we start on a different corner
        array = np.rot90(array, k=corner)

    if direction == "ccw":
        # Transpose the array so we march around counter-clockwise
        array = array.T

    return array[[0, 0, -1, -1], [0, -1, -1, 0]]


def border_polygon(ds, x="longitude", y="latitude"):
    """
    Return the boundary of a grid as a polygon for the specified coordinates.

    Parameters
    ----------
    ds : xarray.Dataset
        A Dataset that contains coordinates 'latitude' and 'longitude'.
    x, y : str
        Specify the x an y coordinates to use. You might want to change
        these to 'lat' and 'lon' if that is what your Dataset has.

    Returns
    -------
    Shapely Polygon geometry.
    """
    lons = border(ds[x])
    lats = border(ds[y])
    return Polygon(zip(lons, lats))


def corners_polygon(ds, x="longitude", y="latitude"):
    """
    Return the boundary of a grid as a polygon for the specified coordinates.

    Be careful to use this correctly. This function is appropriate if
    the grid is in rectangular lat/lon projection. If you have an irregular map
    projection (e.g., Lambert) the domain border will be incorrect, like
    this example showing the HRRR model domain.

    .. figure:: _static/BB_utils/border-corners-polygon.png

    Parameters
    ----------
    ds : xarray.Dataset
        A Dataset that contains coordinates 'latitude' and 'longitude'.
    x, y : str
        Specify the x an y coordinates to use. You might want to change
        these to 'lat' and 'lon' if that is what your Dataset has.

    Returns
    -------
    Shapely Polygon geometry.
    """
    lons = corners(ds[x])
    lats = corners(ds[y])
    return Polygon(zip(lons, lats))
