import pytest

from race_strategist.config import (
    load_config,
    RecorderConfiguration,
    KafkaConfiguration,
    InfluxDBConfiguration,
)
from pathlib import Path


@pytest.fixture
def config_dir():
    return Path(__file__).resolve().parent / 'config_files'


def test_load_config_kafka(config_dir):
    config: RecorderConfiguration = load_config(config_dir / 'kafka.ini')

    assert isinstance(config.kafka, KafkaConfiguration)
    assert config.kafka.bootstrap_servers


def test_load_config_influxdb(config_dir):
    config: RecorderConfiguration = load_config(config_dir / 'influxdb.ini')

    assert isinstance(config.influxdb, InfluxDBConfiguration)
    assert config.influxdb.host
    assert config.influxdb.token
    assert config.influxdb.bucket
    assert config.influxdb.org


def test_load_config_empty(config_dir):
    config: RecorderConfiguration = load_config(config_dir / 'empty.ini')
    assert isinstance(config, RecorderConfiguration)
    assert not config.kafka
    assert not config.influxdb


def test_load_config_missing(config_dir):
    config: RecorderConfiguration = load_config('.')
    assert isinstance(config, RecorderConfiguration)
    assert not config.kafka
    assert not config.influxdb
