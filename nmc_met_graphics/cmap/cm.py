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
import matplotlib.cm
from matplotlib import colors
from matplotlib.colors import ListedColormap, to_rgb, LinearSegmentedColormap
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


def _to_hex(c):
    """Convert arbitray color specification to hex string."""
    ctype = type(c)

    # Convert rgb to hex.
    if ctype is tuple or ctype is np.ndarray or ctype is list:
        return colors.rgb2hex(c)

    if ctype is str:
        # If color is already hex, simply return it.
        regex = re.compile('^#[A-Fa-f0-9]{6}$')
        if regex.match(c):
            return c

        # Convert named color to hex.
        return colors.cnames[c]

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
    cmap = colors.LinearSegmentedColormap.from_list(name, cmap_data)
    plt.register_cmap(name, cmap)

    return cmap


def make_cmap_list(color_list):
    """
    Making color map from color list.

    :param color_list: color list, like ["whitesmoke","dimgray"].
    :return: matplotlib color map.
    """

    # from_list(name, colors, N=256, gamma=1.0)
    return colors.LinearSegmentedColormap.from_list('', color_list)


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
    fig, ax = plt.subplots(figsize=(6,0.5))
    col_map = plt.get_cmap(cmap)
    mpl.colorbar.ColorbarBase(ax, cmap=col_map, orientation = 'horizontal')
    plt.show()


def ncl_cmaps(name):
    """
    Get the ncl color maps.

    :param name: color map name.
    :return: matlibplot color map.
    """

    # color map file directory
    cmap_file = pkg_resources.resource_filename(
        "nmc_met_graphics", "resources/colormaps_ncl/" + name + '.rgb')
    if not os.path.isfile(cmap_file):
        return None

    # read color data
    pattern = re.compile(r'(\d\.?\d*)\s+(\d\.?\d*)\s+(\d\.?\d*)\n')
    with open(cmap_file) as cmap:
        cmap_buff = cmap.read()
    if re.search(r'\s*\d\.\d*', cmap_buff):
        rgb = np.asarray(pattern.findall(cmap_buff), 'f4')
    else:
        rgb = np.asarray(pattern.findall(cmap_buff), 'u1') / 255.

    # construct color map
    return ListedColormap(rgb, name=name)


def guide_cmaps(name):
    """
    Get guide color maps.

    :param name: guide color name number, like 42.
    :return: matplotlib color map.
    """

    # color map file directory
    cmap_file = pkg_resources.resource_filename(
        "nmc_met_graphics", "resources/colormaps_guide/cs" + str(name) + '.txt')
    if not os.path.isfile(cmap_file):
        return None

    # read color data
    rgb = np.loadtxt(cmap_file)

    # construct color map
    return ListedColormap(rgb/255, name=name)


def ndfd_cmaps(name):
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
        return None

    # read color data
    rgb = gmtColormap_openfile(cmap_file, name)

    # construct color map
    return rgb


def ndfd_cmaps_show():
    """  
    Show all ndfd color maps.
    """
    cmap_dir = pkg_resources.resource_filename(
        "nmc_met_graphics", "resources/colormaps_ndfd/")
    
    for file in pathlib.Path(cmap_dir).glob("*.cpt"):
        cptf = open(file, 'r')
        color = gmtColormap_openfile(cptf, file.name)
        plot_colorMaps(color)


class MidpointNormalize(colors.Normalize):
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
        colors.Normalize.__init__(self, vmin, vmax, clip)

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

            cmap = colors.ListedColormap(self._coltbl(cmap_file), name=cname)
            matplotlib.cm.register_cmap(name=cname, cmap=cmap)
            self._cmap_d[cname] = cmap

            cname = cname + '_r'
            cmap = colors.ListedColormap(self._coltbl(cmap_file)[::-1],
                                         name=cname)
            matplotlib.cm.register_cmap(name=cname, cmap=cmap)
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
        self.cmap = colors.ListedColormap(self.colors)
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

