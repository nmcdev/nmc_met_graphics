## Brian Blaylock
## February 3, 2021
## Updated September 18, 2021

"""
=============
Cartopy Tools
=============

General helpers for cartopy plots.

Does projection matter? YES!
(https://www.joaoleitao.com/different-world-map-projections/)

You've looked at maps with distortion that show Greenland the size of
South America. For the same reason, you should show data on appropriate
projection globes. For global plots, consider using Mollweide projetion
over Mercator or Robinson. From the website above,

    [Mollweide] sacrifices the precision of some of the angles and
    shapes, in exchange for a better representation of the planet's
    proportions when that is an important consideration.

    [Robinson] represented the continents more accurately than the
    Mercator Projection, the poles are highly distorted.

This may better help you interpret results. The Winkel Tripel Projection
may also be more appropriate than Robinson, but not yet supported by
Cartopy.

"""
import urllib.request
import warnings

import cartopy.crs as ccrs
import cartopy.feature as feature
import cartopy.io.img_tiles as cimgt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyproj
import requests
import xarray as xr
from cartopy.io import shapereader
from functools import partial
from shapely.ops import transform
from shapely.geometry import GeometryCollection, Point, Polygon, MultiPoint, shape

from nmc_met_graphics.blaylockbk.paint.standard2 import cm_dpt, cm_rh, cm_tmp, cm_wind
from nmc_met_graphics.blaylockbk.toolbox.stock import Path

try:
    from metpy.plots import USCOUNTIES
except Exception as e:
    # warnings.warn(f"{e} Without metpy, you cannot draw COUNTIES on the map.")
    pass
try:
    import geopandas
except Exception as e:
    # warnings.warn(
    #    f'{e} Without geopandas, you cannot subset some NaturalEarthFeatures shapefiles, like "Major Highways" from roads.'
    # )
    pass

pc = ccrs.PlateCarree()
pc._threshold = 0.01  # https://github.com/SciTools/cartopy/issues/8


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
    lon = (lon + 180) % 360 - 180
    return lon


# Map extent regions.
_extents = dict(
    NW=(-180, 0, 0, 90),
    SW=(-180, 0, -90, 0),
    NE=(0, 180, 0, 90),
    SE=(0, 180, -90, 0),
    CONUS=(-130, -60, 20, 55),
)

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


def get_ETOPO1(top="ice", coarsen=None, thin=None):
    """
    Return the ETOPO1 elevation and bathymetry DataArray.

    The ETOPO1 dataset is huge (446 MB). This function saves coarsened
    versions of the data for faster loading.

    Download the data from http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NGDC

    An alternatvie source is https://ngdc.noaa.gov/mgg/global/, but the
    Dataset may have a different structure.


    Parameters
    ----------
    top : {'bedrock', 'ice'}
        There are two types of ETOPO1 files, one that is the top of the
        ice layers, and another that is the top of the bedrock. This
        is necessary for Greenland and Antarctic ice sheets. I'm guessing
        that 99% of the time you will want the top of the ice sheets.
    thin : int
        Thin the Dataset by getting every nth element
    coarsen : int
        Coarsen the Dataset by taking the mean of the nxn box.
    """

    def _reporthook(a, b, c):
        """
        Print download progress in megabytes.

        Parameters
        ----------
        a : Chunk number
        b : Maximum chunk size
        c : Total size of the download
        """
        chunk_progress = a * b / c * 100
        total_size_MB = c / 1000000.0
        print(
            f"\r🚛💨  Download ETOPO1 {top} Progress: {chunk_progress:.2f}% of {total_size_MB:.1f} MB\r",
            end="",
        )

    if coarsen == 1:
        coarsen = None
    if thin == 1:
        thin = None
    assert not all([coarsen, thin]), "Both `coarsen` and `thin` cannot be None."

    # If the ETOPO1 data does not exists, then download it.
    # The coarsen method is slow, so save a copy to load.
    # The thin method is fast, so don't worry about saving a copy.
    src = f"http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NGDC/.ETOPO1/.z_{top}/data.nc"
    dst = Path(f"$HOME/.local/share/ETOPO1/ETOPO1_{top}.nc").expand()
    dst_coarsen = Path(
        f"$HOME/.local/share/ETOPO1/ETOPO1_{top}_coarsen-{coarsen}.nc"
    ).expand()

    if not dst.exists():
        # Download the full ETOPO1 dataset
        if not dst.parent.exists():
            dst.parent.mkdir(parents=True)
        urllib.request.urlretrieve(src, dst, _reporthook)
        print(f"{' ':70}", end="")

    if coarsen:
        if dst_coarsen.exists():
            ds = xr.open_dataset(dst_coarsen)
        else:
            ds = xr.open_dataset(dst)
            ds = ds.coarsen({"lon": coarsen, "lat": coarsen}, boundary="pad").mean()
            ds.to_netcdf(dst_coarsen)
    else:
        ds = xr.open_dataset(dst)
        if thin:
            ds = ds.thin(thin)

    return ds[f"z_{top}"]


class common_features:
    """
    Build a matplotlib/cartopy axes with common map elements.

    This class does about 95% of my Cartopy needs.

    Feature elements from https://www.naturalearthdata.com/features/

    TODO: Rename to CommonFeatures or EasyMap
    """

    def __init__(
        self,
        scale="110m",
        ax=None,
        crs=pc,
        *,
        figsize=None,
        dpi=None,
        dark=False,
        verbose=False,
        add_coastlines=True,
        facecolor=None,
        coastlines_kw={},
        **kwargs,
    ):
        """
        Initialize a Cartopy axes

        Add coastlines with this method. Use other methods to add
        other common features to the Cartopy axes.

        .. tip:: ``ax=None`` is a great way to initialize a new Cartopy axes.

        Methods
        -------
        .adjust_extent
        .center_extent
        .copy_extent

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

        add_coastlines : bool
            For convince, the coastlines are added to the axes by default.
            This can be turned off and instead controlled with the COASTLINES
            method.
        coastlines_kw : dict
            kwargs for the default COASTLINES method.

        figsize : tuple
            Set the figure size
        dpi : int
            Set the figure dpi

        Examples
        --------
        https://github.com/blaylockbk/Carpenter_Workshop/blob/main/notebooks/demo_cartopy_tools.ipynb

        >>> feat = common_features()
        >>> feat.OCEAN().STATES()
        >>> ax = feat.ax

        Alternatively,

        >>> ax = common_features().ax
        >>> feat = ax.common_features
        >>> feat.OCEAN().STATES()
        """
        self.scale = scale
        self.ax = ax
        self.crs = crs
        self.figsize = figsize
        self.dpi = dpi
        self.dark = dark
        self.verbose = verbose
        self.kwargs = kwargs

        self.ax = check_cartopy_axes(ax=self.ax, crs=self.crs, verbose=self.verbose)

        # In a round-about way, you can get this common_features object from the axes
        # >>> ax = common_features().ax
        # >>> ax.common_features.STATES()
        self.ax.common_features = self

        self.kwargs.setdefault("linewidth", 0.75)

        # NOTE: I don't use the 'setdefault' method here because it doesn't
        # work as expect when switching between dark and normal themes.
        # The defaults would be set the first time the function is called,
        # but the next time it is called and `dark=True` the defaults do not
        # reset. I don't know why this is the behavior.
        if self.dark:
            self.land = "#060613"  # dark (default)
            self.land1 = "#3f3f3f"  # lighter (alternative)
            self.water = "#0f2b38"
            # https://github.com/SciTools/cartopy/issues/880
            self.ax.set_facecolor(self.land)  # requires cartopy >= 0.18
            self.kwargs = {**{"edgecolor": ".5"}, **self.kwargs}
        else:
            self.land = "#efefdb"  # tan (default)
            self.land1 = "#dbdbdb"  # grey (alternative)
            self.water = "#97b6e1"
            self.kwargs = {**{"edgecolor": ".15"}, **self.kwargs}

        if facecolor:
            # Instead of applying both LAND and OCEAN,
            # it may be faster to just set the facecolor of land
            # and then only apply the OCEAN method.
            if facecolor.lower() == "land":
                self.ax.set_facecolor(self.land)
            elif facecolor.lower() == "land1":
                self.ax.set_facecolor(self.land1)
            elif facecolor.lower() == "water":
                self.ax.set_facecolor(self.water)
            else:
                self.ax.set_facecolor(facecolor)

        if add_coastlines:
            # Default map will automatically add COASTLINES
            self.COASTLINES(**coastlines_kw)

        if figsize is not None:
            plt.gcf().set_figwidth(self.figsize[0])
            plt.gcf().set_figheight(self.figsize[1])
        if dpi is not None:
            plt.gcf().set_dpi(self.dpi)

        # Add my custom methods
        self.ax.__class__.adjust_extent = _adjust_extent
        self.ax.__class__.center_extent = _center_extent
        self.ax.__class__.copy_extent = _copy_extent

    # Feature Elements
    def COASTLINES(self, **kwargs):
        kwargs.setdefault("zorder", 100)
        kwargs.setdefault("facecolor", "none")
        kwargs = {**self.kwargs, **kwargs}
        self.ax.add_feature(feature.COASTLINE.with_scale(self.scale), **kwargs)
        if self.verbose == "debug":
            print("🐛 COASTLINES:", kwargs)
        return self

    def BORDERS(self, **kwargs):
        """Borders between countries. *Excludes coastlines*"""
        kwargs.setdefault("linewidth", 0.5)
        kwargs = {**self.kwargs, **kwargs}
        self.ax.add_feature(feature.BORDERS.with_scale(self.scale), **kwargs)
        if self.verbose == "debug":
            print("🐛 BORDERS:", kwargs)
        return self

    def STATES(self, **kwargs):
        """US state borders. *Includes coastlines*"""
        kwargs.setdefault("alpha", 0.15)

        kwargs = {**self.kwargs, **kwargs}
        self.ax.add_feature(feature.STATES.with_scale(self.scale), **kwargs)
        if self.verbose == "debug":
            print("🐛 STATES:", kwargs)
        return self

    def COUNTIES(self, counties_scale="20m", **kwargs):
        """US counties. *Includes coastslines*"""
        _counties_scale = {"20m", "5m", "500k"}
        assert (
            counties_scale in _counties_scale
        ), f"counties_scale must be {_counties_scale}"
        kwargs.setdefault("linewidth", 0.33)
        kwargs.setdefault("alpha", 0.15)
        kwargs = {**self.kwargs, **kwargs}
        self.ax.add_feature(USCOUNTIES.with_scale(counties_scale), **kwargs)
        if self.verbose == "debug":
            print("🐛 COUNTIES:", kwargs)
        return self

    def OCEAN(self, **kwargs):
        """Color-filled ocean area"""
        kwargs.setdefault("edgecolor", "none")
        kwargs = {**self.kwargs, **kwargs}

        if self.dark:
            kwargs = {**{"facecolor": self.water}, **kwargs}

        self.ax.add_feature(feature.OCEAN.with_scale(self.scale), **kwargs)
        if self.verbose == "debug":
            print("🐛 OCEAN:", kwargs)
        return self

    def LAND(self, **kwargs):
        """Color-filled land area"""
        kwargs.setdefault("edgecolor", "none")
        kwargs.setdefault("linewidth", 0)

        if not self.dark:
            # If `dark=True`, the face_color is the land color,
            # and we don't need to draw it.
            kwargs = {**self.kwargs, **kwargs}
            self.ax.add_feature(feature.LAND.with_scale(self.scale), **kwargs)
            if self.verbose == "debug":
                print("🐛 LAND:", kwargs)
        return self

    def RIVERS(self, **kwargs):
        """Rivers"""
        kwargs.setdefault("linewidth", 0.3)
        kwargs = {**self.kwargs, **kwargs}

        if self.dark:
            kwargs = {**{"color": self.water}, **kwargs}
        else:
            kwargs = {**{"color": self.water}, **kwargs}

        self.ax.add_feature(feature.RIVERS.with_scale(self.scale), **kwargs)
        if self.verbose == "debug":
            print("🐛 RIVERS:", kwargs)
        return self

    def LAKES(self, **kwargs):
        """Color-filled lake area"""
        kwargs.setdefault("linewidth", 0)
        kwargs = {**self.kwargs, **kwargs}

        if self.dark:
            kwargs = {**{"facecolor": self.water}, **kwargs}
            kwargs = {**{"edgecolor": self.water}, **kwargs}
        else:
            kwargs = {**{"facecolor": feature.COLORS["water"]}, **kwargs}
            kwargs = {**{"edgecolor": feature.COLORS["water"]}, **kwargs}

        self.ax.add_feature(feature.LAKES.with_scale(self.scale), **kwargs)
        if self.verbose == "debug":
            print("🐛 LAKES:", kwargs)
        return self

    def TERRAIN(
        self,
        coarsen=30,
        *,
        top="ice",
        kind="pcolormesh",
        extent=None,
        **kwargs,
    ):
        """
        Plot terrain data from ETOPO1 dataset.

        Parameters
        ----------
        coarsen : int
            ETOPO1 data is a 1-minute arc dataset. This is huge.
            For global plots, you don't need this resolution, and can
            be happy with a 30-minute arc resolution (default).
        top : {"ice", "bedrock"}
            Top of the elevation model. "ice" is top of ice sheets in
            Greenland and Antarctica and "bedrock" is elevation of
            of ground under the ice.
        kind : {"contourf", "pcolormesh"}
            Plot data as a contour plot or pcolormesh
        extent :
            Trim the huge dataset to a specific region. (Variable cases).
            - by hemisphere {"NE", "SE", "NW", "SW"}
            - by region {"CONUS"}
            - by extent (len==4 tuple/list), e.g. `[-130, -100, 20, 50]`
            - by xarray.Dataset (must have coordinates 'lat' and 'lon')
              TODO: Currently does not allow domains that cross -180 lon.
        """
        da = get_ETOPO1(top=top, coarsen=coarsen)

        if extent:
            if isinstance(extent, (list, tuple)):
                assert (
                    len(extent) == 4
                ), "extent tuple must be len 4 (minLon, maxLon, minLat, maxLat)"
            elif isinstance(extent, str):
                assert (
                    extent in _extents
                ), f"extent string must be one of {_extents.keys()}"
                extent = _extents[extent]
            elif hasattr(extent, "coords"):
                # Get extent from lat/lon bounds in xarray DataSet
                extent = extent.rename({"latitude": "lat", "longitude": "lon"})
                extent["lon"] = _to_180(extent["lon"])
                extent = (
                    extent.lon.min().item(),
                    extent.lon.max().item(),
                    extent.lat.min().item(),
                    extent.lat.max().item(),
                )

            da = da.where(
                (da.lon >= extent[0])
                & (da.lon <= extent[1])
                & (da.lat >= extent[2])
                & (da.lat <= extent[3])
            )

        # Get "land" points (elevation is 0 and above, crude estimation)
        da = da.where(da >= 0)

        kwargs.setdefault("zorder", 0)
        kwargs.setdefault("cmap", "YlOrBr")
        kwargs.setdefault("levels", range(0, 8000, 500))
        kwargs.setdefault("vmin", 0)
        kwargs.setdefault("vmax", 8000)

        if kind == "contourf":
            _ = kwargs.pop("vmax")
            _ = kwargs.pop("vmin")
            self.ax.contourf(da.lon, da.lat, da, transform=pc, **kwargs)
        elif kind == "pcolormesh":
            _ = kwargs.pop("levels")
            self.ax.pcolormesh(da.lon, da.lat, da, transform=pc, **kwargs)

        return self

    def BATHYMETRY(
        self,
        coarsen=30,
        *,
        top="ice",
        kind="pcolormesh",
        extent=None,
        **kwargs,
    ):
        """
        Plot bathymetry data from ETOPO1 dataset.

        Parameters
        ----------
        coarsen : int
            ETOPO1 data is a 1-minute arc dataset. This is huge.
            For global plots, you don't need this resolution, and can
            be happy with a 30-minute arc resolution (default).
        top : {"ice", "bedrock"}
            Top of the elevation model. "ice" is top of ice sheets in
            Greenland and Antarctica and "bedrock" is elevation of
            of ground under the ice.
        kind : {"contourf", "pcolormesh"}
            Plot data as a contour plot or pcolormesh
        extent :
            Trim the huge dataset to a specific region. (Variable cases).
            - by hemisphere {"NE", "SE", "NW", "SW"}
            - by region {"CONUS"}
            - by extent (len==4 tuple/list), e.g. `[-130, -100, 20, 50]`
            - by xarray.Dataset (must have coordinates 'lat' and 'lon')
              TODO: Currently does not allow domains that cross -180 lon.
        """
        da = get_ETOPO1(top=top, coarsen=coarsen)

        if extent:
            if isinstance(extent, (list, tuple)):
                assert (
                    len(extent) == 4
                ), "extent tuple must be len 4 (minLon, maxLon, minLat, maxLat)"
            elif isinstance(extent, str):
                assert (
                    extent in _extents
                ), f"extent string must be one of {_extents.keys()}"
                extent = _extents[extent]
            elif hasattr(extent, "coords"):
                # Get extent from lat/lon bounds in xarray DataSet
                extent = extent.rename({"latitude": "lat", "longitude": "lon"})
                extent["lon"] = _to_180(extent["lon"])
                extent = (
                    extent.lon.min().item(),
                    extent.lon.max().item(),
                    extent.lat.min().item(),
                    extent.lat.max().item(),
                )

            da = da.where(
                (da.lon >= extent[0])
                & (da.lon <= extent[1])
                & (da.lat >= extent[2])
                & (da.lat <= extent[3])
            )

        # Get "water" points (elevation is 0 and above, crude estimation)
        da = da.where(da <= 0)

        kwargs.setdefault("zorder", 0)
        kwargs.setdefault("cmap", "Blues_r")
        kwargs.setdefault("levels", range(-10000, 1, 500))
        kwargs.setdefault("vmax", 0)
        kwargs.setdefault("vmin", -10000)

        if kind == "contourf":
            _ = kwargs.pop("vmax")
            _ = kwargs.pop("vmin")
            self.ax.contourf(da.lon, da.lat, da, transform=pc, **kwargs)
        elif kind == "pcolormesh":
            _ = kwargs.pop("levels")
            self.ax.pcolormesh(da.lon, da.lat, da, transform=pc, **kwargs)

        return self

    def PLAYAS(self, **kwargs):
        """Color-filled playa area"""
        kwargs.setdefault("linewidth", 0)
        kwargs = {**self.kwargs, **kwargs}

        if self.dark:
            kwargs = {**{"facecolor": "#4D311A73"}, **kwargs}
            kwargs = {**{"edgecolor": "none"}, **kwargs}
        else:
            kwargs = {**{"facecolor": "#FDA65473"}, **kwargs}
            kwargs = {**{"edgecolor": "none"}, **kwargs}

        playa = feature.NaturalEarthFeature("physical", "playas", "10m")
        self.ax.add_feature(playa, **kwargs)
        if self.verbose == "debug":
            print("🐛 PLAYAS:", kwargs)
        return self

    def TIMEZONE(self, **kwargs):
        """Timezone boundaries"""
        kwargs.setdefault("linewidth", 0.2)
        kwargs.setdefault("facecolor", "none")
        kwargs.setdefault("linestyle", ":")
        kwargs = {**self.kwargs, **kwargs}
        tz = feature.NaturalEarthFeature("cultural", "time_zones", "10m")
        self.ax.add_feature(tz, **kwargs)
        if self.verbose == "debug":
            print("🐛 TIMEZONE:", kwargs)
        return self

    def ROADS(self, road_types=None, **kwargs):
        """
        Major roads

        Parameters
        ----------
        road_types : None, str, list
            Filter the types of roads you want. The road type may be a single
            string or a list of road types.
            e.g. ['Major Highway', 'Secondary Highway']

        Of course, the shapefile has many other road classifiers for each
        road, like "level" (Federal, State, Interstate), road "name",
        "length_km", etc. Filters for each of these could be added if I
        need them later.

        """

        kwargs.setdefault("edgecolor", "#b30000")
        kwargs.setdefault("facecolor", "none")
        kwargs.setdefault("linewidth", 0.2)

        kwargs = {**self.kwargs, **kwargs}

        if road_types is None:
            # Plot all roadways
            roads = feature.NaturalEarthFeature("cultural", "roads", "10m", **kwargs)
            self.ax.add_feature(roads)
        else:
            # Specify the type of road to include in plot
            if isinstance(road_types, str):
                road_types = [road_types]
            shpfilename = shapereader.natural_earth("10m", "cultural", "roads")
            df = geopandas.read_file(shpfilename)
            _types = df["type"].unique()
            assert np.all(
                [i in _types for i in road_types]
            ), f"`ROADS_kwargs['type']` must be a list of these: {_types}"
            road_geom = df.loc[
                df["type"].apply(lambda x: x in road_types)
            ].geometry.values
            self.ax.add_geometries(road_geom, crs=pc, **kwargs)

        if self.verbose == "debug":
            print("🐛 ROADS:", kwargs)
        return self

    def PLACES(
        self,
        country="United States",
        rank=2,
        scatter=True,
        labels=True,
        label_kw={},
        scatter_kw={},
    ):
        """
        Points and labels for major cities

        Parameters
        ----------
        country : str
            Country to filter
        rank : int
            City rank threshold. Large cities have small rank. Small
            cities have large rank.
        scatter : bool
            Add scatter points
        labels : bool
            Add city name labels
        """
        scatter_kw.setdefault("marker", ".")
        label_kw.setdefault("fontweight", "bold")
        label_kw.setdefault("alpha", 0.5)

        places = shapereader.natural_earth("10m", "cultural", "populated_places")
        df = geopandas.read_file(places)

        df = df[df.SOV0NAME == country]
        df = df[df.SCALERANK <= rank]

        xs = df.geometry.values.x
        ys = df.geometry.values.y
        names = df.NAME

        if scatter:
            self.ax.scatter(xs, ys, transform=pc, **scatter_kw)

        if labels:
            for x, y, name in zip(xs, ys, names):
                self.ax.text(x, y, name, clip_on=True, **label_kw)
        return self

    # Tiled images
    def STAMEN(self, style="terrain-background", zoom=3, alpha=1):
        """
        Add Stamen map tiles to background.

        .. note::
            When adding a tile product to a map, it might be better to add
            it to the map first, then set the map extent, then make a separate
            call to ``common_features`` to add other features like roads and
            counties. The reason is because, if you add a tile map to

        Parameters
        ----------
        style : {'terrain-background', 'terrain', 'toner-background', 'toner', 'watercolor'}
            Type of image tile
        zoom : int
            Zoom level between 0 and 10.
        alpha : float
            Alpha value (transparency); a value between 0 and 1.
        """

        # Zoom can't be bigger than 11
        zoom = min(11,zoom)

        # Zoom can't be smaller than 0
        zoom = max(0, zoom)

        if self.verbose:
            print(
                "😎 Please use `ax.set_extent` before increasing Zoom level for faster plotting."
            )
        stamen_terrain = cimgt.Stamen(style)
        self.ax.add_image(stamen_terrain, zoom)

        if alpha < 1:
            # Need to manually put a white layer over the STAMEN terrain
            if self.dark:
                alpha_color = "k"
            else:
                alpha_color = "w"
            poly = self.ax.projection.domain
            self.ax.add_feature(
                feature.ShapelyFeature([poly], self.ax.projection),
                color=alpha_color,
                alpha=1 - alpha,
                zorder=1,
            )
        if self.verbose == "debug":
            print("🐛 STAMEN:", f"{style=}, {zoom=}, {alpha=}")

        return self

    def OSM(self, zoom=1, alpha=1):
        """
        Add Open Street Map tiles as background image.

        .. note::
            When adding a tile product to a map, it might be better to add
            it to the map first, then set the map extent, then make a separate
            call to ``common_features`` to add other features like roads and
            counties. The reason is because, if you add a tile map to

        Parameters
        ----------
        zoom : int
            Zoom level between 0 and ?.
        alpha : float
            Alpha value (transparency); a value between 0 and 1.
        """

        image = cimgt.OSM()
        self.ax.add_image(image, zoom)
        if alpha < 1:
            # Need to manually put a white layer over the STAMEN terrain
            if self.dark:
                alpha_color = "k"
            else:
                alpha_color = "w"
            poly = self.ax.projection.domain
            self.ax.add_feature(
                feature.ShapelyFeature([poly], self.ax.projection),
                color=alpha_color,
                alpha=1 - alpha,
                zorder=1,
            )
        if self.verbose == "debug":
            print("🐛 OSM:", f"{zoom=}, {alpha=}")

        return self

    def STOCK(self, **kwargs):
        """Show stock image background (suitable for full-globe images)"""
        self.ax.stock_img()
        return self

    # Other
    def DOMAIN(
        self,
        x,
        y=None,
        *,
        text=None,
        method="cutout",
        facealpha=0.25,
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
        """
        _method = {"fill", "cutout", "border"}
        assert method in _method, f"Method must be one of {_method}."

        ####################################################################
        # Determine how to handle output...xarray or numpy
        if isinstance(x, (xr.core.dataset.Dataset, xr.core.dataarray.DataArray)):
            if self.verbose:
                print("process input as xarray")

            if "latitude" in x.coords:
                x = x.rename({"latitude": "lat", "longitude": "lon"})
            LON = x.lon.data
            LAT = x.lat.data

        elif isinstance(x, np.ndarray):
            assert y is not None, "Please supply a value for x and y"
            if self.verbose:
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
        transform = self.ax.projection.transform_points(pc, x, y)

        # Remove any points that run off the projection map (i.e., point's value is `inf`).
        transform = transform[~np.isinf(transform).any(axis=1)]

        # These are the x and y points we need to create the Polygon for
        x = transform[:, 0]
        y = transform[:, 1]

        domain_polygon = Polygon(
            zip(x, y)
        )  # This is the boundary of the LAT/LON array supplied.
        global_polygon = (
            self.ax.projection.domain
        )  # This is the projection globe polygon
        cutout = global_polygon.difference(
            domain_polygon
        )  # This is the difference between the domain and glob polygon

        # Plot
        kwargs.setdefault("edgecolors", "k")
        kwargs.setdefault("linewidths", 1)
        if method == "fill":
            kwargs.setdefault("facecolor", (0, 0, 0, facealpha))
            artist = self.ax.add_feature(
                feature.ShapelyFeature([domain_polygon], self.ax.projection),
                **kwargs,
            )
        elif method == "cutout":
            kwargs.setdefault("facecolor", (0, 0, 0, facealpha))
            artist = self.ax.add_feature(
                feature.ShapelyFeature([cutout], self.ax.projection), **kwargs
            )
        elif method == "border":
            kwargs.setdefault("facecolor", "none")
            artist = self.ax.add_feature(
                feature.ShapelyFeature([domain_polygon.exterior], self.ax.projection),
                **kwargs,
            )

        if text:
            text_kwargs.setdefault("verticalalignment", "bottom")
            text_kwargs.setdefault("fontsize", 15)
            xx, yy = outside[0]
            self.ax.text(xx + 0.2, yy + 0.2, text, transform=pc, **text_kwargs)

        self.domain_polygon = domain_polygon
        self.domain_polygon_latlon = domain_polygon_latlon
        return self

    def set_extent(self, *args, **kwargs):
        self.ax.set_extent(*args, **kwargs)
        return self

    def center_extent(self, *args, **kwargs):
        self.ax.center_extent(*args, **kwargs)
        return self

    def adjust_extent(self, *args, **kwargs):
        self.ax.adjust_extent(*args, **kwargs)
        return self


########################################################################
# Useful tools


def point_radius_polygon(lon, lat, radius):
    """
    Create a polygon centered around a point with the specified radius.

    Uses the azimuthal equidistant projection to transform the radius.
    Source: https://gis.stackexchange.com/a/289923/123261

    Parameters
    ----------
    lon, lat : float
        Center location.
    radius : int/float
        Radius from center point, in kilometers

    Returns
    -------
    A shapely polygon (a circle with radius centered at lat/lon)

    """
    proj_wgs84 = pyproj.Proj("+proj=longlat +datum=WGS84")
    aeqd_proj = "+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0"
    project = partial(
        pyproj.transform, pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)), proj_wgs84
    )

    radius_meters = radius * 1000
    buf = Point(0, 0).buffer(radius_meters)  # distance in metres, converted to km
    points = transform(project, buf).exterior.coords[:]
    return Polygon(points)


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

    # PlateCarree is an earth-relative projection system
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


def state_polygon(state=None, country="USA", county=None, verbose=True):
    """
    Return a shapely polygon of US state boundaries or country borders.

    GeoJSON Data: https://raw.githubusercontent.com/johan/world.geo.json
    Helpful tip: https://medium.com/@pramukta/recipe-importing-geojson-into-shapely-da1edf79f41d

    Parameters
    ----------
    state : str
        Abbreviated state {'UT', 'CA', 'ID', etc.}
    country : str
        Abbreviated country {'USA', 'CAN', 'MEX', 'DEU', 'FRA', 'CHN', 'RUS', etc.}
    county : str
        Abbreviated county (for US states only)
    """
    if country == "USA":
        if county is None:
            URL = f"https://raw.githubusercontent.com/johan/world.geo.json/master/countries/USA/{state.upper()}.geo.json"
        else:
            URL = f"https://raw.githubusercontent.com/johan/world.geo.json/master/countries/USA/{state.upper()}/{county}.geo.json"
    else:
        URL = f"https://raw.githubusercontent.com/johan/world.geo.json/master/countries/{country.upper()}.geo.json"

    f = requests.get(URL)

    features = f.json()["features"]
    poly = GeometryCollection(
        [shape(feature["geometry"]).buffer(0) for feature in features]
    )

    if verbose:
        print(
            "Here's the Polygon; you may need to do `_.geoms[i]` to get Polygons from the shape."
        )

    return poly


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
        ds : xarray.Dataset or xarray.DataArray
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
