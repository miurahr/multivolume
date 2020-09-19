import binascii
import hashlib
import os

import multivolumefile as MV

BLOCKSIZE = 8192
testdata_path = os.path.join(os.path.dirname(__file__), 'data')
os.umask(0o022)


def test_read_check_sha1():
    target = [os.path.join(testdata_path, "archive.7z.001"),
              os.path.join(testdata_path, "archive.7z.002")]
    mv = MV.open(target, mode='rb')
    sha = hashlib.sha256()
    data = mv.read(BLOCKSIZE)
    while len(data) > 0:
        sha.update(data)
        data = mv.read(BLOCKSIZE)
    mv.close()
    assert sha.digest() == binascii.unhexlify('e0cfeb8010d105d0e2d56d2f94d2b786ead352cef5bca579cb7689d08b3614d1')


def test_read_seek():
    target = [os.path.join(testdata_path, "archive.7z.001"),
              os.path.join(testdata_path, "archive.7z.002")]
    mv = MV.open(target, mode='rb')
    mv.seek(40000)
    mv.close()


def test_read_context():
    target = [os.path.join(testdata_path, "archive.7z.001"),
              os.path.join(testdata_path, "archive.7z.002")]
    with MV.open(target, mode='rb') as mv:
        mv.seek(24900)
        data = mv.read(200)
        assert len(data) == 100
        data = mv.read(200)
        assert len(data) == 200
