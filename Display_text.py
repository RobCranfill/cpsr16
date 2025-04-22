
import Display_class

class Display_text(Display_class.Display_class):
    '''Being a simple stdout-based display'''

    def render(self):
        print(f"+--------------------------------------+")
        print(f"|  {self._pattern_name:20}             {self._beat_number:2} |")
        print(f"|                                      |")
        print(f"|                                      |")
        print(f"+--------------------------------------+")
    