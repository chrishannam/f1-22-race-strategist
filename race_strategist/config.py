"""
Configurations models for service setup.

Currently supports:
    * Kafka
    * InfluxDB

By default the config should be located in ~/.config/race_strategist/config.ini

Example file:
[influxdb]
host = 192.168.0.101:8086
token = 8DxTEtW0PoCypTmxzXbSzTn8xPF39iiIVvW9bkvmf2wK2i6yth26dy-TabZp5IBAk
org = F1
bucket = telemetry_2020

[kafka]
bootstrap_servers = 192.168.0.102:9092
"""

import configparser

from pathlib import Path
from dataclasses import dataclass
import logging
from typing import Union

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

logger = logging.getLogger(__name__)

HOME: Path = Path.home()
CONFIG_FILE_NAME: str = 'race_strategist.ini'


@dataclass
class KafkaConfiguration:
    bootstrap_servers: str


@dataclass
class InfluxDBConfiguration:
    host: str
    token: str
    org: str
    bucket: str


@dataclass
class RecorderConfiguration:
    kafka: Union[KafkaConfiguration, None] = None
    influxdb: Union[InfluxDBConfiguration, None] = None


def load_config(
    filename: Path = HOME / '.config' / CONFIG_FILE_NAME,
) -> RecorderConfiguration:
    config = configparser.ConfigParser()
    config_file = Path(filename)
    recorder_config = RecorderConfiguration()

    if config_file.is_file():
        config.read(filename)
    else:
        logger.warning('Unable to find config file.')
        return recorder_config

    for section in config.keys():
        if section == 'kafka':
            recorder_config.kafka = KafkaConfiguration(
                bootstrap_servers=config[section]['bootstrap_servers']
            )

        if section == 'influxdb':
            recorder_config.influxdb = InfluxDBConfiguration(
                config[section]['host'],
                config[section]['token'],
                config[section]['org'],
                config[section]['bucket'],
            )

    return recorder_config
