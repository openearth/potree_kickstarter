from setuptools import setup

setup(name='generate potree',
      version='0.1',
      description='Download ahn2 tile and convert to potree',
      url='https://github.com/evetion/potree_kickstarter',
      author='',
      author_email='',
      license='',
      packages=['potree_kickstarter'],
      scripts=['bin/generate_potree'],
      install_requires=[
      		'logging',
      		'numpy',
      		'matplotlib',
      		'owslib',
      		'shapely',
      		'liblas',
      		'lxml',
      		'gdal',
      		'mako',
      		'docopt'
      ],
      zip_safe=False)
