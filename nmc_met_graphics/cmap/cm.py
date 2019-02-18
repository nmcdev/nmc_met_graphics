# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
  Some color map functions.
"""

import os
import sys
import re
import glob
import pkg_resources
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm
from matplotlib import colors
from matplotlib.colors import ListedColormap, to_rgb, LinearSegmentedColormap


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
