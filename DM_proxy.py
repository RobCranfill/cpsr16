"""No, this is the state machine!"""


class DM_proxy:
    """This encapsulates the logic to handle one setup - its kit and patterns, and state transitions."""

    def __init__(self, beat_list):
        """Create the state machine. Not playing. beat_list is dict of pattern_name and sliced beats. (haha)"""

        self._beat_list = beat_list

        self._is_playing = False

        self._patten_names = [ _ for _ in beat_list.keys()]
        print(f"  {self._patten_names=}")
        print(f"  {self._patten_names[0]=}")
    
        self._current_pattern_name = self._patten_names[0]
        self._current_beats = self._beat_list[self._current_pattern_name]


    def get_current_pattern_beats(self):
        """Return (name, beats)"""
        return self._current_pattern_name, self._current_beats

    def current_beat(self):
        return self._current_pattern

    def is_playing(self):
        return self._is_playing

    def start_playing(self):
        self._is_playing = True
    
    def stop_playing(self):
        self._is_playing = False

    def set_playing(self, playing):
        self._is_playing = playing

    def handle_left_button(self):
        pass

    def handle_right_button(self):
        pass


