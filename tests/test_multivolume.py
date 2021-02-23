import binascii
import hashlib
import os
import shutil

import pytest

import multivolumefile as MV

BLOCKSIZE = 8192
testdata_path = os.path.join(os.path.dirname(__file__), 'data')
os.umask(0o022)


def test_read_check_sha1():
    target = os.path.join(testdata_path, "archive.7z")
    mv = MV.open(target, mode='rb')
    sha = hashlib.sha256()
    data = mv.read(BLOCKSIZE)
    while len(data) > 0:
        sha.update(data)
        data = mv.read(BLOCKSIZE)
    mv.close()
    assert sha.digest() == binascii.unhexlify('e0cfeb8010d105d0e2d56d2f94d2b786ead352cef5bca579cb7689d08b3614d1')


def test_read_seek():
    target = os.path.join(testdata_path, "archive.7z")
    mv = MV.open(target, mode='rb')
    assert mv.seekable()
    mv.seek(40000)
    pos = mv.tell()
    assert pos == 40000
    mv.seek(3000)
    pos = mv.tell()
    assert pos == 3000
    mv.close()


def test_read_context():
    target = os.path.join(testdata_path, "archive.7z")
    with MV.open(target, mode='rb') as mv:
        assert mv.readable()
        mv.seek(24900)
        data = mv.read(200)
        assert len(data) == 100
        data = mv.read(200)
        assert len(data) == 200


def test_readinto():
    target = os.path.join(testdata_path, "archive.7z")
    b = bytearray(200)
    with MV.open(target, mode='rb') as mv:
        mv.seek(24900)
        size = mv.readinto(b)
        assert size == 100


def test_read_boundary():
    target = os.path.join(testdata_path, "archive.7z")
    b = bytearray(200)
    with MV.open(target, mode='rb') as mv:
        mv.seek(25000)
        size = mv.readinto(b)
        assert size == 200


def test_write(tmp_path):
    target = tmp_path.joinpath('target.7z')
    with MV.open(target, mode='wb', volume=10240) as volume:
        assert volume.writable()
        with open(os.path.join(testdata_path, "archive.7z.001"), 'rb') as r:
            data = r.read(BLOCKSIZE)
            while len(data) > 0:
                volume.write(data)
                data = r.read(BLOCKSIZE)

        with open(os.path.join(testdata_path, "archive.7z.002"), 'rb') as r:
            data = r.read(BLOCKSIZE)
            while len(data) > 0:
                volume.write(data)
                data = r.read(BLOCKSIZE)
        assert volume.seekable()
        volume.seek(0)
        volume.seek(51000)
        volume.flush()
    created = tmp_path.joinpath('target.7z.0001')
    assert created.exists()
    assert created.stat().st_size == 10240


def test_write_boundary(tmp_path):
    target = tmp_path.joinpath('target.7z')
    with MV.open(target, mode='wb', volume=10240) as volume:
        assert volume.writable()
        with open(os.path.join(testdata_path, "archive.7z.001"), 'rb') as r:
            data = r.read(10000)
            volume.write(data)
            data = r.read(250)
            volume.write(data)
        volume.flush()
    created = tmp_path.joinpath('target.7z.0002')
    assert created.exists()
    assert created.stat().st_size == 10


def test_write_exist(tmp_path):
    target = tmp_path.joinpath('target.7z')
    target_volume = tmp_path.joinpath('target.7z.0001')
    shutil.copyfile(os.path.join(testdata_path, "archive.7z.001"), target_volume)
    #
    with MV.open(target, mode='wb', volume=10240) as volume:
        assert volume.writable()
        with open(os.path.join(testdata_path, "archive.7z.001"), 'rb') as r:
            data = r.read(10000)
            volume.write(data)
        volume.flush()
    created = tmp_path.joinpath('target.7z.0001')
    assert created.stat().st_size == 10000


def test_exclusive_write(tmp_path):
    target = tmp_path.joinpath('target.7z')
    with MV.open(target, mode='xb', volume=10240) as volume:
        assert volume.writable()
        with open(os.path.join(testdata_path, "archive.7z.001"), 'rb') as r:
            data = r.read(BLOCKSIZE)
            while len(data) > 0:
                volume.write(data)
                data = r.read(BLOCKSIZE)

        with open(os.path.join(testdata_path, "archive.7z.002"), 'rb') as r:
            data = r.read(BLOCKSIZE)
            while len(data) > 0:
                volume.write(data)
                data = r.read(BLOCKSIZE)
        assert volume.seekable()
        volume.seek(0)
        volume.seek(51000)
        volume.flush()
    created = tmp_path.joinpath('target.7z.0001')
    assert created.exists()
    assert created.stat().st_size == 10240


def test_exclusive_write_exist(tmp_path):
    target = tmp_path.joinpath('target.7z')
    target_volume = tmp_path.joinpath('target.7z.0001')
    shutil.copyfile(os.path.join(testdata_path, "archive.7z.001"), target_volume)
    with pytest.raises(FileExistsError):
        MV.open(target, 'x')


def test_write_append1(tmp_path):
    target_volume = tmp_path.joinpath('target.7z.0001')
    with target_volume.open(mode='wb') as target:
        with open(os.path.join(testdata_path, "archive.7z.001"), 'rb') as src:
            target.write(src.read(1000))
    #
    target = tmp_path.joinpath('target.7z')
    with MV.open(target, mode='ab', volume=10240) as volume:
        with open(os.path.join(testdata_path, "archive.7z.001"), 'rb') as src:
            src.seek(1000)
            volume.write(src.read(24000))
        with open(os.path.join(testdata_path, "archive.7z.002"), 'rb') as r:
            data = r.read(BLOCKSIZE)
            while len(data) > 0:
                volume.write(data)
                data = r.read(BLOCKSIZE)
        volume.flush()
    #
    existed = tmp_path.joinpath('target.7z.0001')
    assert existed.exists()
    assert existed.stat().st_size == 10240
    created2 = tmp_path.joinpath('target.7z.0002')
    assert created2.exists()
    assert created2.stat().st_size == 10240
    created6 = tmp_path.joinpath('target.7z.0006')
    assert created6.exists()
    assert created6.stat().st_size == 1137


def test_write_append2(tmp_path):
    target = tmp_path.joinpath('target.7z')
    target_volume = tmp_path.joinpath('target.7z.0001')
    shutil.copyfile(os.path.join(testdata_path, "archive.7z.001"), target_volume)
    #
    with MV.open(target, mode='ab', volume=10240) as volume:
        with open(os.path.join(testdata_path, "archive.7z.002"), 'rb') as r:
            data = r.read(BLOCKSIZE)
            while len(data) > 0:
                volume.write(data)
                data = r.read(BLOCKSIZE)
        volume.flush()
    #
    existed = tmp_path.joinpath('target.7z.0001')
    assert existed.exists()
    assert existed.stat().st_size == 25000
    created2 = tmp_path.joinpath('target.7z.0002')
    assert created2.exists()
    assert created2.stat().st_size == 10240
    created4 = tmp_path.joinpath('target.7z.0004')
    assert created4.exists()
    assert created4.stat().st_size == 6857  # 52337 - 25000 - 10240 * 2


def test_read_double_close():
    target = os.path.join(testdata_path, "archive.7z")
    mv = MV.open(target, mode='rb')
    assert not mv.closed
    mv.close()
    assert mv.closed
    mv.close()


def test_read_fileno():
    target = os.path.join(testdata_path, "archive.7z")
    mv = MV.open(target, mode='rb')
    with pytest.raises(RuntimeError):
        mv.fileno()
    mv.close()


def test_write_short_digits(tmp_path):
    target = tmp_path.joinpath('target.7z')
    with MV.MultiVolume(target, mode='wb', volume=10240, ext_digits=3, ext_start=0) as volume:
        assert volume.writable()
        with open(os.path.join(testdata_path, "archive.7z.001"), 'rb') as r:
            data = r.read(10000)
            volume.write(data)
            data = r.read(250)
            volume.write(data)
        volume.flush()
    created = tmp_path.joinpath('target.7z.001')
    assert created.exists()
    assert created.stat().st_size == 10


def test_write_hex_digits(tmp_path):
    target = tmp_path.joinpath('target.7z')
    with MV.MultiVolume(target, mode='wb', volume=800, hex=True, ext_digits=3, ext_start=0) as volume:
        assert volume.writable()
        with open(os.path.join(testdata_path, "archive.7z.001"), 'rb') as r:
            for _ in range(5):
                data = r.read(2000)
                volume.write(data)
            data = r.read(250)
            volume.write(data)
        volume.flush()
    created = tmp_path.joinpath('target.7z.00c')
    assert created.exists()
    assert created.stat().st_size == 650
