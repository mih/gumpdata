======================================
"Forrest Gump" data release IO package
======================================

This repository contains code and data file associated with the "Forrest Gump"
functional magnetic resonance imaging (fMRI) data release. This includes the
scripts used to convert all data from its raw formats into the respective
released form. Data conversion also covers de-identification.

A minimal Python module for data access is provided that serves as a reference
implementation and executable documentation for data organization. Moreover, the
module comes with a set of unit tests that verify certain aspects of data
integrity and known anomalies.

More information on the dataset can be found in Hanke et al. (201x)

.. link list

`Bug tracker <https://github.com/hanke/gumpdata/issues>`_ |
`Documentation <https://gumpdata.readthedocs.org>`_ |
`Downloads <https://github.com/hanke/gumpdata/tags>`_

Repository content
==================

``data/deface/``
  Templates and mask images for the de-facing procedure
``doc/``
  API documentation source files
``gumpdata/``
  Python data access module
``scripts/conversion/``
  Scripts used to convert data from its raw into the released form
``scripts/figures/``
  Scripts to produce figures in the data paper
``scripts/openfmri/``
  Configuration file for the openfmri_helpers package for producing the group
  template images
``scripts/similarity_analysis/``
  Scripts to perform the univariate and multivariate pattern similarity analysis
  in the data paper

Dataset tests
=============

The ``gumpdata`` Python module comes with a number of tests to verify data
integrity and consistency. These tests can be executed using Python ``nose``
package or a similar test framework.

Enter the root directory containing the data release files and run
``nosetests``, while setting the PYTHONPATH environment variable to point to
the directory with the content of this repository::

  $ PYTHONPATH=<path-to-repo-checkout>:$PYTHONPATH nosetests

This will execute all available tests. The source of the tests is also
executable documentation for the data access API.

License
=======

All code is licensed under the terms of the MIT license, or some equally liberal
alternative license. Please see the COPYING file in the source distribution for
more detailed information.


