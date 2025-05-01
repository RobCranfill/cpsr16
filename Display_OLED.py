"""Display using Adafruit 128x32 I2C OLED"""

import board
import busio
import time

import displayio
import i2cdisplaybus
import adafruit_displayio_ssd1306
import terminalio

from adafruit_display_text import label

WIDTH  = 128
HEIGHT =  32 
BORDER =   5

BLACK = 0x00_00_00
WHITE = 0xFF_FF_FF


class Display_OLED:

    def __init__(self):

        displayio.release_displays()
        i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
        display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3c)
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
        

        # # Draw a smaller inner rectangle
        # inner_bitmap = displayio.Bitmap(WIDTH - BORDER * 2, HEIGHT - BORDER * 2, 1)
        # inner_palette = displayio.Palette(1)
        # inner_palette[0] = BLACK
        # inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER)
        # splash.append(inner_sprite)


        # Display is 3 x 20 chars!
    
        y_height = 11

        y = 4
        text_area = label.Label(terminalio.FONT, text="Ready", color=WHITE, x=2, y=y)
        splash.append(text_area)
        self._text_area_1 = text_area

        y += y_height
        text_area = label.Label(terminalio.FONT, text="1234567890123456789!", color=WHITE, x=2, y=y)
        splash.append(text_area)
        self._text_area_2 = text_area

        y += y_height
        text_area = label.Label(terminalio.FONT, text="Decenders Yay or Nay", color=WHITE, x=2, y=y)
        splash.append(text_area)
        self._text_area_3 = text_area

        print(".__init__() OK!")


    def show_pattern_name(self, patt):
        self.set_text_1(patt)

    def set_text_1(self, text):
        self._text_area_1.text = text

    def set_text_2(self, text):
        self._text_area_2.text = text

    def set_text_3(self, text):
        self._text_area_3.text = text


