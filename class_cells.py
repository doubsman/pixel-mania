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

class Cells:
    def __init__(self):
        self.symbol = None
        self.symbol_path = None
        self.symbol_width = 0
        self.symbol_height = 0
        self.symbol_image_scale = 20
        self.symbol_image = None
        self.draw = None
        self.min_x = self.min_y = self.max_x = self.max_y = 0

    def define_dimension(self):
        self.min_x = min([cell[0] for cell in self.symbol])
        self.min_y = min([cell[1] for cell in self.symbol])
        self.max_x = max([cell[0] for cell in self.symbol])
        self.max_y = max([cell[1] for cell in self.symbol])
        self.symbol_width = (self.max_x - self.min_x + 1)
        self.symbol_height = (self.max_y - self.min_y + 1)
    
    def define_scale(self, image_with, image_height):
        if image_with > image_height:
            self.symbol_image_scale = int(image_with / float(self.symbol_width))
        else:
            self.symbol_image_scale = int(image_height / float(self.symbol_height))
    
    def insert_symbol(self, array_symbol=None, image_with=None, image_height=None):
        self.symbol_path = None
        self.symbol = array_symbol
        # modify scale function desired width or height
        if image_with is not None and image_height is not None:
            self.define_scale()
        if hasattr(self, 'symbol') and len(self.symbol) > 0:
            self.define_dimension()
            self.draw_symbol()

    def load_symbol(self, symbol_path):
        if os.path.isfile(symbol_path):
            self.symbol_path = symbol_path
            self.symbol = np.loadtxt(self.symbol_path, dtype=int, delimiter=";")
            self.define_dimension()           
            self.draw_symbol()  

    def save_symbol(self, symbol_path):
        np.savetxt(symbol_path, self.symbol, fmt='%i', delimiter=";")

    def draw_symbol(self):
        width = (self.symbol_width) * self.symbol_image_scale
        height = (self.symbol_height) * self.symbol_image_scale
        self.symbol_image = Image.new('RGB', (width, height), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.symbol_image)
        for cell in self.symbol:
            column, row, cell, color_indice = cell
            column -= self.min_x
            row -= self.min_y
            self.draw_cell(column, row, cell, color_indice)
    
    def draw_cell(self, x, y, cell_type, cell_color, bool_outline=False):
        """Draw a cell according to its type."""
        left = x * self.symbol_image_scale
        top = y * self.symbol_image_scale
        right = (x + 1) * self.symbol_image_scale
        bottom = (y + 1) * self.symbol_image_scale
        color = GRAY_SCALE_DRAW[cell_color]

        if self.symbol_image_scale == 1:
            # 1 cellule = 1 pixel
            self.draw.point((x, y), fill=color)
        else:
            if bool_outline:
                self.draw.rectangle([(left, top), (right, bottom)], fill=(255, 255, 255), outline=(0, 0, 0))
            else:
                self.draw.rectangle([(left, top), (right, bottom)], fill=(255, 255, 255))
            if cell_type == 1:  # carré plein
                if bool_outline: 
                    self.draw.rectangle([(left, top), (right, bottom)], fill=color)
                else:
                    self.draw.rectangle([(left, top), (right, bottom)], fill=color)
            elif cell_type == 3:  # triangle en bas à droite
                self.draw.polygon([(left, bottom), (right, bottom), (right, top)], fill=color)
            elif cell_type == 4:  # triangle en haut à droite
                self.draw.polygon([(left, top), (right, top), (right, bottom)], fill=color)
            elif cell_type == 5:  # triangle en haut à gauche
                self.draw.polygon([(left, top), (right, top), (left, bottom)], fill=color)
            elif cell_type == 6:  # triangle en bas à gauche
                self.draw.polygon([(left, bottom), (left, top), (right, bottom)], fill=color)

    def flipv_cells(self):
        if hasattr(self, 'symbol') and len(self.symbol) > 0:
            max_y = max(cell[1] for cell in self.symbol)
            min_y = min(cell[1] for cell in self.symbol)
            flips = []
            for cell in self.symbol:
                x, y, shape, color = cell
                new_y = max_y + min_y - y
                # Inverser les shapes des triangles
                if shape == 3:
                    new_shape = 4
                elif shape == 4:
                    new_shape = 3
                elif shape == 5:
                    new_shape = 6
                elif shape == 6:
                    new_shape = 5
                else:
                    new_shape = shape
                flips.append((x, new_y, new_shape, color))
            self.symbol = flips
            self.draw_symbol()

    def fliph_cells(self):
        if hasattr(self, 'symbol') and len(self.symbol) > 0:
            max_x = max(cell[0] for cell in self.symbol)
            min_x = min(cell[0] for cell in self.symbol)
            flips = []
            for cell in self.symbol:
                x, y, shape, color = cell
                new_x = max_x + min_x - x
                # Inverser les shapes des triangles
                if shape == 3:
                    new_shape = 6
                elif shape == 4:
                    new_shape = 5
                elif shape == 5:
                    new_shape = 4
                elif shape == 6:
                    new_shape = 3
                else:
                    new_shape = shape
                flips.append((new_x, y, new_shape, color))
            self.symbol = flips
            self.draw_symbol()

    def rotate_l_cells(self):
        if hasattr(self, 'symbol') and len(self.symbol) > 0:
            max_x = max(cell[0] for cell in self.symbol)
            min_x = min(cell[0] for cell in self.symbol)
            min_y = min(cell[1] for cell in self.symbol)
            rotate = []
            for cell in self.symbol:
                x, y, shape, color = cell
                new_x = y - min_y
                new_y = max_x - x + min_x
                # Inverser les shapes des triangles
                if shape == 3:
                    new_shape = 4
                elif shape == 4:
                    new_shape = 5
                elif shape == 5:
                    new_shape = 6
                elif shape == 6:
                    new_shape = 3
                else:
                    new_shape = shape
                rotate.append((new_x, new_y, new_shape, color))
            self.symbol = rotate
            self.define_dimension()
            self.draw_symbol()

    def rotate_r_cells(self):
        if hasattr(self, 'symbol') and len(self.symbol) > 0:
            max_x = max(cell[0] for cell in self.symbol)
            min_x = min(cell[0] for cell in self.symbol)
            min_y = min(cell[1] for cell in self.symbol)
            rotate = []
            for cell in self.symbol:
                x, y, shape, color = cell
                new_x = max_x - y + min_y
                new_y = x - min_x
                # Inverser les shapes des triangles
                if shape == 3:
                    new_shape = 6
                elif shape == 4:
                    new_shape = 3
                elif shape == 5:
                    new_shape = 4
                elif shape == 6:
                    new_shape = 5
                else:
                    new_shape = shape
                rotate.append((new_x, new_y, new_shape, color))
            self.symbol = rotate
            self.define_dimension()
            self.draw_symbol()

    def inverse_colors(self):
        if hasattr(self, 'symbol') and len(self.symbol) > 0:
            invert_cells = []
            for cell in self.symbol:
                column, row, shape, color_indice = cell
                inv_shape, inv_color_indice = self.inverse_cell(shape, color_indice)
                invert_cells.append((column, row, inv_shape, inv_color_indice))
            self.symbol = invert_cells
            self.draw_symbol()

    def inverse_cell(self, shape, color_indice):
        new_color_indice = color_indice
        new_shape = shape
        if shape < 2:
            if color_indice == 0:
                new_color_indice = 5
                new_shape = 1
            if color_indice == 5:
                new_color_indice = 0
                new_shape = 0
        elif shape == 3:
            new_shape = 5
        elif shape == 4:
            new_shape = 6
        elif shape == 5:
            new_shape = 3
        elif shape == 6:
            new_shape = 4
        return new_shape, new_color_indice


if __name__ == '__main__':
    Myclass = Cells()
    Myclass.load_symbol('sym/symbol009.sym')
    #Myclass.image.show()
    Myclass2 = Cells()
    Myclass2.insert_symbol(Myclass.symbol)
    Myclass2.inverse_colors()
    Myclass2.symbol_image.show()
