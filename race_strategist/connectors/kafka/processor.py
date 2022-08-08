
import json
import logging
from typing import Dict

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from race_strategist.config import KafkaConfiguration
from modelling.processor import Processor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class KafkaProcessor(Processor):

    def convert_car_damage_data(self, packet: Dict):
        pass

    def convert_car_telemetry_data(self, packet: Dict):
        pass

    def convert_car_status_data(self, packet: Dict):
        pass

    def convert_motion_data(self, packet: Dict):
        pass

    def convert_car_setup_data(self, packet: Dict):
        return packet

    def save(self, data):
        pass


class KafkaConnector:
    """
    Send the packets as JSON to Kafka.
    """

    in_error: bool = False
    _processor: KafkaProcessor

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
