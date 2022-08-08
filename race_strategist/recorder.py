import logging
from typing import List, Union

from race_strategist.config import RecorderConfiguration
from race_strategist.connectors.influxdb.connector import InfluxDBConnector
from race_strategist.connectors.influxdb.processor import InfluxDBProcessor
from race_strategist.connectors.kafka.connector import KafkaConnector
from race_strategist.modelling.processor import process_laps, process_session_history, process_drivers, \
    process_session
from race_strategist.session.session import Session, Drivers, CurrentLaps
from race_strategist.telemetry.listener import TelemetryFeed


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


class DataRecorder:
    _kafka: Union[KafkaConnector, None] = None
    _kafka_unavailable: bool = False
    _influxdb: Union[InfluxDBConnector, None] = None

    session: Union[Session, None] = None
    drivers: Union[Drivers, None] = None
    laps: Union[CurrentLaps, None] = None
    influxdb_processor: Union[InfluxDBProcessor, None] = None
    session_history = {}

    def __init__(self, configuration: RecorderConfiguration, port: int = 20777, all_drivers=True) -> None:
        self.configuration: RecorderConfiguration = configuration
        self.feed = TelemetryFeed(port=port)
        self.port = port
        self.participants = None
        self._all_drivers = all_drivers

    @property
    def all_drivers(self):
        return self._all_drivers

    @property
    def kafka(self):
        if not self._kafka and self.configuration.kafka and not self._kafka_unavailable:
            self._kafka = KafkaConnector(configuration=self.configuration.kafka)
            if self._kafka.in_error:
                self._kafka_unavailable = True
        return self._kafka

    @property
    def influxdb(self):
        if not self._influxdb and self.configuration.influxdb:
            self._influxdb = InfluxDBConnector(
                configuration=self.configuration.influxdb
            )

        return self._influxdb

    def write_to_influxdb(self, data: List) -> bool:
        if not self.influxdb:
            return False

        self.influxdb.write(data)
        return True

    def write_to_kafka(self, topic: str, data: List) -> bool:
        if not self.kafka:
            return False

        self.kafka.send(topic, data)
        return True

    def prepare_for_processing(self, packet, packet_name) -> bool:

        header = packet.header

        packet_dict = packet.to_dict()

        if not self.session and packet_name == 'PacketSessionData':
            self.session = process_session(packet_dict, header.session_uid)
            return False
        elif packet_name == 'PacketSessionData':
            if self.session.session_link_identifier != header.session_uid:
                self.session = None
                self.drivers = None
                self.laps = None

        if not self.drivers and packet_name == 'PacketParticipantsData':
            self.drivers = process_drivers(packet_dict)
            return False

        if not self.laps and packet_name == 'PacketLapData':
            self.laps = process_laps(packet_dict)
            return False

        if packet_name == 'PacketSessionHistoryData':
            self.session_history = process_session_history(packet_dict)

        return True

    def collect(self):

        while True:
            self.process_packet()

    async def process_packet(self):
        packet, packet_type = self.feed.get_latest()
        packet_name = packet_type.__name__

        self.prepare_for_processing(packet, packet_name)

        if not self.session or not self.drivers or not self.laps:
            return

        if packet_name == 'PacketLapData':
            self.laps = process_laps(packet.to_dict())

        if self.influxdb:
            if not self.influxdb_processor:
                self.influxdb_processor = InfluxDBProcessor(
                    drivers=self.drivers,
                    session=self.session,
                    laps=self.laps,
                )
            self.influxdb_processor.update_laps(self.laps)
            converted = self.influxdb_processor.convert(packet.to_dict(), packet_name)

            if converted:
                self.write_to_influxdb(converted)
