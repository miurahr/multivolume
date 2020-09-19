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
from typing import List, Union


def open(names, *, mode=None, volume=None) -> io.RawIOBase:
    return MultiVolume(names, mode=mode, volume=volume)


class MultiVolume(io.RawIOBase, contextlib.AbstractContextManager):

    def __init__(self, names, *, mode=None, volume=None):
        self._mode = mode
        self._closed = False
        self._files = []
        self._fileinfo = []
        self._position = 0
        self._positions = []
        if mode == 'rb' or mode == 'r':
            self._init_reader(names)
            pos = 0
            self._positions.append(pos)
            for size in self._fileinfo:
                pos += size
                self._positions.append(pos)
        elif mode == 'w':
            self._init_writer(names, mode, volume)
        else:
            raise NotImplementedError

    def _init_reader(self, names):
        for name in names:
            size = os.stat(name).st_size
            self._fileinfo.append(size)
            self._files.append(io.open(name, mode=self._mode))

    def _init_writer(self, names, mode, volume):
        raise NotImplementedError

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
        pass

    def write(self, b: Union[bytes, bytearray, memoryview]):
        raise NotImplementedError

    def close(self) -> None:
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
        raise NotImplementedError

    def isatty(self) -> bool:
        return False

    def readable(self) -> bool:
        return True

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
        return True

    def tell(self) -> int:
        return self._position

    def truncate(self, size=None):
        raise NotImplementedError

    def writable(self) -> bool:
        return False

    def writelines(self, lines):
        raise NotImplementedError

    def __del__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
