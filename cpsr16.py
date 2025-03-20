# CPSR16 - A CircutPython drum machine, 
# functioning more or less like an Alesis SR-16

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


def read_data(filename):
    """Returns the de-JSON-ed data, basically."""
    
    with open(filename) as f:
        data = f.read() 
    print(f">>> read_data: {data}")

    result = json.loads(data)
    return result


def init_audio(n_voices):
    """Return (audio, mixer)"""
    # We must also return the "audio" object so it doesn't get garbage collected!

    au = audiobusio.I2SOut(
        bit_clock=AUDIO_OUT_I2S_BIT, word_select=AUDIO_OUT_I2S_WORD, data=AUDIO_OUT_I2S_DATA)

    mx = audiomixer.Mixer(voice_count=n_voices, 
                            sample_rate=22050, channel_count=2,
                            bits_per_sample=16, samples_signed=True)

    au.play(mx) # attach mixer to audio playback
    return au, mx


def load_wavs(tracks):
    print(f"Loading wav files for '{pattern_name}'...")
    wav_list = []
    for track in tracks:
        filename = track["wav"]
        print(f"  - loading {filename}...")
        wav_list.append(audiocore.WaveFile(open(filename,"rb")))
    print(" * wav files loaded ok!")
    return wav_list


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


def load_setup(setup_dict, index):
    """parse the setup dict to retrun n_voices, more"""

    setup = setup_dict[index]

    setup_name = setup["setup"]
    kit = setup["kit"]
    n_voices = len(kit)

    print(f"{setup_name=} has {n_voices=}")

    wavs = []
    print(f"Loading wav files for '{setup_name}'...")
    wav_list = []
    for voice, filename in kit.items():
        print(f"  - loading {voice} from {filename}...")
        wav_list.append(audiocore.WaveFile(open(filename,"rb")))
    print(f" * {len(wav_list)} wav files loaded ok!")


    return setup_name, n_voices, wavs



###########################################################3

# TODO: needed? "Wait a little bit so USB can stabilize and not glitch audio"
time.sleep(2)

# TODO: Handle malformed data?
setups = read_data(DATA_FILE_NAME)
if len(setups) == 0:
    print("Gotta have some data!")
    sys.exit()
print(f" >> setups: {setups}")


# TODO: select via UI
setup_to_use = 0
name, n_voices, wavs = load_setup(setups, setup_to_use)

audio, mixer = init_audio(n_voices)


# # Select which pattern. TODO: via UI
# #
# pattern_to_use = "main_a"
# print(f"Selecting pattern #{pattern_to_use}: '{patterns[pattern_to_use]["pattern"]}'")

# pattern = patterns[pattern_to_use]
# pattern_name = pattern["rhythm"]
# tracks = pattern["tracks"]

# print(f"{pattern_name=}")
# print(f"  {tracks=}\n")


# wavs = load_wavs(tracks)

beats = make_beats(tracks)

# 120 BPM, sorta
SLEEP_TIME = 1/8


b = 0
playing = True
while True:

    # if not playing:
    #     print("Not playing!")
    #     time.sleep(NOT_PLAYING_DELAY)
    #     playing = check_gesture(gesture_sensor)
    #     continue

    for beat in beats:

        if len(beat) > 0:
            print(f" BEAT '{BEAT_NAMES[b]}': {beat=}")

        for voice_list in beat:

            # print(f"  {voice_list=}")
            track_index, volume = voice_list
            if volume != 0:
                # print(f"     playing {track_index=} @ {volume=} ")
                # print(f" - {mixer.voice}")

                # if mixer.voice[track_index].playing:
                #     # print("stopping voice")
                #     mixer.stop_voice(track_index)
                #     mixer.voice[track_index].stop()

                mixer.voice[track_index].level = volume/9
                mixer.voice[track_index].play(wavs[track_index])

        b = (b+1) % 16

        time.sleep(SLEEP_TIME)

