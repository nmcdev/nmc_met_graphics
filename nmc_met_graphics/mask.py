# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Masking grid with boundary line or shapefile.

Reference:
https://gist.github.com/perrette/a78f99b76aed54b6babf3597e0b331f8
https://ocefpaf.github.io/python4oceanographers/blog/2015/08/17/shapely_in_polygon/
"""

import os
import pkg_resources
import numpy as np
import matplotlib.path as mplp
import shapefile
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from cartopy.io import shapereader
from cartopy.mpl.patch import geos_to_path
from shapely.geometry import Point, Polygon
from shapely.ops import cascaded_union


def crsmask(ax, conf, crs, shpfile=None, region='China', 
            attribute_name='CNTRY_NAME', pathkw=None):
    """
    在cartopy中, 对选定的区域进行白化.
    refer to https://cloud.tencent.com/developer/article/1618341
    TODO: 如果Cartopy设置set_extent, 显示的图像不会剪裁外部等值线, 还未找到有效解决办法.

    Args:
        shpfile (string): 用于白化区域的shapefile文件名.
        region (string): shpfile中包含的区域名.
        ax (GeoAxes instance): cartopy的坐标轴实例
        crs (cartopy.crs): cartopy坐标投影
        conf (matplotlib): matplotlib的contour或contourf绘图返回值
        pathkw (dict, optional): PathPatch关键字参数. Defaults to None.

    Return:
        clipping path, matplotlib.patches.PathPatch
    """

    # get shape file
    if shpfile is None:
        shpfile = pkg_resources.resource_filename(
            'nmc_met_graphics', "resources/maps/country1.shp")
    
    # retrive region geometry
    reader = shapereader.Reader(shpfile)
    countries = reader.records()
    multipoly, = [country.geometry for country in countries
                    if country.attributes['CNTRY_NAME'] == region]
                        
    main_geom = sorted(multipoly.geoms, key=lambda geom: geom.area)[-1]
    path, = geos_to_path(main_geom)
    plate_carre_data_transform = crs._as_mpl_transform(ax)

    for collection in conf.collections:
        collection.set_clip_path(path, plate_carre_data_transform)
    
    # Draw the path of interest.
    path = PathPatch(path, transform = crs, **pathkw)
    
    return path


def contour_shp_clip(originfig, ax, m=None, shpfile=None,
                     region_index=3, region_name=None):
    """
    Mask out the unnecessary data outside the interest region
    on a Matplotlib-plotted output instance.
      http://bbs.06climate.com/forum.php?mod=viewthread&tid=42437&extra=page%3D1

    :param originfig: the Matplotlib contour plot instance
    :param ax: the Axes instance
    :param m: basemap instance, m=Basemap(...)
    :param shpfile: the shape file used for basemap
    :param region_index: the record index of region name.
        If don't know the region index, can explore with:
                           sf = shapefile.Reader(shpfile)
                           print(sf.shapeRecords()[0].record)
    :param region_name: the name of a region of on the basemap,
        outside the region the data is to be maskout

    :return: clip, the the masked-out or clipped matplotlib instance
    """

    # get shape file
    if shpfile is None:
        shpfile = pkg_resources.resource_filename(
            'nmc_met_graphics', "resources/maps/country1.shp")

    # get region name
    if region_name is None:
        region_name = ["China"]

    # check shape file
    if not os.path.isfile(shpfile):
        return None

    # read shape file data
    sf = shapefile.Reader(shpfile)

    # define vertices and codes
    vertices = []
    codes = []

    # loop every records
    for shape_rec in sf.shapeRecords():
        if shape_rec.record[region_index] in region_name:
            pts = shape_rec.shape.points
            prt = list(shape_rec.shape.parts) + [len(pts)]
            for i in range(len(prt) - 1):
                for j in range(prt[i], prt[i + 1]):
                    if m is not None:
                        vertices.append(m(pts[j][0], pts[j][1]))
                    else:
                        vertices.append((pts[j][0], pts[j][1]))
                codes += [Path.MOVETO]
                codes += [Path.LINETO] * (prt[i + 1] - prt[i] - 2)
                codes += [Path.CLOSEPOLY]
            clip = Path(vertices, codes)
            clip = PathPatch(clip, transform=ax.transData)

    # clip contour
    for contour in originfig.collections:
        contour.set_clip_path(clip)

    return clip


def outline_to_mask(line, x, y):
    """Create mask from outline contour

    Parameters
    ----------
    line: array-like (N, 2), not support multiple lines.
    x, y: 1-D grid coordinates (input for meshgrid)

    Returns
    -------
    mask : 2-D boolean array (True inside)

    Examples
    --------
    >>> from shapely.geometry import Point
    >>> poly = Point(0,0).buffer(1)
    >>> x = np.linspace(-5,5,100)
    >>> y = np.linspace(-5,5,100)
    >>> mask = outline_to_mask(poly.boundary, x, y)
    """

    mpath = mplp.Path(line)
    X, Y = np.meshgrid(x, y)
    points = np.array((X.flatten(), Y.flatten())).T
    mask = mpath.contains_points(points).reshape(X.shape)
    return mask


def _grid_bbox(x, y):
    dx = dy = 0
    return x[0] - dx / 2, x[-1] + dx / 2, y[0] - dy / 2, y[-1] + dy / 2


def _bbox_to_rect(bbox):
    l, r, b, t = bbox
    return Polygon([(l, b), (r, b), (r, t), (l, t)])


def shp_mask(shp, x, y, m=None):
    """Use recursive sub-division of space and shapely
    contains method to create a raster mask on a regular grid.

    Parameters
    ----------
    shp : shapely's Polygon or Polygons (or whatever with
          a "contains" method and intersects method)
    x, y : 1-D numpy arrays defining a regular grid
    m : mask to fill, optional (will be created otherwise)

    Returns
    -------
    m : boolean 2-D array, True inside shape.

    Examples
    --------
    >>> from shapely.geometry import Point
    >>> poly = Point(0,0).buffer(1)
    >>> x = np.linspace(-5,5,100)
    >>> y = np.linspace(-5,5,100)
    >>> mask = shp_mask(poly, x, y)
    """
    rect = _bbox_to_rect(_grid_bbox(x, y))

    if m is None:
        m = np.zeros((y.size, x.size), dtype=bool)

    if not shp.intersects(rect):
        m[:] = False

    elif shp.contains(rect):
        m[:] = True

    else:
        k, l = m.shape

        if k == 1 and l == 1:
            m[:] = shp.contains(Point(x[0], y[0]))

        elif k == 1:
            m[:, :l // 2] = shp_mask(shp, x[:l // 2], y, m[:, :l // 2])
            m[:, l // 2:] = shp_mask(shp, x[l // 2:], y, m[:, l // 2:])

        elif l == 1:
            m[:k // 2] = shp_mask(shp, x, y[:k // 2], m[:k // 2])
            m[k // 2:] = shp_mask(shp, x, y[k // 2:], m[k // 2:])

        else:
            m[:k // 2, :l // 2] = shp_mask(
                shp, x[:l // 2], y[:k // 2], m[:k // 2, :l // 2])
            m[:k // 2, l // 2:] = shp_mask(
                shp, x[l // 2:], y[:k // 2], m[:k // 2, l // 2:])
            m[k // 2:, :l // 2] = shp_mask(
                shp, x[:l // 2], y[k // 2:], m[k // 2:, :l // 2])
            m[k // 2:, l // 2:] = shp_mask(
                shp, x[l // 2:], y[k // 2:], m[k // 2:, l // 2:])

    return m


def grid_mask_china(lon, lat):
    """
    Getting masked grid in China.

    :param lon: grid longitude coordinates.
    :param lat: grid latitude coordinates.
    :return: boolean 2-D array, True inside shape.


    >>> lon = np.linspace(0, 359, 360)
    >>> lat = np.linspace(-90, 90 ,181)
    >>> mask = grid_mask_china(lon, lat)
    """

    # read china boundary from shape file
    shp = shapereader.Reader(pkg_resources.resource_filename(
        'nmc_met_graphics', "resources/maps/bou1_4p.shp"))

    # convert to polygons
    geoms = shp.geometries()
    polygons = cascaded_union(list(geoms))

    # return mask grid
    return shp_mask(polygons, lon, lat)

