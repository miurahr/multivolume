#!/usr/bin/env python
#
#    multi-volume file library
#    Copyright (C) 2020 Hiroshi Miura
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
import contextlib
import io
import os
import pathlib
import re
from typing import List, Union


def open(name: Union[pathlib.Path, str], mode=None, volume=None) -> io.RawIOBase:
    return MultiVolume(name, mode=mode, volume=volume)


class _FileInfo:
    def __init__(self, filename, size):
        self.filename = filename
        self.size = size


class MultiVolume(io.RawIOBase, contextlib.AbstractContextManager):

    def __init__(self, basename: Union[pathlib.Path, str], mode=None, volume=None):
        self._mode = mode
        self._closed = False
        self._files = []  # type: List[object]
        self._fileinfo = []  # type: List[_FileInfo]
        self._position = 0
        self._positions = []
        if mode in ['rb', 'r', 'rt']:
            self._init_reader(basename)
        elif mode in ['wb',  'w', 'wt', 'xb', 'x', 'xt', 'ab', 'a', 'at']:
            if volume is None:
                self._volume_size = 10 * 1024 * 1024  # set default to 10MBytes
            else:
                self._volume_size = volume
            self._init_writer(basename)
        else:
            raise NotImplementedError

    def _glob_files(self, basename):
        if isinstance(basename, str):
            basename = pathlib.Path(basename)
        files = basename.parent.glob(basename.name + '.*')
        return sorted(files)

    def _init_reader(self, basename):
        pos = 0
        self._positions.append(pos)
        filenames = self._glob_files(basename)
        for name in filenames:
            size = os.stat(name).st_size
            self._fileinfo.append(_FileInfo(name, size))
            self._files.append(io.open(name, mode=self._mode))
            pos += size
            self._positions.append(pos)

    def _init_writer(self, basename):
        if isinstance(basename, str):
            basename = pathlib.Path(basename)
        target = basename.with_name(basename.name + '.0001')
        if target.exists():
            if self._mode in ['x', 'xb', 'xt']:
                raise FileExistsError
            elif self._mode in ['w', 'wb', 'wt']:
                file = io.open(target, mode=self._mode)
                self._files.append(file)
                file.truncate(0)
                self._fileinfo.append(_FileInfo(target, self._volume_size))
                self._positions = [0, self._volume_size]
            elif self._mode in ['a', 'ab', 'at']:
                filenames = self._glob_files(basename)
                if self._mode == 'ab':
                    mode = 'rb'
                else:
                    mode = 'r'
                pos = 0
                self._positions = [0]
                for i in range(len(filenames) - 2):
                    file = io.open(filenames[i], mode)
                    self._files.append(file)
                    size = filenames[i].stat().st_size
                    self._fileinfo.append(_FileInfo(filenames[i], size))
                    pos += size
                    self._positions.append(pos)
                # last file
                file = io.open(filenames[-1], mode=self._mode)
                self._files.append(file)
                size = filenames[-1].stat().st_size
                self._fileinfo.append(_FileInfo(filenames[i], size))
                pos += size
                self._positions.append(pos)
                file.seek(0, os.SEEK_END)
                self._position = pos
            else:
                raise NotImplementedError
        else:
            file = io.open(target, mode=self._mode)
            self._files.append(file)
            self._fileinfo.append(_FileInfo(target, self._volume_size))
            self._positions = [0, self._volume_size]

    def _current_index(self):
        for i in range(len(self._positions) - 1):
            if self._positions[i] <= self._position < self._positions[i + 1]:
                pos = self._files[i].tell()
                offset = self._position - self._positions[i]
                if pos != offset:
                    self._files[i].seek(offset, io.SEEK_SET)
                return i
        if self._mode == 'rb' or self._mode == 'r':
            return len(self._files) - 1
        else:
            raise NotImplementedError

    def read(self, size: int = 1) -> bytes:
        current = self._current_index()
        file = self._files[current]
        data = file.read(size)
        if len(data) == 0 and current < len(self._files) - 1:
            current = self._current_index()
            file = self._files[current]
            file.seek(0)
            data += file.read(size)
        self._position += len(data)
        return data

    def readall(self) -> bytes:
        raise NotImplementedError

    def readinto(self, b: Union[bytes, bytearray, memoryview]):
        length = len(b)
        data = self.read(length)
        b[:len(data)] = data
        return len(data)

    def write(self, b: Union[bytes, bytearray, memoryview]):
        current = self._current_index()
        file = self._files[current]
        pos = file.tell()
        if pos + len(b) > self._volume_size:
            if current == len(self._files) - 1:
                self._add_volume()
            file.write(b[:self._volume_size - pos])
            file = self._files[current + 1]
            file.seek(0)
            file.write(b[self._volume_size - pos:])
        else:
            file.write(b)
        self._position += len(b)

    def _add_volume(self):
        last = self._fileinfo[-1].filename
        assert last.suffix.endswith(r".{0:04d}".format(len(self._fileinfo)))
        next = last.with_suffix(r".{0:04d}".format(len(self._fileinfo) + 1))
        self._files.append(io.open(next, self._mode))
        self._fileinfo.append(_FileInfo(next, self._volume_size))
        pos = self._positions[-1]
        self._positions.append(pos + self._volume_size)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        for file in self._files:
            file.close()

    @property
    def closed(self) -> bool:
        return self._closed

    def fileno(self) -> int:
        """
        fileno() is incompatible with other implementation.
        multivolume handle multiple file object so we cannot return single value
        """
        return -1

    def flush(self) -> None:
        if self._closed:
            return
        if self._mode == 'wb' or self._mode == 'w':
            for file in self._files:
                file.flush()

    def isatty(self) -> bool:
        return False

    def readable(self) -> bool:
        if self._closed:
            return False
        return all([f.readable() for f in self._files])

    def readline(self, size: int = -1) -> bytes:
        raise NotImplementedError

    def readlines(self, hint: int = -1) -> List[bytes]:
        raise NotImplementedError

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            target = offset
        elif whence == io.SEEK_CUR:
            target = self._position + offset
        else:
            target = self._positions[-1] + offset
        self._position = target
        i = len(self._files) - 1
        while i > 0 and target < self._positions[i]:
            i -= 1
        file = self._files[i]
        file.seek(target - self._positions[i], io.SEEK_SET)

    def seekable(self):
        if self._mode in ['ab', 'at', 'a']:
            return False
        else:
            return all([f.seekable() for f in self._files])

    def tell(self) -> int:
        return self._position

    def truncate(self, size=None):
        raise NotImplementedError

    def writable(self) -> bool:
        return self._mode in ['wb', 'w', 'wt', 'x', 'xb', 'xt', 'ab', 'a', 'at']

    def writelines(self, lines):
        raise NotImplementedError

    def __del__(self):
        # FIXME
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
