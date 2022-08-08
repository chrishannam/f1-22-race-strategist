from typing import Dict


def convert(packet: Dict, packet_type: str):
    if packet_type == 'PacketCarDamageData':
        return convert_car_data(packet)


def convert_car_data(data):
    return data
