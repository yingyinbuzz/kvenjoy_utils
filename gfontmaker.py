#!/usr/bin/env python3

import os
import io
import threading
from functools import partial
from PIL import Image
from kivy.core.image import Image as CoreImage
from kivy.app import App
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, Translate, Scale
from kivy.clock import mainthread

class LoadDialog(FloatLayout):
    confirm = ObjectProperty(None)
    cancel = ObjectProperty(None)

class RootWidget(BoxLayout):
    threshold = NumericProperty(128)
    last_path = StringProperty(os.getcwd())
    image_orig = ObjectProperty(None)

    @mainthread
    def update_image(self, data, *args):
        self.ids.img.texture = CoreImage(data, ext='jpeg').texture
        self.draw_block()

    def on_threshold(self, *args):
        print('threshold changed to {}'.format(self.threshold))
        self.draw_block()

    def on_load_image_file(self, path, filenames):
        self.last_path = path
        self._popup.dismiss()
        self.ids.img.texture = None
        threading.Thread(target=self.load_image, args=(filenames[0],)).start()

    def on_image_clicked(self, instance, touch):
        if touch.is_double_tap:
            content = LoadDialog(confirm=self.on_load_image_file, cancel=lambda *args : self._popup.dismiss())
            content.ids.file_chooser.path = self.last_path
            self._popup = Popup(title='Load image', content=content)
            self._popup.open()

    def load_image(self, filename):
        self.image_orig = Image.open(filename)
        data = io.BytesIO()
        self.image_orig.save(data, format='jpeg')
        data.seek(0)
        self.update_image(data)

    def draw_block(self):
        img = self.ids.img
        height = img.texture_size[1]
        x = self.threshold * 5
        y = self.threshold * 5
        box_size = 50
        img.canvas.after.clear()
        with img.canvas.after:
            Color(1, 0, 0)
            Translate(0, height)
            Scale(1, -1, 0)
            Rectangle(pos=(x, y), size=(box_size, box_size))

class GfontMakerApp(App):
    pass

if __name__ == '__main__':
    GfontMakerApp().run()
