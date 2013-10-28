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

.. link list

`Bug tracker <https://github.com/gumpdata/gumpdata/issues>`_ |
`Documentation <https://gumpdata.readthedocs.org>`_ |
`Downloads <https://github.com/gumpdata/gumpdata/tags>`_ |
`PyPi <http://pypi.python.org/pypi/gumpdata>`_
