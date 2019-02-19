import numpy as np

from PIL import ImageColor
from util import Point
from config import texture_default_color


def rgb2hex(rgb):
    return '{:02x}{:02x}{:02x}'.format(*rgb)


def hex2rgb(hex_):
    return ImageColor.getrgb(hex_)


def nearest_color_code(rgb_color, palette_rgb):
    index = np.argmin([color_distance(ref_rgb, rgb_color)
                       for ref_rgb in palette_rgb])
    return palette_rgb[index]


def color_distance(rgb1, rgb2):
    """ Get the distance between two RGB color arrays.

    algorithm as defined by:
    https://en.wikipedia.org/wiki/Color_difference
    alternatively, simple Euclidean distance might also work well
    """

    delta = np.array(rgb2) - np.array(rgb1)
    r = (rgb1[0] + rgb2[0]) / 2
    residue = (r * (delta[0] ** 2 - delta[2] ** 2)) / 256
    coeffs = Point([2, 4, 3])

    return np.sum(coeffs * (delta ** 2)) + residue


def compute_face_colors(face, vts):
    if not face.texture_info:
        return [texture_default_color] if face.Kd is None else [face.Kd]

    pixel_values, w, h = \
        face.texture_info.data, face.texture_info.w, face.texture_info.h
    get_rgb = lambda x, y: pixel_values[y * w + x]
    get_vts = lambda face_component: vts[face_component.vt][:2]

    return [get_rgb(*np.round((xp*(w-1), (1-yp)*(h-1))).astype(int))
            for xp, yp in map(get_vts, face.components)]
