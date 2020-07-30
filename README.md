# 气象数据绘图功能

提供气象绘图功能函数, 包括颜色表处理, 屏蔽区域, 添加地图边界, 绘制天气分析图等.

Only Python 3 is supported.
建议安装[Anaconda](https://www.anaconda.com/products/individual)数据科学工具库,
已包括scipy, numpy, matplotlib等大多数常用科学程序库.

## Install

Using the fellowing command to install packages:

* 预安装程序库
```
  conda install -c conda-forge cartopy
```

* 使用pypi安装源安装(https://pypi.org/project/nmc-met-graphics/)
```
  pip install nmc-met-graphics
```

* 若要安装Github上的开发版(请先安装[Git软件](https://git-scm.com/)):
```
  pip install git+git://github.com/nmcdev/nmc_met_graphics.git
```

* 或者下载软件包进行安装:
```
  git clone --recursive https://github.com/nmcdev/nmc_met_graphics.git
  cd nmc_met_graphics
  python setup.py install
```

### 可选支持库:

* [Magics](https://anaconda.org/conda-forge/magics), `conda install -c conda-forge magics`

