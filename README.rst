Talis Prism HTTP library
========================

This project provides a simple library for interacting with Talis Prism instances. At the moment one can retrieve various user details, and current and previous loan details. It is also possible to renew existing loans.

.. note ::

   This code has only been tested with Northamptonshires instances. It's entirely possible that there are differences with other instances.

API
---

There are two modules, ``access`` and ``autorenew``.

``access``
~~~~~~~~~~

``access`` contains a ``TalisPrism`` class with the following attributes:

 * ``name``
 * ``email``
 * ``address``
 * ``telephone``
 * ``charges``
 * ``loans``
 * ``history``

There is also a method ``renew``, taking an iterable of LCNs to renew. At the moment it doesn't check that the items were renewed successfully.

``autorenew``
~~~~~~~~~~~~~

TODO.
