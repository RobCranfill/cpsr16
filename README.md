# cpsr16
<b>CircuitPython SR16 sorta thing</b>


Many sounds from https://freesound.org/

## Notes
Convert files to appropriate WAV format (mono, 22050 Hz, 16-bit signed) with command:

<code>
sox {original_file}.mp3 -b 16 -c 1 -r 22050 {output_file}.wav
</code>

## To-Do
* Lidar-based start/stop/fill!

* Build bigger patterns from little ones. (Need better terminology)
* Option for fills, intros, outros.

