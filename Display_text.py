
import gc

import Display_class


class Display_text(Display_class.Display_class):
    '''Being a simple stdout-based display'''

    def render(self):

        gc.collect()
        mem = gc.mem_free()

        print(f"+--------------------------------------+")
        print(f"|  {self._pattern_name:20}             {self._beat_number:2} |")
        print(f"|                                      |")
        print(f"|  {mem:9}                           |")
        print(f"+--------------------------------------+")
    