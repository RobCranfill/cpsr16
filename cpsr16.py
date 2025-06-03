"""
cpsr16 - CircuitPython SR-16 - A CircuitPython drum machine
=================================================

A performance-oriented drum machine, 
inspired by the ancient and venerable Alesis SR-16.

* Author(s): Rob Cranfill - robcranfill@gmail.com

Implementation Notes
--------------------

* Hardcoded for 16ths! :-(
* Untested for other than 1 bar of 4 beats! :-(


**Hardware:**

* `Adafruit Device Description
  <hyperlink>`_ (Product ID: <Product Number>)

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library:
  https://github.com/adafruit/Adafruit_CircuitPython_BusDevice

* Adafruit's Register library:
  https://github.com/adafruit/Adafruit_CircuitPython_Register


**GitHub**
* https://github.com/RobCranfill/cpsr16

"""

# stdlibs
import gc
import json
import sys
import time
import traceback

# adafruit libs
import audiobusio
import audiocore
import audiomixer
import board
import busio
import displayio
import keypad

# our libs
# For debugging you can use the text-only "display".
import Display_OLED
# import Display_text


############# Hardware pin assignments
# Note: Hardware dependent sections are marked with the following:
# FIXME: HARDWARE DEPENDENT
#
# TODO: Automate this - by checking hardware?
# import cpsr_hardware_pico as HARDWARE_CONFIG
import cpsr_hardware_2350 as HARDWARE_CONFIG


__repo__ = "https://github.com/RobCranfill/cpsr16.git"


# TODO: make this variable???
# This is the smallest note/beat we handle. 16 means sixteenth notes, etc.
TICKS_PER_MEASURE = 16

# FIXME: this only works for TICKS_PER_MEASURE = 16
BEAT_NAMES = ["1", "e", "and", "uh", "2", "e", "and", "uh", "3", "e", "and", "uh", "4", "e", "and", "uh"]

# The data file we read.
DATA_FILE_NAME = "rhythms-4-sr16.dict"

# idle loop hander delay - useful/needed?
NOT_PLAYING_DELAY = 0.01

# Mixer buffer size, per voice.
# What is the best value? Esp w/r/t "fancy timing"?
AUDIO_BUFFER_BYTES = 256

SAMPLE_RATE = 22050
CHANNEL_COUNT = 1
BITS_PER_SAMPLE = 16
SAMPLES_SIGNED = True

DISPLAY_TIMEOUT_SECONDS = 60

# I thought this was useful, but setting the Mixer buffer size low seems to work fine!
USE_FANCY_TIMING = False

DICT_KEYWORD_SETUP = "setup"
DICT_KEYWORD_PADS = "pads"
DICT_KEYWORD_PATTERNS = "patterns"
DICT_KEYWORD_MAIN_A = "main a"
DICT_KEYWORD_FILL_A = "fill a"
DICT_KEYWORD_MAIN_B = "main b"
DICT_KEYWORD_FILL_B = "fill b"


def read_json(filename):
    """Returns the de-JSON-ed data, a big object heirarchy."""

    print(f"* Reading config {filename}...")
    with open(filename) as f:
        data = f.read()
    # print(f">>> read_json: {data}")

    # TODO: catch malformed JSON
    result = json.loads(data)
    return result


def init_audio():
    """Return the I2S audio device."""

    # TODO: catch exceptions
    audio_device = audiobusio.I2SOut(
        bit_clock =     HARDWARE_CONFIG.AUDIO_OUT_I2S_BIT,
        word_select =   HARDWARE_CONFIG.AUDIO_OUT_I2S_WORD, 
        data =          HARDWARE_CONFIG.AUDIO_OUT_I2S_DATA)

    return audio_device


def init_mixer(audio_out, n_voices: int):

    print(f"Creating mixer with {n_voices} voices....")
    mixer = audiomixer.Mixer(voice_count=n_voices,
                             sample_rate=SAMPLE_RATE, channel_count=CHANNEL_COUNT,
                             bits_per_sample=BITS_PER_SAMPLE, samples_signed=SAMPLES_SIGNED,
                             buffer_size=AUDIO_BUFFER_BYTES * n_voices)

    audio_out.play(mixer) # attach mixer to audio playback
    return mixer


def init_all_switches():
    """return (footswitch 1, footswitch 2, button 1, button 2, button 3)"""
    return keypad.Keys((HARDWARE_CONFIG.SWITCH_1, HARDWARE_CONFIG.SWITCH_2, 
                        HARDWARE_CONFIG.BUTTON_A, HARDWARE_CONFIG.BUTTON_B, HARDWARE_CONFIG.BUTTON_C), 
                       value_when_pressed=False, pull=True)


def load_setup(setups, setup_name):
    """Find and return the indicated setup, or None."""
    setup = None
    for s in setups:
        if s[DICT_KEYWORD_SETUP] == setup_name:
            setup = s
            break
    return setup


def load_pads(setup, setup_name):
    """
    Load the wave files for the pads and assign mixer channels.
    Return dict of {pad_name: (chan,wav), ...}.
    """
    pads = setup[DICT_KEYWORD_PADS]

    # print(f"Loading {len(pads)} wav files for '{setup_name}'...")

    m1 = get_free_mem()
    print(f"load_pads: Free mem before: {m1}")

    wavs = {}
    channel = 0
    for pad_name, filename in pads.items():
        # print(f"  - loading '{pad_name}' from '{filename}'...")

        # TODO: catch exception?
        wav = audiocore.WaveFile(open(filename, "rb"))
        wavs[pad_name] = (channel, wav)
        channel += 1

    print(f"  * {len(wavs)} wav files loaded ok")
    # print(f"  * {wavs=}")

    m2 = get_free_mem()
    print(f"load_pads:  Free mem after: {m2} - delta = {m1-m2}\n")

    return wavs


def get_setup_names(setups):
    """List of all setup names."""
    print("---- setups ----")
    names = []
    for s in setups:
        name = s[DICT_KEYWORD_SETUP]
        print(f"  {name}")
        names.append(name)
    return names


def make_beats(pad_name, beat_pattern, channel):
    """
    Given the pad name and beat pattern, add all non-zero hits to a list of hits.
    Return a BEATS_PER_MEASURE-slot list of beats like (channel, vol) for this pad.
    """
    # print(f"   make_beats for pad '{pad_name}': '{beat_pattern}'")

    beat_list = [()] * TICKS_PER_MEASURE
    j = -1 # The input is broken into 4-char chunks for readability; j is index into beat_pattern string.

    i_track = channel # OK?

    for beat in range(TICKS_PER_MEASURE):
        if beat % 4 == 0:
            j += 1
        # print(f"Looking at {beat=} from char {j}...")
        beat_char = beat_pattern[j]
        if beat_char != "-":
            # print(f"  beat at {beat}/{j} from {pad_name=} = {beat_char}")
            beat_list[beat] = (i_track, int(beat_char))
            # print(f" - added {beat_list[beat]}")
        j += 1

    # print(f"    {beat_list=}\n")
    return beat_list


def load_beats_for_patterns(setup, wav_dict):
    """Load all the beats for all the patterns, so we are ready to switch as needed."""

    """
    returns a dict like:
      {"main_a": beats,
       "main_b": beats,
       ...
       }
    where beats are like:
        beats = ((),) * TICKS_PER_MEASURE 
           containing, say:
        beats[0] = ((0, wav_dict["snare"], 5),  (0, wav_dict["kick"], 9))
        beats[4] = ((0, wav_dict["snare"], 9))
        beats[6] = ((0, wav_dict["snare"], 9))

        that is
        (
          ((0, wav_dict["snare"], 5),  (0, wav_dict["kick"], 9)),
          (),
          (),
          (),
          ((0, wav_dict["snare"], 9)),
          ...
        )
    """
    # print(f"load_beats_for_patterns {setup=}")

    all_beats = {}
    for pattern_name, pattern_dict in setup[DICT_KEYWORD_PATTERNS].items():

        # print(f" - loading pattern '{pattern_name}' from {pattern_dict=}")
        tracks = []

        for voice, patt in pattern_dict.items():
            channel = wav_dict[voice][0]
            tracks.append(make_beats(voice, patt, channel))
            # print(f"  > tracks now {tracks}")

        # print(f"load_beats_for_patterns: - {tracks=}")

        # take vertical slices from tracks into the beats

        # Note: LESSON LEARNED
        # The following is right; what was wrong was
        #   track_hits = [[]] * BEATS_PER_MEASURE
        #  which is a list of *the same object*
        #  and does very weird stuff! :-/
        #
        track_hits = [[] for _ in range(TICKS_PER_MEASURE)]

        for t in range(len(tracks)):
            for b in range(len(tracks[t])):
                new_hit = tracks[t][b]
                # print(f" looking at {new_hit=}")
                if len(new_hit) > 0:
                    # print(f" > append {new_hit=}]to track_hits[{b}]")
                    track_hits[b].append(new_hit)
                    # print(f" > now track_hits[{b}] = {track_hits[b]}")

        all_beats[pattern_name] = track_hits

    # print(f"  * load_beats_for_patterns returning \n{all_beats}")
    return all_beats

def get_all_events(button_list):
    """Return (f1, f2, a1, a2, a3) states"""

    f1 = False
    f2 = False
    b1 = False
    b2 = False
    b3 = False

    # event will be None if nothing has happened.
    event = button_list.events.get()

    if event:
        # print(f" ***** button {event}")

        if event.pressed and event.key_number == 0:
            f1 = True
        if event.pressed and event.key_number == 1:
            f2 = True

        if event.pressed and event.key_number == 2:
            b1 = True
        if event.pressed and event.key_number == 3:
            b2 = True
        if event.pressed and event.key_number == 4:
            b3 = True

    return (f1, f2, b1, b2, b3)


def get_free_mem():
    gc.collect()
    return gc.mem_free()


def load_setup_pads(setups, name):

    this_setup = load_setup(setups, name)
    if this_setup is None: # shouldn't happen
        print(f"\n!!! Can't find setup {name}")
        sys.exit()

    # Load the wavs for the pads
    wavs_for_channels = load_pads(this_setup, name)
    wav_table = [None] * len(wavs_for_channels)
    for k, v in wavs_for_channels.items():
        chan = v[0]
        wav = v[1]
        wav_table[chan] = wav
    # print(f" * built wave table: {wav_table}")

    return this_setup, wavs_for_channels, wav_table


def load_beats_and_mixer(audio_out, all_setups, setup_name):
    """Return this_setup, wavs_for_channels, wavetable, setup_beats, mixer """

    print(f"Loading setup '{setup_name}'")

    this_setup, wavs_for_channels, wavetable = load_setup_pads(all_setups, setup_name)

    # Load the beats for all patterns for this setup.
    setup_beats = load_beats_for_patterns(this_setup, wavs_for_channels)

    # Allocate a mixer with just enough channels.
    mixer = init_mixer(audio_out, len(wavs_for_channels))

    return this_setup, wavs_for_channels, wavetable, setup_beats, mixer


def bpm_from_tap_time(tap_time_seconds):
    """Get BPM from the user-input 'tap time'."""
    return int(15/tap_time_seconds)


def bpm_to_sleep_time(bpm):
    """Calculate the inter-tick (sixteenth note) delay time from the desired BPM."""
    bps = bpm / 60
    tick_delay = 1 / (bps * 4)
    print(f" {bpm} BPM -> {bps} BPS -> {tick_delay} second tick-delay")
    return tick_delay


###########################################################
def main():

    print(f"Free mem at start: {get_free_mem()}")

    # "Wait a little bit so USB can stabilize and not glitch audio"
    # TODO: needed?
    time.sleep(2)

    switches = init_all_switches()

    ##### Initialize the I2S (not I2C) audio hardware.
    audio_out = init_audio()

    ##### Initialize the I2C hardware.
    try:
        # Not sure why this is needed, but it seems to be:
        displayio.release_displays()

        # FIXME: HARDWARE DEPENDENT
        
        # This is for Pico:
        # i2c = busio.I2C(scl = HARDWARE_CONFIG.BOARD_SCL, sda = HARDWARE_CONFIG.BOARD_SDA)

        # This is for Feather:
        i2c = board.I2C()

    except Exception as e:
        print("No I2C bus?")
        traceback.print_exception(e)
        return # from main

    ##### Initialize the I2C display.
    # FIXME: HARDWARE DEPENDENT
    # display = Display_OLED.Display_32(i2c, 0x3C)
    display = Display_OLED.Display_64(i2c, 0x3D)

    # Or for no I2C display attached,
    # display = Display_text.Display()

    display_timeout_start = time.monotonic()
    display_idle_flag = False
    display_is_blanked = False

    # Load the data file.
    # TODO: Handle malformed data?
    all_setups = read_json(DATA_FILE_NAME)
    if len(all_setups) == 0:
        print("\nGotta have some data!")
        sys.exit()
    # print(f" ! setups: {all_setups}")


########## From here we are working with one 'setup' at a time.
########## in part (mainly?) because we only want to load one set of WAV files.


    # Load all the initial data. Whew!
    setup_index = 0
    setup_names = get_setup_names(all_setups)
    setup_name = setup_names[setup_index]

    this_setup, wavs_for_channels, wavetable, setup_beats, mixer = load_beats_and_mixer(audio_out, all_setups, setup_name)

    bpm = 120
    TICK_SLEEP_TIME = bpm_to_sleep_time(bpm)
    TICK_SLEEP_TIME_MS = TICK_SLEEP_TIME * 1_000

    if USE_FANCY_TIMING:
        print(f" ** {USE_FANCY_TIMING=}: {TICK_SLEEP_TIME=} -> {TICK_SLEEP_TIME_MS=} -> {bpm} BPM")
    else:
        print(f" ** {USE_FANCY_TIMING=}: {TICK_SLEEP_TIME=} -> {bpm} BPM")


    is_playing = False
    is_in_fill = False
    advance_via_fill = False
    fill_downbeat = None

    last_tempo_tap = 0

    current_pattern_name = DICT_KEYWORD_MAIN_A

    # 'plattern_beats' is the main data structure we are using as we play a rhythm.
    # It is a list of size TICKS_PER_MEASURE, with a list of each voice to be played that tick.
    # That is, a list of (channel, volume) pairs.
    #
    plattern_beats = setup_beats[current_pattern_name]
    print(f"{plattern_beats=}")


    display.set_line_1(setup_name)
    display.set_line_2(current_pattern_name)
    display.set_line_3(f"{bpm} BPM")


    print("\n**** READY ****")

    while True:

        # Handle not-playing stuff: start, or tempo tap.
        #
        if not is_playing:

            display_idle_flag = True

            stop_button, fill_button, b1, b2, b3 = get_all_events(switches)
            if stop_button or fill_button or b1 or b2 or b3:
                display_timeout_start = time.monotonic()
                display_idle_flag = False
                if display_is_blanked:
                    print("Un-blanking display...")
                    display.unblank()
                    display_is_blanked = False
            else:
                if display_is_blanked:
                    display.animate_idle()

            if stop_button:
                print("* STARTING")
                is_playing = True
                # print(f" left -> {is_playing=}, {current_pattern_name=}")
                last_tempo_tap = 0

            # User-input "tap time".
            # TODO: This could average the last few taps, or just take the last one, for now.
            #
            if fill_button:
                if last_tempo_tap == 0:
                    last_tempo_tap = time.monotonic_ns()
                else:
                    now = time.monotonic_ns()
                    delta = now - last_tempo_tap
                    last_tempo_tap = now
                    TICK_SLEEP_TIME = delta / 1000000000
                    TICK_SLEEP_TIME /= 4

                    # sanity checks
                    if TICK_SLEEP_TIME > 1:
                        TICK_SLEEP_TIME = 1
                    bpm = bpm_from_tap_time(TICK_SLEEP_TIME)
                    if bpm < 15:
                        bpm = 15
                    elif bpm > 240:
                        bpm = 240

                    print(f" ** tempo tap {TICK_SLEEP_TIME=} -> {bpm} BPM")

                    display.set_line_3(f"{bpm} BPM")

            # Menu buttons?
            if b1 or b2 or b3:
                setup_changed = False
                # print(f"handle button {b1=} {b2=} {b3=}")
                if b1:
                    setup_index = (setup_index+1) % len(setup_names)
                    setup_name = setup_names[setup_index]
                    print(f"go to next setup: {setup_name}")
                    setup_changed = True
                elif b2:
                    setup_index = (setup_index-1) % len(setup_names)
                    setup_name = setup_names[setup_index]
                    print(f"go to prev setup: {setup_name}")
                    setup_changed = True

                if setup_changed:
                    # Get all the data for the new setup.
                    this_setup, wavs_for_channels, wavetable, setup_beats, mixer = load_beats_and_mixer(audio_out, all_setups, setup_name)
                    plattern_beats = setup_beats[current_pattern_name]
                    display.set_line_1(setup_name)

            # Idle handler.
            if not is_playing:

                # TODO: how long to idle? if at all?
                # print("  (idle)")
                time.sleep(NOT_PLAYING_DELAY)

                if display_idle_flag:
                    if time.monotonic() > display_timeout_start + DISPLAY_TIMEOUT_SECONDS:
                        if not display_is_blanked:
                            print("Blanking display...")
                            display.blank()
                            display_is_blanked = True

                continue

        while is_playing:

            for tick_number in range(TICKS_PER_MEASURE):

                # if tick_number % 4 == 0:
                #     display.set_line_3(f"{BEAT_NAMES[tick_number]}")

                tick_start_time_ms = supervisor.ticks_ms()

                # Special stuff on the downbeat, the start of a measure.
                #
                if tick_number == 0:
                    # print(f"Tick zero - {advance_via_fill=}")

                    if advance_via_fill:
                        # print(" ** advance_via_fill")
                        if current_pattern_name == DICT_KEYWORD_FILL_A:
                            current_pattern_name = DICT_KEYWORD_MAIN_B
                        else:
                            current_pattern_name = DICT_KEYWORD_MAIN_A
                        plattern_beats = setup_beats[current_pattern_name]

                        # print(f"  -> Advanced to pattern {current_pattern_name=}")
                        display.set_line_2(current_pattern_name)

                    elif is_in_fill:
                        # no advance - go back to main pattern
                        if current_pattern_name == DICT_KEYWORD_FILL_A:
                            current_pattern_name = DICT_KEYWORD_MAIN_A
                        else:
                            current_pattern_name = DICT_KEYWORD_MAIN_B
                        plattern_beats = setup_beats[current_pattern_name]
                        # print(f"  -> Reverted to pattern {current_pattern_name=}")

                        display.set_line_2(current_pattern_name)

                    advance_via_fill = False
                    is_in_fill = False

                # FIXME: move this to top of loop?

                stop_button, fill_button, b1, b2, b3 = get_all_events(switches)
                if stop_button or fill_button or b1 or b2 or b3:
                    display_timeout_start = time.monotonic()
                    display_idle_flag = False
                    if display_is_blanked:
                        print("Un-blanking display...")
                        display.unblank()
                        display_is_blanked = False

                if stop_button:
                    is_playing = not is_playing
                    # print(f" left -> {is_playing=}, {current_pattern_name=}")
                    if not is_playing:
                        print("* STOPPING")
                        current_pattern_name = DICT_KEYWORD_MAIN_A
                        plattern_beats = setup_beats[current_pattern_name]
                        break

                if fill_button:
                    if is_in_fill:
                        advance_via_fill = True
                        # print(f"  ->  Will advance to next pattern...")
                    else:
                        is_in_fill = True
                        if current_pattern_name == DICT_KEYWORD_MAIN_A:
                            current_pattern_name = DICT_KEYWORD_FILL_A
                        else:
                            current_pattern_name = DICT_KEYWORD_FILL_B
                        plattern_beats = setup_beats[current_pattern_name]
                        fill_downbeat = plattern_beats[0]
                        # print(f"  -> Switched to pattern {current_pattern_name=}")
                        # print(f"     Saving fill downbeat {fill_downbeat=}")


                # Play the current tick
                #
                if tick_number == 0 and fill_downbeat is not None:
                    hit_list = fill_downbeat
                    # print(f"  Playing fill downbeat {hit_list=}")
                    fill_downbeat = None
                else:
                    hit_list = plattern_beats[tick_number]

                # print(f"  Hit list: {hit_list}")
                if len(hit_list) > 0:

                    # TODO: I don't know that we can update the display this often without a performace hit.
                    # display.set_line_3(f"{tick_number}")

                    # print(f" {current_pattern_name} tick #{tick_number}: '{BEAT_NAMES[tick_number]}': {hit_list=}")

                    for channel, volume in hit_list:

                        # print(f"  {channel=} @{volume=}")
                        if volume != 0:

                            # print(f"     playing {track_index=} @ {volume=} ")
                            # print(f" - {mixer.voice}")

                            # We don't seem to need to stop old voices - just re-start them!
                            #
                            # if mixer.voice[channel].playing:
                            #     # print("stopping voice")
                            #     # FIXME: which? are these the same thing?
                            #     mixer.stop_voice(channel)
                            #     # mixer.voice[channel].stop()

                            mixer.voice[channel].level = volume/9
                            wav = wavetable[channel]
                            mixer.voice[channel].play(wav, loop=False)

                # This doesn't seem necessary if we make the Mixer buffers small,
                # which seems to work fine. This may change in the future, depending
                # on our display, other peripherals, etc.

                if USE_FANCY_TIMING:
                    tick_delta_ms = supervisor.ticks_ms() - tick_start_time_ms
                    sleep_ms = TICK_SLEEP_TIME_MS - tick_delta_ms
                    print(f" {tick_start_time_ms=} {tick_delta_ms=} {sleep_ms=}")
                    if sleep_ms > 0:
                        time.sleep(sleep_ms / 1_000)
                else:
                    time.sleep(TICK_SLEEP_TIME)

            # end of tick loop


# Let's do it!

# for performance improvement; otherwise we get audio glitches when auto-reloads.
import supervisor
supervisor.runtime.autoreload = False
print(f"**** {supervisor.runtime.autoreload=}\n")

main()
