import yaml

# This is the unit distance for a plate (i.e. width and depth).
# This will be used to position plate spacing in the resulting 3D grid.
# Default 'unit distance' for plates and bricks is 20
unit_distance = 20

# Safe to assume pieces are square (width and depth),
# and only need to config height. For simplicity, we'll assume
# width/depth are always 1:
plate_height_ratio = 1.2
#plate_height_ratio = 0.4

# Number of plates in a brick. If '1', this functionality should be
# skipped (leaving everything as a plate, above)
plates_to_brick = 3

# desired color palette
colors_hex = [
  '#000000', #black
  '#FFFFFF', #white
  '#FF0000', #red
  '#00FF00', #green
  '#0000FF', #blue
]



# default color if no textures are available for given file
texture_default_color = (256, 256, 256)

# Percentage determining how much to "expand" or "contract" lego bricks when
# computing their dimensions in the model world. If set to 1, no additional
# scaling is done (this is the default behavior, and should be good for most
# - if not all - cases).
brick_expand_jitter = 1

# this is for debugging purposes on my end; color indices
# more or less corresponding to the hex values above
colors_id = [
  0,
  183,
  324,
  2,
  1,
]

class ColorLibrary(object):
    def __init__(self):
        with open("colors.yaml", 'r') as stream:
            color_config = yaml.load(stream)
            self.colors = color_config['colors']
            self.color_sets = color_config['color_sets']
            self.color_sets['all'] = []
            for one in self.colors:
                self.color_sets['all'].append(one)

    def set_to_hex(self, one_set):
        ret = []
        for c in self.color_sets[one_set]:
            ret.append(self.colors[c])
        return ret

library = ColorLibrary()
colors_hex = library.set_to_hex('all')
