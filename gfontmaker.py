#!/usr/bin/env python3

import os
from kivy.app import App
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class RootWidget(BoxLayout):
    threshold = NumericProperty(128)
    last_path = StringProperty(os.getcwd())

    def on_threshold(self, *args):
        print('threshold changed to {}'.format(self.threshold))

    def load(self, path, filenames):
        print('Load {} {}'.format(path, filenames))
        self.last_path = path
        self.ids.img.source = filenames[0]
        self.dismiss_popup()

    def dismiss_popup(self):
        self._popup.dismiss()

    def on_image_clicked(self, instance, touch):
        if touch.is_double_tap:
            content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
            content.ids.file_chooser.path = self.last_path
            self._popup = Popup(title='Load file', content=content)
            self._popup.open()

class GfontMakerApp(App):
    pass

if __name__ == '__main__':
    GfontMakerApp().run()
