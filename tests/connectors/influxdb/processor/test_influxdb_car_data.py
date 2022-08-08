from typing import Dict
from pytest import fixture

from connectors.influxdb import InfluxDBProcessor
from race_strategist.session.session import Session, Lap, Drivers, Driver
from race_strategist.telemetry.constants import DRIVERS, TEAMS


@fixture
def session():
    return Session(
        circuit='test_circuit',
        session_type='winter_test',
        session_link_identifier=12344321
    )


@fixture
def participants(participants_packet_data):
    drivers = []
    for raw_driver in participants_packet_data['participants']:
        if raw_driver['team_id'] != 255:
            # handle custom driver
            if raw_driver['driver_id'] in DRIVERS:
                driver_name = DRIVERS[raw_driver['driver_id']]
            else:
                driver_name = raw_driver['name']

            driver = Driver(
                ai_controlled=raw_driver['ai_controlled'],
                driver_name=driver_name,
                network_id=raw_driver['network_id'],
                team_name=TEAMS[raw_driver['team_id']],
                my_team=raw_driver['my_team'],
                race_number=raw_driver['race_number'],
                nationality=raw_driver['nationality'],
                name=raw_driver['name'],
                your_telemetry=raw_driver['your_telemetry']
            )
            drivers.append(driver)

    return Drivers(drivers=drivers, num_active_cars=participants_packet_data['num_active_cars'])


@fixture
def lap():
    return Lap(number=1)


@fixture
def influxdb_processor(session, participants) -> InfluxDBProcessor:
    return InfluxDBProcessor(session, drivers=participants)


def test_car_damage(car_damage_dict: Dict, influxdb_processor: InfluxDBProcessor, lap):
    damage_points = influxdb_processor.convert_data(car_damage_dict, lap=lap, packet_name='PacketCarDamageData')
    assert len(damage_points) == 540


def test_car_setup(car_setup_dict: Dict, influxdb_processor: InfluxDBProcessor, lap):
    damage_points = influxdb_processor.convert_data(car_setup_dict, lap=lap, packet_name='PacketCarSetupData')
    assert len(damage_points) == 440


def test_car_status(car_status_dict: Dict, influxdb_processor: InfluxDBProcessor, lap):
    damage_points = influxdb_processor.convert_data(car_status_dict, lap=lap, packet_name='PacketCarStatusData')
    assert len(damage_points) == 460


def test_car_telemetry(car_telemetry_dict: Dict, influxdb_processor: InfluxDBProcessor, lap):
    damage_points = influxdb_processor.convert_data(car_telemetry_dict, lap=lap, packet_name='PacketCarTelemetryData')
    assert len(damage_points) == 620
