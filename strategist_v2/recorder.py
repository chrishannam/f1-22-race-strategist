import json
import logging
from typing import Dict
from typing import List, Union

from f1_22_telemetry.appendices import SESSION_TYPE
from f1_22_telemetry.appendices import TRACK_IDS
from urllib3.exceptions import ConnectTimeoutError
from urllib3.exceptions import ReadTimeoutError

from race_strategist.config import RecorderConfiguration
from race_strategist.connectors.influxdb.connector import InfluxDBConnector
from race_strategist.connectors.influxdb.processor import InfluxDBProcessor
from race_strategist.connectors.kafka.connector import KafkaConnector
from f1_22_telemetry.appendices import DRIVER_IDS, TEAM_IDS
from race_strategist.session.session import Driver
from race_strategist.session.session import Lap
from race_strategist.session.session import Session, Drivers, CurrentLaps
from race_strategist.telemetry.listener import TelemetryFeed


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


class SpeedyDataRecorder:
    _kafka: Union[KafkaConnector, None] = None
    _kafka_unavailable: bool = False
    _influxdb: Union[InfluxDBConnector, None] = None

    player_car_index: int = None

    session: Union[Session, None] = None
    drivers: Union[Drivers, None] = None
    laps: Union[CurrentLaps, None] = None
    influxdb_processor: Union[InfluxDBProcessor, None] = None
    session_history = {}

    def __init__(self, configuration: RecorderConfiguration, port: int = 20777, player_only=True) -> None:
        self.configuration: RecorderConfiguration = configuration
        self.feed = TelemetryFeed(port=port)
        self.port = port
        self.participants = None
        self.player_only = player_only

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

    def enrich(self, packet, packet_name):

        header = packet.header
        packet_dict = packet.to_dict()

        if not self.player_car_index:
            self.player_car_index = header.player_car_index

        if not self.session and packet_name == 'PacketSessionData':
            self.session = self.process_session(packet_dict, header.session_uid)

        elif packet_name == 'PacketSessionData':
            if self.session.session_link_identifier != header.session_uid:
                self.session = None
                self.drivers = None
                self.laps = None

        if not self.drivers and packet_name == 'PacketParticipantsData':
            self.drivers = self.process_drivers(packet_dict)

        if not self.laps and packet_name == 'PacketLapData':
            self.laps = self.process_laps(packet_dict)

        if packet_name == 'PacketSessionHistoryData':
            self.process_session_history(packet_dict)

    def update(self):
        packet, packet_type = self.feed.get_latest()
        self.enrich(packet, packet_type.__name__)
        self.process(packet, packet_type.__name__)

    def process(self, packet, packet_name):

        if not self.session or not self.drivers or not self.laps:
            return

        if packet_name == 'PacketLapData':
            self.laps = self.process_laps(packet.to_dict())

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
                converted = self.influxdb_processor.convert(packet.to_dict(), packet_name, self.player_only)

                if converted:
                    try:
                        logger.info('Writing to InfluxDB')
                        self.write_to_influxdb(converted)
                        logger.info('Written to InfluxDB')
                    except (ConnectTimeoutError, ReadTimeoutError) as exc:
                        logger.exception(exc)

    def process_laps(self, data: Dict) -> CurrentLaps:
        laps = []

        for lap in data['lap_data']:
            if lap['lap_distance'] < 0:
                lap['lap_distance'] = 0
            if lap['total_distance'] < 0:
                lap['total_distance'] = 0
            lap = Lap(**lap)
            laps.append(lap)

        return CurrentLaps(laps=laps)

    def process_session(self, data: Dict, session_link_identifier: int) -> Session:
        circuit = TRACK_IDS[data['track_id']]
        session_type = SESSION_TYPE[data['session_type']]
        return Session(
            circuit=circuit,
            session_type=session_type,
            session_link_identifier=session_link_identifier
        )

    def process_drivers(self, data: Dict) -> Drivers:
        drivers: List[Driver] = []

        for raw_driver in data['participants']:
            if raw_driver['team_id'] != 255:

                # handle custom driver
                if raw_driver['driver_id'] in DRIVER_IDS:
                    driver_name = DRIVER_IDS[raw_driver['driver_id']]
                else:
                    driver_name = raw_driver['name']

                if raw_driver['team_id'] in TEAM_IDS:
                    team = TEAM_IDS[raw_driver['team_id']]
                else:
                    team = 'unknown'

                driver = Driver(
                    ai_controlled=raw_driver['ai_controlled'],
                    driver_name=driver_name,
                    network_id=raw_driver['network_id'],
                    team_name=team,
                    my_team=raw_driver['my_team'],
                    race_number=raw_driver['race_number'],
                    nationality=raw_driver['nationality'],
                    name=raw_driver['name'],
                    your_telemetry=raw_driver['your_telemetry']
                )
                drivers.append(driver)

        return Drivers(drivers=drivers, num_active_cars=data['num_active_cars'])

    def process_session_history(self, data: Dict) -> Dict:
        if not self.session_history and data['car_idx'] != 0:
            return

        for k, v in data.items():
            if k == 'header':
                continue
            if data['car_idx'] not in self.session_history:
                self.session_history[data['car_idx']] = {}
            self.session_history[data['car_idx']][k] = v
        return self.session_history
