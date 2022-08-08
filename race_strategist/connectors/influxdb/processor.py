
from influxdb_client import Point
from typing import Dict
from race_strategist.modelling.processor import Processor
from race_strategist.session.session import Driver, CurrentLaps


class InfluxDBProcessor(Processor):

    def convert(self, data: Dict, packet_name: str):
        data_name = packet_name.replace('Packet', '').replace('Data', '').replace('Car', '')

        if packet_name in ['PacketCarSetupData', 'PacketMotionData',
                           'PacketCarDamageData', 'PacketCarTelemetryData',
                           'PacketCarStatusData']:
            return self.extract_car_array_data(packet=data, data_name=data_name)
        elif packet_name == 'PacketLapData':
            return self._process_laps(laps=data, data_name=data_name)
        elif packet_name == 'PacketSessionData':
            return self._process_session(session=data, data_name=data_name)
        elif packet_name == 'PacketSessionHistoryData':
            return self._process_session_history(session=data, data_name=data_name)

    def _process_session_history(self, session: Dict, data_name: str):
        driver = self.drivers.drivers[session['car_idx']]
        points = []

        for name, value in session.items():
            if name in ['header', 'car_idx', 'num_laps']:
                continue
            if isinstance(value, float) or isinstance(value, int):
                points.append(
                    self.create_point(
                        packet_name=data_name,
                        key=name,
                        value=value,
                        lap=self.current_lap.current_lap_num,
                        driver=driver,
                        team=driver.team_name
                    )
                )
            elif isinstance(value, list):
                for index, lap_data in enumerate(value):
                    if name == 'lap_history_data':
                        if lap_data['lap_time_in_ms'] != 0:
                            for k, v in lap_data.items():
                                # 0x01 bit set-lap valid,
                                # 0x02 bit set-sector 1 valid
                                # 0x04 bit set-sector 2 valid
                                # 0x08 bit set-sector 3 valid

                                points.append(
                                    self.create_point(
                                        packet_name=data_name,
                                        key=k,
                                        value=v,
                                        lap=self.current_lap.current_lap_num,
                                        driver=driver,
                                        team=driver.team_name
                                    )
                                )
                    elif name == 'tyre_stints_history_data':
                        for k, v in lap_data.items():
                            if k == 'end_lap' and v == 0:
                                break

                            points.append(
                                self.create_point(
                                    packet_name=data_name,
                                    key=k,
                                    value=v,
                                    lap=self.current_lap.current_lap_num,
                                    driver=driver,
                                    team=driver.team_name
                                )
                            )
        return points

    def _process_session(self, session: Dict, data_name: str):
        points = []
        for name, value in session.items():
            if name == 'header':
                continue
            if isinstance(value, float) or isinstance(value, int):
                points.append(
                    self.create_point(
                        packet_name=data_name,
                        key=name,
                        value=value,
                        lap=self.current_lap.current_lap_num
                    )
                )
            elif isinstance(value, list):
                if name == 'weather_forecast_samples':
                    continue
                else:
                    for i in value:
                        if isinstance(i, dict):
                            for k, v in i.items():
                                points.append(
                                    self.create_point(
                                        packet_name=data_name,
                                        key=k,
                                        value=v,
                                        lap=self.current_lap.current_lap_num
                                    )
                                )
        return points

    def _process_laps(self, laps: Dict, data_name: str):
        points = []
        for driver_index, lap in enumerate(laps['lap_data']):
            if driver_index >= len(self.drivers.drivers):
                continue

            for name, value in lap.items():

                if name == 'current_lap_num':
                    pass
                driver = self.drivers.drivers[driver_index]
                lap_number: int = lap['current_lap_num']
                points.append(
                    self.create_point(
                        packet_name=data_name,
                        key=name,
                        value=value,
                        lap=lap_number,
                        driver=driver,
                        team=driver.team_name
                    )
                )
        return points

    def update_laps(self, laps: CurrentLaps):
        self.laps = laps

    def create_point(self, packet_name: str, key: str, value: float, lap: int, driver: Driver = None, team: str = None,
                     tags: Dict = None) -> Point:

        if tags is None:
            tags = dict()

        point = Point(packet_name).tag('circuit', self.session.circuit) \
            .tag('session_uid', self.session.session_link_identifier) \
            .tag('session_type', self.session.session_type) \
            .tag('lap', lap) \
            .field(key, value)

        if driver:
            point.tag('driver_name', driver.driver_name)
        if team:
            point.tag('team', team)

        for tag_name, tag_value in tags.items():
            point.tag(tag_name, tag_value)

        return point

    def extract_car_array_data(self, packet: Dict, data_name: str):
        points = []

        lap_number = self.laps.laps[packet['header']['player_car_index']].current_lap_num
        driver = self.drivers.drivers[packet['header']['player_car_index']]

        for name, value in packet.items():
            if name == 'header':
                continue

            if isinstance(value, list) and len(value) == 4:
                for location, corner in enumerate(['rear_left', 'rear_right', 'front_left', 'front_right']):
                    points.append(
                        self.create_point(
                            packet_name=data_name,
                            key=name,
                            value=round(value[location], 6),
                            tags={'corner': corner},
                            lap=lap_number,
                            driver=driver,
                            team=driver.team_name
                        )
                    )
            elif isinstance(value, list):
                for idx, data in enumerate(packet[list(packet.keys())[1]]):
                    if idx >= len(self.drivers.drivers):
                        continue

                    for name, value in data.items():
                        driver = self.drivers.drivers[idx]
                        if isinstance(value, list) and len(value) == 4:
                            for location, corner in enumerate(['rear_left', 'rear_right', 'front_left', 'front_right']):
                                points.append(
                                    self.create_point(
                                        packet_name=data_name,
                                        key=name,
                                        value=value[location],
                                        tags={'corner': corner},
                                        lap=lap_number,
                                        driver=driver,
                                        team=driver.team_name
                                    )
                                )
                        elif isinstance(value, list):
                            pass
                        else:
                            points.append(
                                self.create_point(
                                    packet_name=data_name,
                                    key=name,
                                    value=value,
                                    lap=lap_number,
                                    driver=driver,
                                    team=driver.team_name
                                )
                            )
            else:
                points.append(
                    self.create_point(
                        packet_name=data_name,
                        key=name,
                        value=value,
                        lap=lap_number,
                        driver=driver,
                        team=driver.team_name
                    )
                )
        return points
