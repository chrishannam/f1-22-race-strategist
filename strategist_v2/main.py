import asyncio

import click
import logging

from race_strategist.config import load_config
from race_strategist.recorder import DataRecorder
from strategist_v2.recorder import SpeedyDataRecorder

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


def main():
    config = load_config()
    recorder = SpeedyDataRecorder(config, port=20777)

    while True:
        logger.info('Collecting data...')
        recorder.update()
        logger.info('Complete')


if __name__ == "__main__":
    main()
