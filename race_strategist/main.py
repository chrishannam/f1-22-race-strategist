import click
import logging

from race_strategist.config import load_config
from race_strategist.recorder import DataRecorder
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--port", default=20777, help="port to listen on")
@click.option("--all-drivers", default=True, help="collect all driver data", required=False)
def run(port: int = 20777, all_drivers: bool = None):
    config = load_config()
    recorder = DataRecorder(config, port=port, all_drivers=all_drivers)
    logger.info('Collecting data...')
    recorder.collect()


if __name__ == "__main__":
    run()
