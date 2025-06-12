# Defines for Feather RP2350
# This is a temporary solution

import board

print(f"Importing {__name__} for hardware definition.")

############# Hardware pin assignments

# TODO: put pin assignments in a hardware config file?
# TODO: along with other things like sample rates and channel counts?

# for I2S audio with external I2S DAC board

AUDIO_OUT_I2S_BIT  = board.D9
AUDIO_OUT_I2S_WORD = board.D10
AUDIO_OUT_I2S_DATA = board.D11

SWITCH_1 = board.D6 # left-hand (haha) footswitch: start/stop, mostly
SWITCH_2 = board.D5 # right-hand footswitch: fill, tap

BUTTON_A = board.A2 # middle = up
BUTTON_B = board.A1 # left = down
BUTTON_C = board.A0 # does nothing yet, if ever.

# end hardware-dependent section -------------------------------------------------

