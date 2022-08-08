import json
import logging
from typing import Dict

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from race_strategist.config import KafkaConfiguration

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class KafkaConnector:
    """
    Send the packets as JSON to Kafka.
    """

    in_error: bool = False

    def __init__(self, configuration: KafkaConfiguration):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=configuration.bootstrap_servers
            )
        except NoBrokersAvailable:
            logger.error("No Kafka brokers available, skipping sending to Kafka.")
            self.in_error = True

    def send(self, topic, message):
        self.producer.send(topic, json.dumps(message).encode())

    def build_data(self, name: str, value, data: Dict) -> Dict:
        data[name] = value
        return data
