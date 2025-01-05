from kafka import KafkaClient


class KafkaAgent:
    def __init__(self, bootstrap_servers: str):
        self._client = KafkaClient(bootstrap_servers=bootstrap_servers)

    def add_topic(self, topic: str) -> None:
        self._client.add_topic(topic=topic)
