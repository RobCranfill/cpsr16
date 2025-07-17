# Defines for Feather RP2350
# Second config (soldered)

import board

print(f"Importing {__name__} for hardware definition.")

############# Hardware pin assignments

# TODO: put pin assignments in a hardware config file?
# TODO: along with other things like sample rates and channel counts?

# for I2S audio with external I2S DAC board
AUDIO_OUT_I2S_BIT  = board.A1
AUDIO_OUT_I2S_WORD = board.A0
AUDIO_OUT_I2S_DATA = board.A2

SWITCH_1 = board.D5 # left-hand (haha) footswitch: start/stop, mostly
SWITCH_2 = board.D6 # right-hand footswitch: fill, tap

BUTTON_A = board.D11 # middle = up/next
BUTTON_B = board.D9 # left = down/prev
BUTTON_C = board.D10 # does nothing yet, if ever.

NEOPIXEL_STRIP_PIN = board.D13

# end hardware-dependent section -------------------------------------------------

