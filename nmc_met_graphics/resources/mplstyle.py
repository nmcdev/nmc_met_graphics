# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.


import pkg_resources


def get_style_file(name='gadfly'):
    """
    return the matplotlib style file
    
    Args:
        name (string, optional): the matplotlib style file name in resources/mplstyle/ directory.
            gadfly, https://towardsdatascience.com/a-new-plot-theme-for-matplotlib-gadfly-2cffc745ff84
            qb_dark, qb_light, https://github.com/quantumblacklabs/qbstyles
            kit, https://camminady.org/kitstyle/

    Examples:
    >>> plt.style.use(get_style_file(name='gadfly'))
    """

    file_path = pkg_resources.resource_filename(
        "nmc_met_graphics", "resources/mplstyle/"+name+".mplstyle")
    return file_path
