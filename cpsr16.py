# CPSR16 - A CircutPython drum machine, vaguely inspired by the Alesis SR16
# read patterns from text file?

# based on:
# @todbot / Tod Kurt - https://github.com/todbot/plinkykeeb
# Convert files to appropriate WAV format (mono, 22050 Hz, 16-bit signed) with command:
#  sox loop.mp3 -b 16 -c 1 -r 22050 loop.wav

# stdlibs
import json
import random
import sys
import time

# adafruit libs
import audiocore
import audiomixer
import board


def read_data(filename):
    """Returns a list of dict of ..."""
    
    with open(filename) as f:
        data = f.read() 
    # print(f">>> {data=}")

    result = json.loads(data)

    # result = [
    #         {
    #         "rhythm": "Boom-Chuck",
    #         "tracks":
    #             [
    #             {"wav": "wav/snare_1.wav", "pattern": "0000 5000 0000 5000"},
    #             {"wav": "wav/kick_1.wav",  "pattern": "9000 0000 9000 0000"}
    #             ]
    #         },
    #         {
    #         "rhythm": "Chicka-Boom",
    #         "tracks":
    #             [
    #                 {"wav": "wav/snare_1.wav", "pattern": "5000 5000 5000 5000"},
    #                 {"wav": "wav/kick_1.wav",  "pattern": "9000 0000 9000 0000"}
    #             ]
    #         }
    # ]
    return result


def init_audio(n_voices):
    """Return the mixer"""

    # for I2S audio with external I2S DAC board
    AUDIO_OUT_I2S_BIT  = board.D9
    AUDIO_OUT_I2S_DATA = board.D11
    AUDIO_OUT_I2S_WORD = board.D10
    import audiobusio
    audio = audiobusio.I2SOut(
        bit_clock=AUDIO_OUT_I2S_BIT, word_select=AUDIO_OUT_I2S_WORD, data=AUDIO_OUT_I2S_DATA)

    mixer = audiomixer.Mixer(voice_count=n_voices, 
                            sample_rate=22050, channel_count=2,
                            bits_per_sample=16, samples_signed=True)

    audio.play(mixer) # attach mixer to audio playback
    return mixer


###########################################################3
# go time

# TODO: needed?
#  wait a little bit so USB can stabilize and not glitch audio
time.sleep(2)

patterns = read_data("rhythms.dict")
if len(patterns) == 0:
    print("Gotta have some data!")
    sys.exit()
# print(f" >> got {patterns}")

mixer = init_audio(len(patterns))


pattern_to_use = 0
print(f"Selecting pattern #{pattern_to_use}...")

pattern = patterns[pattern_to_use]
pattern_name = pattern["rhythm"]
tracks = pattern["tracks"]

print(f"{pattern_name=}")
print(f"  {tracks=}\n")

print(f"Loading wav files for '{pattern_name}'...")
wavs = []
for track in tracks:
    filename = track["wav"]
    print(f"  - loading {filename}...")
    wavs.append(audiocore.WaveFile(open(filename,"rb")))
print(" * wav files loaded ok!")

# construct a list of list of each voice & volume to use for each beat (and sub-beat)
# so that item i has all the (track,volume) pairs for beat i
#
beats = [None] * 16
# for i in range(16):
#     beats[i] = []

j = -1 # The input is broken into 4-char chunks for readability, so j is index into string
for beat in range(16):
    beats[beat] = []
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
            beats[beat].append(track_and_volume)
        i_track += 1
    j += 1

print(f" >>> {beats}")
print(f" >>> {len(beats)=}")


SLEEP_TIME = 0.1

beat_names = ["1", "e", "and", "uh", "2", "e", "and", "uh", "3", "e", "and", "uh", "4", "e", "and", "uh"]
n = 0
while True:

    for beat in beats:
        print(f" BEAT '{beat_names[n]}': {beat=}")
        for b_list in beat:
            # print(f"  {b_list=}")
            track_index, volume = b_list
            if volume != 0:
                print(f"     playing {track_index=} {volume=} ")
                mixer.voice[track_index].level = volume/9
                mixer.voice[track_index].play(wavs[track_index])

        time.sleep(SLEEP_TIME)
        n = (n+1) % 16
    