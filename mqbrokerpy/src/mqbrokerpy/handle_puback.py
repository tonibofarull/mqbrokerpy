import logging
import socket
from io import BytesIO

from mqbrokerpy.utils import decode_variable_byte_integer

logger = logging.getLogger(__name__)


def handle_puback(
    conn: socket.socket, data: BytesIO, flags: int, configs: dict
) -> None:
    remaining_len = decode_variable_byte_integer(data)
    logger.info(f"remaining_len {remaining_len}")
    packet_identifier = int.from_bytes(data.read(2), byteorder="big", signed=False)
    logger.info(f"packet_identifier {packet_identifier}")
