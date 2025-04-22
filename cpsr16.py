# CPSR16 - A CircutPython drum machine,
# functioning more or less like an Alesis SR-16

# Hardcoded for 16ths! :-(


# stdlibs
import gc
import json
import random
import sys
import time

# adafruit libs
import audiobusio
import audiocore
import audiomixer
import board
import busio

import keypad
from digitalio import DigitalInOut, Pull

# from DM_proxy import DM_proxy


# TODO: make this a variable?
# This is the smallest note/beat we handle. 16 means sixteenth notes, etc.
TICKS_PER_MEASURE = 16

# FIXME: this only works for TICKS_PER_MEASURE = 16
BEAT_NAMES = ["1", "e", "and", "uh", "2", "e", "and", "uh", "3", "e", "and", "uh", "4", "e", "and", "uh"]


DATA_FILE_NAME = "rhythms.dict"

# idle loop hander delay
NOT_PLAYING_DELAY = 0.01


# TODO: put this h/w config stuff in config file??

# for I2S audio with external I2S DAC board

# for my RP2350 testbed:
# AUDIO_OUT_I2S_BIT  = board.D9
# AUDIO_OUT_I2S_DATA = board.D11
# AUDIO_OUT_I2S_WORD = board.D10

# for RP Pico
AUDIO_OUT_I2S_BIT  = board.GP8
AUDIO_OUT_I2S_DATA = board.GP10
AUDIO_OUT_I2S_WORD = board.GP9

SWITCH_1 = board.GP28
SWITCH_2 = board.GP27


import supervisor
supervisor.runtime.autoreload = False
print(f"**** {supervisor.runtime.autoreload=}\n")


def read_json(filename):
    """Returns the de-JSON-ed data."""

    with open(filename) as f:
        data = f.read()
    # print(f">>> read_json: {data}")

    # TODO: catch malformed JSON
    result = json.loads(data)
    return result


def init_audio(n_voices):
    """Return (audio, mixer); audio object only so it doesn't get GCed."""

    au = audiobusio.I2SOut(
        bit_clock=AUDIO_OUT_I2S_BIT, word_select=AUDIO_OUT_I2S_WORD, data=AUDIO_OUT_I2S_DATA)

    # print(f"Creating mixer with {n_voices} voices....")
    mx = audiomixer.Mixer(voice_count=n_voices,
                            sample_rate=22050, channel_count=2,
                            bits_per_sample=16, samples_signed=True)

    au.play(mx) # attach mixer to audio playback

    # We must also return the "audio" object so it doesn't get garbage collected!
    return au, mx


def init_footswitch():
    """Using 'keypad'"""
    keys = keypad.Keys((SWITCH_1,SWITCH_2), value_when_pressed=False, pull=True)
    return keys


def load_setup(setups, setup_name):
    """Find and return the indicated setup, or None."""
    setup = None
    for s in setups:
        if s["setup"] == setup_name:
            setup = s
            break
    return setup


def load_pads(setup, setup_name):
    """
    Load the wave files for the pads and assign mixer channels.
    Return dict of {pad_name: (chan,wav), ...}.
    """
    pads = setup["pads"]

    # print(f"Loading {len(pads)} wav files for '{setup_name}'...")

    wavs = {}
    channel = 0
    for pad_name, filename in pads.items():
        # print(f"  - loading '{pad_name}' from '{filename}'...")

        # TODO: catch exception?
        wav = audiocore.WaveFile(open(filename,"rb"))
        wavs[pad_name] = (channel, wav)
        channel += 1

    # print(f"  * {len(wavs)} wav files loaded ok!")
    # print(f"  * {wavs=}")

    return wavs


def get_setup_names(setups):
    """For GUI?"""
    print("---- setups ----")
    names = []
    for s in setups:
        name = s["setup"]
        print(f"\t{name}")
        names.append(name)
    return names


def make_beats(pad_name, beat_pattern, channel):
    """"
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
    # print(f"load_beats_for_patterns...")

    all_beats = {}
    for pattern_name, pattern_dict in setup["patterns"].items():

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


def handle_events(switch_list):
    """Return (left_button, right_button) states"""

    # event will be None if nothing has happened.
    event = switch_list.events.get()

    left = False
    right = False
    if event:
        # print(f" ***** {event}")
        if event.pressed and event.key_number == 0:
            left = True
        if event.pressed and event.key_number == 1:
            right = True
    return (left, right)


###########################################################

def main():

    switches = init_footswitch()

    # "Wait a little bit so USB can stabilize and not glitch audio"
    # TODO: needed? 
    time.sleep(2)

    # TODO: Handle malformed data?
    all_setups = read_json(DATA_FILE_NAME)
    if len(all_setups) == 0:
        print("\nGotta have some data!")
        sys.exit()
    # print(f" ! setups: {all_setups}")

    # for future use in UI?
    setup_name_list = get_setup_names(all_setups)


########## from here we are working with one 'setup' at a time.
########## in part (mainly?) because we only want to load these WAV files.

    # TODO: select via UI
    setup_name = setup_name_list[0] # "Boom-Chuck" for testing
    this_setup = load_setup(all_setups, setup_name)
    if this_setup is None: # shouldn't happen with GUI
        print(f"\n!!! Can't find setup {setup_name}")
        sys.exit()

    # Load the wavs for the pads
    wavs_for_channels = load_pads(this_setup, setup_name)
    wav_table = [None] * len(wavs_for_channels)
    for k, v in wavs_for_channels.items():
        # print(f" -> {k} = {v}")
        chan = v[0]
        wav = v[1]
        wav_table[chan] = wav
    # print(f" * built wave table: {wav_table}")

    # Allocate a mixer with just enough channels.
    # We only get the audio object so it won't get GCed. :-/
    audio, mixer = init_audio(len(wavs_for_channels))

    # Load the beats for all patterns for this setup.
    # FIXME: we could do this inside the DM object but that needs the WAV stuff. :-/
    all_beats = load_beats_for_patterns(this_setup, wavs_for_channels)


    # 1/4 = 60 BPM
    TICK_SLEEP_TIME = 1/4

    last_tempo_tap = 0


# left button is start/stop.
# if we are stopped, right button is tempo tap
# if we are not stopped, 
#   if we are not in a fill, right button starts a fill.
#   if we are in a fill, right button advances to other pattern at next tick 0.

    is_playing = False
    is_in_fill = False
    advance_via_fill = False

    current_pattern_name = "main_a"
    playing_beats = all_beats[current_pattern_name]

    import Display_text
    display = Display_text.Display_text()
    display.show_pattern_name(current_pattern_name)
    display.show_beat_number(0)
    display.render()

    print("\n**** READY ****")

    while True:

        # Handle not-playing stuff: start, or tempo tap
        #
        if not is_playing:

            left_button, right_button = handle_events(switches)
            if left_button:
                is_playing = not is_playing
                print(f" left -> {is_playing=}, {current_pattern_name=}")

            if right_button:
                if last_tempo_tap == 0:
                    last_tempo_tap = time.monotonic_ns()
                else:
                    now = time.monotonic_ns()
                    delta = now - last_tempo_tap 
                    last_tempo_tap = now
                    TICK_SLEEP_TIME = delta / 1000000000
                    TICK_SLEEP_TIME /= 2

                    # sanity check - ridiculously slow
                    if TICK_SLEEP_TIME > 1:
                        TICK_SLEEP_TIME = 1

                    print(f" ** tempo tap {TICK_SLEEP_TIME=}")

            # Idle handler
            if not is_playing:
                # print("  (idle)")
                time.sleep(NOT_PLAYING_DELAY)
                continue

        while is_playing:

            for tick_number in range(TICKS_PER_MEASURE):

                if tick_number == 0:
                    print(f"Tick zero - {advance_via_fill=}")

                    if advance_via_fill:
                        print(" ** ADVANCE?")
                        if current_pattern_name == "fill_a":
                            current_pattern_name = "main_b"
                        else:
                            current_pattern_name = "main_a"
                        playing_beats = all_beats[current_pattern_name]
                        print(f"  -> Advanced to pattern {current_pattern_name=}")
        
                    elif is_in_fill:
                        # no advance - go back to main pattern
                        if current_pattern_name == "fill_a":
                            current_pattern_name = "main_a"
                        else:
                            current_pattern_name = "main_b"
                        playing_beats = all_beats[current_pattern_name]

                    is_in_fill = False
                    advance_via_fill = False

                left_button, right_button = handle_events(switches)
                if left_button:
                    is_playing = not is_playing
                    print(f" left -> {is_playing=}, {current_pattern_name=}")
                    if not is_playing:
                        print("  STOPPING")

                        # right?
                        current_pattern_name = "main_a"
                        playing_beats = all_beats[current_pattern_name]

                        break

                if right_button:
                    if is_in_fill:
                        advance_via_fill = True
                        print(f"  -> {advance_via_fill=}")
                    else:
                        is_in_fill = True
                        if current_pattern_name == "main_a":
                            current_pattern_name = "fill_a"
                        else:
                            current_pattern_name = "fill_b"
                        playing_beats = all_beats[current_pattern_name]
                        print(f"  -> Switched to pattern {current_pattern_name=}")


                # Play the current tick
                #
                hit_list = playing_beats[tick_number]
                # print(f"  Hit list: {hit_list}")

                if len(hit_list) > 0:
                    print(f" {current_pattern_name} tick #{tick_number}: '{BEAT_NAMES[tick_number]}': {hit_list=}")
                    tick_number = (tick_number+1) % TICKS_PER_MEASURE

                    for channel, volume in hit_list:

                        # print(f"  {channel=} @{volume=}")
                        if volume != 0:

                            # print(f"     playing {track_index=} @ {volume=} ")
                            # print(f" - {mixer.voice}")

                            # we don't seem to need to stop old voices - just re-start them!
                            #
                            # if mixer.voice[track_index].playing:
                            #     # print("stopping voice")
                            #     mixer.stop_voice(track_index)
                            #     mixer.voice[track_index].stop()

                            mixer.voice[channel].level = volume/9
                            wav = wav_table[channel]
                            mixer.voice[channel].play(wav)

                # FIXME: instead of just sleeping for the full time,
                # incorporate this into a loop, above, around the button-check stuff.
                #
                time.sleep(TICK_SLEEP_TIME)

            # end of tick loop


# Let's do it!
main()
