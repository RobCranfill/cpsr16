"""Display using Adafruit 128x64 I2C OLED, product ID 326.
   Display area is x rows of y characters."""

import board
import busio
import time

import displayio
import i2cdisplaybus
import adafruit_displayio_ssd1306
from adafruit_display_text import label
import terminalio


I2C_ADDRESS = 0x3D
WIDTH  = 128
HEIGHT =  64 

BOARD_SCL = board.GP1
BOARD_SDA = board.GP0

BLACK = 0x00_00_00
WHITE = 0xFF_FF_FF


class Display_OLED:

    def __init__(self):

        displayio.release_displays()
        i2c = busio.I2C(scl=BOARD_SCL, sda=BOARD_SDA)
        display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=I2C_ADDRESS)
        display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

        # Make the display context
        splash = displayio.Group()
        display.root_group = splash

        # black background
        color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = BLACK
        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        splash.append(bg_sprite)
        

        y_height = 11

        y = 8
        text_area = label.Label(terminalio.FONT, text="DM Ready!", scale=2, color=WHITE, x=0, y=y)
        splash.append(text_area)
        self._text_area_1 = text_area

        y += y_height * 2
        text_area = label.Label(terminalio.FONT, text="", scale=2, color=WHITE, x=0, y=y)
        splash.append(text_area)
        self._text_area_2 = text_area

        y += y_height
        text_area = label.Label(terminalio.FONT, text="", color=WHITE, x=0, y=y)
        splash.append(text_area)
        self._text_area_3 = text_area

        # print(".__init__() OK!")

    def show_setup_name(self, name):
        # self.__set_text_1(f"Setup: {name}")
        self.__set_text_1(name)

    def show_pattern_name(self, name):
        # self.__set_text_2(f"Patt: {name}")
        self.__set_text_2(name)
    
    # too much actvitiy for display?
    def show_beat_number(self, n):
        self.__set_text_3(f"Beat: {n}")


    def __set_text_1(self, text):
        self._text_area_1.text = text

    def __set_text_2(self, text):
        self._text_area_2.text = text

    def __set_text_3(self, text):
        self._text_area_3.text = text


