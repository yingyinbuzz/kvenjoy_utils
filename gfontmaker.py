#!/usr/bin/env python3

import os
import io
import threading
from functools import partial
from PIL import Image
from kivy.core.image import Image as CoreImage
from kivy.app import App
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, Translate, Scale, Line
from kivy.clock import mainthread

class LoadDialog(FloatLayout):
    confirm = ObjectProperty(None)
    cancel = ObjectProperty(None)

class RootWidget(BoxLayout):
    threshold = NumericProperty(128)
    stroke_threshold = NumericProperty(16)
    last_path = StringProperty(os.getcwd())
    image_orig = ObjectProperty(None)
    green_lines = ListProperty()
    red_lines = ListProperty()

    @mainthread
    def update_image(self, data, *args):
        self.ids.img.texture = CoreImage(data, ext='jpeg').texture

        img = self.ids.img
        img.canvas.after.clear()
        with img.canvas.after:
            Translate(0, img.texture_size[1])
            Scale(1, -1, 0)
            Color(0, 1, 0)
            for line in self.green_lines:
                Line(points=line)
            Color(1, 0, 0)
            for line in self.red_lines:
                Line(points=line)

    def on_threshold(self, *args):
        print('threshold changed to {}'.format(self.threshold))

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
        base_lines = self.find_base_lines(self.image_orig, self.stroke_threshold)
        data.seek(0)
        self.update_image(data)

    def add_to_y(self, ys, y, threshold):
        for i in range(len(ys)):
            p = ys[i]
            if abs(p[0] - y) <= threshold:
                ys[i] = (p[0], p[1] + 1)
                return
        ys.append((y, 1))

    def find_base_lines(self, image, stroke_threshold):
        w, h = image.size
        green_ys = []
        red_ys = []
        color_threshold = 25
        for y in range(h):
            for x in range(w):
                r, g, b = image.getpixel((x, y))
                if r - g >= color_threshold and r - b >= color_threshold:
                    self.add_to_y(red_ys, y, stroke_threshold)
                elif g - r >= color_threshold and g - b >= color_threshold:
                    self.add_to_y(green_ys, y, stroke_threshold)
        self.green_lines.clear()
        for (y, c) in green_ys:
            self.green_lines.append([0, y, w - 1, y])
        self.red_lines.clear()
        for (y, c) in red_ys:
            self.red_lines.append([0, y, w - 1, y])

class GfontMakerApp(App):
    pass

if __name__ == '__main__':
    GfontMakerApp().run()
