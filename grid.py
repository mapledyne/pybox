
import itertools as it
import numpy as np

from util import Point
from intersect import intersects_box
from config import unit_distance, plate_height_ratio, plates_to_brick
from colors import nearest_color_code, compute_face_colors
import progressbar

class Scaling:
    """
    Class for dealing with object scaling. Plate base is assumed to be
    of equal dimensions, and grid dimensions are computed so that there
    is (1/plate_height_ratio) more plates on the y-axis.
    """

    def __init__(self, bounds, plate_height_ratio, height):
        self.bounds = bounds
        self.plate_scale_real = Point(
            [unit_distance, unit_distance * plate_height_ratio, unit_distance])
        self.ratio = Point([plate_height_ratio, 1, plate_height_ratio])
        self.scale = (height / bounds.range_.y) * self.ratio
        self.grid_dimensions = Point.as_int(
            np.ceil(self.scale * bounds.range_))

    def to_world_point(self, grid_point):
        ratio = self.bounds.range_ / self.grid_dimensions
        return ratio * grid_point + self.bounds.lo

    def scale_down(self, world_point):
        return world_point * self.scale

    def to_grid_point(self, world_point):
        val = self.scale_down(world_point - self.bounds.lo)
        grid_index = (0, 0, 0), self.grid_dimensions - 1
        return Point.as_int(np.clip(np.round(val), *grid_index))


class GridObject:
    """
    An object in the resulting lego `Grid`. Brick base is assumed to be
    equal, while its height can vary.
    """

    BRICK_LARGE = '3005.dat'
    BRICK_SMALL = '30008.dat'
    BRICK_HEIGHTS = {
        BRICK_LARGE: plates_to_brick * unit_distance * plate_height_ratio,
        BRICK_SMALL: unit_distance * plate_height_ratio
    }

    def __init__(self, color, brick_type):
        self.color = color
        self.brick_type = brick_type

    def to_ldr_repr(self, matrix_str, position_3d, encode_rgb_callable):
        print(plate_height_ratio)
        x, y, z = position_3d
        height = GridObject.BRICK_HEIGHTS[self.brick_type]
        return '1 {color} {x} {y} {z} {matrix} {brick}'.format(
                color=encode_rgb_callable(self.color),
                x=x*Grid.UNIT_WIDTH,
                y=-(y*Grid.UNIT_HEIGHT + height),
                z=z*Grid.UNIT_DEPTH,
                matrix=matrix_str,
                brick=self.brick_type)


class Grid(np.ndarray):
    """
    Lego grid, composed of GridObjects. Keeps elements in an array where
    the first item represents the x component, second y and third z.
    This makes it easy to query the grid by: grid[(x, y, z)].

    (0, 0, 0) represents the (leftmost, bottommost, front) brick.
    """

    UNIT_HEIGHT = unit_distance*plate_height_ratio
    UNIT_WIDTH = unit_distance
    UNIT_DEPTH = unit_distance

    def __new__(cls, dimension_tuple):
        obj = np.empty(dimension_tuple, dtype=GridObject).view(cls)
        return obj

    def get_bricks_by_layer(self):
        xdim, ydim, zdim = self.shape
        grid_iter_by_y_layer = it.product(
            *(range(dim) for dim in (ydim, zdim, xdim)))
        bricks_by_layer_asc = (
            Point.as_int((x, y, z))
            for (y, z, x) in grid_iter_by_y_layer if self[(x, y, z)])

        return bricks_by_layer_asc

    def normalize(self, plates_to_brick):
        grid = self
        valid_rows = lambda pt: pt.y >= plates_to_brick - 1

        for pt in filter(valid_rows, grid.get_bricks_by_layer()):
            gen_pt = lambda i: (pt.x, pt.y - i, pt.z)
            same_color = lambda i, j: np.allclose(
                grid[i].color, grid[j].color)

            plates_to_replace = [gen_pt(i) for i in range(plates_to_brick)]
            bottom = plates_to_replace[-1]

            if all(grid[i] for i in plates_to_replace) \
                    and all(same_color(i, bottom) for i in plates_to_replace):
                for replace_pt in plates_to_replace[:-1]:
                    grid[replace_pt] = None

                grid[bottom] = GridObject(
                    grid[bottom].color, GridObject.BRICK_LARGE)

        return grid

    @staticmethod
    def create(scaling, parsed_obj, palette_rgb, jitter):
        grid = Grid(scaling.grid_dimensions)
        vs = parsed_obj.vs.values
        vts = parsed_obj.vts.values

        progress = progressbar.ProgressBar(max_value=len(parsed_obj.faces), redirect_stdout=True)
        face_count = 0
        for face in parsed_obj.faces:
            progress.update(face_count)
            face_count += 1
            for pos in to_blocks(scaling, [vs[fc.v] for fc in face], jitter):
                pos = tuple(pos)
                color = np.average(compute_face_colors(face, vts), axis=0)
                grid[pos] = GridObject(
                    nearest_color_code(color, palette_rgb),
                    GridObject.BRICK_SMALL)
        print()
        return grid


def to_blocks(scaling, face, jitter):
    blocks = [scaling.to_grid_point(fc) for fc in face]
    bounds = np.min(blocks, axis=0), np.max(blocks, axis=0) + 1
    grid_dim_real = jitter * (scaling.bounds.range_ / scaling.grid_dimensions)
    ranges = [range(lo, hi) for lo, hi in zip(*bounds)]
    vertices = len(face)
    for i in range(vertices - 2):
        triangle = np.take(face, [j % vertices for j in range(i, i + 3)], axis=0)
        for block in (Point.as_int(block) for block in it.product(*ranges)):
            block_center_real = scaling.to_world_point(block + 0.5)
            if intersects_box(triangle, block_center_real, grid_dim_real):
                yield block
