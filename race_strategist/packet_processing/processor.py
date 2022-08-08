from abc import ABC, abstractmethod
from typing import Dict, List

from race_strategist.session.session import Drivers, Driver, CurrentLaps, Lap, Session
from race_strategist.telemetry.constants import TEAMS, DRIVERS, TRACK_IDS, SESSION_TYPE


class Processor(ABC):
    def __init__(self, session: Session, drivers: Drivers, laps: CurrentLaps):
        self.session = session
        self.drivers = drivers
        self.laps: CurrentLaps = laps
        self.session_history = {}
        self._leader = None
        self._current_lap = None

    @abstractmethod
    def convert(self, data):
        pass

    @property
    def leader(self):
        for driver_index, lap in enumerate(self.laps.laps):
            if lap.car_position == 1:
                self._leader = self.drivers[driver_index]
                break
        return self._leader

    @property
    def current_lap(self):
        for driver_index, lap in enumerate(self.laps.laps):
            if lap.car_position == 1:
                self._current_lap = lap
                break
        return self._current_lap


def process_participants(participants_packet_data):
    drivers = []
    for raw_driver in participants_packet_data['participants']:
        if raw_driver['team_id'] != 255:
            # handle custom driver
            if raw_driver['driver_id'] in DRIVERS:
                driver_name = DRIVERS[raw_driver['driver_id']]
            else:
                driver_name = raw_driver['name']

            if raw_driver['team_id'] in TEAMS:
                team_name = TEAMS[raw_driver['team_id']]
            else:
                team_name = 'Unknown'

            driver = Driver(
                ai_controlled=raw_driver['ai_controlled'],
                driver_name=driver_name,
                network_id=raw_driver['network_id'],
                team_name=team_name,
                my_team=raw_driver['my_team'],
                race_number=raw_driver['race_number'],
                nationality=raw_driver['nationality'],
                name=raw_driver['name'],
                your_telemetry=raw_driver['your_telemetry']
            )
            drivers.append(driver)

    return Drivers(drivers=drivers, num_active_cars=participants_packet_data['num_active_cars'])


def process_laps(data: Dict) -> CurrentLaps:
    laps = []

    for lap in data['lap_data']:
        lap = Lap(**lap)
        laps.append(lap)

    return CurrentLaps(laps=laps)


def process_session(data: Dict, session_link_identifier: int) -> Session:
    circuit = TRACK_IDS[data['track_id']]
    session_type = SESSION_TYPE[data['session_type']]
    return Session(
        circuit=circuit,
        session_type=session_type,
        session_link_identifier=session_link_identifier
    )


def process_drivers(data: Dict) -> Drivers:
    drivers: List[Driver] = []

    for raw_driver in data['participants']:
        if raw_driver['team_id'] != 255:

            # handle custom driver
            if raw_driver['driver_id'] in DRIVERS:
                driver_name = DRIVERS[raw_driver['driver_id']]
            else:
                driver_name = raw_driver['name']

            if raw_driver['team_id'] in TEAMS:
                team = TEAMS[raw_driver['team_id']]
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


def process_session_history(data: Dict) -> Dict:
    session_history = {}
    for k, v in data.items():
        if k == 'header':
            continue
        if data['car_idx'] not in session_history:
            session_history[data['car_idx']] = {}
        session_history[data['car_idx']][k] = v
    return session_history
