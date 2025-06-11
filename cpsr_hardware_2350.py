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

SWITCH_1 = board.D5 # left-hand (haha) footswitch: start/stop, mostly
SWITCH_2 = board.D6 # right-hand footswitch: fill, tap

BUTTON_A = board.D12 # middle = up
# not yet:
BUTTON_B = board.D13 # left = down
BUTTON_C = board.D25 # does nothing yet

# end hardware-dependent section -------------------------------------------------

