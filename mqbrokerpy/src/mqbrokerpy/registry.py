import logging

logger = logging.getLogger(__name__)


class Registry:
    def __init__(self):
        self.subscriptions = {}

    def register(self, client, topic):
        logger.info(f"registering client {client.client_id} to topic {topic}")
        logger.info(topic)
        # exit(1)
        self.subscriptions[topic] = [client]

    def notify(self, publication, payload, configs):
        if publication not in self.subscriptions:
            return
        for client in self.subscriptions[publication]:
            if client.client_id == configs["client_id"]:
                continue
            logger.info(f"Notifying client {client.client_id} of topic {publication}")
            if client.configs["qos"][publication] == 0 and ((payload[0] & 6) >> 1) > 0:
                logger.info("Using qos = 0")
                payload = (
                    payload[: 4 + len(publication)]
                    + payload[4 + len(publication) + 2 :]
                )
                payload[1] -= 2
                payload[0] &= 0b11111001
            client.write(bytes(payload))

    def delete(self, client):
        for topic in list(self.subscriptions.keys()):
            self.subscriptions[topic] = [
                c for c in self.subscriptions[topic] if c != client
            ]


registry = Registry()
