## Brian Blaylock
## November 26, 2021

"""
=============
Simple Colors
=============

20 simple, distinct colors from Sasha Trubetskoy

https://sashamaps.net/docs/resources/20-colors/

If you want to use these colors as your matplotlib color cycle just do

    from paint.simple_colors import simple_colors
    simple_colors().set_rcParams

"""

from cycler import cycler
import matplotlib as mpl

# 95% accessible colors
simple_colors_9500 = {
    "Red": "#e6194B",
    "Green": "#3cb44b",
    "Yellow": "#ffe119",
    "Blue": "#4363d8",
    "Orange": "#f58231",
    "Purple": "#911eb4",
    "Cyan": "#42d4f4",
    "Magenta": "#f032e6",
    "Lime": "#bfef45",
    "Pink": "#fabed4",
    "Teal": "#469990",
    "Lavender": "#dcbeff",
    "Brown": "#9A6324",
    "Beige": "#fffac8",
    "Maroon": "#800000",
    "Mint": "#aaffc3",
    "Olive": "#808000",
    "Apricot": "#ffd8b1",
    "Navy": "#000075",
    "Grey": "#a9a9a9",
    "White": "#ffffff",
    "Black": "#000000",
}

# 99% accessible colors
simple_colors_9900 = {
    "Red": "#e6194B",
    "Green": "#3cb44b",
    "Yellow": "#ffe119",
    "Blue": "#4363d8",
    "Orange": "#f58231",
    "Cyan": "#42d4f4",
    "Magenta": "#f032e6",
    "Pink": "#fabed4",
    "Teal": "#469990",
    "Lavender": "#dcbeff",
    "Brown": "#9A6324",
    "Beige": "#fffac8",
    "Maroon": "#800000",
    "Mint": "#aaffc3",
    "Navy": "#000075",
    "Grey": "#a9a9a9",
    "White": "#ffffff",
    "Black": "#000000",
}

# 99.99% accessible colors
simple_colors_9999 = {
    "Yellow": "#ffe119",
    "Blue": "#4363d8",
    "Orange": "#f58231",
    "Lavender": "#dcbeff",
    "Maroon": "#800000",
    "Navy": "#000075",
    "Grey": "#a9a9a9",
    "White": "#ffffff",
    "Black": "#000000",
}

# 100% accessible colors
simple_colors_10000 = {
    "Yellow": "#ffe119",
    "Blue": "#4363d8",
    "Grey": "#a9a9a9",
    "White": "#ffffff",
    "Black": "#000000",
}


class simple_colors:
    """
    Class for 20 simple, distinct colors (plus black and white).

    Examples
    --------
    To cycle through these colors with Matplotlib, do
    >>> from paint.simple_colors import simple_colors
    >>> simple_colors().set_rcParams
    """

    def __init__(self, accessibility=0.95):
        """
        Parameters
        ----------
        accessibility: float
            Get colors that are at a level of accessibility.
            Default 20 colors (plus black and white) is 95% accessible.
        """
        self.accessibility = accessibility

        if accessibility == 1:
            self.colors = simple_colors_10000
        elif accessibility >= 0.9999:
            self.colors = simple_colors_9999
        elif accessibility >= 0.99:
            self.colors = simple_colors_9900
        else:
            self.colors = simple_colors_9500

        self.color_list = [i for _, i in self.colors.items()]

    @property
    def cycler(self):
        """Create a cycler object with the color list"""
        return cycler(color=self.color_list)

    @property
    def set_rcParams(self):
        """Set the Matplotlib rcParams to cycle through the colors"""
        mpl.rcParams["axes.prop_cycle"] = self.cycler
