import pytest

from s7tools import build_tpkt, parse_tpkt


def test_known_answer():
    assert build_tpkt(b"\x01\x02") == b"\x03\x00\x00\x06\x01\x02"


@pytest.mark.parametrize(
    "payload", 
    [b"", b"\x02\xf0\x80", bytes(65531)], 
    ids=["empty", "small", "max_rfc1006_boundary"],
)
def test_roundtrip(payload):
    assert parse_tpkt(build_tpkt(payload)) == payload


def test_too_large():
    with pytest.raises(ValueError):
        build_tpkt(bytes(65532))


@pytest.mark.parametrize("bad", [b"", b"\x03\x00", b"\x02\x00\x00\x04", b"\x03\x00\x00\x09abc"])
def test_rejects_bad(bad):
    with pytest.raises(ValueError):
        parse_tpkt(bad)
