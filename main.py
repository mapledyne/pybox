
import os
import numpy as np

from config import *
from obj_parser import load_obj_file
from grid import Scaling, Grid
from colors import hex2rgb, rgb2hex
from argparse import ArgumentParser


def increment_on_write_step(file, y, step):
    if y != step:
        print('0 STEP', file=file)
    return y


def output_ldr(filename, grid, palette_rgb):
    transform_matrix_str = ' '.join(str(i) for i in np.ravel(
        [[1, 0, 0],
         [0, 1, 0],
         [0, 0, 1]]))

    colors_hex_0x2 = ['0x2{}'.format(rgb2hex(v)) for v in palette_rgb]
    as_hex_0x2 = lambda rgb: colors_hex_0x2[palette_rgb.index(rgb)]

    # debug method for me. can be deleted
    # as_colors_id = lambda rgb: colors_id[palette_rgb.index(rgb)]

    with open(filename, 'w') as f:
        step = 0

        for x, y, z in grid.get_bricks_by_layer():
            pt = (x, y, z)

            step = increment_on_write_step(f, y, step)
            line = grid[pt].to_ldr_repr(
                transform_matrix_str, pt, as_hex_0x2)

            print(line, file=f)


def output_header_details():
    print('{:#^40}'.format(' Blockify '))
    print()
    print('Input file: {}'.format(args.input))
    print('Output file: {}'.format(args.out))
    print('Height: {}'.format(args.total_height))
    print('Colors: {}'.format(str(color_library.color_sets[args.color_set])))
    if args.bricks_only:
        print('Computing for bricks only (no plates)')
    else:
        print('Computing for plates and bricks')
    print()
    print('{:#^40}'.format(''))


if __name__ == "__main__":
    color_library = ColorLibrary()
    parser = ArgumentParser()
    parser.add_argument(
        'input', type=str, help='.obj input file path')
    parser.add_argument(
        '-c', '--color-set', type=str, help='color set to limit to', default='all')
    parser.add_argument(
        '-o', '--out', type=str, help='.ldr file name', default=None)
    parser.add_argument(
        '-t', '--total-height', type=int, help='Total height of the lego model',
        default=80)
    parser.add_argument(
        '-b', '--bricks-only', action='store_true', help='Use bricks instead of plates')
    args = parser.parse_args()

    if args.bricks_only:
        plates_to_brick = 1
        plate_height_ratio = 1.2

    if args.out is None:
        args.out = os.path.splitext(os.path.basename(args.input))[0] + '.ldr'

    output_header_details()
    obj_file = load_obj_file(args.input)

    scaling = Scaling(obj_file.vs.bounds, plate_height_ratio, args.total_height)

    palette_rgb = [hex2rgb(c) for c in colors_hex]
    grid = Grid.create(scaling, obj_file, palette_rgb, brick_expand_jitter) \
        .normalize(plates_to_brick)

    out_file = args.out or \
        os.path.splitext(os.path.basename(args.input))[0] + '.ldr'

    output_ldr(out_file, grid, palette_rgb)
