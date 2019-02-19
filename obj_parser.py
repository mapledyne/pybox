import os
import glob
import numpy as np

from collections import namedtuple, defaultdict
from PIL import Image
from util import Point, Bounds


TextureInfo = namedtuple("TextureInfo", ['data', 'w', 'h'])
VertexInfo = namedtuple("VertexInfo", ['values', 'bounds'])


class ParsedObjFile:
    """
    Represents the result of parsing a `.obj` file.
    """

    def __init__(self, faces, bounds, vertices):
        self.faces = faces
        self.vs = VertexInfo(vertices['v'], bounds['v'])
        self.vts = VertexInfo(vertices['vt'], bounds['vt'])
        self.vns = VertexInfo(vertices['vn'], bounds['vn'])


class Face:
    """
    Abstraction of a 'face' in a `.obj` file. A face is composed of
    multiple FaceComponent objects.
    """

    def __init__(self, input_array, texture_info, Kd=None):
        self.components = np.array(input_array, dtype=FaceComponent)
        self.texture_info = texture_info
        self.Kd = Kd

    def __getitem__(self, i):
        return self.components[i]

    def __repr__(self):
        return "Face({})".format(self.components)


class FaceComponent:
    """
    Each FaceComponent is composed of three values, representing the
    indices of corresponding vectors, texture vectors and vector normals
    loaded from a `.obj` file.
    """

    def __init__(self, input_array):
        self.elements = np.array(input_array, dtype=int)

    @property
    def v(self):
        return self.elements[0]

    @property
    def vt(self):
        return self.elements[1]

    @property
    def vn(self):
        return self.elements[2] if len(self.elements) > 2 else None

    def __repr__(self):
        return "FaceComponent({})".format(self.elements)


def load_obj_file(obj_location):
    with open(obj_location) as f:
        faces = []
        bounds = defaultdict(Bounds)
        textures = defaultdict(None)
        texture_to_rgb = defaultdict(None)
        vertices = defaultdict(list)

        file_dir = os.path.dirname(obj_location)
        mtl_state = None

        for components in (x.strip().split() for x in f if x.strip()):
            key = components[0]

            if key == 'mtllib':
                mtl_file_location = os.path.join(file_dir, components[1])
                texture_to_file, texture_to_rgb = find_texture_info(
                        mtl_file_location)
                textures = load_textures(file_dir, texture_to_file)
            elif key == 'usemtl':
                mtl_state = components[1]
            elif key.startswith('v'):
                value = Point(components[1:])
                vertices[key].append(value)
                bounds[key].update(value)
            elif key == 'f':
                texture = textures.get(mtl_state, None)
                face = handle_face(components[1:], texture)
                face.Kd = texture_to_rgb.get(mtl_state, None)
                faces.append(face)

    return ParsedObjFile(faces, bounds, vertices)


def handle_face(face_items, mtl):
    # values are 1-indexed in .obj files
    index_or_none = lambda val: (int(val) - 1) if val else -1
    to_index = lambda i: [index_or_none(val) for val in i.split('/')]
    return Face([FaceComponent(to_index(i)) for i in face_items], mtl)


def find_texture_info(mtl_file_location):
    key = None
    texture_to_filename_dict = {}
    texture_to_rgb_dict = {}

    with open(mtl_file_location) as f:
        for components in (x.strip().split() for x in f if x.strip()):
            if components[0] == 'newmtl':
                key = components[1]
            elif components[0] == 'map_Kd' and len(components) >= 2:
                texture_to_filename_dict[key] = components[1]
            elif components[0] == 'Kd' and len(components) >= 2:
                texture_to_rgb_dict[key] = np.array(
                        [float(c) for c in components[1:]]) * 255

    return texture_to_filename_dict, texture_to_rgb_dict


def load_textures(base_dir, texture_to_filename_dict):
    def open_img_recursive_in_subdirs(filename):
        files = glob.glob(base_dir + '/**/' + filename, recursive=True)
        return Image.open(files[0])

    def transform(img):
        return TextureInfo(list(img.getdata()), *img.size)

    return {k: transform(open_img_recursive_in_subdirs(v))
            for k, v in texture_to_filename_dict.items()}
