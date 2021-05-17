#!/usr/bin/env python3

from kivy.app import App
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout

class RootWidget(BoxLayout):
    threshold = NumericProperty(128)

    def on_threshold(self, *args):
        print('threshold changed to {}'.format(self.threshold))

    def on_image_clicked(self, instance, touch):
        if touch.is_double_tap:
            print('double clicked')

class GfontMakerApp(App):
    pass

if __name__ == '__main__':
    GfontMakerApp().run()
