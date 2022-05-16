# _*_ coding: utf-8 _*_

# Copyright (c) 2022 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Create animate image.
"""

import imageio


def as_gif(png_files, fname="new_gif", fps=8):
    """
    Turn a list of image files into an animated gif.

    From Andrew Huang:

    Parameters
    ----------
    png_files : list
        A list of image file paths
    fname : str
        A name for the gif file being created. Default is 'new_gif'
    fps : int
        Frames per second. Default is 8.

    Returns
    -------
    The file name of the new animated gif file.
    """
    gif_file = f"{fname}.gif"
    # Note: mode 'I' means multiple images.
    with imageio.get_writer(gif_file, mode="I", fps=fps) as writer:
        for png_file in png_files:
            if isinstance(png_file, str):
                image = imageio.imread(png_file)
                writer.append_data(image)
    return gif_file