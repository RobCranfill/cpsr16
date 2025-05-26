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
# HEIGHT =  32

BLACK = 0x00_00_00
WHITE = 0xFF_FF_FF

ANIMATION_INTERVAL = 1.0 # seconds


class _Display:

    def __init__(self, i2c, oled_i2c_address, display_height, rows):

        print(f"{__name__}.__init__: {display_height=} x {rows=}")

        self._display_height = display_height
        self._display_rows = rows

        displayio.release_displays()

        display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=oled_i2c_address)
        display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=self._display_height)

        # Make the display context
        splash = displayio.Group()
        display.root_group = splash

        # black background
        color_bitmap = displayio.Bitmap(WIDTH, self._display_height, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = BLACK
        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        splash.append(bg_sprite)

        # Y-coordinates for the labels. This seems to be the most straightforward way.
        go_big = (self._display_rows > 3)
        if go_big:
            ys = [8, 30, 47, 58]
        else:
            ys = [4, 15, 26]

        y = ys[0]
        top_scale = 2 if rows == 4 else 1
    
        text_area = label.Label(terminalio.FONT, text="DM Ready!", scale=top_scale, color=WHITE, x=0, y=y)
        splash.append(text_area)
        self._text_area_1 = text_area

        y = ys[1]
        text_area = label.Label(terminalio.FONT, text="", scale=top_scale, color=WHITE, x=0, y=y)
        splash.append(text_area)
        self._text_area_2 = text_area

        y = ys[2]
        text_area = label.Label(terminalio.FONT, text="", color=WHITE, x=2, y=y)
        splash.append(text_area)
        self._text_area_3 = text_area

        # Only create 4th row if there's room
        if rows > 3:
            y = ys[3]
            text_area = label.Label(terminalio.FONT, text="", color=WHITE, x=0, y=y)
            splash.append(text_area)
            self._text_area_4 = text_area
        else:
            # this is bogus
            text_area = label.Label(terminalio.FONT, text="", color=WHITE, x=0, y=100)
            # splash.append(text_area)
            self._text_area_4 = text_area

        self.__last_anim = time.monotonic()

        # print(".__init__() OK!")

    def show_setup_name(self, text):
        self.__set_text_1(text)

    def show_pattern_name(self, text):
        self.__set_text_2(text)
    
    # # too much actvitiy for display?
    # def show_beat_number(self, n):
    #     self.__set_text_3(f"Beat: {n}")

    def show_extra_info(self, whatever):

        if self._display_rows == 4:
            self.__set_text_4(whatever)
        else:
            self.__set_text_3(whatever)


    def blank(self):
        """Screensaver. Hold the old text for restoration."""

        print("Blanking screen")

        self.__hold_text_1 = self._text_area_1.text
        self.__hold_text_2 = self._text_area_2.text
        self.__hold_text_3 = self._text_area_3.text
        self.__hold_text_4 = self._text_area_4.text

        self.__set_text_1("")
        self.__set_text_2("")
        self.__set_text_3("")
        self.__set_text_4("")

    def unblank(self):
        print("Un-blanking screen")
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

            # FIXME: inelegant?
            if self._display_rows == 3:
                self.__set_text_3("".join(l))
            else:
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


# Public sub-classes

class Display_32(_Display):
    def __init__(self, i2c, oled_i2c_address):
        super().__init__(i2c, oled_i2c_address, 32, 3)


class Display_64(_Display):
    def __init__(self, i2c, oled_i2c_address):
        super().__init__(i2c, oled_i2c_address, 64, 4)

