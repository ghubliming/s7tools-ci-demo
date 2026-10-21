import pytest

from s7tools import parse_address, size_bytes


@pytest.mark.parametrize(
    "text, expected",
    [
        ("DB10.DBX4.3", (10, "X", 4, 3)),
        ("DB1.DBB0", (1, "B", 0, None)),
        ("DB10.DBW4", (10, "W", 4, None)),
        (" db10.dbd100 ", (10, "D", 100, None)),
    ],
)
def test_valid(text, expected):
    assert tuple(parse_address(text)) == expected


@pytest.mark.parametrize("text", ["", "DB0.DBB0", "DB10.DBX4", "DB10.DBX4.8", "DB10.DBB4.1", "M10.0"])
def test_invalid(text):
    with pytest.raises(ValueError):
        parse_address(text)


@pytest.mark.parametrize("text, size", [("DB1.DBX0.1", 1), ("DB1.DBB0", 1), ("DB1.DBW0", 2), ("DB1.DBD0", 4)])
def test_size_bytes(text, size):
    assert size_bytes(parse_address(text)) == size
