import argparse
from PIL import Image
import numpy as np
import math
import os
from scipy.ndimage import center_of_mass
from bid2ascii import bid_2_ascii
from bid2img import bid_2_img
from img2ascii import decode_image_ascii


def classify_cell(cell_image, threshold=128, triangle_ratio=0.2):
    """Classifie une cellule en tant que carré blanc, carré noir ou triangle."""
    pixels = np.array(cell_image)
    h, w = pixels.shape

    # Calcul de la couleur moyenne des pixels de la cellule
    avg_color = np.mean(pixels)

    # On utilise un seuil fixe
    if avg_color > threshold:
        return 0  # Carré blanc
    
    black_pixels = pixels < threshold

    # On calcule le ratio de pixels noirs dans l'image
    black_ratio = np.sum(black_pixels) / (h * w)

    if black_ratio > 1 - triangle_ratio:
        return 1  # Carré noir

    if black_ratio < triangle_ratio:
        return 0  # Carré blanc
    
    # Calcule le centre de masse des pixels noirs
    center = center_of_mass(black_pixels)
    
    if np.isnan(center).any():
        return 2
    
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
    
    return 2


def img_2_bid(image_path, grid_width=40, grid_height=40, bool_no_save=True, bool_no_save_ascii=True, triangle_ratio=0.2, threshold=128):
    """Traite l'image, la divise en grille et la classifie."""
    image = Image.open(image_path).convert('L')
    
    width, height = image.size
    cell_width = math.floor(width / grid_width)
    cell_height = math.floor(height / grid_height)
    grid_codes = np.zeros((grid_height, grid_width), dtype=int)

    for row in range(grid_height):
        for col in range(grid_width):
            left = col * cell_width
            top = row * cell_height
            right = (col + 1) * cell_width
            bottom = (row + 1) * cell_height
            
            cell = image.crop((left, top, right, bottom))
            code = classify_cell(cell, threshold, triangle_ratio)
            grid_codes[row, col] = code

            # Affichage de la cellule et de son code
            #decode_img_ascii(cell)

    if grid_codes is not None:
        if not bool_no_save:
            filename_bid = os.path.splitext(os.path.basename(image_path))[0] + '.bid'
            path_bid = os.path.join('bid', filename_bid)
            output_lines = []
            for row in grid_codes:
                row_str = ""
                for code in row:
                    row_str += str(code)
                output_lines.append(row_str)
            with open(path_bid, 'w') as f:
                for row in output_lines:
                    f.write(row + '\n')
            bid_2_img(path_bid=path_bid, image_scale=50, bool_no_save=bool_no_save, bool_no_display_image=False)
            bid_2_ascii(path_bid=path_bid, model_ascii=1, bool_no_save=bool_no_save_ascii)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Image to bid')
    parser.add_argument('--path_image', action="store", dest='path_image', default='chevalier.png')
    parser.add_argument('--grid_width', action="store", dest='grid_width', type=int, default=1)
    parser.add_argument('--grid_height', action="store", dest='grid_height', type=int, default=1)
    parser.add_argument('--no_save_bid', action="store_true", dest='no_save_bid')
    parser.add_argument('--no_save_ascii', action="store_true", dest='no_save_ascii')
    parser.add_argument('--triangle_ratio', action="store", dest='triangle_ratio', type=float, default=0.30)
    args = parser.parse_args()
    threshold = 128
    img_2_bid(args.path_image, args.grid_width, args.grid_height, args.no_save_bid, args.no_save_ascii, args.triangle_ratio, threshold)

