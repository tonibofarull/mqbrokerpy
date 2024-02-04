import logging
import select
import socket
import uuid

from mqbrokerpy.client import Client
from mqbrokerpy.logger import configure_logger
from mqbrokerpy.parse import get_args
from mqbrokerpy.utils import socket_to_client
from mqbrokerpy.utils import sockets

logger = logging.getLogger(__name__)


def process_clients():
    for client in list(socket_to_client.values()):
        client.process()


def main():
    args = get_args()
    configure_logger(args.loglevel)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((args.host, args.port))
    server_socket.listen(args.listen)

    sockets.append(server_socket)
    while True:
        readable, _, _ = select.select(sockets, [], [], 0.0001)
        if len(readable) == 0:
            process_clients()
            continue

        for sock in readable:
            if sock is server_socket:
                client_socket, addr = server_socket.accept()
                sockets.append(client_socket)
                logger.info(f"New connection to {addr}")
                socket_to_client[client_socket] = Client(
                    uuid.uuid4(), client_socket, addr
                )
                continue

            if sock in socket_to_client:
                socket_to_client[sock].read()
            else:
                logger.info(f"error (?), {sock}")
                logger.info(server_socket)

        process_clients()


if __name__ == "__main__":
    main()
