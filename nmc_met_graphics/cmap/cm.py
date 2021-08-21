# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
  Collection of color map functions.
"""

import os
import sys
import re
import glob
import pathlib
import pkg_resources
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as mplcm
import matplotlib.colorbar as mcbar
from matplotlib.colors import ListedColormap, to_rgb, to_hex, LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from nmc_met_graphics.cmap.cpt import gmtColormap_openfile


def make_cmap(incolors, position=None, rgb=False, hex=False):
    """
    Takes a list of tuples which contain RGB values. The RGB
    values may either be in 8-bit [0 to 255] (in which bit must be set to
    True when called) or arithmetic [0 to 1] (default). make_cmap returns
    a cmap with equally spaced colors.

    :param incolors: RGB or HEX colors. Arrange your tuples so that
                     the first color is the lowest value for the
                     colorbar and the last is the highest.
    :param position: contains values from 0 to 1 to dictate the
                     location of each color.
    :param rgb: incolors are RGB colors
    :param hex: incolors are HEX colors
    :return: matplotlib color map function.

    :Example:
    >>> incolors = ('#996035','#F2DACD','#1E6EC8','#AAFFFF','#01F6E2',
                    '#00FF00','#03E19F','#26BC0D','#88DB07',
    ...             '#FFFF13','#FFE100','#264CFF','#FF7F00','#FF0000',
                    '#B5003C','#7F0067','#9868B4','#F2EBF5',
    ...             '#ED00ED')
    >>> pos = np.array([250,270,280,285,290,295,300,305,
                        310,315,320,330,335,340,345,350,355,360,370])
    >>> cmap = make_cmap(incolors, position=pos, hex=True)
    >>> show_colormap(cmap)
    """

    _colors = []
    if position is None:
        position = np.linspace(0, 1, len(incolors))
    else:
        position = np.array(position)
        if len(position) != len(incolors):
            sys.exit("position length must be the same as colors")

    # normalize position if necessary
    if position.max() > 1 or position.min() < 0:
        positions = (
            position - position.min())/(position.max() - position.min())
    else:
        positions = position

    if hex:
        for i in range(len(incolors)):
            _colors.append(to_rgb(incolors[i]))

    if rgb:
        bit_rgb = np.linspace(0, 1, 256)
        for i in range(len(incolors)):
            _colors.append((bit_rgb[incolors[i][0]],
                            bit_rgb[incolors[i][1]],
                            bit_rgb[incolors[i][2]]))

    cdict = {'red': [], 'green': [], 'blue': []}
    for pos, color in zip(positions, _colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))

    cmap = mpl.colors.LinearSegmentedColormap('my_colormap', cdict, 256)

    return cmap


def discrete_cmap(N, base_cmap=None):
    """Create an N-bin discrete colormap from the specified input map
    
    Examples:
        N = 5
        x = np.random.randn(40)
        y = np.random.randn(40)
        c = np.random.randint(N, size=40)

        # Edit: don't use the default ('jet') because it makes @mwaskom mad...
        plt.scatter(x, y, c=c, s=50, cmap=discrete_cmap(N, 'cubehelix'))
        plt.colorbar(ticks=range(N))
        plt.clim(-0.5, N - 0.5)
        plt.show()
    """

    # Note that if base_cmap is a string or None, you can simply do
    #    return plt.cm.get_cmap(base_cmap, N)
    # The following works for string, None, or a colormap instance:

    base = plt.cm.get_cmap(base_cmap)
    color_list = base(np.linspace(0, 1, N))
    cmap_name = base.name + str(N)
    return base.from_list(cmap_name, color_list, N)


def mpl_colors(cmap=None, N=None):
    """Return a list of RGB values.

    Parameters:
        cmap (str): Name of a registered colormap.
        N (int): Number of colors to return.
            If ``None`` use the number of colors defined in the colormap.
    Returns:
        np.array: Array with RGB and alpha values.
    Examples:
        >>> mpl_colors('viridis', 5)
        array([[ 0.267004,  0.004874,  0.329415,  1.      ],
            [ 0.229739,  0.322361,  0.545706,  1.      ],
            [ 0.127568,  0.566949,  0.550556,  1.      ],
            [ 0.369214,  0.788888,  0.382914,  1.      ],
            [ 0.993248,  0.906157,  0.143936,  1.      ]])
    """
    if cmap is None:
        cmap = plt.rcParams['image.cmap']

    if N is None:
        N = plt.get_cmap(cmap).N

    return plt.get_cmap(cmap)(np.linspace(0, 1, N))


def get_colors_from_cmap(cmap, N):
    """
    Extract linear interpolated N colors (HEX) from cmap. 

    Args:
        cmap ([type]): [description]
        N ([type]): [description]
    """

    colors = cmap(np.linspace(0,1,N))
    colors = [mpl.colors.rgb2hex(c) for c in colors]
    return colors


def _to_hex(c):
    """Convert arbitray color specification to hex string."""
    ctype = type(c)

    # Convert rgb to hex.
    if ctype is tuple or ctype is np.ndarray or ctype is list:
        return mpl.colors.rgb2hex(c)

    if ctype is str:
        # If color is already hex, simply return it.
        regex = re.compile('^#[A-Fa-f0-9]{6}$')
        if regex.match(c):
            return c

        # Convert named color to hex.
        return mpl.colors.cnames[c]

    raise Exception("Can't handle color of type: {}".format(ctype))


def colors2cmap(*args, name=None):
    """Create a colormap from a list of given colors.

    Parameters:
        *args: Arbitrary number of colors (Named color, HEX or RGB).
        name (str): Name with which the colormap is registered.
    Returns:
        LinearSegmentedColormap.
    Examples:
        >>> colors2cmap('darkorange', 'white', 'darkgreen', name='test')
    """
    if len(args) < 2:
        raise Exception("Give at least two colors.")

    cmap_data = [_to_hex(c) for c in args]
    cmap = LinearSegmentedColormap.from_list(name, cmap_data)
    plt.register_cmap(name, cmap)

    return cmap


def make_cmap_list(color_list):
    """
    Making color map from color list.

    :param color_list: color list, like ["whitesmoke","dimgray"].
    :return: matplotlib color map.
    """

    # from_list(name, colors, N=256, gamma=1.0)
    return LinearSegmentedColormap.from_list('', color_list)


def grayify_cmap(cmap):
    """
    Return a grayscale version of the colormap
    :param cmap: cmap instance.
    :return: grayscale colormap
    """

    cols = cmap(np.arange(cmap.N))

    # convert RGBA to perceived greyscale luminance
    # cf. http://alienryderflex.com/hsp.html
    RGB_weight = [0.299, 0.587, 0.114]
    luminance = np.sqrt(np.dot(cols[:, :3] ** 2, RGB_weight))
    cols[:, :3] = luminance[:, np.newaxis]

    return LinearSegmentedColormap.from_list(
        cmap.name + "_grayscale", cols, cmap.N)


def show_colormap(cmap):
    """
    Show color map.
    :param cmap: color map instance.
    :return: None
    """
    im = np.outer(np.ones(10), np.arange(100))
    fig, ax = plt.subplots(2, figsize=(6, 1.5),
                           subplot_kw=dict(xticks=[], yticks=[]))
    fig.subplots_adjust(hspace=0.1)
    ax[0].imshow(im, cmap=cmap)
    ax[1].imshow(im, cmap=grayify_cmap(cmap))
    
    
def plot_colorMaps(cmap):
    """
    Plot color map.
    
    :param cmap: color map instance.
    :return: None
    """
    print(cmap.name)
    _, ax = plt.subplots(figsize=(6,0.5))
    col_map = plt.get_cmap(cmap)
    mpl.colorbar.ColorbarBase(ax, cmap=col_map, orientation = 'horizontal')
    plt.show()


def ncl_cmaps(name, N=None):
    """
    Get the ncl color maps.
    https://github.com/hhuangwx/cmaps

    :param name: color map name.
    :return: matlibplot color map.
    """

    # color map file directory
    cmap_file = pkg_resources.resource_filename(
        "nmc_met_graphics", "resources/colormaps_ncl/" + str(name) + '.rgb')
    if not os.path.isfile(cmap_file):
        raise ValueError('Improper ncl colormap name.')

    # read color data
    pattern = re.compile(r'(\d\.?\d*)\s+(\d\.?\d*)\s+(\d\.?\d*)\n')
    with open(cmap_file) as cmap:
        cmap_buff = cmap.read()
    if re.search(r'\s*\d\.\d*', cmap_buff):
        rgb = np.asarray(pattern.findall(cmap_buff), 'f4')
    else:
        rgb = np.asarray(pattern.findall(cmap_buff), 'u1') / 255.

    # construct color map
    return ListedColormap(rgb, name='ncl_'+str(name), N=N)


def guide_cmaps(name, N=256):
    """
    Get guide color maps.

    :param name: guide color name number, like 42.
    :return: matplotlib color map.
    """

    # color map file directory
    cmap_file = pkg_resources.resource_filename(
        "nmc_met_graphics", "resources/colormaps_guide/cs" + str(name) + '.txt')
    if not os.path.isfile(cmap_file):
        raise ValueError('Improper guide colormap name.')

    # read color data
    rgb = np.loadtxt(cmap_file)

    # construct color map
    return LinearSegmentedColormap.from_list('guide_'+str(name), rgb/255, N=N)


def cmasher_cmaps(name, N=None):
    """
    Get cmsaher color maps.
    https://github.com/1313e/CMasher

    :param name: color name.
    :return: matplotlib color map.
    """

    # color map file directory
    cmap_file = pkg_resources.resource_filename(
        "nmc_met_graphics", "resources/colormaps_cmasher/cm_" + str(name) + '.txt')
    if not os.path.isfile(cmap_file):
        raise ValueError('Improper cmasher colormap name.')

    # read color data
    rgb = np.loadtxt(cmap_file)

    # construct color map
    return ListedColormap(rgb/255, name='cmasher_'+str(name), N=N)

def crameri_cmaps(name, N=None):
    """
    Get Fabio Crameri's perceptually uniform colour maps.
    https://github.com/callumrollo/cmcrameri
    https://www.fabiocrameri.ch/colourmaps/

    :param name: color name.
    :return: matplotlib color map.
    """

    # color map file directory
    cmap_file = pkg_resources.resource_filename(
        "nmc_met_graphics", "resources/colormaps_crameri/" + str(name) + '.txt')
    if not os.path.isfile(cmap_file):
        raise ValueError('Improper crameri colormap name.')

    # read color data
    rgb = np.loadtxt(cmap_file)

    # construct color map
    return ListedColormap(rgb/255, name='crameri_'+str(name), N=N)


def ndfd_cmaps(name, N=256):
    """
    Get ndfd color maps.
    refer to https://github.com/eengl/ndfd-colors.

    :param name: color name number, like "PoP12-Blend".
    :return: matplotlib color map.
    """

    # color map file directory
    cmap_file = pkg_resources.resource_filename(
        "nmc_met_graphics", "resources/colormaps_ndfd/" + str(name) + '.cpt')
    if not os.path.isfile(cmap_file):
        raise ValueError('Improper ndfd colormap name.')

    # read color data
    with open(cmap_file) as cptf:
        rgb = gmtColormap_openfile(cptf, 'ndfd_'+str(name), N=N)

    # construct color map
    return rgb


def ndfd_cmaps_show():
    """  
    Show all ndfd color maps.
    """
    cmap_dir = pkg_resources.resource_filename(
        "nmc_met_graphics", "resources/colormaps_ndfd/")
    
    for file in pathlib.Path(cmap_dir).glob("*.cpt"):
        with open(file, 'r') as cptf:
            color = gmtColormap_openfile(cptf, file.name)
        plot_colorMaps(color)


class MidpointNormalize(mpl.colors.Normalize):
    """
    Introduce MidpointNormalize class that would scale data values to
    colors and add the capability to specify the middle point of a colormap.

    https://ueapy.github.io/filled-contour-plots-and-colormap-normalization.html

    :Examples:
    >>> p3 = ax.contourf(X, Y, Z, norm=MidpointNormalize(midpoint=0.),
                         cmap='RdBu_r')
    """
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        mpl.colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))


class Cmaps(object):
    """colormaps
    Make it easier to use user defined colormaps in matplotlib.
    Default colormaps are from NCL website.
    https://github.com/hhuangwx/cmaps

    :Examples:
    >>> from nmc_met_graphics.color_maps import Cmaps
    >>> import matplotlib.pyplot as plt
    >>> import numpy as np
    >>> x = y = np.arange(-3.0, 3.01, 0.05)
    >>> X, Y = np.meshgrid(x, y)
    >>> Z1 = plt.mlab.bivariate_normal(X, Y, 1.0, 1.0, 0.0, 0.0)
    >>> plt.pcolormesh(X, Y, Z1, cmap=Cmaps().WhBlReWh)
    >>> plt.colorbar()
    """

    def __init__(self, ):
        self._cmap_d = dict()
        self._parse_cmaps()
        for cname in self._cmap_d.keys():
            setattr(self, cname, self._cmap_d[cname])

    def _listfname(self):
        cmapsfile_dir = pkg_resources.resource_filename(
            "nmc_met_graphics", "resources/colormaps_ncl")
        cmapsflist = sorted(glob.glob(os.path.join(cmapsfile_dir, '*.rgb')))
        return cmapsflist

    def _coltbl(self, cmap_file):
        pattern = re.compile(r'(\d\.?\d*)\s+(\d\.?\d*)\s+(\d\.?\d*).*')
        with open(cmap_file) as cmap:
            cmap_buff = cmap.read()
        cmap_buff = re.compile('ncolors.*\n').sub('', cmap_buff)
        if re.search(r'\s*\d\.\d*', cmap_buff):
            return np.asarray(pattern.findall(cmap_buff), 'f4')
        else:
            return np.asarray(pattern.findall(cmap_buff), 'u1') / 255.

    def _parse_cmaps(self):
        for cmap_file in self._listfname():
            cname = os.path.basename(cmap_file).split('.rgb')[0]
            # start with the number will result illegal attribute
            if cname[0].isdigit():
                cname = 'N' + cname
            if '-' in cname:
                cname = cname.replace('-', '_')

            cmap = mpl.colors.ListedColormap(self._coltbl(cmap_file), name=cname)
            mplcm.register_cmap(name=cname, cmap=cmap)
            self._cmap_d[cname] = cmap

            cname = cname + '_r'
            cmap = mpl.colors.ListedColormap(self._coltbl(cmap_file)[::-1],
                                         name=cname)
            mplcm.register_cmap(name=cname, cmap=cmap)
            self._cmap_d[cname] = cmap

    def listcmname(self):
        for ii in (self._cmap_d.keys()):
            print(ii)

    def cmap_dict(self):
        return self._cmap_d


class gradient:
    """
    Creates a color gradient based on passed ranges of values
    refer to:
    https://github.com/tomerburg/python_gallery
    https://github.com/tomerburg/metlib/blob/master/colors/create_gradient.py

    :Examples:

    #This is the call to the list_by_values function. Input parameters are as many ranges
    #as desired. In this example, there are 3 ranges, one starting from #00FFFF for a value
    #of 25 and going to #0000FF for a value of 29.

    #First, create an instance of the gradient class that stores the data used to make the
    #color map. Input parameters are as many ranges as desired.

    obj = gradient([['#00FFFF',25.0],['#0000FF',29.0]],
                   [['#0000FF',29.0],['#0000AA',32.0]],
                   [['#0000AA',32.0],['#FF00FF',38.0]])

    #Create a range of levels going from 25 to 39 with an increment of 0.5:
    clevs = np.arange(25.0,39.0,0.5)

    #To retrieve the gradient colormap matching to the range of levels, use the get_cmap function:
    cmap = obj.get_cmap(clevs)
    """
    
    def __init__(self,*args):
        self.args = args
        
        #Set threshold levels
        self.thres = []
        self.thres_min = []
        
        #Error check arguments
        error = 0
        for arg in args:
            
            #Ensure each argument & subargument has a length of 2
            if len(arg) != 2: error = 1
            if len(arg[0]) != 2: error = 1
            if len(arg[1]) != 2: error = 1
            
            #Ensure the 2nd element of each argument is a number
            if isinstance(arg[0][1], (int, float)) == False: error = 2
            if isinstance(arg[1][1], (int, float)) == False: error = 2
            
            #Ensure that the 1st element of each argument is either a hex str or rgb tuple
            if isinstance(arg[0][0], (str, tuple)) == False: error = 3
            if isinstance(arg[1][0], (str, tuple)) == False: error = 3
            
            #Ensure gradient values are continuous
            if len(self.thres) > 0 and self.thres[-1] != arg[0][1]: error = 4
            
            #Append threshold levels
            self.thres.append(arg[0][1])
            self.thres.append(arg[1][1])
            self.thres_min.append(arg[0][1])
            
        #Ensure values are either constantly increasing or decreasing
        check_thres = np.array(self.thres)
        diff = check_thres[1:] - check_thres[:-1]
        if np.min(diff) == 0 and np.max(diff) > 0:
            pass
        elif np.min(diff) < 0 and np.max(diff) == 0:
            self.thres = self.thres[::-1]
        else:
            error = 4
        
        #Output error messages
        if error == 1: raise RuntimeError('Each argument must have 2 elements, e.g., [["#00FFFF",25.0],["#0000FF",29.0]]')
        if error == 2: raise RuntimeError('The second element must be a number, e.g., [["#00FFFF",25.0]')
        if error == 3: raise RuntimeError('The first element must be a hex string or an rgb tuple, e.g., [["#00FFFF",25.0]')
        if error == 4: raise RuntimeError('Values assigned to the gradient must be continuous, either increasing or decreasing.')
        
    #Returns the hex string corresponding to the passed rgb values
    def rgb(self,r,g,b):
        r = int(r)
        g = int(g)
        b = int(b)
        return '#%02x%02x%02x' % (r, g, b)
        
    #Computes a hex value matching up with the current position relative to the range of colors.
    #position = current position within the range of colors (e.g., 1)
    #rng = range of colors (e.g. 5, so 1/5 would be 20% of the range)
    #col1 = Starting RGB color for the range (e.g. [0,255,255])
    #col2 = Ending RGB color for the range (e.g. [0,0,255])
    def getColor(self,position,rng,col1,col2):
        
        #Retrieve r,g,b values from tuple
        r1,g1,b1 = col1
        r2,g2,b2 = col2
    
        #Get difference in each r,g,b value between start & end 
        rdif = float(r2 - r1)
        gdif = float(g2 - g1)
        bdif = float(b2 - b1)
        
        #Calculate r,g,b values for the specified position within the range
        r3 = r2 + (-1.0 * position * (rdif / float(rng)))
        g3 = g2 + (-1.0 * position * (gdif / float(rng)))
        b3 = b2 + (-1.0 * position * (bdif / float(rng)))
    
        #Return in hex string format
        return self.rgb(r3,g3,b3)

    #Finds the nearest gradient range to use
    def find_nearest(self,arr,val):
        for ival in arr[::-1]:
            if ival <= val:
                return arr.index(ival)
        
    #Create a color map based on passed levels
    def get_cmap(self,levels):
        
        #Add empty color list
        self.colors = []
        
        #Iterate through levels
        for lev in levels:
            
            #Check if level is outside of range
            if lev < self.thres[0]:
                start_hex = self.args[0][0][0]
                if "#" not in start_hex: start_hex = self.rgb(start_hex[0],start_hex[1],start_hex[2])
                self.colors.append(start_hex)
            
            elif lev > self.thres[-1]:
                end_hex = self.args[-1][1][0]
                if "#" not in end_hex: end_hex = self.rgb(end_hex[0],end_hex[1],end_hex[2])
                self.colors.append(end_hex)
                
            else:
                
                #Find closest lower threshold
                idx = self.find_nearest(self.thres_min,lev)
                
                #Retrieve start & end values
                start_value = self.args[idx][0][1]
                end_value = self.args[idx][1][1]
                
                #Calculate start and end RGB tuples, if passed as hex
                start_hex = self.args[idx][1][0]
                end_hex = self.args[idx][0][0]
                if "#" in start_hex:
                    start_hex = start_hex.lstrip('#')
                    end_hex = end_hex.lstrip('#')
                    start_rgb = tuple(int(start_hex[i:i+2], 16) for i in (0, 2 ,4))
                    end_rgb = tuple(int(end_hex[i:i+2], 16) for i in (0, 2 ,4))
                else:
                    start_rgb = start_hex
                    end_rgb = end_hex
    
                #Get hex value for the color at this point in the range
                nrange_color = (end_value - start_value)
                idx = lev - start_value
                hex_val = self.getColor(idx,nrange_color,start_rgb,end_rgb)
                
                #Append color to list
                self.colors.append(hex_val)
        
        #Convert to a colormap and return
        self.cmap = mpl.colors.ListedColormap(self.colors)
        return self.cmap


def rgb2hex(r,g,b):
    """
    Returns the hex string corresponding to the passed rgb values
    """
    r = int(r)
    g = int(g)
    b = int(b)
    return '#%02x%02x%02x' % (r, g, b)


def getColor(position,rng,col1,col2):
    """
    Computes a hex value matching up with the current position relative to the range of colors.
    
    Args:
        position ([type]): current position within the range of colors (e.g., 1)
        rng ([type]): range of colors (e.g. 5, so 1/5 would be 20% of the range)
        col1 ([type]): Starting RGB color for the range (e.g. [0,255,255])
        col2 ([type]): Ending RGB color for the range (e.g. [0,0,255])
    
    Returns:
        [type]: [description]
    """
    
    #Retrieve r,g,b values from tuple
    r1,g1,b1 = col1
    r2,g2,b2 = col2

    #Get difference in each r,g,b value between start & end 
    rdif = float(r2 - r1)
    gdif = float(g2 - g1)
    bdif = float(b2 - b1)
    
    #Calculate r,g,b values for the specified position within the range
    r3 = r2 + (-1.0 * position * (rdif / float(rng)))
    g3 = g2 + (-1.0 * position * (gdif / float(rng)))
    b3 = b2 + (-1.0 * position * (bdif / float(rng)))

    #Return in hex string format
    return rgb2hex(r3,g3,b3)


def list_by_range(*args):
    """
    Returns a list of colors matching up with the range(s) provided
    refer to https://github.com/tomerburg/metlib/blob/master/colors/color_list.py
    
    Examples:
        This is the call to the list_by_range function. Input parameters are as many ranges
        as desired. In this example, there are 2 ranges, one starting from #00FFFF and
        going to #0000FF, with 5 values in the range (where value 1 is the starting color
        and value 5 is the ending color).

        colors = list_by_range(['#00FFFF','#0000FF',5],['#008A05','#00FF09',10])
        print(colors)

    """
    
    #Initialize an empty color list
    colors = []
    
    #Loop through the passed lists, following a format of ['#0000FF','#00FFFF',5]
    #where [0] = start color, [1] = end color, [2] = number of colors in range
    for arg in args:
        
        #Retrieve arguments
        start_hex = arg[1].lstrip('#')
        end_hex = arg[0].lstrip('#')
        nrange_color = arg[2]-1
        
        #Calculate start and end RGB tuples
        start_rgb = tuple(int(start_hex[i:i+2], 16) for i in (0, 2 ,4))
        end_rgb = tuple(int(end_hex[i:i+2], 16) for i in (0, 2 ,4))
            
        #Loop through the number of colors to add into the list
        for x in range(0,nrange_color+1):

            #Get hex value for the color at this point in the range
            hex_val = getColor(x,nrange_color,start_rgb,end_rgb)
            
            #Append to list if this is different than the last color
            if len(colors) == 0 or colors[-1] != hex_val: colors.append(hex_val)
            
    #Return the list of colors
    return colors


def list_by_values(*args):
    """
    Returns a list of colors matching up with the range of numerical values provided
    refer to https://github.com/tomerburg/metlib/blob/master/colors/color_list.py
    
    Examples:
        This is the call to the list_by_values function. Input parameters are as many ranges
        as desired. In this example, there are 3 ranges, one starting from #00FFFF for a value
        of 25 and going to #0000FF for a value of 29.

        colors = list_by_values(
            [['#00FFFF',25.0],['#0000FF',29.0],1.0], [['#0000FF',29.0],['#0000AA',32.0],1.0],
            [['#0000AA',32.0],['#FF00FF',38.0],1.0])
        print(colors)
    """
    
    #Initialize an empty color list
    colors = []
    
    #Loop through the passed lists
    #The format for each argument is: [['#00FFFF',25.0],['#0000FF',29.0],1.0]
    #['#00FFFF',25.0] = [start hex value, start value]
    #['#0000FF',29.0] = [end hex value, end value]
    #1.0 = interval of requested range between start & end values
    for arg in args:
        
        #Retrieve arguments
        start_hex = arg[1][0].lstrip('#')
        end_hex = arg[0][0].lstrip('#')
        start_value = arg[0][1]
        end_value = arg[1][1]
        interval = arg[2]
        
        #Calculate start and end RGB tuples
        start_rgb = tuple(int(start_hex[i:i+2], 16) for i in (0, 2 ,4))
        end_rgb = tuple(int(end_hex[i:i+2], 16) for i in (0, 2 ,4))
            
        #Loop through the number of colors to add into the list
        start_loop = start_value
        end_loop = end_value + interval if arg == args[-1] else end_value
        for x in np.arange(start_loop,end_loop,interval):

            #Get hex value for the color at this point in the range
            nrange_color = (end_value - start_value)
            idx = x - start_value
            hex_val = getColor(idx,nrange_color,start_rgb,end_rgb)
            
            #Append to list if this is different than the last color
            if len(colors) == 0 or colors[-1] != hex_val: colors.append(hex_val)
            
    #Return the list of colors
    return colors


def colorbar(mappable, **kargs):
    """
    Fix the maplotlib colorbar position.
    refer to https://joseph-long.com/writing/colorbars/?s=09

    """
    last_axes = plt.gca()
    ax = mappable.axes
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = fig.colorbar(mappable, cax=cax, **kargs)
    plt.sca(last_axes)
    return cbar


def getColorbarPad(ax, orientation, base_pad=0.0):
    '''Compute padding value for colorbar axis creation
    refer to:
      https://numbersmithy.com/how-to-programmatically-set-the-padding-for-matplotlib-colobar-axis/

    Args:
        ax (Axis obj): axis object used as the parent axis to create colorbar.
        orientation (str): 'horizontal' or 'vertical'.
    Keyword Args:
        base_pad (float): default pad. The resultant pad value is the computed
            space + base_pad.
    Returns:
        pad (float): the pad argument passed to make_axes_gridspec() function.
    '''
    # store axis aspect
    aspect = ax.get_aspect()

    # temporally set aspect to 'auto'
    ax.set_aspect('auto')

    # get renderer
    renderer = ax.get_figure().canvas.get_renderer()

    # get the bounding box of the main plotting area of axis
    b1 = ax.patch.get_extents()

    # get the bounding box the axis
    b2 = ax.get_tightbbox(renderer)
    if orientation == 'horizontal':
        # use the y-coordinate difference as the required pad, plus a base-pad
        bbox = ax.transAxes.inverted().transform([b1.p0, b2.p0])
        print(bbox)
        pad = abs(bbox[0]-bbox[1])[1] + base_pad
    elif orientation == 'vertical':
        # use the x-coordinate difference as the required pad, plus a base-pad
        bbox = ax.transAxes.inverted().transform([b1.p1, b2.p1])
        pad = abs(bbox[0]-bbox[1])[0] + base_pad

    # restore previous aspect
    ax.set_aspect(aspect)
    
    return pad


# Function to take N equally spaced colors from a colormap
def take_cmap_colors(cmap, N, *, cmap_range=(0, 1), return_fmt='float'):
    """
    Takes `N` equally spaced colors from the provided colormap `cmap` and
    returns them.

    Parameters
    ----------
    cmap : str or :obj:`~matplotlib.colors.Colormap` object
        The registered name of the colormap in :mod:`matplotlib.cm` or its
        corresponding :obj:`~matplotlib.colors.Colormap` object.
    N : int or None
        The number of colors to take from the provided `cmap` within the given
        `cmap_range`.
        If *None*, take all colors in `cmap` within this range.

    Optional
    --------
    cmap_range : tuple of float. Default: (0, 1)
        The normalized value range in the colormap from which colors should be
        taken.
        By default, colors are taken from the entire colormap.
    return_fmt : {'float'/'norm'; 'int'/'8bit'; 'str'/'hex'}. Default: 'float'
        The format of the requested colors.
        If 'float'/'norm', the colors are returned as normalized RGB tuples.
        If 'int'/'8bit', the colors are returned as 8-bit RGB tuples.
        If 'str'/'hex', the colors are returned using their hexadecimal string
        representations.

    Returns
    -------
    colors : list of {tuple; str}
        The colors that were taken from the provided `cmap`.

    Examples
    --------
    Taking five equally spaced colors from the 'rainforest' colormap::

        >>> take_cmap_colors('cmr.rainforest', 5)
        [(0.0, 0.0, 0.0),
         (0.226123592, 0.124584033, 0.562997277),
         (0.0548210513, 0.515835251, 0.45667819),
         (0.709615979, 0.722863985, 0.0834727592),
         (1.0, 1.0, 1.0)]

    Requesting their 8-bit RGB values instead::

        >>> take_cmap_colors('cmr.rainforest', 5, return_fmt='int')
        [(0, 0, 0),
         (58, 32, 144),
         (14, 132, 116),
         (181, 184, 21),
         (255, 255, 255)]

    Requesting HEX-code values instead::

        >>> take_cmap_colors('cmr.rainforest', 5, return_fmt='hex')
        ['#000000', '#3A2090', '#0E8474', '#B5B815', '#FFFFFF']

    Requesting colors in a specific range::

        >>> take_cmap_colors('cmr.rainforest', 5, cmap_range=(0.2, 0.8),
                             return_fmt='hex')
        ['#3E0374', '#10528A', '#0E8474', '#5CAD3C', '#D6BF4A']

    Note
    ----
    Using this function on a perceptually uniform sequential colormap, like
    those in *CMasher*, allows one to pick a number of line colors that are
    different but still sequential. This is useful when plotting a set of lines
    that describe the same property, but have a different initial state.

    """

    # Convert provided fmt to lowercase
    return_fmt = return_fmt.lower()

    # Obtain the colormap
    cmap = mplcm.get_cmap(cmap)

    # Check if provided cmap_range is valid
    if not ((0 <= cmap_range[0] <= 1) and (0 <= cmap_range[1] <= 1)):
        raise ValueError("Input argument 'cmap_range' does not contain "
                         "normalized values!")

    # Extract and convert start and stop to their integer indices (inclusive)
    start = int(np.floor(cmap_range[0]*cmap.N))
    stop = int(np.ceil(cmap_range[1]*cmap.N))-1

    # Pick colors
    if N is None:
        index = np.arange(start, stop+1, dtype=int)
    else:
        index = np.array(np.rint(np.linspace(start, stop, num=N)), dtype=int)
    colors = cmap(index)

    # Convert colors to proper format
    if return_fmt in ('float', 'norm', 'int', '8bit'):
        colors = np.apply_along_axis(to_rgb, 1, colors)
        if return_fmt in ('int', '8bit'):
            colors = np.array(np.rint(colors*255), dtype=int)
        colors = list(map(tuple, colors))
    else:
        colors = list(map((lambda x: to_hex(x).upper()), colors))

    # Return colors
    return(colors)


# Function create a colormap using a subset of the colors in an existing one
def get_sub_cmap(cmap, start, stop, *, N=None):
    """
    Creates a :obj:`~matplotlib.cm.ListedColormap` object using the colors in
    the range `[start, stop]` of the provided `cmap` and returns it.

    This function can be used to create a colormap that only uses a portion of
    an existing colormap.
    If `N` is not set to *None*, this function creates a qualitative colormap
    from `cmap` instead.

    Parameters
    ----------
    cmap : str or :obj:`~matplotlib.colors.Colormap` object
        The registered name of the colormap in :mod:`matplotlib.cm` or its
        corresponding :obj:`~matplotlib.colors.Colormap` object.
    start, stop : float
        The normalized range of the colors in `cmap` that must be in the
        sub-colormap.

    Optional
    --------
    N : int or None. Default: None
        The number of color segments to take from the provided `cmap` within
        the range given by the provided `start` and `stop`.
        If *None*, take all colors in `cmap` within this range.

    Returns
    -------
    sub_cmap : :obj:`~matplotlib.colors.ListedColormap`
        The created colormap that uses a subset of the colors in `cmap`.
        If `N` is not *None*, this will be a qualitative colormap.

    Example
    -------
    Creating a colormap using the first 80% of the 'rainforest' colormap::

        >>> get_sub_cmap('cmr.rainforest', 0, 0.8)

    Creating a qualitative colormap containing five colors from the middle 60%
    of the 'lilac' colormap:

        >>> get_sub_cmap('cmr.lilac', 0.2, 0.8, N=5)

    Notes
    -----
    As it can create artifacts, this function does not interpolate between the
    colors in `cmap` to fill up the space. Therefore, using values for `start`
    and `stop` that are too close to each other, may result in a colormap that
    contains too few different colors to be smooth.
    It is recommended to use at least 128 different colors in a colormap for
    optimal results (*CMasher* colormaps have 256 or 511/510 different colors,
    for sequential or diverging/cyclic colormaps respectively).
    One can check the number of colors in a colormap with
    :attr:`matplotlib.colors.Colormap.N`.

    Any colormaps created using this function are not registered in either
    *CMasher* or *MPL*.

    """

    # Obtain the colormap
    cmap = mplcm.get_cmap(cmap)

    # Check value of N to determine suffix for the name
    suffix = '_sub' if N is None else '_qual'

    # Obtain colors
    colors = take_cmap_colors(cmap, N, cmap_range=(start, stop))

    # Create new colormap
    sub_cmap = ListedColormap(colors, cmap.name+suffix, N=len(colors))

    # Return sub_cmap
    return(sub_cmap)


def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    '''
    Extract a subset of a colormap as a new colormap in matplotlib.
        
    https://stackoverflow.com/a/18926541
    '''
    if isinstance(cmap, str):
        cmap = plt.get_cmap(cmap)
    new_cmap = mpl.colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap