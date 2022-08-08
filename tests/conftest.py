import json

import pytest
from pathlib import Path
from race_strategist.config import InfluxDBConfiguration, RecorderConfiguration
from connectors.influxdb import InfluxDBProcessor
from race_strategist.recorder import DataRecorder
from race_strategist.session.session import Session, Drivers, CurrentLaps, Driver, Lap

PACKET_DATA_ROOT = Path(__file__).parent / 'example_packets'


class DummyPacket:
    def __init__(self, data):
        self.data = data

    def to_dict(self):
        return self.data


@pytest.fixture
def laps_dict():
    with open(PACKET_DATA_ROOT / 'lap.json') as file:
        data = json.load(file)

    return data


@pytest.fixture
def participants():
    with open(PACKET_DATA_ROOT / 'participants.json') as file:
        data = json.load(file)

    return data


@pytest.fixture
def car_motion_dict():
    with open(PACKET_DATA_ROOT / 'motion.json') as file:
        data = json.load(file)

    return data


@pytest.fixture
def car_damage_dict():
    with open(PACKET_DATA_ROOT / 'car_damage.json') as file:
        data = json.load(file)

    return data


@pytest.fixture
def car_setup_dict():
    with open(PACKET_DATA_ROOT / 'car_setup.json') as file:
        data = json.load(file)

    return data


@pytest.fixture
def car_status_dict():
    with open(PACKET_DATA_ROOT / 'car_status.json') as file:
        data = json.load(file)

    return data


@pytest.fixture
def car_telemetry_dict():
    with open(PACKET_DATA_ROOT / 'car_telemetry.json') as file:
        data = json.load(file)

    return data


@pytest.fixture
def telemetry_packet_json():
    with open(PACKET_DATA_ROOT / 'car_telemetry.json') as file:
        data = json.load(file)

    return DummyPacket(data)


@pytest.fixture
def session_packet_dict():
    with open(PACKET_DATA_ROOT / 'session.json') as file:
        data = json.load(file)

    return data


@pytest.fixture
def session_history_packet_dict():
    with open(PACKET_DATA_ROOT / 'session_history.json') as file:
        data = json.load(file)

    return data


@pytest.fixture
def participants_packet_data():
    with open(PACKET_DATA_ROOT / 'participants.json') as file:
        data = json.load(file)

    return data


@pytest.fixture
def event_packet_data():
    with open(PACKET_DATA_ROOT / 'event.json') as file:
        data = json.load(file)

    return data


@pytest.fixture
def data_recorder():
    return DataRecorder(RecorderConfiguration())


@pytest.fixture
def influxdb_config():
    return InfluxDBConfiguration(
        host='127.0.0.1',
        token='tokennn',
        org='org',
        bucket='la_bucket'
    )


@pytest.fixture
def session():
    return Session(
        circuit='test_circuit',
        session_type='test_session_type',
        session_link_identifier=1234
    )


@pytest.fixture
def drivers():
    drivers = []
    for i in range(1, 21):
        drivers.append(
            Driver(
                ai_controlled=0,
                driver_name=f'driver_name_{i}',
                network_id=0,
                team_name=f'team_name_{i}',
                my_team=0,
                race_number=0,
                nationality=f'nationality_{i}',
                name=f'driver_name_{i}',
                your_telemetry=0,
            )
        )

    return Drivers(
        drivers=drivers,
        num_active_cars=20
    )


@pytest.fixture
def laps(laps_dict):
    laps = []
    for lap in laps_dict['lap_data']:
        laps.append(Lap(**lap))

    return CurrentLaps(
        laps=laps
    )


@pytest.fixture
def processor(session, drivers, laps):
    return InfluxDBProcessor(session=session, drivers=drivers, laps=laps)
