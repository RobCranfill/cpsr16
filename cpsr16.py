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
import board
import busio

import audiobusio
import audiocore
import audiomixer


DATA_FILE_NAME = "rhythms-v2-b.dict"

NOT_PLAYING_DELAY = 0.1


# for I2S audio with external I2S DAC board
AUDIO_OUT_I2S_BIT  = board.D9
AUDIO_OUT_I2S_DATA = board.D11
AUDIO_OUT_I2S_WORD = board.D10

BEAT_NAMES = ["1", "e", "and", "uh", "2", "e", "and", "uh", "3", "e", "and", "uh", "4", "e", "and", "uh"]


import supervisor
supervisor.runtime.autoreload = False
print(f"{supervisor.runtime.autoreload=}")


def read_json(filename):
    """Returns the de-JSON-ed data, basically."""
    
    with open(filename) as f:
        data = f.read() 
    print(f">>> read_data: {data}")

    # TODO: catch malformed JSON
    result = json.loads(data)
    return result


def init_audio(n_voices):
    """Return (audio, mixer)"""
    # We must also return the "audio" object so it doesn't get garbage collected!

    au = audiobusio.I2SOut(
        bit_clock=AUDIO_OUT_I2S_BIT, word_select=AUDIO_OUT_I2S_WORD, data=AUDIO_OUT_I2S_DATA)

    print(f"Creating mixer with {n_voices} voices....")
    mx = audiomixer.Mixer(voice_count=n_voices, 
                            sample_rate=22050, channel_count=2,
                            bits_per_sample=16, samples_signed=True)

    au.play(mx) # attach mixer to audio playback
    return au, mx


# def load_wavs(tracks):
#     print(f"Loading wav files for '{pattern_name}'...")
#     wav_list = []
#     for track in tracks:
#         filename = track["wav"]
#         print(f"  - loading {filename}...")
#         wav_list.append(audiocore.WaveFile(open(filename,"rb")))
#     print(" * wav files loaded ok!")
#     return wav_list


def make_beats(tracks):
    # Construct a list of list of each voice & volume to use for each beat (and sub-beat)
    # so that item i has all the (track,volume) pairs for beat i
    beat_list = [None] * 16
    j = -1 # The input is broken into 4-char chunks for readability; j is index into string.
    for beat in range(16):
        beat_list[beat] = []
        if beat % 4 == 0:
            j += 1
        # print(f"Looking at {beat}/{j}...")
        i_track = 0
        for track in tracks:
            beat_char = track["pattern"][j]
            if beat_char != "-":
                # print(f"  beat at {beat}/{j} from {track["pattern"]} = {beat_char}")
                track_and_volume = (i_track, int(beat_char))
                # print(f" - adding {track_and_volume}")
                beat_list[beat].append(track_and_volume)
            i_track += 1
        j += 1

    print(f"{beat_list=}")
    return beat_list


def load_setup(setups, setup_name):
    """Find and return the indicated setup, or None."""
    setup = None
    for s in setups:
        if s["setup"] == setup_name:
            setup = s
            break
    return setup


def load_kit(setup, setup_name):
    """Load the wave files for the kit. return ..."""

    kit = setup["kit"]
    n_voices = len(kit)

    wavs = []
    wav_dict = {}

    print(f"Loading {n_voices} wav files for '{setup_name}'...")
    for voice, filename in kit.items():
        print(f"  - loading '{voice}' from '{filename}'...")
        wav = audiocore.WaveFile(open(filename,"rb"))
        wavs.append(wav)

        wav_dict[voice] = wav

    print(f"  * {len(wavs)} wav files loaded ok!")
    return n_voices, wav_dict

def load_patterns(setup):

    for pattern_name, pattern_dict in setup["patterns"].items():
        print(f"loading pattern '{pattern_name}', {pattern_dict=}")
        for v, p in pattern_dict.items():
            print(f" ** parse {v}, {p}")



def load_beats_for_patterns(pattern_name, wav_dict, patterns):

    # The list of "beats" for each 16th note:
    # a beat is a list of (mixer channel, wav, volume) for as many channels as are playing

    beats = [()] * 16
    beats[0] = ((0, wav_dict["snare"], 5),  (0, wav_dict["kick"], 9))
    beats[4] = ((0, wav_dict["snare"], 9),)
    beats[6] = ((0, wav_dict["snare"], 9),)

    return beats


def get_setup_names(setups):
    """For GUI?"""
    print("----- setups -----")
    names = []
    for s in setups:
        name = s["setup"]
        print(f"\t{name}")
        names.append(name)
    print()
    return names


###########################################################3

# TODO: needed? "Wait a little bit so USB can stabilize and not glitch audio"
time.sleep(2)

# TODO: Handle malformed data?
setups = read_json(DATA_FILE_NAME)
if len(setups) == 0:
    print("\nGotta have some data!")
    sys.exit()
# print(f" ! setups: {setups}")

# for future use in UI?
setup_name_list = get_setup_names(setups)

# TODO: select via UI
setup_to_use = setup_name_list[0] # "Boom-Chuck"

setup = load_setup(setups, setup_to_use)

if setup is None: # shouldn't happen with GUI
    print(f"\n!!! Can't find setup {setup_to_use}")
    sys.exit()

n_voices, wav_dict = load_kit(setup, setup_to_use)
patterns = load_patterns(setup)

beats = load_beats_for_patterns("main_a", wav_dict, patterns)

audio, mixer = init_audio(n_voices)

if True:
    print("\nStopping for debug!")
    sys.exit()


# 120 BPM, sorta
SLEEP_TIME = 1/8

# this is just for printing the nice beat name like "one" or "and"
b = 0

print("\n----------------- Starting beat loop -----------------\n")

playing = True
while True:

    # if not playing:
    #     print("Not playing!")
    #     time.sleep(NOT_PLAYING_DELAY)
    #     playing = check_gesture(gesture_sensor)
    #     continue

    for hist_list in beats:
        print(f"{hist_list=}")

        if len(hist_list) > 0:
            print(f" BEAT '{BEAT_NAMES[b]}': {hist_list=}")

        for channel, wav, volume in hist_list:

            # channel, wav, volume = hit_tuple
            print(f"  {channel=}, {wav=}, {volume=}")

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
                mixer.voice[channel].play(wav)

        b = (b+1) % 16

        time.sleep(SLEEP_TIME)

