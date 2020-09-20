===============
multivolumefile
===============

.. image:: https://coveralls.io/repos/github/miurahr/multivolume/badge.svg?branch=master
  :target: https://coveralls.io/github/miurahr/multivolume?branch=master

.. image:: https://github.com/miurahr/multivolume/workflows/Run%20Tox%20tests/badge.svg
  :target: https://github.com/miurahr/multivolume/actions

MultiVolumefile is a python library to provide a file-object wrapping multiple files
as virtually like as a single file.

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

    with multivolumefile.open('archive.7z', 'rb) as vol:
        data = vol.read(100)
        vol.seek(500)

- For writing multi-volue files, that has names `archive.7z.0001`, `archive.7z.0002` and so on,
  you can call multivolumefile as follows;


.. code-block::

    data = b'abcdefg'
    with multivolumefile.open('archive.7z', 'rb) as vol:
        size = vol.write(data)
        vol.seek(0)

you will see file `archive.7z.001` are written.


Contribution
============

You are welcome to contribute the project, as usual on github projects,
Pull-Request are welcome.

License
=======

Multivolume is licensed under GNU Lesser General Public license version 2.1 or later.
