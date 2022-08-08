from typing import List

from flask import Flask, render_template
from datetime import datetime

from influxdb_client import InfluxDBClient

# You can generate an API token from the "API Tokens Tab" in the UI
token = "nRmeV1gIRAstJJVlDW6pWdf0qtsQ1hgsk7qLMl_2nZfNeWKbBx8TPE_5KfxCsAW44beNyWWh8RdpgKzuU4VF3g=="
org = "f1"
bucket = "f1"


app = Flask(__name__,
            static_url_path='',
            static_folder='web/static',
            template_folder='web/templates')


def main():
    # return 17
    values = {}
    with InfluxDBClient(url="http://ultron:8086", token=token, org=org) as client:
        query = """
from(bucket: "f1")
  |> range(start: -10m)
  |> filter(fn: (r) => r["_measurement"] == "Session")
  |> filter(fn: (r) => r["_field"] == "pit_stop_window_ideal_lap" 
  or r["_field"] == "pit_stop_window_latest_lap" 
  or r["_field"] == "pit_stop_rejoin_position" 
  or r["_field"] == "air_temperature" 
  or r["_field"] == "air_temperature_change" 
  or r["_field"] == "track_temperature" 
  or r["_field"] == "track_temperature_change")
  |> aggregateWindow(every: 500ms, fn: mean, createEmpty: false)
  |> yield(name: "mean")
  """
        tables = client.query_api().query(query, org=org)
        for table in tables:
            for record in table.records:
                values[record.values['_field']] = int(record.get_value())

    return values


@app.route("/")
def hello():
    pit_stop_stats = main()
    return render_template('index.html', **pit_stop_stats)


@app.route("/callback")
def callback():
    return "Hello, World!"


if __name__ == "__main__":
    data = main()
    print(data)
