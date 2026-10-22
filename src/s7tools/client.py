"""Ein minimaler TCP-Client, der einen TPKT-Rahmen sendet und genau einen zurückliest."""

import socket
import struct

from s7tools.tpkt import HEADER, build_tpkt


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError(f"connection closed after {len(buf)} of {n} bytes")
        buf += chunk
    return buf


def request_tpkt(host: str, port: int, payload: bytes, timeout: float = 2.0) -> bytes:
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.sendall(build_tpkt(payload))
        version, _reserved, total = struct.unpack(">BBH", _recv_exact(sock, HEADER))
        if version != 3:
            raise ValueError("answer is not TPKT")
        return _recv_exact(sock, total - HEADER)
