# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Load colormaps from a variety of sources, mainly .cpt though

refer to:
https://github.com/j08lue/pycpt
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from urllib.parse import urljoin
from urllib.request import urlretrieve, urlopen, Request
import colorsys
import os
import fnmatch
import copy
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.colorbar import ColorbarBase


def cmap_xmap(function, cmap, name=None):
    """
    Applies function on the indices of colormap cmap. Beware, function
    should map the [0, 1] segment to itself, or you are in for surprises.
    """
    cmap = copy.deepcopy(cmap)
    cdict = cmap._segmentdata
    for key in cdict:
        cdict[key] = sorted([(function(x[0]), x[1], x[2]) for x in cdict[key]])
    if name is not None:
        cmap.name = name
    return mcolors.LinearSegmentedColormap(cmap.name, cdict, cmap.N)


def reverse_cmap(cmap, newname=None):
    """
    Reverse a given matplotlib colormap instance
    """
    if newname is None:
        newname = cmap.name + '_r'
    return cmap_xmap(lambda x: -1.*(x-1.), cmap, name=newname)


def generate_cmap_norm(levels, cm, extend='neither',
                       name='from_list', return_dict=False):
    """
    Generate a color map and norm from levels and a colormap (name)

    Parameters
    ----------
    levels : iterable of levels
        data levels
    cm : cmap or name of registered cmap
        color map
    extend : str [ neither | both | min | max ]
        which edge(s) of the color range to extend
    name : str, optional
        new name for colormap
    return_dict : bool
        return dictionary
    """
    if isinstance(cm, str):
        cm = plt.get_cmap(cm)
    nplus = [-1, 0, 0, 1][['neither', 'min', 'max', 'both'].index(extend)]
    N = len(levels) + nplus
    colors = cm(np.linspace(0, 1, N))
    cmap = mcolors.ListedColormap(colors, name=(name or cm.name))
    if extend in ['min', 'both']:
        cmap.set_under(colors[0])
    else:
        cmap.set_under('none')
    if extend in ['max', 'both']:
        cmap.set_over(colors[-1])
    else:
        cmap.set_over('none')
    cmap.colorbar_extend = extend
    norm = mcolors.BoundaryNorm(levels, N)
    if return_dict:
        return dict(cmap=cmap, norm=norm)
    else:
        return cmap, norm


def _cmap_name_from_path(fpath, root='cpt-city', maxdepth=5):
    """
    Generates a colormap name from a path

    Parameters
    ----------
    fpath : str
        full fpath to cpt file
    root : str, optional
        base path
    maxdepth : int
        max depth of path to include in cmap name

    Function will parse the path down to *root* or
    until *maxdepth* is reached.
    """
    fpath = os.path.splitext(fpath)[0]
    prename = ''
    end = ''
    for i in range(maxdepth):
        fpath, end = os.path.split(fpath)
        if end == root:
            break
        elif end != '':
            if prename == '':
                prename = end
            else:
                prename = end+'/'+prename
    return prename


def find_cpt_files(cmapdir, **kwargs):
    """
    Find .cpt files in a given path and generate names

    Parameters
    ----------
    cmapdir : str
        directory below which the files are
    kwargs : dict
        keyword arguments passed to _cmap_name_from_path()
    """
    cptcitycmaps = {}
    for root, dirnames, filenames in os.walk(cmapdir):
        for filename in fnmatch.filter(filenames, '*.cpt'):
            cmapfile = os.path.join(root, filename)
            cmapname = _cmap_name_from_path(cmapfile, **kwargs)
            cptcitycmaps[cmapname] = cmapfile

    return cptcitycmaps


def register_cptcity_cmaps(cptcitycmaps, urlkw={}, cmapnamekw={}):
    """
    Register cpt-city colormaps from a list of URLs
    and/or files to the current plt.cm space

    Parameters
    ----------
    cptcitycmaps : str, dict, or list
        str will be interpreted as path to scan for .cpt files
        list over file names or urls to .cpt files
        dict can be used to provide (name : fname/url) mappings
    urlkw : dict
        keyword arguments passed to cmap_from_cptcity_url

    Usage
    -----
    To register a set of color maps, use, e.g.

        register_cptcity_cmaps({'ncl_cosam' :
        "http://soliton.vm.bytemark.co.uk/pub/cpt-city/ncl/cosam.cpt"})

    Retrieve the cmap using,

        plt.cm.get_cmap('ncl_cosam')

    """
    def _register_with_reverse(cmap):
        plt.cm.register_cmap(cmap=cmap)
        plt.cm.register_cmap(cmap=reverse_cmap(cmap))

    def _try_reading_methods(cmapfile, cmapname=None):
        try:
            return gmtColormap(cmapfile, name=cmapname)
        except IOError:
            try:
                return cmap_from_cptcity_url(cmapfile, name=cmapname, **urlkw)
            except:
                raise

    if isinstance(cptcitycmaps, str):
        if cptcitycmaps.endswith('.cpt'):
            cptcitycmaps = [cptcitycmaps]
        else:
            cptcitycmaps = find_cpt_files(cptcitycmaps, **cmapnamekw)

    cmaps = []

    if isinstance(cptcitycmaps, dict):
        for cmapname, cmapfile in cptcitycmaps.items():
            cmap = _try_reading_methods(cmapfile, cmapname)
            _register_with_reverse(cmap)
            cmaps.append(cmap)
    else:
        for cmapfile in cptcitycmaps:
            cmap = _try_reading_methods(cmapfile)
            _register_with_reverse(cmap)
            cmaps.append(cmap)

    return cmaps


def gmtColormap_openfile(cptf, name=None):
    """Read a GMT color map from an OPEN cpt file

    Parameters
    ----------
    cptf : open file or url handle
        path to .cpt file
    name : str, optional
        name for color map
        if not provided, the file name will be used
    """
    # generate cmap name
    if name is None:
        name = '_'.join(os.path.basename(cptf.name).split('.')[:-1])

    # process file
    x = []
    r = []
    g = []
    b = []
    lastls = None
    for l in cptf.readlines():
        ls = l.split()

        # skip empty lines
        if not ls:
            continue

        # parse header info
        if ls[0] in ["#", b"#"]:
            if ls[-1] in ["HSV", b"HSV"]:
                colorModel = "HSV"
            else:
                colorModel = "RGB"
            continue

        # skip BFN info
        if ls[0] in ["B", b"B", "F", b"F", "N", b"N"]:
            continue

        # parse color vectors
        x.append(float(ls[0]))
        r.append(float(ls[1]))
        g.append(float(ls[2]))
        b.append(float(ls[3]))

        # save last row
        lastls = ls

    x.append(float(lastls[4]))
    r.append(float(lastls[5]))
    g.append(float(lastls[6]))
    b.append(float(lastls[7]))

    x = np.array(x)
    r = np.array(r)
    g = np.array(g)
    b = np.array(b)

    if colorModel == "HSV":
        for i in range(r.shape[0]):
            # convert HSV to RGB
            rr, gg, bb = colorsys.hsv_to_rgb(r[i]/360., g[i], b[i])
            r[i] = rr
            g[i] = gg
            b[i] = bb
    elif colorModel == "RGB":
        r /= 255.
        g /= 255.
        b /= 255.

    red = []
    blue = []
    green = []
    xNorm = (x - x[0])/(x[-1] - x[0])
    for i in range(len(x)):
        red.append([xNorm[i], r[i], r[i]])
        green.append([xNorm[i], g[i], g[i]])
        blue.append([xNorm[i], b[i], b[i]])

    # return colormap
    cdict = dict(red=red, green=green, blue=blue)
    return mcolors.LinearSegmentedColormap(name=name, segmentdata=cdict)


def gmtColormap(cptfile, name=None):
    """
    Read a GMT color map from a cpt file

    Parameters
    ----------
    cptfile : str or open file-like object
        path to .cpt file
    name : str, optional
        name for color map
        if not provided, the file name will be used
    """
    with open(cptfile, 'r') as cptf:
        return gmtColormap_openfile(cptf, name=name)


def cmap_from_cptcity_url(
        url, baseurl='http://soliton.vm.bytemark.co.uk/pub/cpt-city/',
        download=False, name=None):
    """
    Create a colormap from a url at cptcity

    Parameters
    ----------
    url : str
        relative or absolute URL to a .cpt file
    baseurl : str, optional
        main directory at cptcity
    download : bool
        whether to download the colormap file to the current working directory
    name : str, optional
        name for color map
    """
    if name is None:
        name = '_'.join(os.path.basename(url).split('.')[:-1])

    url = urljoin(baseurl, url)

    if download:
        fname = os.path.basename(url)
        urlretrieve(url, fname)
        return gmtColormap(fname, name=name)

    else:
        # process file directly from online source
        response = urlopen(url)
        return gmtColormap_openfile(response, name=name)


def cmap_from_geo_uoregon(
        cname, baseurl='http://geog.uoregon.edu/datagraphics/color/',
        download=False):
    """
    Parse an online file from geography.uoregon.edu
    to create a Python colormap
    """
    ext = '.txt'

    url = urljoin(baseurl, cname+ext)
    print(url)

    # process file directly from online source
    req = Request(url)
    response = urlopen(req)
    rgb = np.loadtxt(response, skiprows=2)

    # save original file
    if download:
        fname = os.path.basename(url) + ext
        urlretrieve(url, fname)

    return mcolors.ListedColormap(rgb, cname)


def colormap_demo(cmap):
    """
    Make a demo plot of a given colormap with random data.
    """
    fig = plt.figure()
    ax = fig.gca()
    img = ax.pcolor(np.random.rand(10, 10), cmap=cmap)
    cb = plt.colorbar(img)
    cb.ax.set_ylim(cb.ax.get_ylim()[::-1])
    fig.show()
    return fig


def plot_colormaps(cmap_list):
    """
    Plot a list of color gradients with their names

    Credits
    -------
    http://matplotlib.org/examples/color/colormaps_reference.html
    """
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    fig, axes = plt.subplots(
            nrows=len(cmap_list),
            figsize=(6, .5*len(cmap_list)))
    fig.subplots_adjust(top=1, bottom=0, left=0, right=0.9)

    for ax, cmap in zip(axes, cmap_list):
        if isinstance(cmap, basestring):
            cmap = plt.get_cmap(cmap)
        ax.imshow(gradient, aspect='auto', cmap=cmap)
        pos = list(ax.get_position().bounds)
        x_text = pos[0] + pos[2] + 0.02
        y_text = pos[1] + pos[3]/2.
        fig.text(x_text, y_text, cmap.name,
                 va='center', ha='left', fontsize=12)

    # Turn off *all* ticks & spines, not just the ones with colormaps.
    for ax in axes:
        ax.set_axis_off()

    return fig


def plot_colormap(cmap, continuous=True, discrete=True, ndisc=9):
    """
    Make a figure displaying the color map in continuous and/or discrete form
    """
    nplots = int(continuous) + int(discrete)
    fig, axx = plt.subplots(figsize=(6, .5*nplots),
                            nrows=nplots, frameon=False)
    axx = np.asarray(axx)
    i = 0
    if continuous:
        norm = mcolors.Normalize(vmin=0, vmax=1)
        ColorbarBase(axx.flat[i], cmap=cmap, norm=norm,
                     orientation='horizontal')
    if discrete:
        colors = cmap(np.linspace(0, 1, ndisc))
        cmap_d = mcolors.ListedColormap(colors, name=cmap.name)
        norm = mcolors.BoundaryNorm(np.linspace(0, 1, ndisc+1), len(colors))
        ColorbarBase(axx.flat[i], cmap=cmap_d,
                     norm=norm, orientation='horizontal')
    for ax in axx.flat:
        ax.set_axis_off()
    fig.text(0.95, 0.5, cmap.name, va='center', ha='left', fontsize=12)


def show_matplotlib_colormaps():
    """
    Plot a list of all colormaps distributed with matplotlib
    """
    cmaps = [m for m in plt.cm.datad if not m.endswith('_r')]
    cmaps.sort()
    return plot_colormaps(cmaps)


def demo_uoregon():
    """
    Plot a demo of a color map from University of Oregon
    """
    cmap = cmap_from_geo_uoregon('BuOr_8')
    colormap_demo(cmap)


def demo_gmt():
    """
    Plot a demo of a .cpt / GMT color map from cptcity
    """
    cmap = cmap_from_cptcity_url(
        'http://soliton.vm.bytemark.co.uk/pub/'
        'cpt-city/ma/gray/grayscale02.cpt')
    colormap_demo(cmap)


if __name__ == 'main':
    demo_uoregon()
    demo_gmt()
