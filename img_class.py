import argparse
from PIL import Image
import numpy as np
import math
import os
from scipy.ndimage import center_of_mass

class ImageProcessor:
    def __init__(self, path_image, grid_width=10, grid_height=10, triangle_ratio=0.2, threshold=128, display_cells=False, display_cells_scale_reduce=10, no_save_bid=True, model_ascii=1, no_save_ascii=True):
        self.path_image = path_image
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.triangle_ratio = triangle_ratio
        self.threshold = threshold
        self.display_cells = display_cells
        self.display_cells_scale_reduce = display_cells_scale_reduce
        self.no_save_bid = no_save_bid
        self.model_ascii = model_ascii
        self.no_save_ascii = no_save_ascii

        self.GRAY_SCALE = {
            0: (255, 255, 255),  # Blanc
            1: (220, 220, 220),  # Gris très clair
            2: (192, 192, 192),  # Gris clair
            3: (128, 128, 128),  # Gris foncé
            4: (92, 92, 92),     # Gris très foncé
            5: (0, 0, 0)         # Noir
        }

        self.CHARTS_ASCII = {
            1: ['▩ ', '  ', 'X ', '◤ ', '◣ ', '◢ ', '◥ '],
            2: ['▉',' ','X','▛','▙','▟','▜'],
            3: ['▉▉','  ','XX','▛▘','▙▖','▗▟','▝▜'],
            4: ['0 ','1 ','2 ','3 ','4 ','5 ','6 ']
        }

    def classify_shape(self, cell_image):
        """Classifie une cellule en tant que carré ou triangle."""
        pixels = np.array(cell_image)
        h, w = pixels.shape

        black_pixels = pixels < self.threshold
        black_ratio = np.sum(black_pixels) / (h * w)

        if black_ratio > 1 - self.triangle_ratio:
            return 1  # Carré noir

        if black_ratio < self.triangle_ratio:
            return 0  # Carré blanc

        # Calcule le centre de masse des pixels noirs
        center = center_of_mass(black_pixels)

        if np.isnan(center).any():
            return 0  # Carré blanc par défaut

        center_x = center[1]
        center_y = center[0]

        # Vérification de la position du centre de masse pour déterminer la direction du triangle
        if center_x < w / 2 and center_y < h / 2:
            return 5  # Triangle en haut à gauche
        elif center_x > w / 2 and center_y < h / 2:
            return 4  # Triangle en haut à droite
        elif center_x < w / 2 and center_y > h / 2:
            return 6  # Triangle en bas à gauche
        elif center_x > w / 2 and center_y > h / 2:
            return 3  # Triangle en bas à droite

        return 2  # Carré X

    def classify_color(self, image):
        """Classifie la couleur d'une cellule en tant que blanc, gris très clair, gris clair, gris foncé, gris très foncé ou noir."""
        pixels = np.array(image)
        non_white_pixels = pixels[pixels < 255]

        if non_white_pixels.size > 0:
            avg_color = np.mean(non_white_pixels)
        else:
            avg_color = 255  # Si tous les pixels sont blancs

        if avg_color > 240 - 5:
            return 0  # Blanc
        elif avg_color > 185 - 5:
            return 1  # Gris très clair
        elif avg_color > 121 - 5:
            return 2  # Gris clair
        elif avg_color > 57 - 5:
            return 3  # Gris foncé
        elif avg_color > 16 - 5:
            return 4  # Gris très foncé
        else:
            return 5  # Noir

    def process_image(self):
        """Traite l'image, la divise en grille et la classifie."""
        image = Image.open(self.path_image).convert('L')
        width, height = image.size
        cell_width = math.floor(width / self.grid_width)
        cell_height = math.floor(height / self.grid_height)
        shape_codes = np.zeros((self.grid_height, self.grid_width), dtype=int)
        color_codes = np.zeros((self.grid_height, self.grid_width), dtype=int)
        ascii_codes = np.zeros((self.grid_height, self.grid_width), dtype='<U2')
        chart_ascii = self.CHARTS_ASCII[self.model_ascii]

        for row in range(self.grid_height):
            if self.display_cells:
                cells_out_lines = [''] * (math.floor(cell_height / self.display_cells_scale_reduce) + 2)
                
            for col in range(self.grid_width):
                left = col * cell_width
                top = row * cell_height
                right = (col + 1) * cell_width
                bottom = (row + 1) * cell_height

                cell = image.crop((left, top, right, bottom))
                color_code = self.classify_color(cell)
                shape_code = self.classify_shape(cell)
                shape_codes[row, col] = shape_code
                color_codes[row, col] = color_code
                ascii_codes[row, col] = chart_ascii[shape_code]

                if self.display_cells:
                    charts_ascii = "▩⬚X◤◣◢◥"
                    image_display = image.crop((left, top, right, bottom))
                    image_display = image_display.resize(
                        (math.floor(cell_width / self.display_cells_scale_reduce),
                         math.floor(cell_height / self.display_cells_scale_reduce)),
                        Image.Resampling.BICUBIC)
                    # Ici, vous devriez appeler la fonction decode_image_ascii
                    # mais elle n'est pas définie dans le code que vous avez fourni
                    # cells_out_lines = decode_image_ascii(image_display, cells_out_lines)
            if self.display_cells:
                print('\n'.join(cells_out_lines))

        if shape_codes is not None and not self.no_save_ascii:
            filename_asc = os.path.splitext(os.path.basename(self.path_image))[0] + '.ascii'
            path_asc = os.path.join('wrk', filename_asc)
            np.savetxt(path_asc, ascii_codes, fmt='%s', delimiter="", encoding='utf-8')

        if shape_codes is not None and not self.no_save_bid:
            filename_bid = os.path.splitext(os.path.basename(self.path_image))[0] + '.bid'
            path_bid = os.path.join('wrk', filename_bid)
            np.savetxt(path_bid, shape_codes, fmt='%i', delimiter="")
            
            filename_col = os.path.splitext(os.path.basename(self.path_image))[0] + '.color'
            path_col = os.path.join('wrk', filename_col)
            np.savetxt(path_col, color_codes, fmt='%i', delimiter="")

    def run(self):
        """Lance le traitement de l'image."""
        self.process_image()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Image to bid')
    parser.add_argument('--path_image', action="store", dest='path_image', default='chevalier.png')
    parser.add_argument('--grid_width', action="store", dest='grid_width', type=int, default=48)
    parser.add_argument('--grid_height', action="store", dest='grid_height', type=int, default=48)
    parser.add_argument('--triangle_ratio', action="store", dest='triangle_ratio', type=float, default=0.30)
    parser.add_argument('--threshold', action="store", dest='threshold', type=int, default=128)
    parser.add_argument('--display_cells', action="store_true", dest='display_cells')
    parser.add_argument('--display_cells_scale_reduce', action="store", dest='display_cells_scale_reduce', type=int, default=10)
    parser.add_argument('--no_save_bid', action="store_true", dest='no_save_bid')
    parser.add_argument('--model_ascii', action="store", dest='model_ascii', type=int, default=1)
    parser.add_argument('--no_save_ascii', action="store_true", dest='no_save_ascii')
    args = parser.parse_args()
    processor = ImageProcessor(args.path_image, args.grid_width, args.grid_height, args.triangle_ratio, args.threshold, args.display_cells, args.display_cells_scale_reduce, args.no_save_bid, args.model_ascii, args.no_save_ascii)
    processor.run()
