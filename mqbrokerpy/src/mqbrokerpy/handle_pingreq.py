import logging
import socket
from io import BytesIO

from mqbrokerpy.enums import ControlPacketType
from mqbrokerpy.utils import decode_variable_byte_integer
from mqbrokerpy.utils import socket_to_client

logger = logging.getLogger(__name__)


def handle_pingreq(
    conn: socket.socket, data: BytesIO, flags: int, configs: dict
) -> None:
    remaining_len = decode_variable_byte_integer(data)
    logger.info("remaining_len", remaining_len)
    message = BytesIO()
    byte_1 = (ControlPacketType.PINGRESP.value << 4).to_bytes(1, byteorder="big")
    message.write(byte_1)
    message.write((0).to_bytes(1, byteorder="big"))
    client = socket_to_client[conn]
    client.write(message.getvalue())
