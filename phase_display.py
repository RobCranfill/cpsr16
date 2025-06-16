"""NeoPixel stick LED display.
8 LEDs"""

# TODO: Use phases "DICT_KEYWORD_FILL_A", etc?

import time
import board
import neopixel


pixel_pin = board.D13
num_pixels = 8
ORDER = neopixel.GRB

black = (0, 0, 0)
red = (0, 255, 0)
green = (255, 0, 0)
phase_colors = [black, green, red, green, red]


class Phase_Display:
    """Display the pattern 'pjhase' on a NeoPixel Strip."""
    def __init__(self):

        self._pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2,
                                         auto_write=False, pixel_order=ORDER)

    def set_phase(self, phase):
        """Phase is 0-4, inclusive."""
        # print(f" {__name__}: {phase=}")
        
        self._pixels.fill(phase_colors[0])

        for j in range(1, phase+1):
            l1 = 2*(j-1)
            self._pixels[l1] = phase_colors[j]
            self._pixels[l1+1] = phase_colors[j]
        self._pixels.show()

# not really used?

    def wheel(self, pos):

        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.

        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
        return (r, g, b) if ORDER in {neopixel.RGB, neopixel.GRB} else (r, g, b, 0)

    def rainbow_cycle(self, wait):
        for j in range(255):
            for i in range(num_pixels):
                pixel_index = (i * 256 // num_pixels) + j
                self._pixels[i] = self.wheel(pixel_index & 255)
            self._pixels.show()
            time.sleep(wait)
