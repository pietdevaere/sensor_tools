import sensing_tools
import time

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_co2 import BrickletCO2
from tinkerforge.bricklet_segment_display_4x7 import BrickletSegmentDisplay4x7
from tinkerforge.bricklet_ambient_light_v2 import BrickletAmbientLightV2

co2_UID = "EnX"
segment_UID = "wNw"
ambient_light_UID = "yCP"

def int2segments(value):
    digit2segments = [0x3f,0x06,0x5b,0x4f,
                    0x66,0x6d,0x7d,0x07,
                    0x7f,0x6f,0x77,0x7c,
                    0x39,0x5e,0x79,0x71] # // 0~9,A,b,C,d,E,F

    significant = False
    segment_index = 0
    segment_values = [0x00, 0x00, 0x00, 0x00]
    digit_position = 1000
    while digit_position > 0:
        # Extract digit
        digit = (value // digit_position) % 10
        if digit != 0:
            significant = True

        # set segment display value
        if significant or segment_index == 4:
            segment_values[segment_index] = digit2segments[digit]

        digit_position = digit_position // 10
        segment_index = segment_index + 1

    return segment_values

reporter = sensing_tools.InfluxReporter("secrets.json")
brick_config = sensing_tools.read_secrets("secrets.json")["tinkerforge"]

ipcon = IPConnection()
co2_bricklet = BrickletCO2(co2_UID, ipcon)
segment_bricklet = BrickletSegmentDisplay4x7(segment_UID, ipcon)
ambient_light_bricklet = BrickletAmbientLightV2(ambient_light_UID, ipcon)
ipcon.connect(brick_config['host'], brick_config['port'])

while True:
    co2_concentration = co2_bricklet.get_co2_concentration()
    print("CO2 concentration: {} ppm".format(co2_concentration))
    segment_bricklet.set_segments(int2segments(co2_concentration), 7, False)
    reporter.report("co2", "tinkerforge", "CAB F81", co2_concentration)

    illuminance = ambient_light_bricklet.get_illuminance() / 100.0
    print("Illuminance: {} lx".format(illuminance))
    reporter.report("ambient_light", "LTR329ALS", "CAB F81", illuminance)

    time.sleep(1)
