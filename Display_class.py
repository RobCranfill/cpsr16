
class Display_class:
    '''Being a superclass for any display.'''

    def __init__(self):
        self._pattern_name = ""
        self._beat_number = 0

    def render(self):
        pass

    def show_pattern_name(self, name):
        self._pattern_name = name
    
    def show_beat_number(self, number):
        self._beat_number = number

