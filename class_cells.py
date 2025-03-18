import os
import numpy as np
from PIL import Image, ImageDraw


GRAY_SCALE_DRAW = {
    0: (255, 255, 255),  # Blanc
    1: (227, 227, 227),  # Gris très clair
    2: (192, 192, 192),  # Gris clair
    3: (128, 128, 128),  # Gris foncé
    4: (64, 64, 64),     # Gris très foncé
    5: (0, 0, 0)         # Noir
}

class Cells:
    def __init__(self):
        self.symbol = None
        self.symbol_path = None
        self.symbol_width = 0
        self.symbol_height = 0
        self.image_scale = 20
        self._last_scale = None  # Pour suivre la dernière échelle utilisée
        self.symbol_image = None
        self.draw = None
        self.min_x = self.min_y = self.max_x = self.max_y = 0

    def get_color(self, color_index):
        """Get the RGB color for a given color index"""
        return GRAY_SCALE_DRAW.get(color_index, (255, 255, 255))  # Default to white if index not found

    def define_dimension(self):
        self.min_x = min([cell[0] for cell in self.symbol])
        self.min_y = min([cell[1] for cell in self.symbol])
        self.max_x = max([cell[0] for cell in self.symbol])
        self.max_y = max([cell[1] for cell in self.symbol])
        self.symbol_width = (self.max_x - self.min_x + 1)
        self.symbol_height = (self.max_y - self.min_y + 1)
    
    def define_scale(self, image_with, image_height, grid_width, grid_height):
        image_grid_width = grid_width * self.image_scale
        image_grid_height = grid_height * self.image_scale
        if image_grid_width >= image_grid_height:
            self.image_scale = int(image_with / float(grid_width))
        else:
            self.image_scale = int(image_height / float(grid_height))
    
    def insert_symbol(self, array_symbol):
        self.symbol_path = None
        self.symbol = array_symbol
        if hasattr(self, 'symbol') and len(self.symbol) > 0:
            self.draw_cells(force_redraw=True)

    def load_symbol(self, symbol_path):
        if os.path.isfile(symbol_path):
            self.symbol_path = symbol_path
            self.symbol = np.loadtxt(self.symbol_path, dtype=int, delimiter=";")
            self.draw_cells(force_redraw=True)
        return self.symbol

    def save_symbol(self, symbol_path):
        np.savetxt(symbol_path, self.symbol, fmt='%i', delimiter=";")

    def draw_cell(self, x, y, cell_type, cell_color, bool_outline=False, alpha=255):
        """Draw a cell according to its type."""
        left = x * self.image_scale
        top = y * self.image_scale
        right = (x + 1) * self.image_scale
        bottom = (y + 1) * self.image_scale
        color = GRAY_SCALE_DRAW[cell_color]
        color_with_alpha = color + (alpha,)  # Ajouter le canal alpha à la couleur

        if self.image_scale == 1:
            # 1 cellule = 1 pixel
            self.draw.point((x, y), fill=color_with_alpha)
        else:
            if bool_outline:
                self.draw.rectangle([(left, top), (right, bottom)], 
                                  fill=(255, 255, 255, alpha), 
                                  outline=(0, 0, 0, alpha))
            else:
                self.draw.rectangle([(left, top), (right, bottom)], 
                                  fill=(255, 255, 255, alpha))
            if cell_type == 1:  # carré plein
                self.draw.rectangle([(left, top), (right, bottom)], 
                                  fill=color_with_alpha)
            elif cell_type == 3:  # triangle en bas à droite
                self.draw.polygon([(left, bottom), (right, bottom), (right, top)], 
                                fill=color_with_alpha)
            elif cell_type == 4:  # triangle en haut à droite
                self.draw.polygon([(left, top), (right, top), (right, bottom)], 
                                fill=color_with_alpha)
            elif cell_type == 5:  # triangle en haut à gauche
                self.draw.polygon([(left, top), (right, top), (left, bottom)], 
                                fill=color_with_alpha)
            elif cell_type == 6:  # triangle en bas à gauche
                self.draw.polygon([(left, bottom), (left, top), (right, bottom)], 
                                fill=color_with_alpha)

    def draw_cells(self, force_redraw=False):
        """Draw cells only if necessary (scale changed or force_redraw is True)"""
        if self._last_scale != self.image_scale or force_redraw:
            self.define_dimension()
            width = (self.symbol_width) * self.image_scale
            height = (self.symbol_height) * self.image_scale
            # Créer une image RGBA pour supporter la transparence
            self.symbol_image = Image.new('RGBA', (width, height), (255, 255, 255, 0))  # Fond transparent
            self.draw = ImageDraw.Draw(self.symbol_image)

            # Créer un dictionnaire des cellules sélectionnées pour une recherche plus rapide
            selected_cells = {(cell[0], cell[1]): True for cell in self.symbol}

            # Dessiner toutes les cellules
            for y in range(height // self.image_scale):
                for x in range(width // self.image_scale):
                    # Position absolue de la cellule
                    abs_x = x + self.min_x
                    abs_y = y + self.min_y
                    
                    # Vérifier si la cellule est sélectionnée
                    if (abs_x, abs_y) in selected_cells:
                        # Trouver les propriétés de la cellule
                        for cell in self.symbol:
                            if cell[0] == abs_x and cell[1] == abs_y:
                                self.draw_cell(x, y, cell[2], cell[3], alpha=255)  # Cellule opaque
                                break
                    else:
                        # Cellule non sélectionnée - complètement transparente
                        self.draw_cell(x, y, 0, 0, alpha=0)
            
            self._last_scale = self.image_scale

    def flipv_cells(self):
        if hasattr(self, 'symbol') and len(self.symbol) > 0:
            max_y = max(cell[1] for cell in self.symbol)
            min_y = min(cell[1] for cell in self.symbol)
            flips = []
            for cell in self.symbol:
                x, y, shape, color = cell
                new_y = max_y + min_y - y
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
            self.draw_cells(force_redraw=True)
            return self.symbol

    def fliph_cells(self):
        if hasattr(self, 'symbol') and len(self.symbol) > 0:
            max_x = max(cell[0] for cell in self.symbol)
            min_x = min(cell[0] for cell in self.symbol)
            flips = []
            for cell in self.symbol:
                x, y, shape, color = cell
                new_x = max_x + min_x - x
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
            self.draw_cells(force_redraw=True)
            return self.symbol

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
            self.draw_cells(force_redraw=True)
            return self.symbol

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
            self.draw_cells(force_redraw=True)
            return self.symbol

    def inverse_colors(self):
        if hasattr(self, 'symbol') and len(self.symbol) > 0:
            invert_cells = []
            for cell in self.symbol:
                column, row, shape, color_indice = cell
                inv_shape, inv_color_indice = self.inverse_cell(shape, color_indice)
                invert_cells.append((column, row, inv_shape, inv_color_indice))
            self.symbol = invert_cells
            self.draw_cells(force_redraw=True)
            return self.symbol

    def inverse_cell(self, shape, color_indice):
        new_color_indice = color_indice
        new_shape = shape
        
        # Inversion des couleurs en passant par les gris
        if color_indice == 0:  # Blanc -> Noir
            new_color_indice = 5
        elif color_indice == 1:  # Gris très clair -> Gris très foncé
            new_color_indice = 4
        elif color_indice == 2:  # Gris clair -> Gris foncé
            new_color_indice = 3
        elif color_indice == 3:  # Gris foncé -> Gris clair
            new_color_indice = 2
        elif color_indice == 4:  # Gris très foncé -> Gris très clair
            new_color_indice = 1
        elif color_indice == 5:  # Noir -> Blanc
            new_color_indice = 0
            
        # Inversion des formes
        if shape < 2:
            if color_indice == 0:
                new_shape = 1
                new_color_indice = 5  # Blanc -> Noir
            if color_indice == 5:
                new_shape = 0
                new_color_indice = 0  # Noir -> Blanc
        elif shape == 3:  # triangle en bas à droite -> triangle en haut à gauche
            new_shape = 5
            new_color_indice = 5  # Garde la couleur noire
        elif shape == 4:  # triangle en haut à droite -> triangle en bas à gauche
            new_shape = 6
            new_color_indice = 5  # Garde la couleur noire
        elif shape == 5:  # triangle en haut à gauche -> triangle en bas à droite
            new_shape = 3
            new_color_indice = 5  # Garde la couleur noire
        elif shape == 6:  # triangle en bas à gauche -> triangle en haut à droite
            new_shape = 4
            new_color_indice = 5  # Garde la couleur noire
            
        return new_shape, new_color_indice


if __name__ == '__main__':
    Myclass = Cells()
    Myclass.load_symbol('sym/symbol009.sym')
    #Myclass.image.show()
    Myclass2 = Cells()
    Myclass2.insert_symbol(Myclass.symbol)
    Myclass2.inverse_colors()
    Myclass2.symbol_image.show()
