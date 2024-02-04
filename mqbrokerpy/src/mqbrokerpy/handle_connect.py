import logging
import socket
from io import BytesIO

from mqbrokerpy.enums import ControlPacketType
from mqbrokerpy.utils import decode_variable_byte_integer
from mqbrokerpy.utils import socket_to_client
logger = logging.getLogger(__name__)


def send_connack(conn: socket.socket) -> None:
    logger.info("in send_connack")
    data = BytesIO()
    reserved = 0
    control_packet_type = ControlPacketType.CONNACK.value << 4
    first_byte = control_packet_type | reserved
    data.write(first_byte.to_bytes(1, byteorder="big"))

    data.write((2).to_bytes(1, byteorder="big"))

    session_present_flag = 0
    connect_ack = session_present_flag
    data.write(connect_ack.to_bytes(1, byteorder="big"))

    connect_return_code = 0
    data.write(connect_return_code.to_bytes(1, byteorder="big"))

    data.seek(0)
    logger.info(data.read())

    try:
        conn.sendall(data.getvalue())
    except:
        client = socket_to_client[conn]
        client.delete()
        raise Exception("Error while sending data")

    logger.info("done! ack")


def handle_connect(
    conn: socket.socket, data: BytesIO, flags: int, configs: dict
) -> None:
    remaining_len = decode_variable_byte_integer(data)
    logger.info(remaining_len)

    logger.info("---")
    # assuming CONENCT
    length = int.from_bytes(data.read(2), byteorder="big", signed=False)
    assert length == 4
    assert data.read(4) == b"MQTT"
    protocol_level = ord(data.read(1))
    if protocol_level == 4:
        logger.info("Version 3.1.1")
    else:
        raise Exception("Version not supported")

    connect_flags = ord(data.read(1))
    if connect_flags & 1 != 0:
        raise Exception("Control packet is not 0")

    user_name_flag = connect_flags & 128 != 0
    password_flag = connect_flags & 64 != 0
    will_retain_flag = connect_flags & 32 != 0
    will_qos = (connect_flags >> 3) & 3
    will_flag = connect_flags & 4 != 0
    clean_session = connect_flags & 2 != 0
    logger.info("flags:")
    logger.info(user_name_flag)
    logger.info(password_flag)
    logger.info(will_retain_flag)
    logger.info(will_qos)
    logger.info(will_flag)
    logger.info(clean_session)
    logger.info("--")

    keep_alive = int.from_bytes(data.read(2), byteorder="big", signed=False)
    logger.info(f"keep_alive during {keep_alive}s")

    client_id_len = int.from_bytes(data.read(2), byteorder="big", signed=False)
    client_id = data.read(client_id_len) if client_id_len else None
    logger.info(f"{client_id_len}, {client_id!r}")

    if will_flag:
        will_topic_len = int.from_bytes(data.read(2), byteorder="big", signed=False)
        will_topic = data.read(will_topic_len) if will_topic_len else None  # noqa: F841

        will_message_len = int.from_bytes(data.read(2), byteorder="big", signed=False)
        will_message = (  # noqa: F841
            data.read(will_message_len) if will_message_len else None
        )

    if user_name_flag:
        username_len = int.from_bytes(data.read(2), byteorder="big", signed=False)
        username = data.read(username_len) if username_len else None

        logger.info(username)

    send_connack(conn)
