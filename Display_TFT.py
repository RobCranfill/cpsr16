import board
import busio
import displayio
import terminalio
from adafruit_display_text import label
from fourwire import FourWire

from adafruit_st7735r import ST7735R

import Display_class


class Display_TFT(Display_class.Display_class):

    def __init__(self):


        Display_class.Display_class()

        tft_cs = board.GP5
        tft_dc = board.GP0
        tft_reset = board.GP1

        spi_clock = board.GP2
        spi_mosi = board.GP3
        spi_miso = board.GP4
        

        # Release any resources currently in use for the displays
        displayio.release_displays()

        # not on Pico
        # spi = board.SPI()
        spi = busio.SPI(clock=spi_clock, MOSI=spi_mosi, MISO=board.GP4)
        display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
        display = ST7735R(display_bus, width=128, height=128, colstart=2, rowstart=1, rotation=92700)

        # Make the display context
        splash = displayio.Group()
        display.root_group = splash

        color_bitmap = displayio.Bitmap(128, 128, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0x404040

        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        splash.append(bg_sprite)

        # Draw a smaller inner rectangle
        inner_bitmap = displayio.Bitmap(108, 108, 1)
        inner_palette = displayio.Palette(1)
        inner_palette[0] = 0x202020
        inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=10, y=10)
        splash.append(inner_sprite)

        # The labels

        label_x = 20
        label_y = 20

        text_area_1 = label.Label(terminalio.FONT, text="", color=0x0000FF, x=label_x, y=label_y)
        splash.append(text_area_1)
        self._text_area_1 = text_area_1

        label_y += 20
        text_area_2 = label.Label(terminalio.FONT, text="", color=0x0000FF, x=label_x, y=label_y)
        splash.append(text_area_2)
        self._text_area_2 = text_area_2

        label_y += 20
        text_area_3 = label.Label(terminalio.FONT, text="", color=0x0000FF, x=label_x, y=label_y)
        splash.append(text_area_3)
        self._text_area_3 = text_area_3

        label_y += 20
        text_area_4 = label.Label(terminalio.FONT, text="", color=0x0000FF, x=label_x, y=label_y)
        splash.append(text_area_4)
        self._text_area_4 = text_area_4


    def set_text(self, text):
        self._text_area_1.text = text

    def render(self):
        pass

    def show_pattern_name(self, name):
        self._text_area_2.text = name
    
    def show_beat_number(self, number):
        self._text_area_3.text = number
