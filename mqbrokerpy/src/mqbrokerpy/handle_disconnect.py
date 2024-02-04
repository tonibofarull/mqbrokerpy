import logging
import socket
from io import BytesIO

from mqbrokerpy.utils import decode_variable_byte_integer

logger = logging.getLogger(__name__)


def handle_disconnect(
    conn: socket.socket, data: BytesIO, flags: int, configs: dict
) -> None:
    assert flags == 0
    remaining_len = decode_variable_byte_integer(data)
    assert remaining_len == 0
    conn.close()
    logger.info("disconneted")
