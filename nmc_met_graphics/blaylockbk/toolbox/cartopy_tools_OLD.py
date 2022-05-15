## Brian Blaylock
## February 3, 2021

"""
=============
Cartopy Tools
=============

General helpers for cartopy plots.

"""
import warnings

import cartopy.crs as ccrs
import cartopy.feature as feature
import cartopy.io.img_tiles as cimgt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import xarray as xr
from cartopy.io import shapereader
from paint.standard2 import cm_dpt, cm_rh, cm_tmp, cm_wind
from shapely.geometry import GeometryCollection, Polygon, shape

try:
    from metpy.plots import USCOUNTIES
except Exception as e:
    warnings.warn(f"{e} Without metpy, you cannot draw USCOUNTIES on the map.")
try:
    import geopandas
except Exception as e:
    warnings.warn(
        f'{e} Without geopandas, you cannot subset some NaturalEarthFeatures, like "Major Highways" from roads.'
    )

warnings.warn("Migrate to new `cartopy_tools` for latest updates and features.")

pc = ccrs.PlateCarree()
pc._threshold = 0.01  # https://github.com/SciTools/cartopy/issues/8

########################################################################
# Methods attached to axes created by `common_features`
def _adjust_extent(self, pad="auto", fraction=0.05, verbose=False):
    """
    Adjust the extent of an existing cartopy axes.

    This is useful to fine-tune the extent of a map after the extent
    was automatically made by a cartopy plotting method.

    Parameters
    ----------
    pad : float or dict
        If float, pad the map the same on all sides. Default is half a degree.
        If dict, specify pad on each side.
            - 'top' - padding north of center point
            - 'bottom'- padding south of center point
            - 'left' - padding east of center point
            - 'right' - padding west of center point
            - 'default' - padding when pad is unspecified
        Example: ``pad=dict(top=.5, default=.2)`` is the same as
                 ``pad=dict(top=.5, bottom=.2, left=.2, right=.2)``
        Note: Use negative numbers to remove padding.
    fraction : float
        When pad is 'auto', adjust the sides by a set fraction.
        The default 0.05 will give 5% padding on each side.
    """
    # Can't shrink the map extent by more than half in each direction, duh.
    assert fraction > -0.5, "Fraction must be larger than -0.5."

    crs = self.projection

    west, east, south, north = self.get_extent(crs=crs)

    if pad == "auto":
        pad = {}

    if isinstance(pad, dict):
        xmin, xmax = self.get_xlim()
        default_pad = (xmax - xmin) * fraction
        pad.setdefault("default", default_pad)
        for i in ["top", "bottom", "left", "right"]:
            pad.setdefault(i, pad["default"])
    else:
        pad = dict(top=pad, bottom=pad, left=pad, right=pad)

    ymin, ymax = crs.y_limits
    north = np.minimum(ymax, north + pad["top"])
    south = np.maximum(ymin, south - pad["bottom"])
    east = east + pad["right"]
    west = west - pad["left"]

    self.set_extent([west, east, south, north], crs=crs)

    if verbose:
        print(f"📐 Adjust Padding for {crs.__class__}: {pad}")

    return self.get_extent(crs=crs)


def _center_extent(
    self,
    lon=None,
    lat=None,
    city=None,
    state=None,
    *,
    pad="auto",
    verbose=False,
):
    """
    Change the map extent to be centered on a point and adjust padding.

    Parameters
    ----------
    lon, lat : float or None
        Latitude and Longitude of the center point **in degrees**.
        If None, must give argument for ``city``.
    city : str or None
        If string, center over city location.
    pad : float or dict
        Default is 'auto', which defaults to ~5 degree padding on each side.
        If float, pad the map the same on all sides (in crs units).
        If dict, specify pad on each side (in crs units).
            - 'top' - padding north of center point
            - 'bottom'- padding south of center point
            - 'left' - padding east of center point
            - 'right' - padding west of center point
            - 'default' - padding when pad is unspecified (default is 5)
        Example: ``pad=dict(top=5, default=10)`` is the same as
                 ``pad=dict(top=5, bottom=10, left=10, right=10)``
    """
    crs = self.projection

    if city is not None:
        places = shapereader.natural_earth("10m", "cultural", "populated_places")
        df = geopandas.read_file(places)
        point = df[df.NAME == city]
        assert len(point) > 0, f"🏙 Sorry, the city '{city}' was not found."
        lat = point.LATITUDE.item()
        lon = point.LONGITUDE.item()
    elif state is not None:
        state_center = state_polygon(state).centroid
        lon = state_center.x
        lat = state_center.y

    # Convert input lat/lon in degrees to the crs units
    lon, lat = crs.transform_point(lon, lat, src_crs=pc)

    if pad == "auto":
        pad = dict()

    if isinstance(pad, dict):
        # This default gives 5 degrees padding on each side
        # for a PlateCarree projection. Pad is similar for other
        # projections but not exactly 5 degrees.
        xmin, xmax = crs.x_limits
        default_pad = (xmax - xmin) / 72  # Because 360/72 = 5 degrees
        pad.setdefault("default", default_pad)
        for i in ["top", "bottom", "left", "right"]:
            pad.setdefault(i, pad["default"])
    else:
        pad = dict(top=pad, bottom=pad, left=pad, right=pad)

    ymin, ymax = crs.y_limits
    north = np.minimum(ymax, lat + pad["top"])
    south = np.maximum(ymin, lat - pad["bottom"])
    east = lon + pad["right"]
    west = lon - pad["left"]

    self.set_extent([west, east, south, north], crs=crs)

    if verbose:
        print(f"📐 Padding from point for {crs.__class__}: {pad}")

    return self.get_extent(crs=crs)


def _copy_extent(self, src_ax):
    """
    Copy the extent from an axes.

    .. note::
        Copying extent from different projections might not result in
        what you expect.

    Parameters
    ----------
    src_ax : cartopy axes
        A source cartopy axes to copy extent from onto the existing axes.

    Examples
    --------
    >>> # Copy extent of ax2 to ax1
    >>> ax1.copy_extent(ax2)

    """
    src_ax = check_cartopy_axes(src_ax)

    self.set_extent(src_ax.get_extent(crs=pc), crs=pc)

    return self.get_extent(crs=pc)


def _add_cbar(artist, ax=None, labels=None, **cbar_kwargs):
    """
    Add a colorbar for an artist to an axis.

    Parameters
    ----------
    artist : object from pcolormesh or with a cmap
        An pyplot object with a cmap.
    ax : pyplot.axesis the axes
        An axes. If none is provided, one will be created.
    labels : list
        A list of tick labels for the colorbar.

    """
    if ax is None:
        ax = plt.gca()

    cbar_kwargs.setdefault("orientation", "horizontal")
    cbar_kwargs.setdefault("pad", 0.02)
    cbar_kwargs.setdefault("fraction", 0.045)

    c = plt.colorbar(artist, ax=ax, **cbar_kwargs)

    if labels is not None:
        assert (
            "ticks" in cbar_kwargs
        ), "You gave me `labels`...Please supply the `ticks` kwarg, too."

        if cbar_kwargs["orientation"] == "horizontal":
            c.ax.set_xticklabels(labels, rotation=90)
        else:
            c.ax.set_yticklabels(labels)

    return c


@xr.register_dataset_accessor("xmap")
class xr_to_cartopy:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj
        self._center = None

    def plot_xr(
        self,
        variable=None,
        *,
        kind="pcolormesh",
        u="u10",
        v="v10",
        cbar=True,
        ax=None,
        cbar_kwargs={},
        verbose=True,
        **kwargs,
    ):
        """
        Plot vector magnitude (wind speed) on cartopy axes.

        The Dataset should only have 2 dimensions (x and y).

        Parameters
        ----------
        ds : xarrray.Dataset or xarray.DataArray
            A 2-dimension Dataset or DataArray.
        variable : {'spd', 'wspd', OTHER VARIABLE in `ds`}
            The variable from the Dataset `ds` to plot.

            If 'spd' or 'wspd', will use the u and v args to plot wind speed.
        """
        ds = self._obj

        assert len(ds.dims) == 2, "The Dataset should only have 2 dimensions"

        if variable is None and isinstance(ds, xr.Dataset):
            if len(ds) == 1:
                variable = list(ds)[0]
                if verbose:
                    print(
                        f"This Dataset has one variable, so I will assume you want to plot '{variable}'."
                    )
            else:
                raise TypeError(
                    f"Please give me a DataArray or assign `variable` as one of {set(ds)}."
                )

        if "crs" in ds.attrs:
            ax = check_cartopy_axes(ax, crs=ds.crs)
        else:
            ax = check_cartopy_axes(ax)

        if "latitude" in ds.coords:
            ds = ds.rename({"latitude": "lat", "longitude": "lon"})

        kwargs.setdefault("transform", pc)
        kwargs.setdefault("shading", "nearest")

        if hasattr(ds, "standard_name"):
            if "wind" in ds.standard_name:
                cm = cm_wind()
                kwargs = {**cm.cmap_kwargs, **kwargs}

        if variable is not None:
            if variable.lower() in ["spd", "wspd", "speed", "wind"]:
                if verbose:
                    print(f"Using '{u}' and '{v}' to compute wind speed.")
                cm = cm_wind()
                ds = np.sqrt(ds[u] ** 2 + ds[v] ** 2)
                kwargs = {**cm.cmap_kwargs, **kwargs}
                cbar_kwargs.setdefault("label", cm.label)
                ax.set_title("Wind", loc="left", fontweight="bold")
            else:
                ds = ds[variable]

        if hasattr(ds, "standard_name") and hasattr(ds, "units"):
            if ds.standard_name == "air_temperature" and ds.units == "K":
                cm = cm_tmp()
                kwargs = {**cm.cmap_kwargs, **kwargs}
                cbar_kwargs = {**dict(label=cm.label), **cbar_kwargs}
                ax.set_title(cm.name, loc="left", fontweight="bold")
                ds = ds.copy(deep=True) - 273.15
            elif ds.standard_name == "relative_humidity" and ds.units == "%":
                cm = cm_rh()
                kwargs = {**cm.cmap_kwargs, **kwargs}
                cbar_kwargs = {**dict(label=cm.label), **cbar_kwargs}
                ax.set_title(cm.name, loc="left", fontweight="bold")
        elif hasattr(ds, "long_name") and hasattr(ds, "units"):
            # Not all variables read by cfgrib have standard_name, like DPT
            if "dewpoint" in ds.long_name and ds.units == "K":
                kwargs = {**cm_dpt(), **kwargs}
                cbar_kwargs = {**dict(label="Dew Point Temperature (C)"), **cbar_kwargs}
                ax.set_title("Dew Point", loc="left", fontweight="bold")
                ds = ds.copy(deep=True) - 273.15

        if kind.lower() in "pcolormesh":
            artist = ax.pcolormesh(ds.lon, ds.lat, ds, **kwargs)
            if cbar:
                _add_cbar(artist, ax=ax, **cbar_kwargs)
        elif kind.lower() in "contour":
            kwargs.setdefault("linewidths", 1.7)
            if ds.GRIB_name == "Geopotential Height":
                kwargs.setdefault("levels", range(0, 12000, 60))
            artist = ax.contour(
                ds.lon, ds.lat, ds, **kwargs
            )  # Don't use inferred interval
            plt.clabel(artist, inline=1, fmt="%2.f")

        if hasattr(ds, "valid_time"):
            date_str = ds.valid_time.dt.strftime("%H:%M UTC %d %b %Y").item()
            if hasattr(ds, "step"):
                hours = ds.step.dt.seconds.item() / 3600 + ds.step.dt.days.item() * 24
                ax.set_title(f"F{hours:02.0f}  Valid: {date_str}", loc="right")
            else:
                ax.set_title(f"Valid:{date_str}", loc="right")

        return ax

    def plot_xr_vector(
        self,
        *,
        u="u10",
        v="v10",
        marker="barbs",
        thin="auto",
        ax=None,
        rotate_winds=True,
        verbose=True,
        **kwargs,
    ):
        """
        Plot vector barbs or quiver on cartopy axes.

        The Dataset should only have 2 dimensions (x and y).

        Parameters
        ----------
        ds : xarray.Dataset
        u, v : str
            variable names for the u and v vector components
        marker : {'barbs', 'quiver'}
            Add either barbs or quivers to the cartopy axes.
        thin : {int, 'auto'}
            If 'auto', then will only plot a maximum of 10x10 barbs.
        rotate_winds : bool
            Rotate wind vectors. Sometimes this can cause an issue if the
            data isn't exactly how it is suppoed to be, so
            you can turn it off, just not that the vectors will be off.

        """
        ds = self._obj

        assert len(ds.dims) == 2, "The Dataset should only have 2 dimensions"

        if "crs" in ds.attrs:
            ax = check_cartopy_axes(ax, crs=ds.crs)
        else:
            ax = check_cartopy_axes(ax)

        # Thin the data
        if thin == "auto":
            thin = int(np.max(ds[u].shape) / 10)
        ds = ds.thin(thin)

        ## Convert vectors from grid-relative to earth-relative.
        ## (Requires a cartopy.crs object in the `ds`)
        if "crs" in ds.attrs and rotate_winds:
            _, ds = grid_and_earth_relative_vectors(ds, u=u, v=v)
            if verbose:
                print(
                    "!! NOTICE: Vectors have been rotated from grid- to earth-relative"
                )
                print("!! NOTICE: because the xarray.Dataset has a crs attribute.")
                print(
                    "!! NOTICE: Vector rotation is only important if plotting vectors on "
                )
                print("!! NOTICE: a map other than the domain projection ")
        else:
            if verbose:
                warnings.warn(
                    "Vectors have not been rotated from grid- to earth-relative. Vectors will be wrong if plotted on a map different from the domain projection."
                )

        if "latitude" in ds.coords:
            ds = ds.rename({"latitude": "lat", "longitude": "lon"})

        kwargs.setdefault("transform", pc)

        if marker == "barbs":
            kwargs.setdefault("barb_increments", dict(half=2.5, full=5, flag=25))
            kwargs.setdefault("linewidth", 0.5)
            kwargs.setdefault("length", 5)
            artist = ax.barbs(
                ds.lon.data, ds.lat.data, ds[u].data, ds[v].data, **kwargs
            )
        elif marker == "quiver":
            kwargs.setdefault("scale", 100)
            kwargs.setdefault("units", "height")  # or us 'xy' units
            # kwargs.setdefault('width', .01)
            artist = ax.quiver(
                ds.lon.data, ds.lat.data, ds[u].data, ds[v].data, **kwargs
            )

        ax.set_title("Wind", loc="left", fontweight="bold")
        if "valid_time" in ds:
            date_str = ds.valid_time.dt.strftime("%H:%M UTC %d %b %Y").item()
            if "step" in ds:
                hours = ds.step.dt.seconds.item() / 3600 + ds.step.dt.days.item() * 24
                ax.set_title(f"F{hours:02.0f}  Valid: {date_str}", loc="right")
            else:
                ax.set_title(f"Valid:{date_str}", loc="right")

        return ax


########################################################################
# Main Functions
def check_cartopy_axes(ax=None, crs=pc, *, verbose=False):
    """
    Check if an axes is a cartopy axes, else create a new cartopy axes.

    Parameters
    ----------
    ax : {None, cartopy.mpl.geoaxes.GeoAxesSubplot}
        If None and plt.gca() is a cartopy axes, then use current axes.
        Else, create a new cartopy axes with specified crs.
    crs : cartopy.crs
        If the axes being checked is not a cartopy axes, then create one
        with this coordinate reference system (crs, aka "projection").
        Default is ccrs.PlateCarree()
    """
    # A cartopy axes should be of type `cartopy.mpl.geoaxes.GeoAxesSubplot`
    # One way to check that is to see if ax has the 'coastlines' attribute.
    if ax is None:
        if hasattr(plt.gca(), "coastlines"):
            if verbose:
                print("🌎 Using the current cartopy axes.")
            return plt.gca()
        else:
            if verbose:
                print(
                    f"🌎 The current axes is not a cartopy axes. Will create a new cartopy axes with crs={crs.__class__}."
                )
            # Close the axes we just opened in our test
            plt.close()
            # Create a new cartopy axes
            return plt.axes(projection=crs)
    else:
        if hasattr(ax, "coastlines"):
            if verbose:
                print("🌎 Thanks! It appears the axes you provided is a cartopy axes.")
            return ax
        else:
            raise TypeError("🌎 Sorry. The `ax` you gave me is not a cartopy axes.")


def common_features(
    scale="110m",
    ax=None,
    crs=pc,
    *,
    figsize=None,
    dpi=None,
    counties_scale="20m",
    dark=False,
    verbose=False,
    COASTLINES=True,
    COASTLINES_kwargs={},
    BORDERS=False,
    BORDERS_kwargs={},
    STATES=False,
    STATES_kwargs={},
    COUNTIES=False,
    COUNTIES_kwargs={},
    OCEAN=False,
    OCEAN_kwargs={},
    LAND=False,
    LAND_kwargs={},
    RIVERS=False,
    RIVERS_kwargs={},
    LAKES=False,
    LAKES_kwargs={},
    ROADS=False,
    ROADS_kwargs={},
    PLACES=False,
    PLACES_kwargs={},
    STAMEN=False,
    STAMEN_kwargs={},
    OSM=False,
    OSM_kwargs={},
    **kwargs,
):
    """
    Add common features to a cartopy axis.

    This completes about 95% of my cartopy needs.

    .. tip:: This is a great way to initialize a new cartopy axes.

    Parameters
    ----------
    scale : {'10m', '50m' 110m'}
        The cartopy feature's level of detail.
        .. note::  The ``'10m'`` scale for OCEAN and LAND takes a *long* time.
    ax : plot axes
        The axis to add the feature to.
        If None, it will create a new cartopy axes with ``crs``.
    crs : cartopy.crs
        Coordinate reference system (aka "projection") to create new map
        if no cartopy axes is given. Default is ccrs.PlateCarree.
    dark : bool
        If True, use alternative "dark theme" colors for land and water.

        .. figure:: _static/BB_maps/common_features-1.png
        .. figure:: _static/BB_maps/common_features-2.png

    counties_scale: {'20m', '5m', '500k'}
        Counties are plotted via MetPy and have different resolutions
        available than other features.
        -  20m = 20,000,000 resolution (Ok if you show a large area)
        -   5m =  5,000,000 resolution (provides good detail)
        - 500k =    500,000 resolution (high resolution, plots very slow)
    figsize : tuple
        Set the figure size
    dpi : int
        Set the figure dpi
    FEATURES : bool
        Toggle on various features. By default, only COASTLINES is
        turned on. Each feature has a cooresponding ``FEATURE_kwargs={}``
        dictionary to supply additional arguments to cartopy's add_feature
        method (e.g., change line color or width by feature type).

        ========== =========================================================
        FEATURE    Description
        ========== =========================================================
        COASTLINES Coastlines, boundary between land and ocean.
        BORDERS    Borders between countries. *Does not includes coast*.
        STATES     US state borders. Includes coast.
        COUNTIES   US Counties. Includes coast.
        OCEAN      Colored ocean area
        LAND       Colored land area
        RIVERS     Lines where rivers exist
        LAKES      Colored lake area
        ROADS      All major roads. Can break filter by road type.
        PLACES     Points and labels for major cities (filter by rank).
        ========== =========================================================

        ========== =========================================================
        MAP TILE   Description
        ========== =========================================================
        Stamen     Specify type and zoom level. http://maps.stamen.com/
                   Style: ``terrain-background``, ``terrain``,
                          ``toner-background``, ``toner``, `watercolor``
                   zoom: int [0-10]
                   alpha: [0-1]
                   alpha_color: an overlay color to put on top of map
                        use 'k' to darken background
                        use 'w' to lighten background
        OSM        Open Street Maps
                   zoom: int
        ========== =========================================================

    .. note::
        For ``ROADS_kwargs`` you may provide a key for 'type' to filter
        out the types of roads you want. The road type may be a single
        string or a list of road types. For example
        ``ROADS_kwargs=dict(type='Major Highway')`` or
        ``ROADS_kwargs=dict(type=['Secondary Highway', 'Major Highway'])

        Of course, the shapefile has many other road classifiers for each
        road, like "level" (Federal, State, Interstate), road "name",
        "length_km", etc. Filters for each of these could be added if I
        need them later.

    .. note::
        When adding a tile product to a map, it might be better to add
        it to the map first, then set the map extent, then make a separate
        call to ``common_features`` to add other features like roads and
        counties. The reason is because, if you add a tile map to

    Methods
    -------
    .adjust_extent
    .center_extent
    .copy_extent

    Examples
    --------
    https://github.com/blaylockbk/Carpenter_Workshop/blob/main/notebooks/demo_cartopy_tools.ipynb

    Returns
    -------
    The cartopy axes (obviously you don't need this if you gave an ax
    as an argument, but it is useful if you initialize a new map).

    """

    ax = check_cartopy_axes(ax=ax, crs=crs, verbose=verbose)

    if (LAND or OCEAN) and scale in ["10m"]:
        if verbose:
            warnings.warn(
                "🕖 OCEAN or LAND features at 10m may take a long time (3+ mins) to display on large maps."
            )

    kwargs.setdefault("linewidth", 0.75)

    COASTLINES_kwargs.setdefault("zorder", 100)
    COASTLINES_kwargs.setdefault("facecolor", "none")

    COUNTIES_kwargs.setdefault("linewidth", 0.5)

    STATES_kwargs.setdefault("alpha", 0.15)

    LAND_kwargs.setdefault("edgecolor", "none")
    LAND_kwargs.setdefault("linewidth", 0)

    OCEAN_kwargs.setdefault("edgecolor", "none")

    LAKES_kwargs.setdefault("linewidth", 0)

    # NOTE: I don't use the 'setdefault' method here because it doesn't
    # work as expect when switching between dark and normal themes.
    # The defaults would be set the first time the function is called,
    # but the next time it is called and `dark=True` the defaults do not
    # reset. I don't know why this is the behavior.
    if dark:
        land = "#060613"
        water = "#0f2b38"

        # https://github.com/SciTools/cartopy/issues/880
        ax.set_facecolor(land)  # requires cartopy >= 0.18

        kwargs = {**{"edgecolor": ".5"}, **kwargs}
        LAND_kwargs = {**{"facecolor": land}, **LAND_kwargs}
        OCEAN_kwargs = {**{"facecolor": water}, **OCEAN_kwargs}
        RIVERS_kwargs = {**{"edgecolor": water}, **RIVERS_kwargs}
        LAKES_kwargs = {**{"facecolor": water}, **LAKES_kwargs}

    else:
        kwargs = {**{"edgecolor": ".15"}, **kwargs}
        RIVERS_kwargs = {**{"edgecolor": feature.COLORS["water"]}, **RIVERS_kwargs}
        LAKES_kwargs = {**{"edgecolor": feature.COLORS["water"]}, **LAKES_kwargs}

    ##------------------------------------------------------------------
    ## Add each element to the plot
    ## When combining kwargs,
    ##  - kwargs is the main value
    ##  - FEATURE_kwargs is the overwrite for the feature
    ## For example:
    ##     {**kwargs, **FEATURE_kwargs}
    ## the kwargs are overwritten by FEATURE_kwargs
    ##------------------------------------------------------------------

    if COASTLINES:
        # ax.coastlines(scale, **kwargs)  # Nah, use the crs.feature instead
        ax.add_feature(
            feature.COASTLINE.with_scale(scale), **{**kwargs, **COASTLINES_kwargs}
        )
        if verbose == "debug":
            print("🐛 COASTLINES:", {**kwargs, **COASTLINES_kwargs})
    if BORDERS:
        ax.add_feature(
            feature.BORDERS.with_scale(scale), **{**kwargs, **BORDERS_kwargs}
        )
        if verbose == "debug":
            print("🐛 BORDERS:", {**kwargs, **BORDERS_kwargs})
    if STATES:
        ax.add_feature(feature.STATES.with_scale(scale), **{**kwargs, **STATES_kwargs})
        if verbose == "debug":
            print("🐛 STATES:", {**kwargs, **STATES_kwargs})
    if COUNTIES:
        _counties_scale = {"20m", "5m", "500k"}
        assert (
            counties_scale in _counties_scale
        ), f"counties_scale must be {_counties_scale}"
        ax.add_feature(
            USCOUNTIES.with_scale(counties_scale), **{**kwargs, **COUNTIES_kwargs}
        )
        if verbose == "debug":
            print("🐛 COUNTIES:", {**kwargs, **COUNTIES_kwargs})
    if OCEAN:
        ax.add_feature(feature.OCEAN.with_scale(scale), **{**kwargs, **OCEAN_kwargs})
        if verbose == "debug":
            print("🐛 OCEAN:", {**kwargs, **OCEAN_kwargs})
    if LAND and not dark:
        # If `dark=True`, the face_color is the land color.
        ax.add_feature(feature.LAND.with_scale(scale), **{**kwargs, **LAND_kwargs})
        if verbose == "debug":
            print("🐛 LAND:", {**kwargs, **LAND_kwargs})
    if RIVERS:
        ax.add_feature(feature.RIVERS.with_scale(scale), **{**kwargs, **RIVERS_kwargs})
        if verbose == "debug":
            print("🐛 RIVERS:", {**kwargs, **RIVERS_kwargs})
    if LAKES:
        ax.add_feature(feature.LAKES.with_scale(scale), **{**kwargs, **LAKES_kwargs})
        if verbose == "debug":
            print("🐛 LAKES:", {**kwargs, **LAKES_kwargs})
    if ROADS:
        ROADS_kwargs.setdefault("edgecolor", "#b30000")
        ROADS_kwargs.setdefault("facecolor", "none")
        ROADS_kwargs.setdefault("linewidth", 0.2)

        if "type" not in ROADS_kwargs:
            # Plot all roadways
            roads = feature.NaturalEarthFeature(
                "cultural", "roads", "10m", **ROADS_kwargs
            )
            ax.add_feature(roads)
        else:
            # Specify the type of road to include in plot
            road_types = ROADS_kwargs.pop("type")
            if isinstance(road_types, str):
                road_types = [road_types]
            shpfilename = shapereader.natural_earth("10m", "cultural", "roads")
            df = geopandas.read_file(shpfilename)
            _types = df["type"].unique()
            assert np.all(
                [i in _types for i in road_types]
            ), f"`ROADS_kwargs['type']` must be a list of these: {_types}"
            road_geos = df.loc[
                df["type"].apply(lambda x: x in road_types)
            ].geometry.values
            ax.add_geometries(road_geos, crs=pc, **ROADS_kwargs)
        if verbose == "debug":
            print("🐛 ROADS:", ROADS_kwargs)
    if PLACES:
        PLACES_kwargs.setdefault("country", "United States")
        PLACES_kwargs.setdefault("rank", 2)
        PLACES_kwargs.setdefault("scatter_kw", {"marker": "."})
        PLACES_kwargs.setdefault("label_kw", dict(fontweight="bold", alpha=0.5))

        country = PLACES_kwargs.pop("country")
        rank = PLACES_kwargs.pop("rank")
        scatter_kw = PLACES_kwargs.pop("scatter_kw")
        label_kw = PLACES_kwargs.pop("label_kw")

        places = shapereader.natural_earth("10m", "cultural", "populated_places")
        df = geopandas.read_file(places)

        df = df[df.SOV0NAME == country]
        df = df[df.SCALERANK <= rank]

        xs = df.geometry.values.x
        ys = df.geometry.values.y
        names = df.NAME

        if scatter_kw is not None:
            ax.scatter(xs, ys, transform=pc, **scatter_kw)

        if label_kw is not None:
            for x, y, name in zip(xs, ys, names):
                plt.text(x, y, name, clip_on=True, **label_kw)

    if STAMEN:
        if verbose:
            print(
                "😎 Please use `ax.set_extent` before increasing Zoom level for faster plotting."
            )
        STAMEN_kwargs.setdefault("style", "terrain-background")
        STAMEN_kwargs.setdefault("zoom", 3)

        stamen_terrain = cimgt.Stamen(STAMEN_kwargs["style"])
        ax.add_image(stamen_terrain, STAMEN_kwargs["zoom"])

        if "alpha" in STAMEN_kwargs:
            # Need to manually put a white layer over the STAMEN terrain
            if dark:
                STAMEN_kwargs.setdefault("alpha_color", "k")
            else:
                STAMEN_kwargs.setdefault("alpha_color", "w")
            poly = ax.projection.domain
            ax.add_feature(
                feature.ShapelyFeature([poly], ax.projection),
                color=STAMEN_kwargs["alpha_color"],
                alpha=1 - STAMEN_kwargs["alpha"],
                zorder=1,
            )
        if verbose == "debug":
            print("🐛 STAMEN:", STAMEN_kwargs)
    if OSM:
        image = cimgt.OSM()
        OSM_kwargs.setdefault("zoom", 1)
        ax.add_image(image, OSM_kwargs["zoom"])
        if "alpha" in OSM_kwargs:
            # Need to manually put a white layer over the STAMEN terrain
            if dark:
                OSM_kwargs.setdefault("alpha_color", "k")
            else:
                OSM_kwargs.setdefault("alpha_color", "w")
            poly = ax.projection.domain
            ax.add_feature(
                feature.ShapelyFeature([poly], ax.projection),
                color=OSM_kwargs["alpha_color"],
                alpha=1 - OSM_kwargs["alpha"],
                zorder=1,
            )
        if verbose == "debug":
            print("🐛 OSM:", OSM_kwargs)

    if figsize is not None:
        plt.gcf().set_figwidth(figsize[0])
        plt.gcf().set_figheight(figsize[1])
    if dpi is not None:
        plt.gcf().set_dpi(dpi)

    # Add my custom methods
    ax.__class__.adjust_extent = _adjust_extent
    ax.__class__.center_extent = _center_extent
    ax.__class__.copy_extent = _copy_extent

    return ax


def grid_and_earth_relative_vectors(
    srcData,
    *,
    srcProj=None,
    u="u10",
    v="v10",
):
    """
    Rotate vector quantities from grid-relative to earth-relative orientation.

    NOTE: When plotting vector data on a map, be aware of which projection
    system should be used. Cartopy's `transform_vectors` method should be
    used to rotate vectors between different coordinate systems.

    Often, model data provides latitude and longitude in decimal degrees
    and the u, and v component are oriented "grid-relative." This
    function will return two copies of the data with correctly
    rotated vectors:

    1. Latitude and longitude points in the *projection coordinates*
       with *grid-relative* vectors.
    2. Latitude and longitude in *decimal degrees* with *earth-relative*
       vectors.

    Parameters
    ----------
    srcData : xarray.Dataset
        xarray.Dataset that contains variables for
            'latitude' and 'longitude' in decimal degrees
            and u and v vector components. (Note: u and v variable
            names are specified by the `u` and `v` argument).
    srcProj : {None, cartopy.crs}
        The projection of the data (i.e, grid-relative projection).
        If None (default), this will attempt to determine the projection
        from the variable attributes if it was read in by the cfgrib
        engine for xarray.open_dataset.
        Else, you need to provide a projection coordinate system for
        the data you provide.
    u, v: str
        The name of the u and v component in the srcData Dataset.
        Default is 'u10' and 'v10' for 10 meter v-component wind.

    Returns
    -------
    Two copies of the provided xarray.Dataset
        grid_relative: the original dataset with the latitude and
                       longitude points transformed to map coordinates.
        earth_relative: the original dataset with u and v components
                        rotated from grid to earth relative values.
    The cooresponding coordinate projection system is also included.
    """
    if "lat" in srcData.coords:
        srcData = srcData.rename({"lat": "latitude", "lon": "longitude"})

    # Plate Carree is an earth-relative projection system
    # i.e, map gridlines align with the left-right/down-up directions.
    pc = ccrs.PlateCarree()

    # Determine the source projection. This works if the dataset was
    # opened with xarray.open_dataset('file.grib2', engine='cfgrib') and
    # the dataset is in lambert projection.
    if srcProj is None:
        var_attrs = srcData[u].attrs
        if var_attrs["GRIB_gridType"] == "lambert":
            lc_HRRR_kwargs = {
                "central_latitude": var_attrs["GRIB_LaDInDegrees"],
                "central_longitude": var_attrs["GRIB_LoVInDegrees"],
                "standard_parallels": (
                    var_attrs["GRIB_Latin1InDegrees"],
                    var_attrs["GRIB_Latin2InDegrees"],
                ),
            }
            srcProj = ccrs.LambertConformal(**lc_HRRR_kwargs)
        else:
            raise TypeError(
                f"I'm not programmed to decode the {var_attrs['GRIB_gridType']} grid type yet.\
            \nTry giving me a specific cartopy.projection object to `srcProj` kwarg."
            )

    # Transform Latitude and Longitude coordinate points (PlateCarree)
    # to the source projection coordinates. We need the lat/lon in the
    # projection coordinate space before we do the vector transform.
    srcProj_coords = srcProj.transform_points(
        pc, srcData.longitude.data, srcData.latitude.data
    )

    # Extract the X and Y coordinate arrays for the src projection.
    X = srcProj_coords[:, :, 0]
    Y = srcProj_coords[:, :, 1]

    # Transform the U and V vectors to the earth-relative orientation
    U_t, V_t = pc.transform_vectors(srcProj, X, Y, srcData[u].data, srcData[v].data)

    ####################################################################
    # Return two copies of the data (earth and grid relative)
    ####################################################################
    dims = srcData["latitude"].dims  # For HRRR data, this is ('y', 'x')

    # Grid-relative orientation:
    # The U and V values are the same as the data supplied, but return
    # the latitude and longitude values as map projection coordinate.
    grid_relative = srcData.copy(deep=True)
    grid_relative["latitude"] = (dims, Y)  # lat in the map coordinates
    grid_relative["longitude"] = (dims, X)  # lon in the map coordinates
    grid_relative[u] = (dims, srcData[u].data)
    grid_relative[v] = (dims, srcData[v].data)
    grid_relative.attrs["crs"] = srcProj
    grid_relative.attrs["vector direction"] = "grid relative"

    # Earth-relative orientation:
    # The latitude and longitude values are the same as the data
    # supplied (in decimal degrees), but return the rotated U and V
    # values expressed in earth-relative orientation.
    earth_relative = srcData.copy(deep=True)
    earth_relative[u] = (dims, U_t)
    earth_relative[v] = (dims, V_t)
    earth_relative.attrs["crs"] = pc
    earth_relative.attrs["vector direction"] = "earth relative"

    return grid_relative, earth_relative


########################################################################
# Useful tools
def domain_border(
    x,
    y=None,
    *,
    ax=None,
    text=None,
    method="cutout",
    verbose=False,
    facealpha=0.25,
    polygon_only=False,
    text_kwargs={},
    **kwargs,
):
    """
    Add a polygon of the domain boundary to a map.

    The border is drawn from the outside values of the latitude and
    longitude xarray coordinates or numpy array.
    Lat/lon values should be given as degrees.

    Parameters
    ----------
        x : xarray.Dataset or numpy.ndarray
            If xarray, then should contain 'latitude' and 'longitude' coordinate.
            If numpy, then 2D numpy array for longitude and `y` arg is required.
        y : numpy.ndarray
            Only required if x is a numpy array.
            A numpy array of latitude values.
        ax : cartopy axis
            The axis to add the border to.
            Default None and will get the current axis (will create one).
        text : str
            If not None, puts the string in the bottom left.
        method : {'fill', 'cutout', 'border'}
            Plot the domain as a filled area Polygon, a Cutout from the
            map, or as a simple border.
        facealpha : float between 0 and 1
            Since there isn't a "facealpha" attribute for plotting,
            this will be it.
        polygon_only : bool
            - True: Only return the polygons and don't plot on axes.

    Returns
    -------
    Adds a border around domain to the axis and returns the artist,
    a polygon in the crs coordinates and crs in lat/lon coordinates.
    """
    if hasattr(x, "crs"):
        ax = check_cartopy_axes(ax, crs=x.crs)
        if verbose:
            print(f"crs is {x.crs}")
    else:
        print("crs is not in the xarray.Dataset")
        ax = check_cartopy_axes(ax)

    _method = {"cutout", "fill", "border"}
    assert method in _method, f"Method must be one of {_method}."

    ####################################################################
    # Determine how to handle output...xarray or numpy
    if isinstance(x, (xr.core.dataset.Dataset, xr.core.dataarray.DataArray)):
        if verbose:
            print("process input as xarray")

        if "latitude" in x.coords:
            x = x.rename({"latitude": "lat", "longitude": "lon"})
        LON = x.lon.data
        LAT = x.lat.data

    elif isinstance(x, np.ndarray):
        assert y is not None, "Please supply a value for x and y"
        if verbose:
            print("process input as numpy array")
        LON = x
        LAT = y
    else:
        raise ValueError("Review your input")
    ####################################################################

    # Path of array outside border starting from the lower left corner
    # and going around the array counter-clockwise.
    outside = (
        list(zip(LON[0, :], LAT[0, :]))
        + list(zip(LON[:, -1], LAT[:, -1]))
        + list(zip(LON[-1, ::-1], LAT[-1, ::-1]))
        + list(zip(LON[::-1, 0], LAT[::-1, 0]))
    )
    outside = np.array(outside)

    ## Polygon in latlon coordinates
    ## -----------------------------
    x = outside[:, 0]
    y = outside[:, 1]
    domain_polygon_latlon = Polygon(zip(x, y))

    ## Polygon in projection coordinates
    ## ----------------------------------
    transform = ax.projection.transform_points(pc, x, y)

    # Remove any points that run off the projection map (i.e., point's value is `inf`).
    transform = transform[~np.isinf(transform).any(axis=1)]

    # These are the x and y points we need to create the Polygon for
    x = transform[:, 0]
    y = transform[:, 1]

    domain_polygon = Polygon(
        zip(x, y)
    )  # This is the boundary of the LAT/LON array supplied.
    global_polygon = ax.projection.domain  # This is the projection globe polygon
    cutout = global_polygon.difference(
        domain_polygon
    )  # This is the differencesbetween the domain and glob polygon

    if polygon_only:
        plt.close()
        return domain_polygon, domain_polygon_latlon
    else:
        # Plot
        kwargs.setdefault("edgecolors", "k")
        kwargs.setdefault("linewidths", 1)
        if method == "fill":
            kwargs.setdefault("facecolor", (0, 0, 0, facealpha))
            artist = ax.add_feature(
                feature.ShapelyFeature([domain_polygon], ax.projection), **kwargs
            )
        elif method == "cutout":
            kwargs.setdefault("facecolor", (0, 0, 0, facealpha))
            artist = ax.add_feature(
                feature.ShapelyFeature([cutout], ax.projection), **kwargs
            )
        elif method == "border":
            kwargs.setdefault("facecolor", "none")
            artist = ax.add_feature(
                feature.ShapelyFeature([domain_polygon.exterior], ax.projection),
                **kwargs,
            )

        if text:
            text_kwargs.setdefault("verticalalignment", "bottom")
            text_kwargs.setdefault("fontsize", 15)
            xx, yy = outside[0]
            ax.text(xx + 0.2, yy + 0.2, text, transform=pc, **text_kwargs)

        return artist, domain_polygon, domain_polygon_latlon


def state_polygon(state):
    """
    Return a shapely polygon of US state boundaries.

    GeoJSON Data: https://raw.githubusercontent.com/johan/world.geo.json
    Helpful tip: https://medium.com/@pramukta/recipe-importing-geojson-into-shapely-da1edf79f41d

    Parameters
    ----------
    state : str
        Abbreviated state
    """
    URL = (
        "https://raw.githubusercontent.com/johan/world.geo.json/master/countries/USA/%s.geo.json"
        % state.upper()
    )
    f = requests.get(URL)

    features = f.json()["features"]
    poly = GeometryCollection(
        [shape(feature["geometry"]).buffer(0) for feature in features]
    )
    return poly


########################################################################
# ⚰ Dead code. Do not use. This is dead code.
########################################################################

# OLD
def center_extent(
    lon,
    lat,
    *,
    ax=None,
    pad="auto",
    crs=pc,
    verbose=False,
):
    """
    Change the map extent to be centered on a point and adjust padding.

    Parameters
    ----------
    lon, lat : float
        Latitude and Longitude of the center point **in degrees**.
    ax : cartopy axes
        Default None will create a new PlateCarree cartopy.mpl.geoaxes.
    pad : float or dict
        Default is 'auto', which defaults to ~5 degree padding on each side.
        If float, pad the map the same on all sides (in crs units).
        If dict, specify pad on each side (in crs units).
            - 'top' - padding north of center point
            - 'bottom'- padding south of center point
            - 'left' - padding east of center point
            - 'right' - padding west of center point
            - 'default' - padding when pad is unspecified (default is 5)
        Example: ``pad=dict(top=5, default=10)`` is the same as
                 ``pad=dict(top=5, bottom=10, left=10, right=10)``
    crs : cartopy coordinate reference system
        Default is ccrs.PlateCarree()
    """
    warnings.warn(
        "OLD Use the ax.center_extent method added to the axes by common_features"
    )
    ax = check_cartopy_axes(ax, crs, verbose=verbose)

    # Convert input lat/lon in degrees to the crs units
    lon, lat = crs.transform_point(lon, lat, src_crs=pc)

    if pad == "auto":
        pad = dict()

    if isinstance(pad, dict):
        # This default gives 5 degrees padding on each side
        # for a PlateCarree projection. Pad is similar for other
        # projections but not exactly 5 degrees.
        xmin, xmax = crs.x_limits
        default_pad = (xmax - xmin) / 72  # Because 360/72 = 5 degrees
        pad.setdefault("default", default_pad)
        for i in ["top", "bottom", "left", "right"]:
            pad.setdefault(i, pad["default"])
    else:
        pad = dict(top=pad, bottom=pad, left=pad, right=pad)

    ymin, ymax = crs.y_limits
    north = np.minimum(ymax, lat + pad["top"])
    south = np.maximum(ymin, lat - pad["bottom"])
    east = lon + pad["right"]
    west = lon - pad["left"]

    ax.set_extent([west, east, south, north], crs=crs)

    if verbose:
        print(f"📐 Padding from point for {crs.__class__}: {pad}")

    return ax.get_extent(crs=crs)


# OLD
def adjust_extent(ax=None, pad="auto", fraction=0.05, verbose=False):
    """
    Adjust the extent of an existing cartopy axes.

    This is useful to fine-tune the extent of a map after the extent
    was automatically made by a cartopy plotting method.

    Parameters
    ----------
    ax : cartopy axes
    pad : float or dict
        If float, pad the map the same on all sides. Default is half a degree.
        If dict, specify pad on each side.
            - 'top' - padding north of center point
            - 'bottom'- padding south of center point
            - 'left' - padding east of center point
            - 'right' - padding west of center point
            - 'default' - padding when pad is unspecified
        Example: ``pad=dict(top=.5, default=.2)`` is the same as
                 ``pad=dict(top=.5, bottom=.2, left=.2, right=.2)``
        Note: Use negative numbers to remove padding.
    fraction : float
        When pad is 'auto', adjust the sides by a set fraction.
        The default 0.05 will give 5% padding on each side.
    """
    warnings.warn(
        "OLD Use the ax.center_extent method added to the axes by common_features"
    )
    # Can't shrink the map extent by more than half in each direction, duh.
    assert fraction > -0.5, "Fraction must be larger than -0.5."

    ax = check_cartopy_axes(ax)

    crs = ax.projection

    west, east, south, north = ax.get_extent(crs=crs)

    if pad == "auto":
        pad = {}

    if isinstance(pad, dict):
        xmin, xmax = ax.get_xlim()
        default_pad = (xmax - xmin) * fraction
        pad.setdefault("default", default_pad)
        for i in ["top", "bottom", "left", "right"]:
            pad.setdefault(i, pad["default"])
    else:
        pad = dict(top=pad, bottom=pad, left=pad, right=pad)

    ymin, ymax = crs.y_limits
    north = np.minimum(ymax, north + pad["top"])
    south = np.maximum(ymin, south - pad["bottom"])
    east = east + pad["right"]
    west = west - pad["left"]

    ax.set_extent([west, east, south, north], crs=crs)

    if verbose:
        print(f"📐 Adjust Padding for {crs.__class__}: {pad}")

    return ax.get_extent(crs=crs)


# OLD
def copy_extent(src_ax, dst_ax):
    """
    Copy the extent from an axes.

    .. note::
        Copying extent from different projections might not result in
        what you expect.

    Parameters
    ----------
    src_ax, dst_ax : cartopy axes
        A source cartopy axes to copy extent from onto the destination axes.
    """
    warnings.warn(
        "OLD Use the ax.copy_extent method added to the axes by common_features"
    )
    src_ax = check_cartopy_axes(src_ax)
    dst_ax = check_cartopy_axes(dst_ax)

    dst_ax.set_extent(src_ax.get_extent(crs=pc), crs=pc)

    return dst_ax.get_extent(crs=pc)
