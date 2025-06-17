"""NeoPixel stick LED display.
8 LEDs"""

# support "pre-next" phases (fill_a -> b and fill_b -> a)

import time
import board
import neopixel


# pixel_pin = board.D13
NUM_PIXELS = 8
ORDER = neopixel.GRB

# wtf? i thought this was GRB order, as noted above, but now it's not
off =   ( 0, 0, 0)
red =   (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

off2 = (off, off)
red2 = (red, red)
green2 = (green, green)
blue2 = (blue, blue)

phase_dict = {
    "off":    off2 + off2 + off2 + off2,

    "main a": red2 + off2 + off2 + off2,
    "fill a": red2 + green2 + off2 + off2,
    "next b": red2 + red2 + off2 + off2,  # fill_a -> b

    "main b": red2 + red2 + red2 + off2,
    "fill b": red2 + red2 + red2 + green2,
    "next a": red2 + red2 + red2 + red2  # fill_b -> a
    }


class Phase_Display:
    """Display the pattern 'phase' on the NeoPixel Strip."""
    def __init__(self, pixel_pin):

        self._pixels = neopixel.NeoPixel(pixel_pin, NUM_PIXELS, brightness=0.2,
                                         auto_write=False, pixel_order=ORDER)

    def set_phase_by_name(self, phase):
        """Set the phase as indicated in the list passed in at object construction."""

        pix = phase_dict[phase]
        for i in range(8):
            self._pixels[i] = pix[i]
        self._pixels.show()


# not used

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
