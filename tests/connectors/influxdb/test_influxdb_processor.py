from typing import Dict

from connectors.influxdb import InfluxDBProcessor


def test_process_event_packet(laps_dict: Dict, processor: InfluxDBProcessor):

    results = processor._process_laps(laps_dict, 'test_laps')
    assert len(results) == 480


def test_process_motion_packet(car_motion_dict: Dict, processor: InfluxDBProcessor):

    results = processor.extract_car_array_data(car_motion_dict, 'test_motion')
    assert len(results) == 375


def test_process_session(session_packet_dict: Dict, processor: InfluxDBProcessor):
    results = processor._process_session(session=session_packet_dict, packet_name='test_session')
    assert len(results) == 526


def test_process_session_history(session_history_packet_dict: Dict, processor: InfluxDBProcessor):
    results = processor._process_session_history(session=session_history_packet_dict, packet_name='test_session')
    assert len(results) == 28
