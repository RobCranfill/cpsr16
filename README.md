# cpsr16

A CircuitPython-based drum machine, suitable for accompanying live performaces.

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


## TO DO
  * Show BPM on display.


## Credits
* Shout out to the wonderful Adafruit!
* SR-16 samples from https://www.polynominal.com/sample-packs/Alesis-SR16-sample-pack/
* Drum patterns from https://drumhelper.com/learning-drums/rock-drum-beats-and-patterns/


## Notes
Convert files to appropriate WAV format (mono, 22050 Hz, 16-bit signed) with command:

<code>
sox {original_file}.mp3 -b 16 -c 1 -r 22050 {output_file}.wav
</code>


# Notes from SR-16 manual
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


