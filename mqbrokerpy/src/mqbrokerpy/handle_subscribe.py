import logging
import socket
from io import BytesIO

from mqbrokerpy.enums import ControlPacketType
from mqbrokerpy.registry import registry
from mqbrokerpy.utils import decode_variable_byte_integer
from mqbrokerpy.utils import socket_to_client

logger = logging.getLogger(__name__)


def send_suback(conn: socket.socket, packet_identifier: int) -> None:
    logger.info("in send_suback")
    data = BytesIO()
    reserved = 0
    control_packet_type = ControlPacketType.SUBACK.value << 4
    first_byte = control_packet_type | reserved
    data.write(first_byte.to_bytes(1, byteorder="big"))

    data.write((3).to_bytes(1, byteorder="big"))

    data.write(packet_identifier.to_bytes(2, byteorder="big"))
    # 0 == success
    data.write((0).to_bytes(1, byteorder="big"))

    data.seek(0)
    logger.info(data.read())

    try:
        conn.sendall(data.getvalue())
    except:
        # TODO: disconnect client if error
        raise Exception("Error while sending data")
    logger.info("done! ack")


def handle_subscribe(
    conn: socket.socket, data: BytesIO, flags: int, configs: dict
) -> None:
    if flags != 0b0010:
        logger.info("Malformed reserved")
        conn.close()
        exit(1)
    remaining_len = decode_variable_byte_integer(data)
    logger.info(f"remaining_len {remaining_len}")

    packet_identifier = int.from_bytes(data.read(2), byteorder="big", signed=False)
    logger.info(f"packet_identifier {packet_identifier}")

    topic_filer_len = int.from_bytes(data.read(2), byteorder="big", signed=False)
    topic_filer = data.read(topic_filer_len).decode("utf-8")
    logger.info(f"topic filter {topic_filer}")
    requested_qos = ord(data.read(1))
    assert (requested_qos >> 2) == 0
    qos = requested_qos & 3
    logger.info(f"qos {qos}")

    configs["qos"] = {topic_filer: qos}

    # assuming 1 subscribe
    assert remaining_len == 2 + 2 + 1 + topic_filer_len
    send_suback(conn, packet_identifier)
    registry.register(socket_to_client[conn], topic_filer)
