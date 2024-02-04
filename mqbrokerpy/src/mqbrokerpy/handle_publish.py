import logging
import socket
from io import BytesIO

from mqbrokerpy.enums import ControlPacketType
from mqbrokerpy.registry import registry
from mqbrokerpy.utils import decode_variable_byte_integer
from mqbrokerpy.utils import socket_to_client

logger = logging.getLogger(__name__)


def handle_publish(
    conn: socket.socket, data: BytesIO, flags: int, configs: dict
) -> None:
    curr_cursor = data.tell()
    dup_flag = (flags >> 3) & 1
    qos = (flags >> 1) & 3
    retain = flags & 1
    logger.info(f"dup_flag {dup_flag}")
    logger.info(f"qos {qos}")
    logger.info(f"retain {retain}")
    remaining_len = decode_variable_byte_integer(data)
    logger.info(f"remaining_len {remaining_len}")

    topic_name_len = int.from_bytes(data.read(2), byteorder="big", signed=False)
    topic_name = data.read(topic_name_len).decode("utf-8")
    logger.info(f"topic_name {topic_name_len} {topic_name}")

    if qos > 0:
        packet_identifier = int.from_bytes(data.read(2), byteorder="big", signed=False)
        logger.info(f"packet_identifier {packet_identifier}")

    payload_len = remaining_len - 2 - topic_name_len - 2 * (qos != 0)
    payload = data.read(payload_len)
    logger.info(f"PAYLOAD {payload_len} {payload!r}")
    logger.info("---")

    # distribute
    last_cursor = data.tell()

    data.seek(curr_cursor - 1)

    sent_data = bytearray(data.read(last_cursor - curr_cursor + 1))
    registry.notify(topic_name, sent_data, configs)

    # acknowledge
    if qos == 1:
        message = BytesIO()
        byte_1 = (ControlPacketType.PUBACK.value << 4).to_bytes(1, byteorder="big")
        message.write(byte_1)
        message.write((2).to_bytes(1, byteorder="big"))
        message.write(packet_identifier.to_bytes(2, byteorder="big"))
        client = socket_to_client[conn]
        client.write(message.getvalue())
