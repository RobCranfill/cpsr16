"""Display using Adafruit 128x32 I2C OLED.
   Display area is 3 rows of 20 characters."""

import board
import busio
import random
import time

import displayio
import i2cdisplaybus
import adafruit_displayio_ssd1306
from adafruit_display_text import label
import terminalio


WIDTH  = 128
HEIGHT =  32 

BLACK = 0x00_00_00
WHITE = 0xFF_FF_FF

ANIMATION_INTERVAL = 1.0 # seconds


class Display:

    def __init__(self, i2c, oled_i2c_address):

        displayio.release_displays()

        display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=oled_i2c_address)
        display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

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

        y = 4
        text_area = label.Label(terminalio.FONT, text="DM Ready!", color=WHITE, x=2, y=y)
        splash.append(text_area)
        self._text_area_1 = text_area

        y += y_height
        text_area = label.Label(terminalio.FONT, text="", color=WHITE, x=2, y=y)
        splash.append(text_area)
        self._text_area_2 = text_area

        y += y_height
        text_area = label.Label(terminalio.FONT, text="", color=WHITE, x=2, y=y)
        splash.append(text_area)
        self._text_area_3 = text_area

        self.__last_anim = time.monotonic()

        # print(".__init__() OK!")

    def show_setup_name(self, name):
        self.__set_text_1(f"Setup: {name}")

    def show_pattern_name(self, name):
        self.__set_text_2(f"Patt: {name}")
    
    # # too much actvitiy for display?
    # def show_beat_number(self, n):
    #     self.__set_text_3(f"Beat: {n}")

    def blank(self):
        self.__hold_text_1 = self._text_area_1.text
        self.__hold_text_2 = self._text_area_2.text
        self.__hold_text_3 = self._text_area_3.text
        self.__hold_text_4 = self._text_area_4.text

        self.__set_text_1("")
        self.__set_text_2("")
        self.__set_text_3("")
        self.__set_text_4("")

    def unblank(self):
        self.__set_text_1(self.__hold_text_1)
        self.__set_text_2(self.__hold_text_2)
        self.__set_text_3(self.__hold_text_3)
        self.__set_text_4(self.__hold_text_4)

    def animate_idle(self):
        if time.monotonic() - ANIMATION_INTERVAL > self.__last_anim:
            c = chr(random.randrange(97, 97 + 26))
            p = random.randint(0, 20)
            l = [' '] * 21
            l[p] = c
            self.__set_text_4("".join(l))
            self.__last_anim = time.monotonic()


## Private methods

    def __set_text_1(self, text):
        self._text_area_1.text = text

    def __set_text_2(self, text):
        self._text_area_2.text = text

    def __set_text_3(self, text):
        self._text_area_3.text = text

    def __set_text_4(self, text):
        self._text_area_4.text = text

