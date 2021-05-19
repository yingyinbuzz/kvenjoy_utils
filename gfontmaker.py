#!/usr/bin/env python3

import os
import io
from PIL import Image
from kivy.core.image import Image as CoreImage
from kivy.app import App
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class RootWidget(BoxLayout):
    threshold = NumericProperty(128)
    last_path = StringProperty(os.getcwd())

    def on_threshold(self, *args):
        print('threshold changed to {}'.format(self.threshold))
        img = self.ids.img
        size = img.texture_size
        img.canvas.after.clear()
        with img.canvas.after:
            Color(1, 0, 0)
            Rectangle(pos=(self.threshold * 5, size[1] - self.threshold * 5 - 100), size=(100, 100))

    def load(self, path, filenames):
        print('Load {} {}'.format(path, filenames))
        self.dismiss_popup()
        self.last_path = path
        img = Image.open(filenames[0])
        data = io.BytesIO()
        img.save(data, format='png')
        data.seek(0)
        core_img = CoreImage(data, ext='png')
        self.ids.img.texture = core_img.texture

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
