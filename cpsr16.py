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

    print(f"Creating mixer with {n_voices} voices....")
    mx = audiomixer.Mixer(voice_count=n_voices,
                            sample_rate=22050, channel_count=2,
                            bits_per_sample=16, samples_signed=True)

    au.play(mx) # attach mixer to audio playback

    # We must also return the "audio" object so it doesn't get garbage collected!
    return au, mx


def load_setup(setups, setup_name):
    """Find and return the indicated setup, or None."""
    setup = None
    for s in setups:
        if s["setup"] == setup_name:
            setup = s
            break
    return setup


def load_kit(setup, setup_name):
    """
    Load the wave files for the kit and assign mixer channels.
    Return dict of {pad_name: (chan,wav), ...}.
    """
    kit = setup["kit"]
    print(f"Loading {len(kit)} wav files for '{setup_name}'...")
    wavs = {}
    channel = 0
    for pad_name, filename in kit.items():
        print(f"  - loading '{pad_name}' from '{filename}'...")

        # TODO: catch exception?
        wav = audiocore.WaveFile(open(filename,"rb"))
        wavs[pad_name] = (channel, wav)
        channel += 1

    print(f"  * {len(wavs)} wav files loaded ok!")
    print(f"  * {wavs=}")

    return wavs


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


def make_beats(pad_name, beat_pattern, channel):
    """"
    Given the pad name and beat pattern, add all non-zero hits to a list of hits.
    Return a 16-slot list of beats like (channel, vol) for this pad.
    """
    # print(f"   make_beats for pad '{pad_name}': '{beat_pattern}'")

    beat_list = [()] * 16
    j = -1 # The input is broken into 4-char chunks for readability; j is index into beat_pattern string.

    i_track = channel # OK?

    for beat in range(16):
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


def load_beats_for_patterns(setup, wav_table):
    """Load all the beats for all the patterns, so we are ready to switch as needed."""

    """
    returns a dict like:
      {"main_a": beats,
       "main_b": beats,
       ...
       }
    where beats are like:
        beats = ((),) * 16
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
            channel = wav_table[voice][0]
            tracks.append(make_beats(voice, patt, channel))
            # print(f"  > tracks now {tracks}")

        # print(f"load_beats_for_patterns: - {tracks=}")

        # take vertical slices from tracks into the beats

        # Note: LESSON LEARNED
        # The following is right; what was wrong was
        #   track_hits = [[]] * 16
        #  which is a list of *the same object*
        #  and does very weird stuff! :-/
        #
        track_hits = [[] for _ in range(16)]

        for t in range(len(tracks)):
            for b in range(len(tracks[t])):
                new_hit = tracks[t][b]
                # print(f" looking at {new_hit=}")
                if len(new_hit) > 0:
                    # print(f" > append {new_hit=}]to track_hits[{b}]")
                    track_hits[b].append(new_hit)
                    # print(f" > now track_hits[{b}] = {track_hits[b]}")

        all_beats[pattern_name] = track_hits

    print(f"  * load_beats_for_patterns returning \n{all_beats}\n")
    return all_beats



###########################################################

def main():

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

    # Load the wavs for the pads
    wavs_for_channels = load_kit(setup, setup_to_use)
    wav_table = [None] * len(wavs_for_channels)
    for k, v in wavs_for_channels.items():
        # print(f" -> {k} = {v}")
        chan = v[0]
        wav = v[1]
        wav_table[chan] = wav
    # print(f" * built wave table: {wav_table}")

    audio, mixer = init_audio(len(wavs_for_channels))

    # Load the beats for all patterns
    beats = load_beats_for_patterns(setup, wavs_for_channels)

    # to start
    pattern = beats["main_a"]
    print(f"\nPattern: {pattern}\n")

    # 120 BPM, sorta
    SLEEP_TIME = 1/8

    # this is just for printing the nice beat name like "one" or "and"
    beat = 0

    k = 0 # for debug, test

    playing = True
    while True:

        # if not playing:
        #     print("Not playing!")
        #     time.sleep(NOT_PLAYING_DELAY)
        #     playing = check_gesture(gesture_sensor)
        #     continue

        # for hit_list in pattern:
        for beat in range(16):

            hit_list = pattern[beat]
            print(f"  Hit list: {hit_list}")

            k = k + 1
            if k == 40:
                print("\n *** switching pattern!\n")
                pattern = beats["main_b"]
                hit_list = pattern[beat]
                print(f"  Hit list now: {hit_list}")

            if len(hit_list) > 0:
                print(f" BEAT '{BEAT_NAMES[beat]}': {hit_list=}")
                beat = (beat+1) % 16

                # for channel, volume in hit_list:
                for cv_tuple in hit_list:
                    if len(cv_tuple) == 2:
                        channel = cv_tuple[0]
                        volume = cv_tuple[1]

                        wav = wav_table[channel]

                        print(f"  {channel=} @{volume=}")

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


            time.sleep(SLEEP_TIME)
            # print("\n**** STOPPING after 1 beat")
            # break

        # print("\n**** STOPPING after 1 measure")
        # break

# Let's do it!
main()
