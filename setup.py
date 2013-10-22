# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the gumpdata package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
""""""

import os
import sys
from os.path import join as opj
import gumpdata
from distutils.core import setup
from glob import glob


__docformat__ = 'restructuredtext'

extra_setuptools_args = {}
if 'setuptools' in sys.modules:
    extra_setuptools_args = dict(
        tests_require=['nose'],
        test_suite='nose.collector',
        zip_safe=False,
        extras_require = dict(
            doc='Sphinx>=0.3',
            test='nose>=0.10.1')
    )

def main(**extra_args):
    setup(name         = 'gumpdata',
          version      = gumpdata.__version__,
          author       = 'Michael Hanke and the gumpdata developers',
          author_email = 'michael.hanke@gmail.com',
          license      = 'MIT License',
          url          = 'https://github.com/neurodebian/gumpdata',
          download_url = 'https://github.com/neurodebian/gumpdata/tags',
          description  = 'test and evaluate heterogeneous data processing pipelines',
          long_description = open('README.rst').read(),
          classifiers  = ["Development Status :: 3 - Alpha",
                          "Environment :: Console",
                          "Intended Audience :: Science/Research",
                          "License :: OSI Approved :: MIT License",
                          "Operating System :: OS Independent",
                          "Programming Language :: Python",
                          "Topic :: Scientific/Engineering"],
          platforms    = "OS Independent",
          provides     = ['gumpdata'],
          # please maintain alphanumeric order
          packages     = [ 'gumpdata',
                           'gumpdata.io',
                           'gumpdata.tests',
                           ],
          )

if __name__ == "__main__":
    main(**extra_setuptools_args)
