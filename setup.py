'''
Created on May 1, 2016

@author: David Stocker
'''

from distutils.core import setup
setup(
  name = 'ghcndextractor',
  packages = ['ghcndextractor'], # this must be the same as the name above
  version = '0.2',
  description = 'A simple extractor for the GHCN-Daily dataset .dly files into CSV or dict format.',
  author = 'David Stocker',
  author_email = 'mrdave991@gmail.com',
  url = 'https://github.com/davidhstocker/ghcndextractor', # use the URL to the github repo
  download_url = 'https://github.com/davidhstocker/ghcndextractor/tarball/0.2', 
  keywords = ['ghcnd', 'ghcnddaily', 'climatedata'], # arbitrary keywords
  classifiers = [],
)
