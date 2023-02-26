import json
import logging
from typing import List, Union

from urllib3.exceptions import ConnectTimeoutError
from urllib3.exceptions import ReadTimeoutError

from race_strategist.config import RecorderConfiguration
from race_strategist.connectors.influxdb.connector import InfluxDBConnector
from race_strategist.connectors.influxdb.processor import InfluxDBProcessor
from race_strategist.connectors.kafka.connector import KafkaConnector
from race_strategist.modelling.processor import process_laps, process_session_history, process_drivers, \
    process_session
from race_strategist.otel_helpers import time_method
from race_strategist.session.session import Session, Drivers, CurrentLaps
from race_strategist.telemetry.listener import TelemetryFeed

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


# https://opentelemetry.io/docs/instrumentation/python/getting-started/
# https://opentelemetry-python.readthedocs.io/en/latest/exporter/jaeger/jaeger.html

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "RaceStrategist"})
    )
)
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    # configure agent
    agent_host_name='localhost',
    agent_port=6831,
)

# Create a BatchSpanProcessor and add the exporter to it
span_processor = SimpleSpanProcessor(jaeger_exporter)

# add to the tracer
trace.get_tracer_provider().add_span_processor(span_processor)


class DataRecorder:
    _kafka: Union[KafkaConnector, None] = None
    _kafka_unavailable: bool = False
    _influxdb: Union[InfluxDBConnector, None] = None

    player_car_index: int = None

    session: Union[Session, None] = None
    drivers: Union[Drivers, None] = None
    laps: Union[CurrentLaps, None] = None
    influxdb_processor: Union[InfluxDBProcessor, None] = None
    session_history = {}

    def __init__(self, configuration: RecorderConfiguration, port: int = 20777, all_drivers=False) -> None:
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

        if not self.player_car_index:
            self.player_car_index = header.player_car_index

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

    @time_method
    def process_packet(self):
        packet, packet_type = self.feed.get_latest()
        packet_name = packet_type.__name__

        self.prepare_for_processing(packet, packet_name)

        if not self.session or not self.drivers or not self.laps:
            return

        if packet_name == 'PacketLapData':
            self.laps = process_laps(packet.to_dict())

        if packet_name == 'PacketCarTelemetryData':

            if self.influxdb:
                if not self.influxdb_processor:
                    self.influxdb_processor = InfluxDBProcessor(
                        drivers=self.drivers,
                        session=self.session,
                        laps=self.laps,
                        player_car_index=self.player_car_index
                    )
                self.influxdb_processor.update_laps(self.laps)
                converted = self.influxdb_processor.convert(packet.to_dict(), packet_name, self.all_drivers)

                if converted:
                    try:
                        logger.info('Writing to InfluxDB')
                        logger.info(json.dumps(packet.to_dict()["car_telemetry_data"][self.player_car_index], indent=4))
                        self.write_to_influxdb(converted)
                        logger.info('Written to InfluxDB')
                    except (ConnectTimeoutError, ReadTimeoutError) as exc:
                        logger.exception(exc)
