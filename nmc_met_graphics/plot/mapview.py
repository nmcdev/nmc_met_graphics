# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
定义地图底图.
"""

import os
import pkg_resources
from datetime import datetime, timedelta
import numpy as np
from numpy.lib.arraysetops import isin
from numpy.core.fromnumeric import ndim
import scipy.ndimage as ndimage
import pandas as pd
import xarray as xr
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from matplotlib.path import Path
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, PathPatch
from matplotlib.font_manager import FontProperties
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.transforms import offset_copy
from mpl_toolkits.axes_grid1 import make_axes_locatable

import shapefile
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.img_tiles as cimgt
from cartopy.io.shapereader import Reader
from cartopy.mpl.patch import geos_to_path
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

from nmc_met_io.util import get_sub_grid
from nmc_met_graphics.util import get_map_region
import nmc_met_graphics.cmap as nmgcmap


def add_china_map_2basemap(mp, ax, name='province', facecolor='none',
                           edgecolor='c', lw=2, **kwargs):
    """
    Add china province boundary to basemap instance.

    :param mp: basemap instance.
    :param ax: matplotlib axes instance.
    :param name: map name.
    :param facecolor: fill color, default is none.
    :param edgecolor: edge color.
    :param lw: line width.
    :param kwargs: keywords passing to Polygon.
    :return: None.
    """

    # map name
    names = {'nation': "bou1_4p", 'province': "bou2_4p",
             'county': "BOUNT_poly", 'river': "hyd1_4p",
             'river_high': "hyd2_4p"}

    # get shape file and information
    shpfile = pkg_resources.resource_filename(
        'nmc_met_graphics', "resources/maps/"+names[name])
    _ = mp.readshapefile(shpfile, 'states', drawbounds=True)

    for _, shp in zip(mp.states_info, mp.states):
        poly = Polygon(
            shp, facecolor=facecolor, edgecolor=edgecolor, lw=lw, **kwargs)
        ax.add_patch(poly)


def add_china_map_2cartopy(ax, name='province', facecolor='none',
                           edgecolor='c', lw=2, **kwargs):
    """
    Draw china boundary on cartopy map.

    :param ax: matplotlib axes instance.
    :param name: map name.
    :param facecolor: fill color, default is none.
    :param edgecolor: edge color.
    :param lw: line width.
    :return: None
    """

    # map name
    names = {'nation': "bou1_4p", 'province': "bou2_4p",
             'county': "BOUNT_poly", 'river': "hyd1_4l",
             'river_high': "hyd2_4l"}

    # get shape filename
    shpfile = pkg_resources.resource_filename(
        'nmc_met_graphics', "resources/maps/" + names[name] + ".shp")

    # add map
    ax.add_geometries(
        Reader(shpfile).geometries(), ccrs.PlateCarree(),
        facecolor=facecolor, edgecolor=edgecolor, lw=lw, **kwargs)


def label_fmt(x):
    """
    This custom formatter removes trailing zeros, e.g. "1.0" becomes "1", and
    then adds a percent sign.
    """
    s = f"{x:.1f}"
    if s.endswith("0"):
        s = f"{x:.0f}"
    return rf"{s}" if plt.rcParams["text.usetex"] else f"{s}"


class BaseMap():
    
    def __init__(self, projection='PlateCarree', ax=None, res='50m', **kwargs):
        """
        Initialize a Map instance with a passed Cartopy projection which this object acts
        as a wrapper for.

        https://github.com/tomerburg/Map/blob/master/Map/__init__.py
        
        Parameters:
        ----------------------
        projection
            String representing the cartopy map projection.
        ax
            Axis on which to draw on. Default is None.
        res
            String representing the default geography boundary resolution ("110m", "50m", and "10m").
            Default resolution is moderate '50m'. This can also be changed individually for each function
            that plots boundaries.
        **kwargs
            Additional arguments that are passed to those associated with projection.
            
        Returns:
        ----------------------
        Instance of a Map object

        Examples:

        from nmc_met_graphics.plot.china_map import BaseMap
        m = BaseMap(projection='PlateCarree',central_longitude=110.0,res='10m')
        plt.figure(figsize=(14,12))
        m.ax = plt.axes(projection=m.proj)
        m.set_extent([115, 116, 39, 40])
        m.tianditu(scale=12, map_type='Satellite')
        m.drawcoastlines(linewidth=1.0)
        m.drawstates(linewidth=1.0,color='gray')
        m.drawrivers()
        """
        
        self.proj = getattr(ccrs, projection)(**kwargs)
        self.ax = ax
        self.res = res
        self.extent = None

    def _check_ax(self):
        """
        Adapted from Basemap - checks to see if an axis is specified, if not, returns plt.gca().
        """
        
        if self.ax is None:
            ax = plt.gca(projection=self.proj)
        else:
            ax = self.ax
            
        return ax
        
    def check_for_digits(self,text):
        """
        Checks if a string contains digits.
        
        Parameters:
        ----------------------
        text
            String to check for digits
            
        Returns:
        ----------------------
        Boolean, True if string contains digits, otherwise False
        """
        
        check = False
        for i in text:
            if i.isdigit(): check = True
        return check
        
    def check_res(self,res,counties=False):
        """
        Checks if a resolution string contains digits. If yes, then that value is returned
        and is passed into the cartopy "with_scale()" argument. If it's solely a string
        representing the type of resolution ('l','m','h'), then that value is converted to
        a resolution with digits depending on the type of boundary being plotted.
        
        Parameters:
        ----------------------
        res
            String representing the passed resolution
            
        Returns:
        ----------------------
        String representing the converted resolution
        """
        
        #If resolution contains digits (e.g., '50m'), assumed to be valid input and simply returned
        if self.check_for_digits(res) == True:
            return res
        
        #Otherwise, attach numerical values to low, medium and high resolutions
        else:
            #Use cartopy's available options for everything but counties
            if counties == False:
                if res == 'l':
                    return '110m'
                elif res == 'h':
                    return '10m'
                else:
                    return '50m'
            #Use MetPy's available options for county resolutions
            else:
                if res == 'l':
                    return '20m'
                elif res == 'h':
                    return '500k'
                else:
                    return '5m'

    def set_extent(self, region='中国陆地', ax=None):
        """
        设置地图范围.

        Args:
            region (str, optional): [description]. Defaults to '中国陆地'.
        """

        #Get current axes if not specified
        ax = ax or self._check_ax()

        #Set map extend
        self.extent = get_map_region(region)
        ax.set_extent(self.extent, crs=ccrs.PlateCarree())
    
    def drawcoastlines(self,linewidths=1.2,linestyle='solid',
                       color='k',res=None,ax=None,**kwargs):
        """
        Draws coastlines similarly to Basemap's m.drawcoastlines() function.
        
        Parameters:
        ----------------------
        linewidths
            Line width (default is 1.2)
        linestyle
            Line style to plot (default is solid)
        color
            Color of line (default is black)
        res
            Resolution of coastline. Can be a character ('l','m','h') or one of cartopy's available
            resolutions ('110m','50m','10m'). If none is specified, then the default resolution specified
            when creating an instance of Map is used.
        ax
            Axes instance, if not None then overrides the default axes instance.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Error check resolution
        if res is None: res = self.res
        res = self.check_res(res)
        
        #Draw coastlines
        coastlines = ax.add_feature(
            cfeature.COASTLINE.with_scale(res),linewidths=linewidths,
            linestyle=linestyle,edgecolor=color,**kwargs)
        
        #Return value
        return coastlines
    
    def drawcountries(self,linewidths=1.2,linestyle='solid',color='k',
                      res=None,ax=None,**kwargs):
        """
        Draws country borders similarly to Basemap's m.drawcountries() function.
        
        Parameters:
        ----------------------
        linewidths
            Line width (default is 1.2)
        linestyle
            Line style to plot (default is solid)
        color
            Color of line (default is black)
        res
            Resolution of country borders. Can be a character ('l','m','h') or one of cartopy's available
            resolutions ('110m','50m','10m'). If none is specified, then the default resolution specified
            when creating an instance of Map is used.
        ax
            Axes instance, if not None then overrides the default axes instance.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Error check resolution
        if res is None: res = self.res
        res = self.check_res(res)
        
        #Draw coastlines
        countries = ax.add_feature(
            cfeature.BORDERS.with_scale(res),linewidths=linewidths,
            linestyle=linestyle,edgecolor=color,**kwargs)
        
        #Return value
        return countries

    def drawnation(self,linewidths=1.0,linestyle='solid',color='k',
                   facecolor='none',ax=None,**kwargs):
        """
        Draws china nation borders.
        
        Parameters:
        ----------------------
        linewidths
            Line width (default is 0.7)
        linestyle
            Line style to plot (default is solid)
        color
            Color of line (default is black)
        facecolor
            Color of filled (default is none).
        ax
            Axes instance, if not None then overrides the default axes instance.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        # get shape filename
        shpfile = pkg_resources.resource_filename(
            'nmc_met_graphics', "resources/maps/bou1_4p.shp")

        # add map
        states = ax.add_geometries(
            Reader(shpfile).geometries(), ccrs.PlateCarree(),
            linewidths=linewidths, linestyle=linestyle, 
            edgecolor=color, facecolor=facecolor, **kwargs)

        #Return value
        return states
    
    def drawstates(self,linewidths=0.7,linestyle='solid',color='k',
                   facecolor='none',ax=None,**kwargs):
        """
        Draws state borders similarly to Basemap's m.drawstates() function.
        
        Parameters:
        ----------------------
        linewidths
            Line width (default is 0.7)
        linestyle
            Line style to plot (default is solid)
        color
            Color of line (default is black)
        facecolor
            Color of filled (default is none).
        ax
            Axes instance, if not None then overrides the default axes instance.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        # get shape filename
        shpfile = pkg_resources.resource_filename(
            'nmc_met_graphics', "resources/maps/bou2_4p.shp")

        # add map
        states = ax.add_geometries(
            Reader(shpfile).geometries(), ccrs.PlateCarree(),
            linewidths=linewidths, linestyle=linestyle, 
            edgecolor=color, facecolor=facecolor, **kwargs)

        #Return value
        return states

    def drawcounties(self,linewidths=0.7,linestyle='solid',
                     color='k',facecolor='none',ax=None,**kwargs):
        """
        Draws counties borders similarly to Basemap's m.drawcounties() function.
        
        Parameters:
        ----------------------
        linewidths
            Line width (default is 0.7)
        linestyle
            Line style to plot (default is solid)
        color
            Color of line (default is black)
        facecolor
            Color of filled (default is none).
        ax
            Axes instance, if not None then overrides the default axes instance.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        # get shape filename
        shpfile = pkg_resources.resource_filename(
            'nmc_met_graphics', "resources/maps/BOUNT_poly.shp")

        # add map
        counties = ax.add_geometries(
            Reader(shpfile).geometries(), ccrs.PlateCarree(),
            linewidths=linewidths, linestyle=linestyle, 
            edgecolor=color, facecolor=facecolor, **kwargs)

        #Return value
        return counties

    def drawrivers(self,linewidths=0.8,linestyle='solid',color='blue',
                   facecolor='none',ax=None,**kwargs):
        """
        Draws counties borders similarly to Basemap's m.drawcounties() function.
        
        Parameters:
        ----------------------
        linewidths
            Line width (default is 0.7)
        linestyle
            Line style to plot (default is solid)
        color
            Color of line (default is black)
        facecolor
            Color of filled (default is none).
        ax
            Axes instance, if not None then overrides the default axes instance.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        # get shape filename
        shpfile = pkg_resources.resource_filename(
            'nmc_met_graphics', "resources/maps/hyd1_4l.shp")

        # add map
        counties = ax.add_geometries(
            Reader(shpfile).geometries(), ccrs.PlateCarree(),
            linewidths=linewidths, linestyle=linestyle, 
            edgecolor=color, facecolor=facecolor, **kwargs)

        #Return value
        return counties

    def drawbasemap(self, ax=None, res=None, county=False, 
                    linewidths=1.0, style='tburg'):
        """
        绘制默认的地图背景, 参照http://arctic.som.ou.edu/tburg/products/的产品样式.
        """

        #Get current axes if not specified
        ax = ax or self._check_ax()

        #Error check resolution
        if res is None: res = self.res
        res = self.check_res(res)

        #Draw background
        if style.lower() == 'tburg':
            # features
            ax.add_feature(cfeature.OCEAN.with_scale(res),facecolor='#edfbff',edgecolor=None)
            ax.add_feature(cfeature.LAKES.with_scale(res),facecolor='#edfbff',edgecolor=None)
            ax.add_feature(cfeature.LAND.with_scale(res),facecolor='#fbf5ea',edgecolor='gray',
                           linewidths=0.3*linewidths)
            # map bounaries
            self.drawnation(linewidths=2.0*linewidths, color='#694322')
            self.drawstates(linewidths=0.6*linewidths, color="#694322")
            if county:
                self.drawcounties(linewidths=0.3*linewidths, color='gray')
            self.drawrivers(linewidths=1.2*linewidths, color="#6fb0f8")
            self.ax.spines['geo'].set_linewidth(3)
            
        elif style.lower() == 'white':
            self.drawnation(linewidths=3.0*linewidths, color='black')
            self.drawstates(linewidths=3.0*linewidths, color="black")
            self.drawcounties(linewidths=0.4*linewidths, color='gray')
            self.drawrivers(linewidths=1.0*linewidths, color="blue")
            self.ax.spines['geo'].set_linewidth(4*linewidths)
        else:
            print('The {} style is not supported.'.format(style))

    def tianditu(self, ax=None, scale=5, map_type='VECTOR', token=None):
        """
        增加天地图作为地图背景.
        http://lbs.tianditu.gov.cn/server/MapService.html

        Parameters:
        ----------------------
        ax
            Axes instance, if not None then overrides the default axes instance.
        scale
            Map scale, large value for detail map.
        token
            Tianditu api token, if not given, default token will be used.
        type
            map type, 'VECTOR', 'TERAIN', or 'SATELLITE'.
        """

        #Get current axes if not specified
        ax = ax or self._check_ax()

        #Check token
        if token is None:
            # token =  CONFIG.CONFIG['TIANDITU']['token']
            token = '4267820f43926eaf808d61dc07269beb'

        #Create image tile URL
        map_types = {'VECTOR':'vec_w', 'TERAIN':'ter_w', 'SATELLITE':'img_w'}
        map_type = map_types.get(map_type.upper(), 'VECTOR')
        url = "http://t3.tianditu.gov.cn/DataServer?T=%s&x={x}&y={y}&l={z}&tk=%s" % (map_type, token)

        # add image
        image = cimgt.GoogleTiles(url=url)
        return ax.add_image(image, scale)

    def arcgis(self, ax=None, scale=4, map_type='World_Physical_Map', 
               service='server.arcgisonline.com'):
        """
        以ArcGIS地图在线服务为背景.

        refer to:
        https://server.arcgisonline.com/arcgis/rest/services
        http://map.geoq.cn/arcgis/rest/services

        Args:
            ax (object, optional): Axes instance, if not None then overrides the default axes instance.
            scale (int, optional): Map scale, large value for detail map, defaults to 5.
            type (str, optional): Map type string. Defaults to 'World_Physical_Map'.
                                  'server.arcgisonline.com', scale 0~8,
                                      NatGeo_World_Map, USA_Topo_Maps, World_Imagery,
                                      World_Physical_Map, World_Shaded_Relief,
                                      World_Street_Map, World_Terrain_Base, World_Topo_Map
                                  'map.geoq.cn', scale 0-19
                                      ChinaOnlineCommunity_Mobile, ChinaOnlineCommunityENG,
                                      ChinaOnlineCommunity, ChinaOnlineStreetGray, 
                                      ChinaOnlineStreetPurplishBlue, ChinaOnlineStreetWarm
            service (str, optional): Map service, Detaults to 'server.arcgisonline.com'.
        """

        #Get current axes if not specified
        ax = ax or self._check_ax()

        #Create image tile URL
        url = "http://%s/arcgis/rest/services/%s/MapServer/tile/{z}/{y}/{x}" % (service, map_type)

        # add image
        image = cimgt.GoogleTiles(url=url)
        return ax.add_image(image, scale)
    
    def filloceans(self,color='#C8E7FF',res=None,ax=None,**kwargs):
        """
        Fills oceans with solid colors.
        
        Parameters:
        ----------------------
        color
            Fill color for oceans (default is light blue)
        res
            Resolution of data. Can be a character ('l','m','h') or one of cartopy's available
            resolutions ('110m','50m','10m'). If none is specified, then the default resolution specified
            when creating an instance of Map is used.
        ax
            Axes instance, if not None then overrides the default axes instance.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Error check resolution
        if res is None: res = self.res
        res = self.check_res(res)
        
        #Fill oceans
        ocean_mask = ax.add_feature(cfeature.OCEAN.with_scale(res),facecolor=color,edgecolor='face',**kwargs)

        return ocean_mask
        
    def filllakes(self,color='#C8E7FF',res=None,ax=None,**kwargs):
        """
        Fills lakes with solid colors.
        
        Parameters:
        ----------------------
        color
            Fill color for lakes (default is light blue)
        res
            Resolution of data. Can be a character ('l','m','h') or one of cartopy's available
            resolutions ('110m','50m','10m'). If none is specified, then the default resolution specified
            when creating an instance of Map is used.
        ax
            Axes instance, if not None then overrides the default axes instance.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Error check resolution
        if res is None: res = self.res
        res = self.check_res(res)
        
        #Fill lakes
        lake_mask = ax.add_feature(cfeature.LAKES.with_scale(res),facecolor=color,edgecolor='face',**kwargs)
        
        #Return value
        return lake_mask
    
    def fillcontinents(self,color='#e6e6e6',res=None,ax=None,**kwargs):
        """
        Fills land with solid colors.
        
        Parameters:
        ----------------------
        color
            Fill color for land (default is light gray)
        res
            Resolution of data. Can be a character ('l','m','h') or one of cartopy's available
            resolutions ('110m','50m','10m'). If none is specified, then the default resolution specified
            when creating an instance of Map is used.
        ax
            Axes instance, if not None then overrides the default axes instance.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Error check resolution
        if res is None: res = self.res
        res = self.check_res(res)
        
        #Fill continents
        continent_mask = ax.add_feature(cfeature.LAND.with_scale(res),facecolor=color,edgecolor='face',**kwargs)
        
        #Return value
        return continent_mask

    def maskcountries(self, conf, ax=None, regions=["China"],
                      pathkw=dict(facecolor='none',edgecolor='black', linewidth=1.5)):
        """
        在cartopy中, 对选定的国家进行白化.
        refer to https://cloud.tencent.com/developer/article/1618341

        Args:
            conf (matplotlib object): matplotlib的contour或contourf绘图返回值.
            ax (object, optional): Axes instance, if not None then overrides the default axes instance.
            regions (list, optional): 指定无需白化的国家. Defaults to ["China"].
            pathkw (dict, optional): PathPatch关键字参数. Defaults to dict(facecolor='none',edgecolor='black', linewidth=1.0).

        Returns:
            clipping path, matplotlib.patches.PathPatch
        """

        #Get current axes if not specified
        ax = ax or self._check_ax()

        #Convert region name to upper
        regions = list(regions)
        regions = [region.upper() for region in regions]

        # get shape file
        shpfile = pkg_resources.resource_filename(
            'nmc_met_graphics', "resources/maps/country1.shp")
        
        # retrive region geometry
        reader = Reader(shpfile)
        countries = reader.records()
        multipoly, = [country.geometry for country in countries
                        if country.attributes['CNTRY_NAME'].upper() in regions]
                            
        main_geom = sorted(multipoly.geoms, key=lambda geom: geom.area)[-1]

        path, = geos_to_path(main_geom)

        plate_carre_data_transform = ccrs.PlateCarree()._as_mpl_transform(ax)

        for collection in conf.collections:
            collection.set_clip_path(path, plate_carre_data_transform)
        
        # Draw the path of interest.
        path = PathPatch(path, transform = ccrs.PlateCarree(), **pathkw)
        return path

    def maskprovinces(self, conf, ax=None,  regions=["四川"],
                      pathkw=dict(facecolor='none',edgecolor='black', linewidth=1.0)):
        """
        白化指定省份外的区域.

        Args:
            conf (matplotlib object): matplotlib的contour或contourf绘图返回值.
            ax (ojbect, optional): Axes instance, if not None then overrides the default axes instance.
            regions (list, optional): 指定无需白化的省份简写名. Defaults to ["四川"].
            pathkw (dict, optional): PathPatch关键字参数. Defaults to dict(facecolor='none',edgecolor='black', linewidth=1.0).

        Returns:
            clipping path, matplotlib.patches.PathPatch
        """
    
        #Get current axes if not specified
        ax = ax or self._check_ax()

        #Region code
        region_code = {'安徽':340000, '北京':110000, '福建':350000, '甘肃':620000, '广东':440000, '广西':450000,
                       '贵州':520000, '海南':460000, '河北':130000, '河南':410000, '黑龙江':230000, '湖北':420000,
                       '湖南':430000, '吉林':220000, '江苏':320000, '江西':360000, '辽宁':210000, '内蒙古':150000,
                       '宁夏':640000, '青海':630000, '山东':370000, '山西':140000, '陕西':610000, '上海':310000,
                       '四川':510000, '台湾':710000, '天津':120000, '西藏':540000, '香港':810000, '新疆':650000,
                       '云南':530000, '浙江':330000, '重庆':500000}
        regions = list(regions)
        regions = [region_code.get(region) for region in regions]

        # get shape file
        shpfile = pkg_resources.resource_filename(
            'nmc_met_graphics', "resources/maps/bou2_4p.shp")
        
        # retrive region geometry
        sf = shapefile.Reader(shpfile, encoding='gbk')
        vertices = []
        codes = []
        for shape_rec in sf.shapeRecords():
            if shape_rec.record[5] in regions:
                pts = shape_rec.shape.points
                prt = list(shape_rec.shape.parts) + [len(pts)]
                for i in range(len(prt) - 1):
                    for j in range(prt[i], prt[i + 1]):
                        vertices.append((pts[j][0], pts[j][1]))
                    codes += [Path.MOVETO]
                    codes += [Path.LINETO] * (prt[i + 1] - prt[i] - 2)
                    codes += [Path.CLOSEPOLY]
        
        # Draw the path of interest
        clip = Path(vertices, codes)
        clip = PathPatch(clip, transform=ccrs.PlateCarree()._as_mpl_transform(ax), clip_on=True)
        for contour in conf.collections:
            contour.set_clip_path(clip)
        return clip

    def gridlines(self, ax=None, draw_labels=True, font_size=16, linewidth=1,
                  color='gray', alpha=0.5, linestyle='--', dms=True,
                  x_inline=False, y_inline=False, **kwargs):
        """
        绘制经纬度线.

        Args:
            ax (object, optional): Axes instance, if not None then overrides the default axes instance.
        """

        #Get current axes if not specified
        ax = ax or self._check_ax()

        #Add grid lines
        gl = ax.gridlines(draw_labels=draw_labels, linewidth=linewidth,
                          color=color, alpha=alpha, linestyle=linestyle, 
                          dms=dms, x_inline=x_inline, y_inline=y_inline, **kwargs)
        gl.top_labels = gl.right_labels = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': font_size}
        gl.ylabel_style = {'size': font_size}
        return gl

    def logo(self, ax=None, logo_file="nmc_medium.png", alpha=0.7, zoom=1, loc='left_top'):
        """
        Add logo image.

        Args:
            ax (object, optional): Axes instance, if not None then overrides the default axes instance.
            logo_file (str, optional): logo file name. Defaults to "nmc_medium.png".
            alpha (float, optional): logo transparency. Defaults to 0.7.
            zoom (int, optional): logo zoom scale. Defaults to 1.
            loc (str, optional): logo image location, 'left_top', 'left_bottom'.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()

        #Check logo file
        if not os.path.isfile(logo_file):
            logo_file = pkg_resources.resource_filename(
                'nmc_met_graphics', os.path.join("resources/logo/", logo_file))
        img = Image.open(logo_file)

        corner = ax.get_extent(crs=ccrs.PlateCarree())
        if loc.upper() == "LEFT_TOP":
            position = [corner[0], corner[3]]
            box_alignment = (-0.05, 1.05)
        else:
            position = [corner[0], corner[2]]
            box_alignment=(-0.05, -0.05)
        
        imagebox = OffsetImage(img, zoom=zoom, alpha=alpha, resample=True)
        imagebox.image.axes = ax
        transform = ccrs.PlateCarree()._as_mpl_transform(ax)
        ab = AnnotationBbox(
            imagebox, position, xycoords=transform,
            box_alignment=box_alignment, pad=0, frameon=False)
        return ax.add_artist(ab)

    def southsea(self, ax=None, logo_file="south_china_sea_01.jpg", alpha=1.0, zoom=0.4, loc='left_bottom'):
        """
        Add China south sea image.

        Args:
            ax (object, optional): Axes instance, if not None then overrides the default axes instance.
            logo_file (str, optional): logo file name. Defaults to "nmc_medium.png".
            alpha (float, optional): logo transparency. Defaults to 0.7.
            zoom (int, optional): logo zoom scale. Defaults to 1.
            loc (str, optional): logo image location, 'right_bottom', 'left_bottom'.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()

        #Check logo file
        if not os.path.isfile(logo_file):
            logo_file = pkg_resources.resource_filename(
                'nmc_met_graphics', os.path.join("resources/logo/", logo_file))
        img = Image.open(logo_file)

        corner = ax.get_extent(crs=ccrs.PlateCarree())
        if loc.upper() == "LEFT_BOTTOM":
            position = [corner[0], corner[2]]
            box_alignment=(-0.005, -0.005)
        else:
            position = [corner[1], corner[2]]
            box_alignment=(1.0, 0.0)
        
        imagebox = OffsetImage(img, zoom=zoom, alpha=alpha, resample=True)
        imagebox.image.axes = ax
        transform = ccrs.PlateCarree()._as_mpl_transform(ax)
        ab = AnnotationBbox(
            imagebox, position, xycoords=transform,
            box_alignment=box_alignment, pad=0, frameon=False)
        return ax.add_artist(ab)


    def title(self, ax=None, left_title=None, center_title=None,
              right_title=None, font_size=18, family='Microsoft YaHei',
              **kwargs):
        """
        Add title text.

        Args:
            ax (object, optional): Axes instance, if not None then overrides the default axes instance.
            left_title (str, optional): left title string. Defaults to None.
            center_title (str, optional): center title string. Defaults to None.
            right_title (str, optional): right title string. Defaults to None.
            font_size (int, optional): font size. Defaults to 18.
            family (str, optional): font family, 'sans-serif', .... Defaults to 'Microsoft YaHei'.
        """

        #Get current axes if not specified
        ax = ax or self._check_ax()

        #Set font properties
        font1 = FontProperties(family=family, size=font_size)
        font2 = FontProperties(family=family, size=int(font_size*0.8))
        font3 = FontProperties(family=family, size=int(font_size*0.6))

        if left_title is not None:
            ax.set_title(left_title,loc='left', fontproperties=font1, **kwargs)
        if center_title is not None:
            ax.set_title(center_title,loc='center', fontproperties=font2, **kwargs)
        if right_title is not None:
            ax.set_title(right_title,loc='right', fontproperties=font3, **kwargs)

    def left_title(self, name, ax=None, time=None, fhour=None, atime=0, 
                   time_zone=None, font_size=18, family='Microsoft YaHei',
                   **kwargs):
        """
        Add product name and time information to left title.

        Args:
            name (str): product name. Defaults to 'Model'.
            ax (object, optional): Axes instance, if not None then overrides the default axes instance.
            time (datetime, optional): model initial time or observational time. Defaults to None.
            fhour (int, optional): forecast hour. Defaults to None.
            atime (int, optional): accumulation time, if not 0, will show period. Defaults to 0.
            font_size (int, optional): title font size. Defaults to 18.
            family (str, optional): title font family. Defaults to 'Microsoft YaHei'.
        """

        #Get current axes if not specified
        ax = ax or self._check_ax()

        #title string
        titlestr = name

        #Add time information
        if time is not None:
            #Check time and convert to datetime object
            if isinstance(time, np.datetime64):
                time = pd.to_datetime(str(time)).replace(tzinfo=None).to_pydatetime()
            elif isinstance(time, pd.Timestamp):
                time = time.replace(tzinfo=None).to_pydatetime()
            elif isinstance(time, str):
                time = pd.to_datetime(time)

            if fhour is not None:  # model forecast
                if isinstance(fhour, np.ndarray):
                    fhour = fhour[0]
                valid_time = time + timedelta(hours=fhour)
                time_str = time.strftime('Init %Y-%m-%dT%H')
                if isinstance(time_zone,str):
                    time_str = time_str + '('+time_zone+')'
                if atime == 0:
                    valid_str = valid_time.strftime('Valid %m-%dT%H')
                else:
                    valid_str = (
                        (valid_time-timedelta(hours=atime)).strftime('Valid %m-%dT%H') +
                        valid_time.strftime(' to %dT%H'))
                fhour_str = "Hour {:03d}".format(int(fhour))
                titlestr = titlestr+' . '+time_str+'\n'+valid_str+' | '+fhour_str
            else:
                if atime == 0:
                    time_str = time.strftime('%Y-%m-%dT%H')
                else:
                    time_str = (
                        (time-timedelta(hours=atime)).strftime('%Y-%m-%dT%H') +
                        time.strftime(' to %m-%dT%H'))
                titlestr = titlestr+'\n'+time_str
                if  isinstance(time_zone,str):
                    titlestr = titlestr + '('+time_zone+')'

        # draw title
        font = FontProperties(family=family, size=font_size, weight='bold')
        ax.set_title(titlestr,loc='left', fontproperties=font, **kwargs)

    def right_title(self, elements, ax=None, font_size=14, 
                   family='sans-serif', **kwargs):
        """
        Add graphics element information.

        Args:
            elements (str): graphics elements, use '\n' for multiple lines.
            ax (object, optional): Axes instance, if not None then overrides the default axes instance.
            font_size (int, optional): font size. Defaults to 12.
            family (str, optional): font family. Defaults to 'SimHei'.
        """

        #Get current axes if not specified
        ax = ax or self._check_ax()

        #title string
        titlestr = elements

        # draw title
        font = FontProperties(family=family, size=font_size)
        ax.set_title(titlestr,loc='right', fontproperties=font, **kwargs)

    def info(self, x=0.98, y=0.01, info_text=None, ax=None, font_size=16, 
             family='sans-serif', **kwargs):
        """
        Add graphics information.

        Args:
            info_text (str): graphics information, use '\n' for multiple lines.
            ax (object, optional): Axes instance, if not None then overrides the default axes instance.
            font_size (int, optional): font size. Defaults to 12.
            family (str, optional): font family. Defaults to 'SimHei'.
        """

        #Get current axes if not specified
        ax = ax or self._check_ax()

        #title string
        if info_text is None:
            info_text = "Graphics by NMC-WFT"

        # draw title
        font = FontProperties(family=family, size=font_size, weight='bold')
        ax.text(x, y, info_text, color='black',
                verticalalignment='bottom', horizontalalignment='right',
                fontproperties=font, transform=ax.transAxes, 
                path_effects=[path_effects.withStroke(linewidth=4, foreground ="w")],
                **kwargs)
 
    def cities(self, ax=None, city_type='capital', color_style='black', 
               marker_size=5, font_size=16):
        """
        Draw city texts.

        Args:
            ax (object, optional): Axes instance, if not None then overrides the default axes instance.
            city_type (str, optional): the type name of city information. Defaults to 'capital'.
            color_style (str, optional): color style for city label. Defaults to 'white'.
            marker_size (int, optional): markder size. Defaults to 8.
            font_size (int, optional): font size. Defaults to 18.
        """

        #Get current axes if not specified
        ax = ax or self._check_ax()

        # check style
        color_style = color_style.lower()
        if color_style == 'white':
            color = 'white'; foreground = 'black'; markcolor = 'white'
        elif color_style == 'black':
            color = 'black'; foreground = 'white'; markcolor = 'black'
        else:
            color = 'white'; foreground = 'black'; markcolor = 'white'
            
        # get station information
        city_type = city_type.lower()
        if city_type == "capital":        # 省会城市
            cities = pd.read_csv(pkg_resources.resource_filename(
                'nmc_met_graphics', "resources/stations/provincial_capital.csv"))
        elif city_type == 'base_station': # 260个基本站点信息
            cities = pd.read_csv(pkg_resources.resource_filename(
                'nmc_met_graphics', "resources/stations/cma_city_station_info.dat"),  delimiter=r"\s+")
        elif city_type == 'station':      # 2420个基本站点信息
            cities = pd.read_csv(pkg_resources.resource_filename(
                'nmc_met_graphics', "resources/stations/cma_national_station_info.dat"))
        elif city_type == 'adcode':       # 3555个中国行政区划代码
            cities = pd.read_csv(pkg_resources.resource_filename(
                'nmc_met_graphics', "resources/stations/adcode-release-20191218.csv"))
        elif city_type == 'world':        # 154个全球站点信息
            cities = pd.read_csv(pkg_resources.resource_filename(
                'nmc_met_graphics', "resources/stations/cma_world_city_station_info.dat"),  delimiter=r"\s+")
        else:
            raise ValueError('Improper city_type entered.')

        # extract subregion
        if self.extent is not None:
            limit = self.extent
            cities = cities[(limit[2] <= cities['lat']) & (cities['lat'] <= limit[3]) &
                            (limit[0] <= cities['lon']) & (cities['lon'] <= limit[1])]
        if len(cities) == 0:
            return

        # draw station information
        font = FontProperties(family='SimHei', size=font_size, weight='bold')
        geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
        for _, row in cities.iterrows():
            text_transform = offset_copy(geodetic_transform, units='dots', x=-5)
            ax.plot(row['lon'], row['lat'], marker='s', color=markcolor, linestyle='None',
                    markersize=marker_size, alpha=0.7, transform=ccrs.PlateCarree())
            ax.text(row['lon'], row['lat'], row['city_name'], clip_on=True,
                    verticalalignment='center', horizontalalignment='right',
                    transform=text_transform, fontproperties=font, color=color,
                    path_effects=[path_effects.Stroke(linewidth=1, foreground=foreground),
                    path_effects.Normal()])

    def topo_hatches(self, ax=None, levels=[800], colors='gray', cut_extent=True,
                     hatches=['////'], sigma=None, alpha=0.3, **kwargs):
        """
        Draw filled-hatches topography overlay on map.
        You can use sigma to smooth topography.
        
        Examples:
        > m.topo_hatches(levels=[400, 800, 10000], hatches=['..','///'])
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Check contour levels
        if np.isscalar(levels):
            levels = list(levels)
        if len(levels) == 1:
            levels.append(10000)
            
        #Read topo data
        topofile = pkg_resources.resource_filename(
            'nmc_met_graphics', "resources/topo/topo_china.nc")
        topo = xr.open_dataset(topofile)
        lon = topo.coords['Longitude'].values
        lat = topo.coords['Latitude'].values
        topo = topo['topo'].values
        
        #Cut the grid data for fast plot.
        if cut_extent and self.extent is not None:
            topo, lon, lat = get_sub_grid(topo, lon, lat, limit=self.extent)
        
        #Draw hatches
        self.contourf(lon, lat, topo, ax=ax, transform=ccrs.PlateCarree(),
                      levels=levels, colors=colors, hatches=hatches,
                      sigma=sigma, alpha=alpha, **kwargs)
    
    def points(self, lon, lat, ax=None, transform=None,
               marker='o', size=10, facecolor='red',
               edgewidth=2, edgecolor='white',alpha=0.8,
               **kwargs):
        """
        Draw points symbol on the map.

        Args:
            lon (np.array): longitude coordinates.
            lat (np.array): latitude coordinates.
            ax (Axes, optional): Cartopy GeoAxes. Defaults to None.
            transform (crs, optional): Cartopy crs object. Defaults to None.
            markers (str, optional): matplotlib markers. Defaults to 'o'.
            size (int, optional): marker size. Defaults to 10.
            facecolor (str, optional): marker facecolor. Defaults to 'red'.
            edgewidth (int, optional): marker edge width. Defaults to 2.
            edgecolors (str, optional): marker edge colors. Defaults to 'black'.
            alpha (float, optional): marker transparency. Defaults to 0.8.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Check transform if not specified
        if transform is None: transform = ccrs.PlateCarree()
        
        # extract subregion
        lon = np.asarray(lon)
        lat = np.asarray(lat)
        if self.extent is not None:
            limit = self.extent
            idx = (limit[0] <= lon) & (lon <= limit[1]) & \
                  (limit[2] <= lat) & (lat <= limit[3])
            lon = lon[idx]
            lat = lat[idx]
        if len(lon) == 0 or len(lat) == 0:
            return
        
        #Draw points
        ax.plot(lon, lat, marker=marker, markersize=size, linestyle='None',
                markerfacecolor=facecolor, markeredgecolor=edgecolor,
                markeredgewidth=edgewidth, alpha=alpha,  transform=transform,
                **kwargs)
    
    def markers(self,lon,lat,values,clevs,ax=None,transform=None,
                markers='o', colors=None, sizes=12, alpha=0.8,
                edgecolors='black', linewidths=0.3, 
                legend_loc='lower left', legend_fontsize=14,
                legend_title='', **kwargs):
        """
        Plot point markers for different levels with colors, sizes and so on.

        Args:
            lon (np.array): longitude coordinates for markers.
            lat (np.array): latitude coordinates for markers.
            values (np.array): point values for markers.
            clevs (list or np.array): levels for values
            ax (Axes, optional): Cartopy GeoAxes. Defaults to None.
            transform (crs, optional): Cartopy crs object. Defaults to None.
            markers (str, optional): matplotlib markers. Defaults to 'o'.
            colors (list or str, optional): colors for clevs. Defaults to None.
            sizes (int or list, optional): marker sizes, int or list for clevs. Defaults to 12.
            alpha (float, optional): marker transparency. Defaults to 0.8.
            edgecolors (str, optional): marker edge colors. Defaults to 'black'.
            linewidths (float, optional): linewidths. Defaults to 0.3.
        """

        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Check transform if not specified
        if transform is None: transform = ccrs.PlateCarree()

        #Create dataframe
        data = pd.DataFrame({'lon':lon,'lat':lat,'values':values})

        #Check graphic parameters
        nlevs = len(clevs)
        if len(markers) == 1:
            markers = [markers for lev in clevs]
        if not hasattr(sizes, '__len__'):
            sizes   = [sizes for lev in clevs]
        if not hasattr(alpha, '__len__'):
            alpha   = [alpha for lev in clevs]
        if colors is None:
            colors  = nmgcmap.cm.get_colors_from_cmap(nmgcmap.cm.guide_cmaps('2'), nlevs)
        if len(colors) == 1:
            colors  = [colors for lev in clevs]
            
        # extract subregion
        lon = np.asarray(lon)
        lat = np.asarray(lat)
        if self.extent is not None:
            limit = self.extent
            idx = (limit[0] <= lon) & (lon <= limit[1]) & \
                  (limit[2] <= lat) & (lat <= limit[3])
            lon = lon[idx]
            lat = lat[idx]
            values = values[idx]
        if len(lon) == 0 or len(lat) == 0:
            return

        #Loop every levels
        legend_elements = []
        for ilev, lev in enumerate(clevs):
            if ilev == len(clevs)-1:
                temp = data[(data['values'] >= clevs[ilev])]
                label = label_fmt(lev)+'~Inf'
            else:
                temp = data[(data['values'] >= clevs[ilev]) & (data['values'] < clevs[ilev+1])]
                label = label_fmt(clevs[ilev])+'~'+label_fmt(clevs[ilev+1])
            
            # append legend
            legend_elements.append(
                Line2D([0], [0], marker=markers[ilev], color='w', label=label,
                       markerfacecolor=colors[ilev], markersize=15))
            
            # check data
            if len(temp) == 0:
                continue

            # draw data symbols
            ax.scatter(temp['lon'], temp['lat'], marker=markers[ilev],color=colors[ilev],
                       s=sizes[ilev], alpha=alpha[ilev], edgecolors=edgecolors,
                       linewidths=linewidths, transform=transform, **kwargs)

        # add legend
        font = FontProperties(family='sans-serif', size=legend_fontsize, weight='bold')
        lg = ax.legend(handles=legend_elements, loc=legend_loc, prop=font)
        font = FontProperties(family='SimHei', size=legend_fontsize*1.2)
        lg.set_title(legend_title, prop=font)
        
    def colorbar(self,mappable=None,ax_cb=None, location='right',size="2.5%",pad='1%',
                 label_size=13,label_fmt=label_fmt,fig=None,ax=None,**kwargs):
        """
        Uses the axes_grid toolkit to add a colorbar to the parent axis and rescale its size to match
        that of the parent axis, similarly to Basemap's functionality.
        
        Parameters:
        ----------------------
        mappable
            The image mappable to which the colorbar applies. If none specified, matplotlib.pyplot.gci() is
            used to retrieve the latest mappable.
        ax_cb
            Given the colorbar axes, will ignore the location parameter.
        location
            Location in which to place the colorbar ('right','left','top','bottom'). Default is right.
        size
            Size of the colorbar. Default is 3%.
        pad
            Pad of colorbar from axis. Default is 1%.
        ax
            Axes instance to associated the colorbar with. If none provided, or if no
            axis is associated with the instance of Map, then plt.gca() is used.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Get current mappable if none is specified
        if fig is None or mappable is None:
            import matplotlib.pyplot as plt
        if fig is None:
            fig = plt.gcf()
            
        if mappable is None:
            mappable = plt.gci()
        
        #Create axis to insert colorbar in
        if ax_cb is None:
            divider = make_axes_locatable(ax)
            if location == "left":
                orientation = 'vertical'
                ax_cb = divider.new_horizontal(size, pad, pack_start=True, axes_class=plt.Axes)
            elif location == "right":
                orientation = 'vertical'
                ax_cb = divider.new_horizontal(size, pad, pack_start=False, axes_class=plt.Axes)
            elif location == "bottom":
                orientation = 'horizontal'
                ax_cb = divider.new_vertical(size, pad, pack_start=True, axes_class=plt.Axes)
            elif location == "top":
                orientation = 'horizontal'
                ax_cb = divider.new_vertical(size, pad, pack_start=False, axes_class=plt.Axes)
            else:
                raise ValueError('Improper location entered')
        
        #Create colorbar
        fig.add_axes(ax_cb)
        cb = plt.colorbar(mappable, orientation=orientation, cax=ax_cb, **kwargs)
        for l in cb.ax.yaxis.get_ticklabels():
            l.set_weight("bold")
            l.set_fontsize(label_size)
        cb.ax.set_yticklabels([label_fmt(i) for i in cb.get_ticks()])
        
        #Reset parent axis as the current axis
        fig.sca(ax)
        return cb

    def pcolormesh(self,lon,lat,data,*args,ax=None,transform=None,
                   cut_extent=True, sigma=None, **kwargs):
        """
        Wrapper to matplotlib's pcolormesh function. Assumes lat and lon arrays are passed instead
        of x and y arrays. Default data projection is ccrs.PlateCarree() unless a different
        data projection is passed.
        Note: if you want to mask some values, the colormap is not work and set to np.nan will work.
        """

        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Check transform if not specified
        if transform is None: transform = ccrs.PlateCarree()
        
        #Cut the grid data for fast plot.
        if cut_extent and self.extent is not None:
            data, lon, lat = get_sub_grid(data, lon, lat, limit=self.extent)

        #make 2D grid coordinates
        if lon.ndim == 1:
            lon, lat = np.meshgrid(lon, lat)

        #smooth the 2D filed if sigma set.
        data = np.squeeze(data)
        if sigma is not None:
            data = ndimage.gaussian_filter(data, sigma=sigma,order=0)

        #draw pcolormesh
        pcm = ax.pcolormesh(lon,lat,data,*args,transform=transform, **kwargs)
        return pcm

    def imshow(self, data, *args,ax=None,transform=None,
               sigma=None, **kwargs):
        """
        Wrapper to matplotlib's imshow function. Coordinates are set by 
        extent (left, right, bottom, top). Default data projection is 
        ccrs.PlateCarree() unless a different data projection is passed.
        """

        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Check transform if not specified
        if transform is None: transform = ccrs.PlateCarree()

        #smooth the 2D filed if sigma set.
        data = np.squeeze(data)
        if sigma is not None:
            data = ndimage.gaussian_filter(data, sigma=sigma,order=0)
        
        #Fill contour data
        cs = ax.imshow(data, *args, transform=transform, **kwargs)
        return cs

    def contourf(self,lon,lat,data,*args,ax=None,transform=None,
                 cut_extent=True, sigma=None, **kwargs):
        """
        Wrapper to matplotlib's contourf function. Assumes lat and lon arrays are passed instead
        of x and y arrays. Default data projection is ccrs.PlateCarree() unless a different
        data projection is passed.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Check transform if not specified
        if transform is None: transform = ccrs.PlateCarree()
        
        #Cut the grid data for fast plot.
        if cut_extent and self.extent is not None:
            data, lon, lat = get_sub_grid(data, lon, lat, limit=self.extent)

        #make 2D grid coordinates
        if lon.ndim == 1:
            lon, lat = np.meshgrid(lon, lat)

        #smooth the 2D filed if sigma set.
        data = np.squeeze(data)
        if sigma is not None:
            data = ndimage.gaussian_filter(data, sigma=sigma,order=0)
        
        #Fill contour data
        cs = ax.contourf(lon,lat,data,*args,transform=transform, **kwargs)
        return cs
    
    def contour(self,lon,lat,data,*args,ax=None,transform=None,sigma=None, cut_extent=True,
                label=True, label_size=12, label_fmt=label_fmt, **kwargs):
        """
        Wrapper to matplotlib's contour function. Assumes lat and lon arrays are passed instead
        of x and y arrays. Default data projection is ccrs.PlateCarree() unless a different
        data projection is passed.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Check transform if not specified
        if transform is None: transform = ccrs.PlateCarree()
        
        #Cut the grid data for fast plot.
        if cut_extent and self.extent is not None:
            data, lon, lat = get_sub_grid(data, lon, lat, limit=self.extent)

        #make 2D grid coordinates
        if lon.ndim == 1:
            lon, lat = np.meshgrid(lon, lat)
        
        #smooth the 2D filed if sigma set.
        data = np.squeeze(data)
        if sigma is not None:
            data = ndimage.gaussian_filter(data, sigma=sigma,order=0)
        
        #Contour data
        cs = ax.contour(lon,lat,data,*args,transform=transform,**kwargs)
        if label:
            ax.clabel(cs, cs.levels, inline=True, inline_spacing=1, 
                      fmt=label_fmt, fontsize=label_size, rightside_up=True)
        return cs
    
    def barbs(self,lon,lat,u,v,*args,ax=None,transform=None,cut_extent=True, **kwargs):
        """
        Wrapper to matplotlib's barbs function. Assumes lat and lon arrays are passed instead
        of x and y arrays. Default data projection is ccrs.PlateCarree() unless a different
        data projection is passed. Flips barbs for southern hemisphere.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Check transform if not specified
        if transform is None: transform = ccrs.PlateCarree()
        
        #Cut the grid data for fast plot.
        if cut_extent and self.extent is not None:
            u, _, _ = get_sub_grid(u, lon, lat, limit=self.extent)
            v, lon, lat = get_sub_grid(v, lon, lat, limit=self.extent)
        
        #Ensure lon and lat arrays are 2D
        if lon.ndim == 1 and lat.ndim == 1:
            lon,lat = np.meshgrid(lon,lat)
        elif lon.ndim == 2 and lat.ndim == 2:
            pass
        else:
            raise ValueError('Both lon and lat must have the same number of dimensions')
        
        #Plot north hemisphere barbs
        u_nh = u.copy(); u_nh[np.logical_or(lat < 0.0,lat == 90.0)] = np.nan
        v_nh = v.copy(); v_nh[np.logical_or(lat < 0.0,lat == 90.0)] = np.nan
        barb_nh = ax.barbs(lon,lat,u_nh,v_nh,*args,**kwargs,transform=transform)
        
        #Plot south hemisphere barbs
        u_sh = u.copy(); u_sh[np.logical_or(lat > 0.0,lat == -90.0)] = np.nan
        v_sh = v.copy(); v_sh[np.logical_or(lat > 0.0,lat == -90.0)] = np.nan
        kwargs['flip_barb'] = True
        barb_sh = ax.barbs(lon,lat,u_sh,v_sh,*args,**kwargs,transform=transform)
        
        #Return values
        return barb_nh, barb_sh
    
    def quiver(self,lon,lat,u,v,*args,ax=None,transform=None,
               cut_extent=True, **kwargs):
        """
        Wrapper to matplotlib's quiver function. Assumes lat and lon arrays are passed instead
        of x and y arrays. Default data projection is ccrs.PlateCarree() unless a different
        data projection is passed.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Check transform if not specified
        if transform is None: transform = ccrs.PlateCarree()
        
        #Cut the grid data for fast plot.
        if cut_extent and self.extent is not None:
            u, _, _ = get_sub_grid(u, lon, lat, limit=self.extent)
            v, lon, lat = get_sub_grid(v, lon, lat, limit=self.extent)
            
        #Ensure lon and lat arrays are 2D
        if lon.ndim == 1 and lat.ndim == 1:
            lon,lat = np.meshgrid(lon,lat)
        elif lon.ndim == 2 and lat.ndim == 2:
            pass
        else:
            raise ValueError('Both lon and lat must have the same number of dimensions')

        #Plot north hemisphere barbs
        qv = ax.quiver(lon,lat,u,v,*args,**kwargs,transform=transform)

        #Return values
        return qv

