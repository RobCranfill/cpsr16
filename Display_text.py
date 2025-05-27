# Mostly for debugging, when my testbed doesn't have a display.

import gc


class Display_text():
    '''Being a simple stdout-based display'''

    def __init__(self):
        self._line_1 = ""
        self._line_2 = ""
        self._line_3 = ""

    def set_line_1(self, text):
        self._line_1 = text
        self._render()

    def set_line_2(self, text):
        self._line_2 = text
        self._render()
    
    def set_line_3(self, text):
        self._line_3 = text
        self._render()

    def blank(self):
        pass

    def animate_idle(self):
        pass


    def _render(self):

        gc.collect()
        mem = gc.mem_free()

        print(f"+--------------------------------------+")
        print(f"|  {self._line_1:20} ")
        print(f"|  {self._line_2:20} ")
        print(f"|  {self._line_3:20} ")
        print(f"|")
        print(f"|  {mem:9} ")
        print(f"+--------------------------------------+")
