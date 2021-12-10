========
soaculib
========

This is a Python package to support communication with the ACU
(Antenna Control Unit) for `Simons Observatory`_.  It is intended to
support low-level function testing and to serve as the hardware access
library for the OCS Agent (see `OCS`_ and `SOCS`_).

The package includes:

- The ``soaculib`` module
- Command-line utilities (``acu-*``)
- Special scripts for testing functionality (``function_testing/``)

Upon installation, only the module and command-line utilities will be
installed to the standard system (or user) directories.  The special
scripts are not installed anywhere and should be run from the source
tree.

To install the code, along with all requirements (including those only
needed for special backends)::

  pip install -r requirements.txt .

For more conservative installation, see the comments in
requirements.txt, then pip install only what you need, then::

  pip install .

.. _`Simons Observatory`: https://simonsobservatory.org/
.. _`OCS`: https://github.com/simonsobs/ocs/
.. _`SOCS`: https://github.com/simonsobs/socs/

Documentation
-------------
Documentation is hosted on `simons1`_. To build the documentation locally,
first install the required dependencies::

  pip install -r docs/requirements.txt

Then build with Sphinx::

  cd docs/
  make html

.. _`simons1`: https://simons1.princeton.edu/docs/soaculib/
