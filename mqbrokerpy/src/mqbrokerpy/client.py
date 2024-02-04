import logging
import socket
import uuid
from io import BytesIO
from typing import Any

from mqbrokerpy.enums import ControlPacketType
from mqbrokerpy.handle_connect import handle_connect
from mqbrokerpy.handle_disconnect import handle_disconnect
from mqbrokerpy.handle_pingreq import handle_pingreq
from mqbrokerpy.handle_puback import handle_puback
from mqbrokerpy.handle_publish import handle_publish
from mqbrokerpy.handle_subscribe import handle_subscribe
from mqbrokerpy.registry import registry
from mqbrokerpy.utils import socket_to_client
from mqbrokerpy.utils import sockets

ControlPacketTypeMap = {enum.value: enum for enum in ControlPacketType}
logger = logging.getLogger(__name__)


class Client:
    def __init__(self, client_id: uuid.UUID, sock: socket.socket, addr: Any):
        self.client_id = client_id
        self.sock = sock
        self.addr = addr
        self.queued_data = BytesIO()
        self.configs = {"client_id": client_id}

    def process(self):
        curr_byte = self.queued_data.read(1)
        if not curr_byte:
            return
        curr_byte = ord(curr_byte)
        control_packet_type = curr_byte >> 4
        flags = curr_byte % 16

        control_packet = ControlPacketTypeMap[control_packet_type]
        logger.info(f"New operation {control_packet} for client {self.client_id}")

        operation = {
            ControlPacketType.CONNECT: handle_connect,
            ControlPacketType.PUBLISH: handle_publish,
            ControlPacketType.DISCONNECT: handle_disconnect,
            ControlPacketType.SUBSCRIBE: handle_subscribe,
            ControlPacketType.PUBACK: handle_puback,
            ControlPacketType.PINGREQ: handle_pingreq,
        }.get(control_packet)

        if not operation:
            raise Exception("Unkown")
        try:
            operation(self.sock, self.queued_data, flags, self.configs)
        except Exception:
            # handle format error vs tcp connection
            logger.info(
                f"error while sending data to client {self.client_id} {control_packet}"
            )
            self.delete()

        if control_packet == ControlPacketType.DISCONNECT:
            self.delete()

        self.queued_data = BytesIO(self.queued_data.read())

    def read(self):
        pending_data = bytearray(self.queued_data.read())
        data = BytesIO()
        data.write(pending_data)
        total_size = len(pending_data)
        try:
            while True:
                received = self.sock.recv(1024)
                total_size += len(received)
                data.write(received)
                if len(received) < 1024:
                    break
        except Exception:
            logger.warn(f"Client {self.client_id} abruptly disconnected")
            self.delete()
            return

        data.seek(0)
        self.queued_data = data

    def write(self, buff):
        try:
            self.sock.sendall(buff)
        except Exception:
            logger.info(f"error while sending data to client {self.client_id}")
            self.delete()

    def delete(self):
        logger.info(f"Deleting client {self.client_id}")
        sockets.remove(self.sock)
        del socket_to_client[self.sock]
        registry.delete(self)

    def __str__(self):
        logger.info(f"Client: client_id={self.client_id}, addr={self.addr}")
