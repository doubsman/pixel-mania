import os
import numpy as np
from PIL import Image, ImageDraw


GRAY_SCALE_DRAW = {
    0: (255, 255, 255),  # Blanc
    1: (192, 192, 192),  # Gris très clair
    2: (128, 128, 128),  # Gris clair
    3: (64, 64, 64),     # Gris foncé
    4: (32, 32, 32),     # Gris très foncé
    5: (0, 0, 0)         # Noir
}

class BidFile:
    def __init__(self):
        self.path_bid = None
        self.grid_bid = None
        self.path_color = None
        self.grid_colors = None
        self.bool_color = True
        self.grid_width = 0
        self.grid_height = 0
        self.image_scale = 1
        self.result_width = 1024
        self.result_height = 0
        self.image = None
        self.draw = None
        self.bid = []

    def load_bidfile(self, path_bid, result_width=None):
        if result_width is not None:
            self.result_width = result_width
        self.path_bid = path_bid
        self.grid_bid = np.genfromtxt(self.path_bid, delimiter=1, dtype=int, ndmin=2)
        self.grid_width = len(self.grid_bid[0])
        self.grid_height = int(self.grid_bid.size / self.grid_width)

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

    def new_bid(self, result_width=None):
        if result_width is not None:
            self.result_width = result_width
        self.bool_color = True
        self.grid_height = self.grid_width = 48
        self.grid_bid = np.zeros((self.grid_height, self.grid_width), dtype=int)
        self.grid_colors = np.zeros((self.grid_height, self.grid_width), dtype=int)
        self.draw_bidfile()
        return self.image

    def draw_bidfile(self, bool_outline=False):
        self.image_scale = int(self.result_width / float(self.grid_width))
        self.image = Image.new('RGB', (self.grid_width * self.image_scale, self.grid_height * self.image_scale), color=(255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)
        self.bid = []
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
                self.bid.append((column, row, cell, color_indice))
                self.draw_cellule(column, row, cell, color_indice, bool_outline)

    def draw_cellule(self, x, y, cell_type, cell_color, bool_outline=False):
        """Dessine une cellule en fonction de son type."""
        left = x * self.image_scale
        top = y * self.image_scale
        right = (x + 1) * self.image_scale
        bottom = (y + 1) * self.image_scale
        color = GRAY_SCALE_DRAW[cell_color]

        if self.image_scale == 1:
            # 1 cellule = 1 pixel
            self.draw.point((x, y), fill=color)
        else:
            if bool_outline:
                self.draw.rectangle([(left, top), (right, bottom)], fill=(255, 255, 255), outline=(0, 0, 0))
            else:
                self.draw.rectangle([(left, top), (right, bottom)], fill=(255, 255, 255), outline=(255, 255, 255))
            if cell_type == 1:  # carré plein
                if bool_outline: 
                    self.draw.rectangle([(left, top), (right, bottom)], fill=color, outline=(0, 0, 0))
                else:
                    self.draw.rectangle([(left, top), (right, bottom)], fill=color, outline=color)
            elif cell_type == 3:  # triangle en bas à droite
                self.draw.polygon([(left, bottom), (right, bottom), (right, top)], fill=color)
            elif cell_type == 4:  # triangle en haut à droite
                self.draw.polygon([(left, top), (right, top), (right, bottom)], fill=color)
            elif cell_type == 5:  # triangle en haut à gauche
                self.draw.polygon([(left, top), (right, top), (left, bottom)], fill=color)
            elif cell_type == 6:  # triangle en bas à gauche
                self.draw.polygon([(left, bottom), (left, top), (right, bottom)], fill=color)

    def draw_part_cells(self, cells):  #cell(column, row, cell, color_indice)
        min_x = min([cell[0] for cell in cells])
        min_y = min([cell[1] for cell in cells])
        max_x = max([cell[0] for cell in cells])
        max_y = max([cell[1] for cell in cells])

        width = (max_x - min_x + 1) * self.image_scale
        height = (max_y - min_y + 1) * self.image_scale

        backup_draw = self.draw
        thumbnail = Image.new('RGB', (width, height), (255, 255, 255))
        self.draw = ImageDraw.Draw(thumbnail)
        for cell in cells:
            column, row, cell, color_indice = cell
            column -= min_x
            row -= min_y
            self.draw_cellule(column, row, cell, color_indice, False)
        self.draw = backup_draw
        return thumbnail, width/height

    def save_bidfile(self, path_bid):
        if not path_bid.endswith(".bid"):
            self.path_bid = path_bid + '.bid'
        else:
            self.path_bid = path_bid
        np.savetxt(self.path_bid, self.grid_bid, fmt='%i', delimiter="")
        path_color = self.path_bid.replace('.bid','.color')
        np.savetxt(path_color, self.grid_colors, fmt='%i', delimiter="")

    def save_imagefile(self, path_image, image_scale=50,bool_outline=True):
        if not path_image.endswith(".png"):
            path_image = path_image + '.png'
        backup_result_width = self.result_width
        self.result_width = image_scale * self.grid_width
        self.draw_bidfile(bool_outline=bool_outline)
        self.image.save(path_image)
        self.result_width = backup_result_width
        self.draw_bidfile()


if __name__ == '__main__':
    Myclass = BidFile()
    image = Myclass.load_bidfile('bid/balls.bid')
    image.show()