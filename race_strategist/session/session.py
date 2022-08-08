from dataclasses import dataclass
from typing import List


@dataclass
class Session:
    circuit: str
    session_type: str
    session_link_identifier: int


@dataclass
class Lap:
    number: int


@dataclass
class Driver:
    ai_controlled: int
    driver_name: str
    network_id: int
    team_name: str
    my_team: int
    race_number: int
    nationality: str
    name: str
    your_telemetry: int


@dataclass
class Lap:
    last_lap_time_in_ms: float
    current_lap_time_in_ms: float
    sector1_time_in_ms: float
    sector2_time_in_ms: float
    lap_distance: float
    total_distance: float
    safety_car_delta: float
    car_position: float
    current_lap_num: int
    pit_status: float
    num_pit_stops: float
    sector: float
    current_lap_invalid: float
    penalties: float
    warnings: float
    num_unserved_drive_through_pens: float
    num_unserved_stop_go_pens: float
    grid_position: float
    driver_status: float
    result_status: float
    pit_lane_timer_active: float
    pit_lane_time_in_lane_in_ms: float
    pit_stop_timer_in_ms: float
    pit_stop_should_serve_pen: float


@dataclass
class CurrentLaps:
    laps: List[Lap]


@dataclass
class Drivers:
    """List of drivers based on the order from the game."""

    drivers: List[Driver]
    num_active_cars: int
