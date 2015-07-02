
from __future__ import print_function
from builtins import super

__author__ = 'vsp'
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button


class RhythmMaker(FloatLayout):
    num_instruments = 4
    num_beats = 4
    def __init__(self):
        super().__init__()

        self.add_widget(Measure(
            orientation='vertical',spacing=10
        ))


class Menu(Widget):
    pass


class Instrument(BoxLayout):
    #orientation = 'horizontal'
    def __init__(self,no_beats=4,**kwargs):
        #initialize the layout normally
        super(Instrument,self).__init__(**kwargs)

        for i in range(no_beats):
            self.add_widget(Button(
                #pos_hint ={'top':0.9,'x':float(i)/no_beats},
                #size_hint = (.9,.9)

            ))

class Beat(BoxLayout):
    def __init__(self):
        super().__init__()
        self.add_widget(Button())

class CurrentProgressBar(Widget):
    pass

class Measure(BoxLayout):
    #orientation = 'vertical'
    def __init__(self,no_instruments=4,no_beats=4,**kwargs):
        #initialize the layout normally
        super().__init__(**kwargs)

        for i in range(no_instruments):
            self.add_widget(Instrument(
                no_beats=no_beats,
                orientation='horizontal',
                spacing = 10,
                #pos_hint = {'top':1-float(i)/no_instruments}
            ))


class PolyRhythmApp(App):

    def build(self):
        self.root= root = RhythmMaker()
        return root


if __name__ == '__main__':
    PolyRhythmApp().run()
