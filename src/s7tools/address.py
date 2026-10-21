"""S7-Adressen wie DB10.DBX4.3, DB10.DBB4, DB10.DBW4, DB10.DBD4."""

import re
from typing import NamedTuple, Optional

_PATTERN = re.compile(r"DB(\d+)\.DB([XBWD])(\d+)(?:\.(\d+))?")
_SIZES = {"X": 1, "B": 1, "W": 2, "D": 4}


class Address(NamedTuple):
    db: int
    kind: str
    offset: int
    bit: Optional[int]


def parse_address(text: str) -> Address:
    match = _PATTERN.fullmatch(text.strip().upper())
    if not match:
        raise ValueError(f"not an S7 DB address: {text!r}")
    db, kind, offset, bit = match.groups()
    db_nr, offset_nr = int(db), int(offset)
    if not 1 <= db_nr <= 65535 or offset_nr > 65535:
        raise ValueError(f"DB number or offset out of range: {text!r}")
    if kind == "X":
        if bit is None or int(bit) > 7:
            raise ValueError(f"bit address needs a bit 0..7: {text!r}")
        return Address(db_nr, kind, offset_nr, int(bit))
    if bit is not None:
        raise ValueError(f"only X addresses have a bit: {text!r}")
    return Address(db_nr, kind, offset_nr, None)


def size_bytes(addr: Address) -> int:
    return _SIZES[addr.kind]
