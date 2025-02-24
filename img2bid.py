import argparse
from PIL import Image
import numpy as np
import math
import os
from scipy.ndimage import center_of_mass
from bid2ascii import bid_2_ascii
from bid2img import bid_2_img
from img2ascii import decode_image_ascii


GRAY_SCALE = {
    0: (255, 255, 255),  # Blanc
    1: (220, 220, 220),  # Gris très clair
    2: (192, 192, 192),  # Gris clair
    3: (128, 128, 128),  # Gris foncé
    4: (92, 92, 92),     # Gris très foncé
    5: (0, 0, 0)         # Noir
}

CHARTS_ASCII = {
    1: ['▩ ', '  ', 'X ', '◤ ', '◣ ', '◢ ', '◥ '],
    2: ['▉',' ','X','▛','▙','▟','▜'],
    3: ['▉▉','  ','XX','▛▘','▙▖','▗▟','▝▜'],
    4: ['0 ','1 ','2 ','3 ','4 ','5 ','6 ']
}


def classify_shape(cell_image, threshold=128, triangle_ratio=0.2):
    """Classifie une cellule en tant que carré ou triangle."""
    pixels = np.array(cell_image)
    h, w = pixels.shape

    black_pixels = pixels < threshold
    black_ratio = np.sum(black_pixels) / (h * w)

    if black_ratio > 1 - triangle_ratio:
        return 1  # Carré noir

    if black_ratio < triangle_ratio:
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


def classify_color(image, tolerance=5):
    """Classifie la couleur d'une cellule en tant que blanc, gris très clair, gris clair, gris foncé, gris très foncé ou noir."""
    pixels = np.array(image)
    non_white_pixels = pixels[pixels < 255]

    if non_white_pixels.size > 0:
        avg_color = np.mean(non_white_pixels)
    else:
        avg_color = 255  # Si tous les pixels sont blancs

    if avg_color > 240 - tolerance:
        return 0  # Blanc
    elif avg_color > 185 - tolerance:
        return 1  # Gris très clair
    elif avg_color > 121 - tolerance:
        return 2  # Gris clair
    elif avg_color > 57 - tolerance:
        return 3  # Gris foncé
    elif avg_color > 16 - tolerance:
        return 4  # Gris très foncé
    else:
        return 5  # Noir
    

def img_2_bid(path_image, grid_width=10, grid_height=10, triangle_ratio=0.2, threshold=128, display_cells=False, display_cells_scale_reduce=10, no_save_bid=True, model_ascii=1, no_save_ascii=True):
    """Traite l'image, la divise en grille et la classifie."""
    image = Image.open(path_image).convert('L')
    width, height = image.size
    cell_width = math.floor(width / grid_width)
    cell_height = math.floor(height / grid_height)
    shape_codes = np.zeros((grid_height, grid_width), dtype=int)
    color_codes = np.zeros((grid_height, grid_width), dtype=int)
    ascii_codes = np.zeros((grid_height, grid_width), dtype='<U2')
    chart_ascii = CHARTS_ASCII[model_ascii]

    for row in range(grid_height):
        if display_cells:
            cells_out_lines = [''] * (math.floor(cell_height / display_cells_scale_reduce) + 2)
            
        for col in range(grid_width):
            left = col * cell_width
            top = row * cell_height
            right = (col + 1) * cell_width
            bottom = (row + 1) * cell_height

            cell = image.crop((left, top, right, bottom))
            color_code = classify_color(cell)
            shape_code = classify_shape(cell, threshold, triangle_ratio)
            if shape_code == 0 and color_code == 5:
                color_code = 0
            shape_codes[row, col] = shape_code
            color_codes[row, col] = color_code
            ascii_codes[row, col] = chart_ascii[shape_code]

            if display_cells:
                charts_ascii = "▩⬚X◤◣◢◥"
                image_display = image.crop((left, top, right, bottom))
                image_display = image_display.resize(
                    (math.floor(cell_width / display_cells_scale_reduce),
                     math.floor(cell_height / display_cells_scale_reduce)),
                    Image.Resampling.BICUBIC)
                decode_image_ascii(image_display, cells_out_lines)
                cells_out_lines[0] = cells_out_lines[0].replace('┌─────────',
                                                    f'┌ {row:02d},{col:02d} {charts_ascii[shape_code]} ')
        if display_cells:
            print('\n'.join(cells_out_lines))

    if shape_codes is not None and not no_save_ascii:
        filename_asc = os.path.splitext(os.path.basename(path_image))[0] + '.ascii'
        path_asc = os.path.join('wrk', filename_asc)
        np.savetxt(path_asc, ascii_codes, fmt='%s', delimiter="", encoding='utf-8')

    if shape_codes is not None and not no_save_bid:
        filename_bid = os.path.splitext(os.path.basename(path_image))[0] + '.bid'
        path_bid = os.path.join('wrk', filename_bid)
        np.savetxt(path_bid, shape_codes, fmt='%i', delimiter="")
        
        filename_col = os.path.splitext(os.path.basename(path_image))[0] + '.color'
        path_col = os.path.join('wrk', filename_col)
        np.savetxt(path_col, color_codes, fmt='%i', delimiter="")

        bid_2_img(path_bid=path_bid, image_scale=50, bool_no_save=no_save_bid, bool_no_display_image=False)
        find_shape = np.where(shape_codes > 1)
        model_ascii = 3 if find_shape[0].size == 0 else 1
        bid_2_ascii(path_bid=path_bid, model_ascii=model_ascii)


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
    img_2_bid(path_image=args.path_image,
              grid_width=args.grid_width,
              grid_height=args.grid_height,
              triangle_ratio=args.triangle_ratio,
              threshold=args.threshold,
              display_cells=args.display_cells,
              display_cells_scale_reduce=args.display_cells_scale_reduce,
              no_save_bid=args.no_save_bid,
              model_ascii=args.model_ascii,
              no_save_ascii=args.no_save_ascii)
