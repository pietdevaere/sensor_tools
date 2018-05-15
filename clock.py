#!/usr/bin/env python
# -*- coding: utf-8 -*-

HOST = "192.168.1.9"
PORT = 4223
UID = "Bku" # Change XYZ to the UID of your OLED 128x64 Bricklet

import time
import datetime

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_oled_128x64 import BrickletOLED128x64

from PIL import Image, ImageDraw, ImageFont

DISP_WIDTH  = 128
DISP_HEIGHT = 64
DISP_ROWS   = 8
ROW_HEIGHT  = DISP_HEIGHT // DISP_ROWS


def make_byte_for_display(row, column, bitmap):
    multiplier = 1
    cursor = row * ROW_HEIGHT * DISP_WIDTH + column
    result = 0
    for i in range(ROW_HEIGHT):
        result += bitmap[cursor] * multiplier
        multiplier *= 2
        cursor += DISP_WIDTH
    return result

def draw_bitmap(display, bitmap):
    display.new_window(0, DISP_WIDTH - 1, 0, DISP_ROWS - 1)

    buffer = list()
    for row in range(DISP_ROWS):
        for column in range(DISP_WIDTH):
            buffer.append(make_byte_for_display(row, column, bitmap))
            if len(buffer) == 64:
                display.write(buffer)
                buffer = list()

if __name__ == "__main__":
    ipcon = IPConnection() # Create IP connection
    oled = BrickletOLED128x64(UID, ipcon) # Create device object

    ipcon.connect(HOST, PORT) # Connect to brickd
    # Don't use device before ipcon is connected

    font = ImageFont.truetype("DroidSansMono.ttf", size=40)

    while True:
        image = Image.new("1", (DISP_WIDTH, DISP_HEIGHT))
        draw = ImageDraw.Draw(image)
        current_time = datetime.datetime.now()
        #text = time.strftime("%H{}%M".format(":" if current_time.second % 2 else " "))
        text = time.strftime("%H:%M")
        draw.text((5, 10), text, 1, font=font)
    #    oled.clear_display()
        bitmap = list(image.getdata())
        if current_time.second % 2:
            bitmap[-1] = 1
        draw_bitmap(oled, bitmap)
        time.sleep(1 - current_time.microsecond/1e6)

    ipcon.disconnect()
