# cpsr16

A CircuitPython-based drum machine, suitable for accompanying live performaces. 

Uses a 2-button footswitch to advance patterns, select fills, tap tempo.

Inspired by the ancient and venerable Alesis SR-16 - hence the name, <b>C</b>ircuit<b>P</b>ython <b>SR-16</b>.


## Features
 * Two-button foot switch: Start/Stop (we will refer to as "SS", on left) and Count/Fill ("CF", on right).
   * If DM is stopped, pressing CF more than once sets tempo.
     ** This just uses the *last two* presses; better would be to average several.
   * If DM is stopped, pressing SS starts pattern MAIN A.
   * If DM is playing, pressing SS stops play immediately.
   * Fill; if DM is playing,
     * As soon as you press CF, FILL X takes over from MAIN X and plays until the end of the fill *plus the following fill downbeat*.
       * The "following downbeat" is a nice feature of the SR-16; see "Notes from SR-16 manual" below.
     * Normally after playing FILL X, DM will revert back to MAIN X.
     * If a fill is playing and the CF button is pressed again, after playing FILL X it will transition to MAIN Y.
  * Display
    * This is problematic. The Pico doesn't work well with SPI displays - not with what I'm asking of it.
    * A small I2C OLED display seems to work OK. Adafruit product #4440 (128x32) or #326 (128x64).


## Hardware List
  * Raspberry Pi Pico or similar MCU - https://www.adafruit.com/product/4864
    * Or upgrade to an RP2350-based MCU!
    * And/or use a Feather, for battery power!
  * I2S Stereo decoder like https://www.adafruit.com/product/3678
  * OLED display: 128 x 64 https://www.adafruit.com/product/326
  * I2C cable - 6"-12"
    * StemmaQT/Pigtails for Pico https://www.adafruit.com/product/4209
    * StemmaQT/StemmaQT for Feather https://www.adafruit.com/product/4401
  * 3 momentary pushbuttons (only 2 used so far!) like https://www.adafruit.com/product/1505
  * 1/4" stereo ("TRS") jack.
  * 1/8" panel-mount stereo extension cable like https://www.adafruit.com/product/3319
  * 2-unit footswitch like Rowin Beatloop or Boss FS-6.
  * Some kind of box
  * USB power cable for MCU


## TO DO
  * Longer measures?
  * Implement hardware config file?
  * "Ready" beep?
  * Overall volume control?

## Data file format
The input JSON file is basically just an encoding of a Python object.
It's a <b>list</b> of <b>dictionaries</b>, each of which has the following keys:

 * "file comment": A string that will be ignored, for documentation. (Of course, *any* unknown key will act the same.)
 * "setup": The name that will be displayed on the GUI.
 * "comment": Doc string.
 * "bpm": An integer
 * "ticks_per_measure": An integer, usually 16.
 * "measures_per_pattern": An integer, usually 1 or 2.
 * "pads": A dictionary of 
   * {pad name}: {wav file path}
 * "patterns": A dictionary with the keys "main a", "fill a", "main b", "fill b",
    each of which is a dictionary with one or more (zero or more?) keys of
    {pad name} (where {pad name} was declared in the "pads" section), with a key value
    of a string. The string has ({ticks_per_measure} * {measures_per_pattern}) non-blank characters (blanks are ignored)
    that are either "-", meaning that pad isn't played on that tick, or a digit 0 thru 9, 
    meaning the pad is played at that relative volume. (So "-" and "0" are equivalent).



  




## Hardware Configuration

| Signal   | Pico Pin # | RP2350 Pin # | Device |
| -------- | -- | -- | ------- |
| I2C SDA  | 1  | - | Display SDA |
| I2C SCL  | 2  | - | Display SCL |
| GND      | 3* | ? | Display GND |
| AUDIO_OUT_I2S_BIT  | 11 (board.GP8)  | ? |  PCM BCLK |
| AUDIO_OUT_I2S_WORD | 12 (board.GP9)  | ? |  PCM WSEL |
| AUDIO_OUT_I2S_DATA | 14 (board.GP10) | ? |  PCM DIN  |
| GND      | 18* | ? |  PCM GND |
| BUTTON_B | 21 (board.GP16) | ? | Center menu button |
| BUTTON_A | 22 (board.GP17) | ? | Left-hand menu button |
| GND      | 23*             | ? | (all 3 buttons)
| BUTTON_C | 24 (board.GP18) | ? | Right-hand menu button |
| GND      | 33* | ? | Footswitch jack SLEEVE |
| SWITCH_1 | 31 (board.GP28) | ? | Footswitch jack RING |
| SWITCH_2 | 32 (board.GP27) | ? | Footswitch jack TIP |
| 3v3      | 36 | ? |  PCM VIN |
| 3v3      | 36 | - | Display VIN |
| 3v3      | ?  | D13 | NeoPixel VIN |


*Note: GND is GND - use whatever pin you want! For 

Also note: Pico is using "Adafruit UDA1334 I2S DAC" board; does not need XXX line tied to ground, as does the Amazon part.


## Credits
* Shout-out to the wonderful Adafruit! & TodBot & DanH
* SR-16 samples from https://www.polynominal.com/sample-packs/Alesis-SR16-sample-pack/
* Drum patterns from https://drumhelper.com/learning-drums/rock-drum-beats-and-patterns/


## Notes
Convert files to appropriate WAV format (mono, 22050 Hz, 16-bit signed) with command:

<code>
sox {original_file}.mp3 -b 16 -c 1 -r 22050 {output_file}.wav
</code>


## Reference
### Patterns
 * See https://www.synthmania.com/sr-16.htm

### Notes from SR-16 manual
*This is not actually what we do, but it was the inspiration.*

There are 50 of each type of Pattern, numbered 00-49. However, each numbered Pattern
actually contains four different "sub-Patterns":

• A pair of independent Main Patterns (A and B, selected by their respective buttons).
• A pair of associated Fill Patterns (A Fill and B Fill, selected by pressing the FILL button when
either A or B is selected). The Fills primarily provide transitional Patterns between Main
Patterns, which makes for more realistic drum parts. The associated Fill Patterns share the
same length, Drum Set, and name as their Main Patterns (e.g., if A is 16 beats, A Fill is 16
beats). Otherwise, they are independent.

The reason for pairing the two different A and B Patterns together is simply so that you can
switch back and forth between them rapidly in live performance or while improvising.
However, A and B Patterns can be treated as completely independent Patterns if desired and
can have different lengths, Drum Sets, etc.

Always think of the Main Pattern and its associated Fill as a unit. For example, if you copy a
Main Pattern to another Main Pattern, its Fill will travel along with it.
Note that even though there are "only" 50 Patterns, the A and B variations double that to 100
Patterns, and the Fills double that again to 200 Patterns. Added to the Preset Patterns, 400
total Patterns are available.

Fill Patterns are the key to creating expressive drum parts. However, Fill is a sophisticated
feature that requires some explanation.

...

Remember that Fills are always the same length, and use the same Drum Set, as the
associated Main Pattern. This lets you "drop in" a Fill at any time. As soon as you press the
FILL button, the Fill takes over from the Main Pattern and starts playing until the end of the Fill.

Generally, Fills are transitional Patterns. Example: Suppose an 8-beat A Main Pattern is
playing and you press the FILL button on beat 4. The A Fill Pattern will play the last 4 beats
and then automatically transition into the B Main Pattern. Conversely, if B Main is playing and
you press Fill, after B Fill has played, the SR-16 will transition to the A Main Pattern. You can
select the Fill at any time the Main Pattern is playing.

However, Fills do not have to be transitional Patterns. If you press the FILL button (or
footswitch) before the Fill has finished playing and hold it down until after the Fill has played
(i.e., past the downbeat of the next Pattern), the SR-16 will return to the original Main Pattern.

Example: Suppose an 8-beat A Main Pattern is playing and you press the FILL button on beat
4 but hold it down past beat 8. The A Fill Pattern will play the last 4 beats, then the SR-16 will
return to the A Main Pattern.

Fills cannot start on the downbeat since a Fill, by definition, starts at some point into the Main
Pattern. However, anything you record on the Fill downbeat will play on the first downbeat
following the Fill (i.e., the downbeat of the next Pattern). To show why this is a useful feature,
consider that when coming out of a fill, you'll often want to hit something like a cymbal crash
on the downbeat of the next Pattern yet not have that crash repeat every time the Pattern
plays. This way of handling Fills lets the downbeat cymbal crash be part of the Fill instead of
the Pattern.

Background 

This way of handling Patterns explains the logic behind having A, B, and Fill Patterns. In typical
pop tunes, A would be the verse and B the chorus. A Fill provides the Fill that transitions from verse
to chorus, and B Fill provides the Fill that transitions from chorus to verse. Thus, one of the 
numbered Patterns may be all you need to put together a tune.

This structure makes it possible to put together songs in minutes using the Preset Patterns. It also
makes it easy to play drum parts live. For example, if there's a solo happening over the A Main
Pattern, you can keep the Pattern repeating until the solo is about to end, at which point you
select the Fill that leads out of the A Main Pattern.


