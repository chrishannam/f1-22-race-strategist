# F1 2021 - The Official Video Game from Codemasters
A tool for forwarding the UDP telemetry data from the simulator game F1 2021 to InfluxDB
for display via any graphing application.

[UDP Specification](https://forums.codemasters.com/topic/80231-f1-2021-udp-specification/)

# Data Storage
Is done by [InfluxDB](https://www.influxdata.com/) which is a great time series 
database.
See [Docker Hub](https://hub.docker.com/_/influxdb).
```bash
docker pull quay.io/influxdb/influxdb:latest
```

# Graphing Using Grafana
You can use Grafana to connect to InfluxDB. See - https://grafana.com/docs/grafana/latest/installation/docker/
```bash
docker run -d -p 3000:3000 grafana/grafana
```

## Connection to InfluxDB
Connecting to InfluxDB 2 requires Grafana 7.1 and above.

![Top half of config of datasource](docs/images/influxdb_grafana_config_1.png)
![Bottom half of config of datasource](docs/images/influxdb_grafana_config_2.png)

## Refresh Rate
To enable sub second updates, alter the following in `/etc/grafana/grafana.ini`

```ini
#################################### Dashboards History ##################
[dashboards]
# Number dashboard versions to keep (per dashboard). Default: 20, Minimum: 1
;versions_to_keep = 20
min_refresh_interval = 100ms
```

Next add the refresh rate as an option in the dashboard setting, otherwise you won't be able
to select it.

![Set refresh rate](docs/images/grafana_refresh_rate.png)

# Links
* Excellent Telemetry tool [PXG F1](https://bitbucket.org/Fiingon/pxg-f1-telemetry/src)
* Similar project using [Kafka](https://www.youtube.com/watch?v=Re9LOAYZi2A) and
  with [Camel](https://www.youtube.com/watch?v=2efOtyFAZ4s)

# Demo
YouTube:
* [Grafana Demo](https://youtu.be/zWDqIcY03e0)


# Telemetry
Wheel speed in meters per second.
Wheel slip is 0 -> 1  


https://www.reddit.com/user/jeppe96/posts/
