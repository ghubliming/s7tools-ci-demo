import socket
import struct
import threading

import pytest


def _handle(conn: socket.socket) -> None:
    """Simulierte SPS: beantwortet jeden TPKT-Rahmen mit 0xFF + den empfangenen Nutzdaten."""
    with conn:
        while True:
            header = conn.recv(4)
            if len(header) < 4:
                return
            total = struct.unpack(">H", header[2:4])[0]
            payload = b""
            while len(payload) < total - 4:
                chunk = conn.recv(total - 4 - len(payload))
                if not chunk:
                    return
                payload += chunk
            answer = b"\xff" + payload
            conn.sendall(struct.pack(">BBH", 3, 0, len(answer) + 4) + answer)


@pytest.fixture
def fake_plc():
    """Startet die simulierte SPS auf einem freien Port und gibt den Port zurück."""
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(5)
    srv.settimeout(0.1)
    stop = threading.Event()

    def loop() -> None:
        while not stop.is_set():
            try:
                conn, _ = srv.accept()
            except socket.timeout:
                continue
            conn.settimeout(None)
            threading.Thread(target=_handle, args=(conn,), daemon=True).start()

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    yield srv.getsockname()[1]
    stop.set()
    thread.join()
    srv.close()
