import click

from race_strategist.config import load_config
from race_strategist.recorder import DataRecorder


@click.command()
@click.option("--port", default=20777, help="port to listen on")
def main(port: int = 20777):
    config = load_config()
    recorder = DataRecorder(config, port=port)
    recorder.collect()


if __name__ == "__main__":
    main()
