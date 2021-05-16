#!/usr/bin/env python3

from kivy.app import App
from kivy.properties import NumericProperty

class GfontMaker(App):
    threshold = NumericProperty(128)

if __name__ == '__main__':
    app = GfontMaker()
    app.run()
