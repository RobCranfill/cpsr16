# Defines for Pico
# This is a temporary solution

import board

print(f"Importing {__name__} for hardware definition.")

############# Hardware pin assignments

# TODO: put pin assignments in a hardware config file?
# TODO: along with other things like sample rates and channel counts?

# For Pico
BOARD_SCL = board.GP1
BOARD_SDA = board.GP0

# for I2S audio with external I2S DAC board

AUDIO_OUT_I2S_BIT  = board.GP8
AUDIO_OUT_I2S_WORD = board.GP9
AUDIO_OUT_I2S_DATA = board.GP10

SWITCH_1 = board.GP28 # left-hand (haha) footswitch: start/stop, mostly
SWITCH_2 = board.GP27 # right-hand footswitch: fill, tap

BUTTON_A = board.GP17 # middle = up
BUTTON_B = board.GP16 # left = down
BUTTON_C = board.GP18 # does nothing yet
