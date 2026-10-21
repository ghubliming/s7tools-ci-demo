import pytest

from s7tools import request_tpkt

pytestmark = pytest.mark.integration


def test_request_against_fake_plc(fake_plc):
    assert request_tpkt("127.0.0.1", fake_plc, b"\x04\x00\x0a") == b"\xff\x04\x00\x0a"


def test_large_request_against_fake_plc(fake_plc):
    payload = bytes(range(256)) * 40
    assert request_tpkt("127.0.0.1", fake_plc, payload) == b"\xff" + payload
