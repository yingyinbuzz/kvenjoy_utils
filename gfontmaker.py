#!/usr/bin/env python3

from kivy.app import App
from kivy.properties import NumericProperty

class GfontMaker(App):
    threshold = NumericProperty(128)

    def on_threshold(self, *args):
        print('threshold changed to {}'.format(self.threshold))

if __name__ == '__main__':
    GfontMaker().run()
