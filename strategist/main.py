import click
import logging

from race_strategist.config import load_config
from race_strategist.recorder import DataRecorder

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


# https://opentelemetry.io/docs/instrumentation/python/getting-started/
# https://opentelemetry-python.readthedocs.io/en/latest/exporter/jaeger/jaeger.html

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "Bernie"})
    )
)
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    # configure agent
    agent_host_name='localhost',
    agent_port=6831,
)


@click.command()
@click.option("--port", default=20777, help="port to listen on")
@click.option("--all-drivers", default=True, help="collect all driver data", required=False)
def run(port: int = 20777, all_drivers: bool = None):
    config = load_config()
    recorder = DataRecorder(config, port=port, all_drivers=all_drivers)
    logger.info('Collecting data...')

    with tracer.start_as_current_span("fetch_packet") as fetch_packet:
        packet_name = recorder.collect()
        fetch_packet.set_attribute("packet.name", packet_name)


if __name__ == "__main__":
    run()