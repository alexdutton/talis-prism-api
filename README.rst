Talis Prism HTTP library
========================

This project provides a simple library for interacting with Talis Prism instances. At the moment one can retrieve various user details, and current and previous loan details. It is also possible to renew existing loans.

.. note ::

   This code has only been tested with Northamptonshires instances. It's entirely possible that there are differences with other instances.

API
---

There are three modules, ``access``, ``autorenew`` and ``config``.

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

Example usage::

   from access import TalisPrism

   tp = TalisPrism('http://library.example.com/TalisPrism/', '1234567890', '0000')
   print "%s <%s>" % (tp.name, tp.email)
   
   # Attempt to renew the first item currently loaned.
   tp.renew([tp.loans[0]['lcn']])

When invoked as a script, it takes an instance name (see ``config``, below), a username and password, and prints all available details as a Python data structure to stdout.


``autorenew``
~~~~~~~~~~~~~

This module contains a single function, ``autorenew``, taking the base URL for the instance, a username, a password, and a ``datetime.timedelta`` specifying a minimum desired period before due dates. Those with less than this are renewed. The last argument defaults to two days.

Example usage::

   from datetime import timedelta
   from autorenew import autorenew

   autorenew('http://library.example.com/TalisPrism/', '1234567890', '0000', timedelta(1))

When invokes as a script, it taks an instance name (see ``config``, below), a username and password, and attempts to renew all books with less than two days remaining on their loan periods.

``config``
~~~~~~~~~~

Currently contains one member, ``INSTANCES`` whose attributes are known base URLs for Talis Prism instances.

There is currently only one such URL:

 * ``northamptonshire = "http://www.library.northamptonshire.gov.uk/TalisPrism/"``

These instance names are passed as the first argument when the previous two modules are invoked as scripts.
