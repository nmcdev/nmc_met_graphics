# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Draw china map.
"""

import os
import pkg_resources
import numpy as np
from numpy.lib.arraysetops import isin
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib.patheffects as path_effects
from matplotlib.path import Path
from matplotlib.patches import Polygon, PathPatch
from matplotlib.font_manager import FontProperties
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.transforms import offset_copy
from mpl_toolkits.axes_grid1 import make_axes_locatable

import shapefile
import cartopy.feature as cfeature
import cartopy.io.img_tiles as cimgt
from cartopy import crs as ccrs
from cartopy import util as cu
from cartopy.io.shapereader import Reader
from cartopy.mpl.patch import geos_to_path
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

from nmc_met_graphics.util import get_map_region


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


class BaseMap():
    
    def __init__(self, projection='PlateCarree', ax=None, res='m', **kwargs):
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
            String representing the default geography boundary resolution ('l'=low,'m'=moderate,'h'=high).
            Default resolution is moderate 'm'. This can also be changed individually for each function
            that plots boundaries.
        **kwargs
            Additional arguments that are passed to those associated with projection.
            
        Returns:
        ----------------------
        Instance of a Map object

        Examples:

        from nmc_met_graphics.plot.china_map import BaseMap
        m = BaseMap(projection='PlateCarree',central_longitude=110.0,res='h')
        plt.figure(figsize=(14,12))
        ax = plt.axes(projection=m.proj)
        ax.set_extent([115, 116, 39, 40])
        m.tianditu(scale=12, map_type='Satellite')
        m.drawcoastlines(linewidth=1.0)
        m.drawstates(linewidth=1.0,color='gray')
        m.drawrivers()
        """
        
        self.proj = getattr(ccrs, projection)(**kwargs)
        self.ax = ax
        self.res = res
        
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
        map_region = get_map_region(region)
        ax.set_extent(map_region, crs=ccrs.PlateCarree())
    
    def drawcoastlines(self,linewidths=1.2,linestyle='solid',color='k',res=None,ax=None,**kwargs):
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
        coastlines = ax.add_feature(cfeature.COASTLINE.with_scale(res),linewidths=linewidths,linestyle=linestyle,edgecolor=color,**kwargs)
        
        #Return value
        return coastlines
    
    def drawcountries(self,linewidths=1.2,linestyle='solid',color='k',res=None,ax=None,**kwargs):
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

    def drawnation(self,linewidths=1.0,linestyle='solid',color='k',facecolor='none',ax=None,**kwargs):
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
    
    def drawstates(self,linewidths=0.7,linestyle='solid',color='k',facecolor='none',ax=None,**kwargs):
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

    def drawcounties(self,linewidths=0.7,linestyle='solid',color='k',facecolor='none',ax=None,**kwargs):
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

    def drawrivers(self,linewidths=0.8,linestyle='solid',color='blue',facecolor='none',ax=None,**kwargs):
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
    
    def _check_ax(self):
        """
        Adapted from Basemap - checks to see if an axis is specified, if not, returns plt.gca().
        """
        
        if self.ax is None:
            try:
                ax = plt.gca(projection=self.proj)
            except:
                import matplotlib.pyplot as plt
                ax = plt.gca(projection=self.proj)
        else:
            ax = self.ax(projection=self.proj)
            
        return ax

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

    def gridlines(self, ax=None, font_size=14, linewidth=1,
                  color='gray', alpha=0.5, linestyle='--', **kwargs):
        """
        绘制经纬度线.

        Args:
            ax (object, optional): Axes instance, if not None then overrides the default axes instance.
        """

        #Get current axes if not specified
        ax = ax or self._check_ax()

        #Add grid lines
        gl = ax.gridlines(draw_labels=True, linewidth=linewidth,
                          color=color, alpha=alpha, linestyle=linestyle, **kwargs)
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
              right_title=None, font_size=18, family='Microsoft YaHei'):
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
            ax.set_title(left_title,loc='left', fontsize=font1)
        if center_title is not None:
            ax.set_title(center_title,loc='center', fontsize=font2)
        if right_title is not None:
            ax.set_title(right_title,loc='right', fontsize=font3)

    def cities(self, ax=None, city_type='capital', color='white',
               foreground='black', font_size=18):
        """
        Draw city texts.

        Args:
            ax ([type], optional): [description]. Defaults to None.
            city_type (str, optional): [description]. Defaults to 'capital'.
            color (str, optional): [description]. Defaults to 'white'.
            foreground (str, optional): [description]. Defaults to 'black'.
            font_size (int, optional): [description]. Defaults to 18.
        """

        #Get current axes if not specified
        ax = ax or self._check_ax()

        if city_type.upper() == "CAPITAL":
            cities = pd.read_csv(pkg_resources.resource_filename(
                'nmc_met_graphics', "resources/stations/provincial_capital.csv"))
        else:
            cities = pd.read_csv(pkg_resources.resource_filename(
                'nmc_met_graphics', "resources/stations/cma_city_station_info.dat"),  delimiter=r"\s+")

        font = FontProperties(family='SimHei', size=font_size, weight='bold')
        geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
        for _, row in cities.iterrows():
            text_transform = offset_copy(geodetic_transform, units='dots', x=-5)
            ax.plot(row['lon'], row['lat'], marker='o', color='white', markersize=8,
                    alpha=0.7, transform=ccrs.PlateCarree())
            ax.text(row['lon'], row['lat'], row['city_name'], clip_on=True,
                    verticalalignment='center', horizontalalignment='right',
                    transform=text_transform, fontproperties=font, color=color,
                    path_effects=[
                        path_effects.Stroke(linewidth=1, foreground=foreground),path_effects.Normal()])

    def colorbar(self,mappable=None,location='right',size="3%",pad='1%',fig=None,ax=None,**kwargs):
        """
        Uses the axes_grid toolkit to add a colorbar to the parent axis and rescale its size to match
        that of the parent axis, similarly to Basemap's functionality.
        
        Parameters:
        ----------------------
        mappable
            The image mappable to which the colorbar applies. If none specified, matplotlib.pyplot.gci() is
            used to retrieve the latest mappable.
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
        
        #Reset parent axis as the current axis
        fig.sca(ax)
        return cb

    def contourf(self,lon,lat,data,*args,ax=None,transform=None,**kwargs):
        """
        Wrapper to matplotlib's contourf function. Assumes lat and lon arrays are passed instead
        of x and y arrays. Default data projection is ccrs.PlateCarree() unless a different
        data projection is passed.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Check transform if not specified
        if transform is None: transform = ccrs.PlateCarree()
        
        #Fill contour data
        cs = ax.contourf(lon,lat,data,*args,**kwargs,transform=transform)
        return cs
    
    def contour(self,lon,lat,data,*args,ax=None,transform=None,**kwargs):
        """
        Wrapper to matplotlib's contour function. Assumes lat and lon arrays are passed instead
        of x and y arrays. Default data projection is ccrs.PlateCarree() unless a different
        data projection is passed.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Check transform if not specified
        if transform is None: transform = ccrs.PlateCarree()
        
        #Contour data
        cs = ax.contour(lon,lat,data,*args,**kwargs,transform=transform)
        return cs
    
    def barbs(self,lon,lat,u,v,*args,ax=None,transform=None,**kwargs):
        """
        Wrapper to matplotlib's barbs function. Assumes lat and lon arrays are passed instead
        of x and y arrays. Default data projection is ccrs.PlateCarree() unless a different
        data projection is passed. Flips barbs for southern hemisphere.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Check transform if not specified
        if transform is None: transform = ccrs.PlateCarree()
        
        #Ensure lon and lat arrays are 2D
        lon_shape = len(np.array(lon).shape)
        lat_shape = len(np.array(lat).shape)
        if lon_shape == 1 and lat_shape == 1:
            lon,lat = np.meshgrid(lon,lat)
        elif lon_shape == 2 and lat_shape == 2:
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
    
    def quiver(self,lon,lat,u,v,*args,ax=None,transform=None,**kwargs):
        """
        Wrapper to matplotlib's quiver function. Assumes lat and lon arrays are passed instead
        of x and y arrays. Default data projection is ccrs.PlateCarree() unless a different
        data projection is passed.
        """
        
        #Get current axes if not specified
        ax = ax or self._check_ax()
        
        #Check transform if not specified
        if transform is None: transform = ccrs.PlateCarree()

        #Plot north hemisphere barbs
        qv = ax.quiver(lon,lat,u,v,*args,**kwargs,transform=transform)

        #Return values
        return qv
