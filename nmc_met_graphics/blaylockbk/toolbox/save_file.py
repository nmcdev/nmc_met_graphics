## Brian Blaylock
## November 22, 2019

"""
=====================
Saving Data as Output
=====================

Various methods for saving data as output

    - xarray_to_netcdf_compressed
    
"""

import xarray
import os
from BB_utils.stock import full_path


def xarray_to_netcdf_compressed(ds, outfile, level=5):
    """
    Save a xarray DataSet as a NetCDF file, with compression.

    Parameters
    ----------
    ds : xarray.DataSet
        An xarray DataSet you wish to save as a netcdf file.
    outfile : str
        The path and file name string to save the file.
        E.g., '/path/to/dir/name.nc`
    level : int {1, 2, 3, 4, 5, 6, 7, 8, 9}
        Compression level between 0 and 9.
        Default is 5.
    """
    # Replace '~', '..', and '$CENTER' envrionment variables with path.
    outfile = full_path(outfile)

    # Create the directory path if it doesn't exist
    OUTDIR = "/".join(outfile.split("/")[:-1])
    if not os.path.exists(OUTDIR):
        os.makedirs(OUTDIR)
        print(f"Created Path: {OUTDIR}")

    # Specify compression and encoding for each variable in ds
    comp = dict(zlib=True, complevel=5)

    encoding = {var: comp for var in ds.data_vars}
    ds.to_netcdf(outfile, encoding=encoding)

    print(f"Saved: {outfile}")
