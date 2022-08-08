from connectors.influxdb import formatter


def test_telemetry_packet_formatting(telemetry_packet_json, race):

    result = formatter(data=telemetry_packet_json, index=19, race=race, lap=2)

    assert result

