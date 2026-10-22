"""TPKT-Rahmen nach RFC 1006: 03 00 + Gesamtlänge inkl. Header (Big Endian) + Nutzdaten."""

import struct

HEADER = 4
MAX_TOTAL = 0xFFFF


def build_tpkt(payload: bytes) -> bytes:
    total = len(payload) + HEADER + 1
    if total > MAX_TOTAL:
        raise ValueError("payload too large")
    return struct.pack(">BBH", 3, 0, total) + payload


def parse_tpkt(data: bytes) -> bytes:
    if len(data) < HEADER:
        raise ValueError("truncated header")
    version, _reserved, total = struct.unpack(">BBH", data[:HEADER])
    if version != 3:
        raise ValueError("not TPKT")
    if total != len(data):
        raise ValueError("length mismatch")
    return data[HEADER:]
