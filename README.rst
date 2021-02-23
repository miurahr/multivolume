===============
multivolumefile
===============

.. image:: https://coveralls.io/repos/github/miurahr/multivolume/badge.svg?branch=master
  :target: https://coveralls.io/github/miurahr/multivolume?branch=master

.. image:: https://github.com/miurahr/multivolume/workflows/Run%20Tox%20tests/badge.svg
  :target: https://github.com/miurahr/multivolume/actions

MultiVolumefile is a python library to provide a file-object wrapping multiple files
as virtually like as a single file. It inherit io.RawIOBase class and support some of
its standard methods.

See API details at `python library reference`_

.. _`python library reference`: https://docs.python.org/3/library/io.html

Status
======

multivolumefile module is under active development and considered as ***Alpha*** state.
It is not good idea to use it on production systems, but it may work well in a limited range
of usage. Please check limitations and passed test cases.


Install
=======

You can install it as usual public libraries, you can use pip command

```
pip install multivolumefile
```

You are also able to add it to your setup.py/cfg as dependency.

Usages
------

- For reading multi-volume files, that has names `archive.7z.0001`, `archive.7z.0002` and so on,
  you can call multivolumefile as follows;

.. code-block::

    with multivolumefile.open('archive.7z', 'rb') as vol:
        data = vol.read(100)
        vol.seek(500)

- For writing multi-volue files, that has names `archive.7z.0001`, `archive.7z.0002` and so on,
  you can call multivolumefile as follows;


.. code-block::

    data = b'abcdefg'
    with multivolumefile.open('archive.7z', 'wb') as vol:
        size = vol.write(data)
        vol.seek(0)

you will see file `archive.7z.001` are written.

Limitations and known issues
============================

- fileno() is not supported and when call it, you will get RuntimeError exception.
- There are several non-implemented functions such as truncate() and writeline() that will raise NotimplementedError
- There are several non-implemented functions such as readlines(), readline() and readall().
- Text mode is not implemented.
- ***Caution***: When globbing existent volumes, it glob all files other than 4-digit extensions, it may break your data.


Contribution
============

You are welcome to contribute the project, as usual on github projects, Pull-Requests are always welcome.

License
=======

Multivolume is licensed under GNU Lesser General Public license version 2.1 or later.
