from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate an API token from the "API Tokens Tab" in the UI
token = "nRmeV1gIRAstJJVlDW6pWdf0qtsQ1hgsk7qLMl_2nZfNeWKbBx8TPE_5KfxCsAW44beNyWWh8RdpgKzuU4VF3g=="
org = "f1"
bucket = "Telegraf"


def main():
    with InfluxDBClient(url="http://ultron:8086", token=token, org=org) as client:
        query = """
        from(bucket: "f1")
  |> range(start: time(v: 2022-04-10T10:12:18.500Z), stop: time(v: 2022-04-10T11:12:18.500Z))
  |> filter(fn: (r) => r["_measurement"] == "Session")
  |> filter(fn: (r) => r["_field"] == "pit_stop_rejoin_position")
  |> aggregateWindow(every: 500ms, fn: mean, createEmpty: false)
  |> yield(name: "mean")
  """
        tables = client.query_api().query(query, org=org)
        for table in tables:
            for record in table.records:
                print(record)


if __name__ == '__main__':
    main()
