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
    glyph_threshold = NumericProperty(4)
    last_path = StringProperty(os.getcwd())
    image_orig = ObjectProperty(None)
    image_bw = ObjectProperty(None)
    green_lines = ListProperty()
    red_lines = ListProperty()
    brown_lines = ListProperty()
    glyph_boxes = ListProperty()

    @mainthread
    def update_image(self, data, *args):
        self.ids.img.texture = CoreImage(data, ext='jpeg').texture

    @mainthread
    def update_image_decorations(self):
        print('update_image_decorations')
        img = self.ids.img
        img.canvas.after.clear()
        img_w, img_h = img.texture_size
        with img.canvas.after:
            Translate(0, img_h)
            Scale(1, -1, 0)
            Color(0, 1, 0, 0.5)
            for line in self.green_lines:
                Line(points=line)
            Color(1, 0, 0, 0.5)
            for line in self.red_lines:
                Line(points=line)
            Color(0.72, 0.47, 0.34, 0.5)
            delta = 5
            for bys in self.brown_lines:
                Line(points=[0, bys[0] - delta, img_w - 1, bys[0] - delta])
                Line(points=[0, bys[1] + delta, img_w - 1, bys[1] + delta])
            Color(1, 0, 1)
            for (left, top, right, bottom) in self.glyph_boxes:
                Line(points=[left, top, right, top, right, bottom, left, bottom, left, top])

    def on_threshold(self, *args):
        self.find_base_lines(self.image_orig, self.stroke_threshold)
        self.update_image_decorations()

    def on_glyph_threshold(self, *args):
        self.find_base_lines(self.image_orig, self.stroke_threshold)
        self.update_image_decorations()

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
        self.find_base_lines(self.image_orig, self.stroke_threshold)
        self.image_bw = self.bw_glyphs(self.image_orig)
        self.image_bw.save(data, format='jpeg')
        data.seek(0)
        self.update_image(data)
        self.update_image_decorations()

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

        # Mark lines with brown lines
        ys = []
        ys.extend(y for (y, c) in green_ys)
        ys.extend(y for (y, c) in red_ys)
        ys = sorted(ys)
        last_y = ys[0]
        last_dist = None
        brown_y = last_y
        for y in ys[1:]:
            dist = y - last_y
            if last_dist is not None and dist > last_dist * 1.5:
                self.brown_lines.append((brown_y, last_y))
                last_dist = None
                brown_y = y
            last_dist = dist
            last_y = y
        if last_dist is not None:
            self.brown_lines.append((brown_y, last_y))

        # Mark characters with purple lines
        left = None
        right = None
        boxes = []
        for (y_top, y_bottom) in self.brown_lines:
            for x in range(w):
                has_stroke = False
                for y in range(y_top, y_bottom + 1):
                    r, g, b = image.getpixel((x, y))
                    if r <= self.threshold and g <= self.threshold and b <= self.threshold:
                        # Black pixel means stroke
                        has_stroke = True
                        break
                if has_stroke:
                    if left is None:
                        left = x - self.glyph_threshold // 2 if x > self.glyph_threshold // 2 else x
                    right = x
                elif right is not None:
                    if x - right >= self.glyph_threshold:
                        boxes.append((left, y_top, (x + right) // 2, y_bottom))
                        left = None
                        right = None
            if left is not None:
                boxes.append((left, y_top, w, y_bottom))
        self.glyph_boxes = boxes

    def bw_glyphs(self, image):
        oimg = Image.new('L', image.size, color=255)
        for (left, top, right, bottom) in self.glyph_boxes:
            for y in range(top, bottom):
                for x in range(left, right):
                    r, g, b = image.getpixel((x, y))
                    if r <= self.threshold and g <= self.threshold and b <= self.threshold:
                        oimg.putpixel((x, y), 0)
                    else:
                        oimg.putpixel((x, y), 255)
        return oimg

class GfontMakerApp(App):
    pass

if __name__ == '__main__':
    GfontMakerApp().run()
