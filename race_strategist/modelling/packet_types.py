from dataclasses import dataclass
from typing import List


@dataclass
class FrontLeftReading:
    value: float


@dataclass
class FrontRightReading:
    value: float


@dataclass
class RearLeftReading:
    value: float


@dataclass
class RearRightReading:
    value: float


@dataclass
class CornerReadings:
    front_left: FrontLeftReading
    front_right: FrontRightReading
    rear_right: RearRightReading
    rear_left: RearLeftReading


@dataclass
class CarDamage:

    tyre_wear: CornerReadings
    tyre_damage: CornerReadings
    brakes_damage: CornerReadings
    front_left_wing_damage: float
    front_right_wing_damage: float
    rear_wing_damage: float
    floor_damage: float
    diffuser_damage: float
    sidepod_damage: float
    drs_fault: float
    gear_box_damage: float
    engine_damage: float
    engine_mguhwear: float
    engine_eswear: float
    engine_cewear: float
    engine_icewear: float
    engine_mgukwear: float
    engine_tcwear: float

    def dump(self, processor):
        processor.dump()