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
        self.grid_color = None
        self.bool_color = False
        self.grid_width = 0
        self.grid_height = 0
        self.image_scale = 0
        self.result_width= 1024
        self.result_height=0
        self.image = None
        self.draw = None

    def load_bidfile(self, path_bid, result_width=None):
        if result_width is not None:
            self.result_width = result_width
        self.path_bid = path_bid
        self.grid_bid = np.loadtxt(self.path_bid, dtype=str)
        try:
            self.grid_width = len(str(self.grid_bid[0])) 
            self.grid_height = self.grid_bid.size
        except:
            # one line
            self.grid_width = len(str(self.grid_bid))
            self.grid_height = 1
            tmp_shapes = np.zeros((self.grid_height), dtype=f'<U{self.grid_width}')
            tmp_shapes[0] = self.grid_bid
            self.grid_bid = tmp_shapes

        # colors
        self.path_color = self.path_bid.replace('.bid','.color')
        self.bool_color = os.path.isfile(self.path_color)
        if self.bool_color:
            self.grid_colors = np.loadtxt(self.path_color, dtype=str)
        
        # draw bid
        self.draw_bidfile()
        return self.image

    def draw_bidfile(self):
        self.image_scale = int(self.result_width / float(self.grid_width))
        self.image = Image.new('RGB', (self.grid_width * self.image_scale, self.grid_height * self.image_scale), color=(255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)
        for row in range(self.grid_height):
            for column in range(self.grid_width):
                cell = int(self.grid_bid[row][column])
                if self.bool_color:
                    color_indice = int(self.grid_colors[row][column])
                else:
                    color_indice = 0 if cell == 0 else 5
                color = GRAY_SCALE_DRAW[color_indice]
                self.draw_cellule(column, row, cell, color)

    def draw_cellule(self, x, y, cell_type, cell_color):
        """Dessine une cellule en fonction de son type."""
        left = x * self.image_scale
        top = y * self.image_scale
        right = (x + 1) * self.image_scale
        bottom = (y + 1) * self.image_scale

        if self.image_scale == 1:
            # 1 cellule = 1 pixel
            self.draw.point((x, y), fill=cell_color)
        else:
            self.draw.rectangle([(left, top), (right, bottom)], fill=(255, 255, 255), outline=(0, 0, 0))
            if cell_type == 1:  # carré noir
                self.draw.rectangle([(left, top), (right, bottom)], fill=cell_color, outline=(0, 0, 0))
            elif cell_type == 3:  # triangle en bas à droite
                self.draw.polygon([(left, bottom), (right, bottom), (right, top)], fill=cell_color)
            elif cell_type == 4:  # triangle en haut à droite
                self.draw.polygon([(left, top), (right, top), (right, bottom)], fill=cell_color)
            elif cell_type == 5:  # triangle en haut à gauche
                self.draw.polygon([(left, top), (right, top), (left, bottom)], fill=cell_color)
            elif cell_type == 6:  # triangle en bas à gauche
                self.draw.polygon([(left, bottom), (left, top), (right, bottom)], fill=cell_color)

    def display_bidfile(self):
        if self.grid_bid is not None:
            self.image.show()



if __name__ == '__main__':
	Myclass = BidFile()
	Myclass.load_bidfile('e:/download/africa.bid')
	Myclass.display_bidfile()