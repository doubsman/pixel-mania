import os
import numpy as np
from PIL import Image, ImageDraw
from class_cells import Cells


class BidFile(Cells):
    def __init__(self):
        Cells.__init__(self)
        self.path_bid = None
        self.grid_bid = None
        self.path_color = None
        self.grid_colors = None
        self.bool_color = True
        self.grid_width = 0
        self.grid_height = 0
        self.image = None
        self.draw = None

    def load_bidfile(self, path_bid, image_with=None, image_height=None):
        self.path_bid = path_bid
        self.grid_bid = np.genfromtxt(self.path_bid, delimiter=1, dtype=int, ndmin=2)
        self.grid_width = len(self.grid_bid[0])
        self.grid_height = int(self.grid_bid.size / self.grid_width)
        if image_with is not None and image_height is not None:
            self.define_scale(image_with, image_height, self.grid_width, self.grid_height)
        # colors
        self.path_color = self.path_bid.replace('.bid','.color')
        self.bool_color = os.path.isfile(self.path_color)
        if self.bool_color:
            self.grid_colors = np.genfromtxt(self.path_color, delimiter=1, dtype=int, ndmin=2)
        else:
            self.grid_colors = np.zeros((self.grid_height, self.grid_width), dtype=int)
        
        # draw bid
        self.draw_bidfile()
        return self.image

    def new_bid(self, image_with=None, image_height=None, grid_width=48, grid_height=48):
        self.bool_color = True
        self.grid_height = grid_height
        self.grid_width = grid_width
        if image_with is not None and image_height is not None:
            self.define_scale(image_with, image_height, self.grid_width, self.grid_height)
        self.grid_bid = np.zeros((self.grid_height, self.grid_width), dtype=int)
        self.grid_colors = np.zeros((self.grid_height, self.grid_width), dtype=int)
        self.draw_bidfile()
        return self.image

    def change_bid_size(self, image_with, image_height, grid_width, grid_height):
        if grid_width < self.grid_width or grid_height < self.grid_height:
            self.reduce_grid(grid_width, grid_height)
        if grid_width > self.grid_width or grid_height > self.grid_height:
            self.extend_grid(grid_width, grid_height)
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.define_scale(image_with, image_height, self.grid_width, self.grid_height)
        self.draw_bidfile()

    def extend_grid(self, grid_width, grid_height):
        extend_rows = int((grid_height - self.grid_height) // 2)
        extend_columns = int((grid_width - self.grid_width) // 2)
        self.grid_bid = np.pad(self.grid_bid, ((extend_rows, extend_rows), (extend_columns, extend_columns)), mode='constant', constant_values=0)
        self.grid_colors = np.pad(self.grid_colors, ((extend_rows, extend_rows), (extend_columns, extend_columns)), mode='constant', constant_values=0)

    def reduce_grid(self, grid_width, grid_height):
        reduce_rows = (self.grid_height - grid_height) // 2
        reduce_columns = (self.grid_width - grid_width) // 2
        start_row = reduce_rows
        end_row = self.grid_height - reduce_rows
        start_col = reduce_columns
        end_col = self.grid_width - reduce_columns
        self.grid_bid = self.grid_bid[start_row:end_row, start_col:end_col]
        self.grid_colors = self.grid_colors[start_row:end_row, start_col:end_col]

    def draw_bidfile(self, bool_outline=False):
        self.image = Image.new('RGB', (self.grid_width * self.image_scale, self.grid_height * self.image_scale), color=(255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)
        for row in range(self.grid_height):
            for column in range(self.grid_width):
                cell = self.grid_bid[row][column]
                if self.bool_color:
                    color_indice = self.grid_colors[row][column]
                    # plain square if color: compatiblity old version
                    if cell == 0 and color_indice > 0:
                        cell = 1
                else:
                    # not greys
                    color_indice = 0 if cell == 0 else 5
                    self.grid_colors[row][column] = color_indice
                self.draw_cell(column, row, cell, color_indice, bool_outline)

    def save_bidfile(self, path_bid):
        if not path_bid.endswith(".bid"):
            self.path_bid = path_bid + '.bid'
        else:
            self.path_bid = path_bid
        np.savetxt(self.path_bid, self.grid_bid, fmt='%i', delimiter="")
        path_color = self.path_bid.replace('.bid','.color')
        np.savetxt(path_color, self.grid_colors, fmt='%i', delimiter="")

    def save_imagefile(self, path_image, image_scale=50, bool_outline=True):
        if not path_image.endswith(".png"):
            path_image = path_image + '.png'
        backup_scale = self.image_scale
        self.image_scale = image_scale
        self.draw_bidfile(bool_outline=bool_outline)
        self.image.save(path_image)
        self.image_scale = backup_scale
        self.draw_bidfile()

    def load_combined_file(self, path_combined):
        data = np.load(path_combined)
        self.grid_bid = data['grid_bid']
        self.grid_colors = data['grid_colors']
        image_array = data['image']
        self.image = Image.fromarray(image_array)
        self.draw = ImageDraw.Draw(self.image)

    def save_combined_file(self, path_combined):
        image_array = np.array(self.image)
        np.savez(path_combined, grid_bid=self.grid_bid, grid_colors=self.grid_colors, image=image_array)

if __name__ == '__main__':
    Myclass = BidFile()
    image = Myclass.load_bidfile('bid/balls.bid')
    image.show()