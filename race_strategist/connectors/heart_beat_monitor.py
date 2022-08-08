"""
Read data from serial port.
By default we assume the data coming over the serial port
is JSON.

This can be changed to expect csv by:

sensor = SerialSensor(port='ttyUSB0', json_data=False)
"""

import glob
import json
import logging
from json import JSONDecodeError

import serial
import os.path
import time

# usual linux ports
# from race_strategist.connectors.influxdb import InfluxDBConnector
#
# PORTS = ["ttyUSB0", "ttyUSB1", "ttyAMA0", "ttyACM0"]
# SERIAL_PORT_PATH_ROOT = "/dev/"
#
#
# logging.basicConfig(
#     level=logging.ERROR,
#     format="%(asctime)s.%(msecs)03d %(levelname)s: %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )
#
# logger = logging.getLogger(__name__)
#
#
# class SerialSensor:
#     def __init__(self, port=None, json_data=True, debug=True):
#         if port:
#             self.serial_port = port
#         else:
#             logger.info("Finding port.")
#             self.serial_port = _detect_port()
#         self.ser = serial.Serial(self.serial_port, 9600, timeout=1)
#
#         self.debug = debug
#         self.json_data = json_data
#
#         logger.debug(f"Using {self.serial_port} as serial port")
#
#     def read(self, timeout=1):
#
#         if not self.serial_port:
#             logger.error("Unable to find anything on the serial port to read from.")
#             return
#
#         stop = time.time() + timeout
#         i = 0
#
#         while time.time() < stop:
#             i = i + 1
#             raw_serial = self.ser.readline()
#
#             logger.debug(f"Attempt {i}: Received: {raw_serial}")
#
#             if self.json_data and raw_serial:
#                 try:
#                     return json.loads(raw_serial)
#                 except JSONDecodeError:
#                     logger.debug(f"Failed to decode to JSON: {raw_serial}")
#             else:
#                 logger.debug("Failed to decode anything")
#
#
# def _detect_port():
#
#     device_path = None
#
#     for port in PORTS:
#         device = SERIAL_PORT_PATH_ROOT + port
#         if os.path.exists(device):
#             device_path = device
#
#     if not device_path:
#         # lets try osx stuff
#         for file_name in glob.glob1("/dev", "tty.usbserial-*"):
#             device_path = SERIAL_PORT_PATH_ROOT + file_name
#     return device_path
#
#
# if __name__ == "__main__":
#     print("starting!")
#     # influx_conn = InfluxDBConnector('/Users/channam/.config/race_strategist/config.ini')
#     while True:
#         sensor_reader = SerialSensor(port=_detect_port())
#         reading = sensor_reader.read()
#
#         if reading:
#             print(f"{reading}")
#             data = [f"health,tag=pulse pulse={reading['bpm']}"]
#             # influx_conn.write(data)
