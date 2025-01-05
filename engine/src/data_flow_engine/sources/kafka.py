from confluent_kafka.admin import AdminClient, NewTopic
from loguru import logger


class KafkaAgent:
    def __init__(self, bootstrap_servers: str):
        self._client = AdminClient({"bootstrap.servers": bootstrap_servers})

    def add_topic(self, topic: str) -> None:
        new_topic = NewTopic(topic)
        fs = self._client.create_topics(new_topics=[new_topic])
        for topic, f in fs.items():
            try:
                f.result()
                logger.info(f"Topic {topic} created")
            except Exception as e:
                logger.warning(f"Failed to create topic {topic}: {e}")
