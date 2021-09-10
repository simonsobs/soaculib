==========================
soaculib - class reference
==========================

.. py:module:: soaculib

AcuControl
==========

An AcuControl object exposes high and low-level control of the ACU
motion functions.  It can be used with Twisted or Standard backends.
Note that the API is presented with underscore prefixes, but should be
accessed without those prefixes, i.e. call **AcuControl.mode()** not
AcuControl._mode().

.. autoclass:: AcuControl
   :undoc-members:
   :members: __init__,_mode,_go_to,_stop,_Values,_Command,_Write


Mode (enum)
===========

.. autoclass:: Mode
   :undoc-members:
   :members:


AcuHttpInterface
================

.. autoclass:: AcuHttpInterface
   :undoc-members:
   :members: __init__,Values,Command,Write,Documentation,Meta

PositionBroadcast
=================

.. autoclass:: BroadcastStreamControl
   :undoc-members:
   :members: _enable,_set_destination,_set_port,_set_config,_get_status

