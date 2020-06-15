# 气象数据绘图功能
提供气象绘图功能函数, 包括颜色表处理, 屏蔽区域, 添加地图边界, 绘制天气分析图等.

Only Python 3 is supported.
建议安装[Anaconda](https://www.anaconda.com/products/individual)数据科学工具库,
已包括scipy, numpy, matplotlib等大多数常用科学程序库.

## Dependencies
请预先安装下列程序库:

- [Cartopy](https://scitools.org.uk/cartopy/docs/latest/), `conda install -c conda-forge cartopy`
- [Numpy](https://numpy.org/), `conda install -c conda-forge numpy`
- [Matplotlib](https://matplotlib.org/),`conda install -c conda-forge matplotlib`
- [Xarray](https://github.com/pydata/xarray), `conda install -c conda-forge xarray`
- [Pandas](https://anaconda.org/conda-forge/pandas), `conda install -c conda-forge pandas`
- [Metpy](https://anaconda.org/conda-forge/metpy), `conda install -c conda-forge metpy`
- [netCDF4](http://github.com/Unidata/netcdf4-python), `conda install -c conda-forge netcdf4`
- [pyshp](https://pypi.python.org/pypi/pyshp), `conda install -c conda-forge pyshp`
- [Shapely](https://anaconda.org/conda-forge/pyshp), `conda install -c conda-forge pyshp`
- [Magics](https://anaconda.org/conda-forge/magics), 可选 `conda install -c conda-forge magics`
- [nmc_met_io](https://github.com/nmcdev/nmc_met_io), 详见说明
- [nmc_met_base](https://github.com/nmcdev/nmc_met_base), 详见说明.

## Install
Using the fellowing command to install packages:
```
  pip install git+git://github.com/nmcdev/nmc_met_graphics.git
```

or download the package and install:
```
  git clone --recursive https://github.com/nmcdev/nmc_met_graphics.git
  cd nmc_met_graphics
  python setup.py install
```