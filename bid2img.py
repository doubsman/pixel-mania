import argparse
from PIL import Image, ImageDraw
import os
from img2ascii import img_2_ascii
import numpy as np


GRAY_SCALE_DRAW = {
    0: (255, 255, 255),  # Blanc
    1: (192, 192, 192),  # Gris très clair
    2: (128, 128, 128),  # Gris clair
    3: (64, 64, 64),     # Gris foncé
    4: (32, 32, 32),     # Gris très foncé
    5: (0, 0, 0)         # Noir
}


def draw_cellule(draw, x, y, cell_type, cell_color, image_scale):
    """Dessine une cellule en fonction de son type."""
    left = x * image_scale
    top = y * image_scale
    right = (x + 1) * image_scale
    bottom = (y + 1) * image_scale

    if image_scale == 1:
        # 1 cellule = 1 pixel
        draw.point((x, y), fill=cell_color)
    else:
        #draw.rectangle([(left, top), (right, bottom)], fill=(255, 255, 255), outline=(0, 0, 0))
        if cell_type == 1:  # carré noir
            draw.rectangle([(left, top), (right, bottom)], fill=cell_color, outline=(0, 0, 0))
        elif cell_type == 3:  # triangle en bas à droite
            draw.polygon([(left, bottom), (right, bottom), (right, top)], fill=cell_color)
        elif cell_type == 4:  # triangle en haut à droite
            draw.polygon([(left, top), (right, top), (right, bottom)], fill=cell_color)
        elif cell_type == 5:  # triangle en haut à gauche
            draw.polygon([(left, top), (right, top), (left, bottom)], fill=cell_color)
        elif cell_type == 6:  # triangle en bas à gauche
            draw.polygon([(left, bottom), (left, top), (right, bottom)], fill=cell_color)


def bid_2_img(path_bid, image_scale=50, bool_no_save=True, bool_no_display_image=True):
    """Convertit un fichier BID en image."""
    # shape
    grid_bid = np.loadtxt(path_bid, dtype=str)
    try:
        bid_width = len(str(grid_bid[0])) 
        bid_height = grid_bid.size
    except:
        # one line
        bid_width = len(str(grid_bid))
        bid_height = 1
        tmp_shapes = np.zeros((bid_height), dtype=f'<U{bid_width}')
        tmp_shapes[0] = grid_bid
        grid_bid = tmp_shapes

    # colors
    path_color = path_bid.replace('.bid','.color')
    bool_color = os.path.isfile(path_color)
    if bool_color:
        grid_colors = np.loadtxt(path_color, dtype=str)

    # image
    image = Image.new('RGB', (bid_width * image_scale, bid_height * image_scale), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    for row in range(bid_height):
        for column in range(bid_width):
            cell = int(grid_bid[row][column])
            if bool_color:
                color_indice = int(grid_colors[row][column])
            else:
                color_indice = 0 if cell == 0 else 5
            color = GRAY_SCALE_DRAW[color_indice]
            draw_cellule(draw, column, row, cell, color, image_scale)

    if not bool_no_save:
        filename_img = os.path.splitext(os.path.basename(path_bid))[0]
        filename_img += f'_{bid_width}x{bid_height}.png'
        file_img = os.path.join('wrk', filename_img)
        image.save(file_img)
        if not bool_no_display_image:
            img_2_ascii(file_img, scale=(1/image_scale)*3)
            image.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='bid to image png')
    parser.add_argument('--path_bid', action="store", dest='path_bid')
    parser.add_argument('--image_scale', action="store", dest='image_scale', type=int, default=50)
    parser.add_argument('--no_save', action="store_true", dest='no_save')
    parser.add_argument('--no_display_image', action="store_true", dest='no_display_image')
    args = parser.parse_args()
    bid_2_img(args.path_bid, args.image_scale, args.no_save, args.no_display_image)
