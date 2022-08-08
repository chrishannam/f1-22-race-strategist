from race_strategist.constants import TAGS
from race_strategist.recorder import extract_car_data


def test_extract_car_data(telemetry_packet_json, participants):
    extract_car_data(telemetry_packet_json, participants, TAGS)


def test_extract_session_data(session_packet_json, data_recorder):
    session_packet_json.pop('header')
    data_recorder.tags['session_uid'] = 1234
    data_recorder.tags['circuit'] = 'test'
    points = data_recorder.extract_session_data(session_packet_json)
    assert len(points) == 505
