import io
import os
import pathlib
import sys

from hypothesis import given
from hypothesis import strategies as st
from pytest import fixture

import multivolumefile as MV

counter = 0


@fixture(scope="session")
def basepath(tmp_path_factory):
    return tmp_path_factory.getbasetemp()


def numbered_tempdir(base: pathlib.Path, common, suffix):
    global counter
    counter += 1
    tmpdir = base.joinpath(common).joinpath("{0}{1}".format(suffix, counter))
    os.makedirs(tmpdir, exist_ok=True)
    return tmpdir


@given(
    obj=st.binary(min_size=10, max_size=10 << 10),
    volume=st.integers(min_value=5, max_value=1 << 10),
)
def test_fuzzer_once(obj, volume, basepath):
    target = numbered_tempdir(basepath, "test_fuzzer", "once").joinpath("target.bin")
    with MV.open(target, mode="wb", volume=volume) as f:
        f.write(obj)
    with MV.open(target, mode="rb") as f:
        result = f.read()
    assert result == obj


@given(
    obj=st.binary(min_size=10, max_size=10 << 10),
    volume=st.integers(min_value=5, max_value=1 << 10),
    wblock=st.integers(min_value=5, max_value=5 << 9),
    rblock=st.integers(min_value=5, max_value=5 << 9),
)
def test_fuzzer_block(obj, volume, wblock, rblock, basepath):
    target = numbered_tempdir(basepath, "test_fuzzer", "block").joinpath("target.bin")
    src = io.BytesIO(obj)
    result = b""
    with MV.open(target, mode="wb", volume=volume) as f:
        data = src.read(wblock)
        while len(data) > 0:
            f.write(data)
            data = src.read(wblock)
    with MV.open(target, mode="rb") as f:
        data = f.read(rblock)
        while len(data) > 0:
            result += data
            data = f.read(rblock)
    assert result == obj


if __name__ == "__main__":
    import atheris  # type: ignore  # noqa

    atheris.Setup(sys.argv, test_fuzzer_block.hypothesis.fuzz_one_input)
    atheris.Fuzz()
