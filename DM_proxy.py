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

    def go_to_pattern(self, pattern_name):
        """Go to the specified pattern and return same as get_current_pattern_beats() does."""

        # TODO: check that pattern_name is valid
        self._current_pattern_name = pattern_name
        self._current_beats = self._beat_list[pattern_name]
        print(f"  -> Going to pattern {pattern_name=}")
        print(f"     Beat list (len {len(self._current_beats)}):  {self._current_beats}")
    
        return self._current_beats


    def go_to_next_pattern(self):
        """Go to the next pattern and return same as get_current_pattern_beats() does."""
        # FIXME: this needs to be smarter
        patt = self._current_pattern_name
        if patt == "main_a":
            return self.go_to_pattern("main_b")
        elif patt == "main_b":
            return self.go_to_pattern("main_a")
        elif patt == "fill_a":
            return self.go_to_pattern("main_b")
        elif patt == "fill_b":
            return self.go_to_pattern("main_a")
        # else ???

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


