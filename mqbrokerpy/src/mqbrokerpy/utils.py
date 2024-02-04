import socket
from io import BytesIO
from typing import Any

sockets: list[socket.socket] = []
socket_to_client: dict[socket.socket, Any] = {}


def decode_variable_byte_integer(buf: BytesIO) -> int:
    multiplier = 1
    value = 0
    while True:
        encoded = ord(buf.read(1))
        value += (encoded & 127) * multiplier
        if multiplier > 128 * 128 * 128:
            raise Exception("Wrong format variable byte array")
        multiplier *= 128
        if (encoded & 128) == 0:
            break
    return value
