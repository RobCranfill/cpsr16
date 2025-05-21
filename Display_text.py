# Mostly for debugging, when my testbed doesn't have a display.

import gc


class Display_text():
    '''Being a simple stdout-based display'''

    def __init__(self):
        self.__setup = ""
        self.__pattern = ""

    def render(self):

        gc.collect()
        mem = gc.mem_free()

        print(f"+--------------------------------------+")
        print(f"|  {self.__setup:20} ")
        print(f"|  {self.__pattern:20} ")
        print(f"|")
        print(f"|  {mem:9} ")
        print(f"+--------------------------------------+")
    
    def show_setup_name(self, setup):
        self.__setup = setup
        self.render()
        
    def show_pattern_name(self, pattern):
        self.__pattern = pattern
        self.render()

# just eat it
    def show_beat_number(self, beat):
        # self.__beat = beat
        self.render()

    def blank(self):
        pass

    def animate_idle(self):
        pass


