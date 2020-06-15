# _*_ coding: utf-8 _*_

from os import path
from setuptools import setup, find_packages
from codecs import open

name = "nmc_met_graphics"
author = __import__(name).__author__
version = __import__(name).__version__

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# setup
setup(
    name=name,

    version=version,

    description='A collection for meteorological graphic functions.',
    long_description=long_description,

    # author
    author=author,
    author_email='kan.dai@foxmail.com',

    # LICENSE
    license='GPL3',

    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 3',
    ],

    packages=find_packages(exclude=['tests', 'examples']),
    include_package_data=True,
    exclude_package_data={'': ['.gitignore']},

    install_requires=['numpy', 'matplotlib', 'xarray', 'pandas',
                      'cartopy', 'metpy', 'netCDF4', 'pyshp', 'Shapely'],
    python_requires='>=3',
    zip_safe = False
)

# development mode (DOS command):
#     python setup.py develop
#     python setup.py develop --uninstall

# build mode：
#     python setup.py build --build-base=D:/test/python/build

# distribution mode:
#     python setup.py sdist             # create source tar.gz file in /dist
#     python setup.py bdist_wheel       # create wheel binary in /dist
