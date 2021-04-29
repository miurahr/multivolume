=========
ChangeLog
=========

All notable changes to this project will be documented in this file.

`Unreleased`_
=============

Added
-----

Changed
-------

Fixed
-----

Deprecated
----------

Removed
-------

Security
--------

`v0.2.3`_
=========

Added
-----
* implement readall()

Chnaged
-------
* lint with black


`v0.2.2`_
=========

Added
-----

* Add py.typed file for type hinting.


`v0.2.1`_
=========

Added
-----

* Add `name` property that indicate basename of volumes
* Add `stat()` that return `stat_result` which has as mostly same methods as `os.stat_result` class
  except for platform dependent methods.


`v0.2.0`_
=========

Added
-----

* Type hint information bundled.

Fixed
-----

* Seek() returns current position.

Changed
-------

* Explanation of unsupported methods an modes in README

`v0.1.4`_
=========

Fixed
-----

* Fix append mode bug.

`v0.1.3`_
=========

Fixed
-----

* Fix added volume size become wrong

`v0.1.2`_
=========

Fixed
-----

* Fix append mode (#1)

`v0.1.1`_
=========

Fixed
-----

* Fin NotImplementedError when writing boudning of target files

`v0.1.0`_
=========

* ***API changed***

Added
-----

* Add mode 'x', 'xb' and 'xt'
* Add mode 'a', 'ab' and 'at'
* Support flush()

Changed
-------

* Change API: file argument of 'r' and 'rb' now single basename instead of list of files

`v0.0.5`_
=========

* Support context manager
* Support read functions.

.. History links
.. _Unreleased: https://github.com/miurahr/py7zr/compare/v0.2.2...HEAD
.. _v0.2.2: https://github.com/miurahr/py7zr/compare/v0.2.1...v0.2.2
.. _v0.2.1: https://github.com/miurahr/py7zr/compare/v0.2.0...v0.2.1
.. _v0.2.0: https://github.com/miurahr/py7zr/compare/v0.1.4...v0.2.0
.. _v0.1.4: https://github.com/miurahr/py7zr/compare/v0.1.3...v0.1.4
.. _v0.1.3: https://github.com/miurahr/py7zr/compare/v0.1.2...v0.1.3
.. _v0.1.2: https://github.com/miurahr/py7zr/compare/v0.1.1...v0.1.2
.. _v0.1.1: https://github.com/miurahr/py7zr/compare/v0.1.0...v0.1.1
.. _v0.1.0: https://github.com/miurahr/py7zr/compare/v0.0.5...v0.1.0
.. _v0.0.5: https://github.com/miurahr/py7zr/compare/v0.0.1...v0.0.5
