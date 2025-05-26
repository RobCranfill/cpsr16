"""Display using Adafruit 128x64 I2C OLED, product ID 326.
   Two lines of double height, then two single-height lines."""

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
HEIGHT =  64 

BLACK = 0x00_00_00
WHITE = 0xFF_FF_FF

ANIMATION_INTERVAL = 1.0 # seconds


class Display:
    """For Adafruit 128x64 I2C OLED, product ID 326."""

    def __init__(self, i2c, oled_i2c_address):

        displayio.release_displays()

        display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=oled_i2c_address)
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
        
        # First two lines are double-size.

        y_height = 11
        y = 8
        text_area = label.Label(terminalio.FONT, text="DM Ready!", scale=2, color=WHITE, x=0, y=y)
        splash.append(text_area)
        self._text_area_1 = text_area

        y += y_height * 2
        text_area = label.Label(terminalio.FONT, text="", scale=2, color=WHITE, x=0, y=y)
        splash.append(text_area)
        self._text_area_2 = text_area

        # Bottom two lines are 21 whole characters wide (a partal 22nd)

        y += y_height + 6
        text_area = label.Label(terminalio.FONT, text="", color=WHITE, x=0, y=y)
        splash.append(text_area)
        self._text_area_3 = text_area

        y += y_height
        text_area = label.Label(terminalio.FONT, text="", color=WHITE, x=0, y=y)
        splash.append(text_area)
        self._text_area_4 = text_area

        self.__last_anim = time.monotonic()

        # print(".__init__() OK!")

## Public methods

    def show_setup_name(self, name):
        # Labelling these takes too much space:
        # self.__set_text_1(f"Setup: {name}")
        self.__set_text_1(name)

    def show_pattern_name(self, name):
        # self.__set_text_2(f"Patt: {name}")
        self.__set_text_2(name)
    
    def show_bpm(self, bpm):
        self.__set_text_3(f"{bpm} BPM")

    def show_extra_info(self, whatever):
        self.__set_text_4(whatever)

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

            # c = chr(random.randrange(97, 97 + 26))
            c = chr(random.randrange(33, 126))

            ## more printable chars? not for OLED maybe
            # l = list(range(33,127)) + list(range(161,255))
            # c = chr(random.choice(l))

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

