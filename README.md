# 气象数据绘图功能
提供气象绘图功能函数, 包括颜色表处理, 屏蔽区域, 添加地图边界, 绘制天气分析图等.

Only Python 3 is supported.

## Dependencies
Other required packages:

- numpy
- matplotlib
- basemap
- netCDF4
- pandas
- pyshp
- cartopy
- Shapely

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