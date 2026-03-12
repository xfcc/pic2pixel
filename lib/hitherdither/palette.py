# Vendored from https://github.com/hbldh/hitherdither (MIT)
from __future__ import division, print_function, unicode_literals, absolute_import

import numpy as np
from PIL import Image
from PIL.ImagePalette import ImagePalette

from .exceptions import PaletteCouldNotBeCreatedError

try:
    string_type = basestring
except NameError:
    string_type = str


def hex2rgb(h):
    if isinstance(h, string_type):
        return hex2rgb(int(h[1:] if h.startswith("#") else h, 16))
    return (h >> 16) & 0xFF, (h >> 8) & 0xFF, h & 0xFF


def rgb2hex(r, g, b):
    return (r << 16) + (g << 8) + b


class Palette(object):
    def __init__(self, data):
        if isinstance(data, np.ndarray):
            if data.ndim == 1:
                self.colours = data.reshape((3, len(data) // 3)).T
            else:
                self.colours = data
            self.hex = [rgb2hex(*colour) for colour in self.colours]
        elif isinstance(data, ImagePalette):
            _tmp = np.frombuffer(data.palette, "uint8")
            self.colours = _tmp.reshape((len(_tmp) // 3, 3))
            self.hex = [rgb2hex(*c) for c in self.colours]
        elif isinstance(data, Image.Image):
            if data.palette is None:
                raise PaletteCouldNotBeCreatedError(
                    "Image of mode {0} has no PIL palette.".format(data.mode)
                )
            _colours = data.getcolors()
            _n_colours = len(_colours)
            _tmp = np.array(data.getpalette())[: 3 * _n_colours]
            self.colours = _tmp.reshape((len(_tmp) // 3, 3))
            self.hex = [rgb2hex(*colour) for colour in self.colours]
        elif isinstance(data, (list, tuple)):
            if isinstance(data[0], string_type):
                self.hex = data
                self.colours = np.array([hex2rgb(c) for c in data])
            elif isinstance(data[0], int):
                self.hex = data
                self.colours = np.array([hex2rgb(c) for c in data])
            else:
                self.colours = np.array(data)
                self.hex = [rgb2hex(*colour) for colour in data]
        else:
            raise TypeError("Unsupported palette data type")

    def __iter__(self):
        for colour in self.colours:
            yield colour

    def __len__(self):
        return self.colours.shape[0]

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.colours[item, :]
        raise IndexError("Can only reference colours by integer values.")

    def pixel_distance(self, pixel, order=2):
        return np.array([np.linalg.norm(pixel - colour, ord=order) for colour in self.colours])

    def pixel_closest_colour(self, pixel, order=2):
        return self.colours[
            np.argmin(self.pixel_distance(pixel, order=order)), :
        ].copy()

    def image_distance(self, image, order=2):
        ni = np.array(image, "float")
        distances = np.zeros((ni.shape[0], ni.shape[1], len(self)), "float")
        for i, colour in enumerate(self.colours):
            distances[:, :, i] = np.linalg.norm(ni - colour, ord=order, axis=2)
        return distances

    def image_closest_colour(self, image, order=2):
        return np.argmin(self.image_distance(image, order=order), axis=2)

    def create_PIL_png_from_rgb_array(self, img_array):
        cc = self.image_closest_colour(img_array, order=2)
        pa_image = Image.new("P", (cc.shape[1], cc.shape[0]))
        pa_image.putpalette(self.colours.flatten().tolist())
        im = Image.fromarray(np.array(cc, "uint8")).im.convert("P", 0, pa_image.im)
        try:
            return pa_image._new(im)
        except AttributeError:
            return pa_image._makeself(im)
