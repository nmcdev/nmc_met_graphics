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
    long_description_content_type='text/markdown',
    url='https://github.com/nmcdev/nmc_met_graphics',

    # author
    author=author,
    author_email='kan.dai@foxmail.com',

    # LICENSE
    license='GPL3',

    classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Topic :: Scientific/Engineering',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3.7',
      'Programming Language :: Python :: 3.8',
      'Operating System :: POSIX :: Linux',
      'Operating System :: MacOS :: MacOS X',
      'Operating System :: Microsoft :: Windows'],
    
    python_requires='>=3.6',
    zip_safe = False,
    platforms = ["all"],

    packages=find_packages(exclude=[
      'documents', 'docs', 'examples', 'notebooks', 'tests', 'build', 'dist']),
    include_package_data=True,
    exclude_package_data={'': ['.gitignore']},

    install_requires=[
      'numpy>=1.17.0',
      'scipy>=1.4.0',
      'pandas>=1.0.0',
      'xarray>=0.16.0',
      'matplotlib>=2.2.5',
      'Cartopy>=0.17.0',
      'metpy>=0.12.0',
      'netCDF4>=1.5.3',
      'pyshp>=2.1.0',
      'Shapely>=1.7.0',
      'Pillow>=7.0.0',
      'nmc-met-io>=0.1.0',
      'nmc-met-base>=0.1.0']
)

# development mode (DOS command):
#     python setup.py develop
#     python setup.py develop --uninstall

# build mode：
#     python setup.py build --build-base=D:/test/python/build

# distribution mode:
#     python setup.py sdist build              # create source tar.gz file in /dist
#     twine upload --skip-existing dist/*      # upload package to pypi
