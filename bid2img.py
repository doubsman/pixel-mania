import argparse
from PIL import Image, ImageDraw
import os
from img2ascii import img_2_ascii


def draw_cellule(draw, x, y, cell_type, image_scale):
    """Dessine une cellule en fonction de son type."""
    left = x * image_scale
    top = y * image_scale
    right = (x + 1) * image_scale
    bottom = (y + 1) * image_scale

    if image_scale == 1:
        # 1 cellule = 1 pixel
        if cell_type == 0:  # carré blanc
            draw.point((x, y), fill=(255, 255, 255))
        elif cell_type == 1:  # carré noir
            draw.point((x, y), fill=(0, 0, 0))
        elif cell_type == 3:  # triangle en bas à droite
            draw.point((x, y), fill=(0, 0, 0))
        elif cell_type == 4:  # triangle en haut à droite
            draw.point((x, y), fill=(0, 0, 0))
        elif cell_type == 5:  # triangle en haut à gauche
            draw.point((x, y), fill=(0, 0, 0))
        elif cell_type == 6:  # triangle en bas à gauche
            draw.point((x, y), fill=(0, 0, 0))
    else:
        # Cas général pour image_scale > 1
        if cell_type == 0:  # carré blanc
            draw.rectangle([(left, top), (right, bottom)], fill=(255, 255, 255), outline=(0, 0, 0))
        elif cell_type == 1:  # carré noir
            draw.rectangle([(left, top), (right, bottom)], fill=(0, 0, 0), outline=(0, 0, 0))
        elif cell_type == 3:  # triangle en bas à droite
            draw.polygon([(left, bottom), (right, bottom), (right, top)], fill=(0, 0, 0))
        elif cell_type == 4:  # triangle en haut à droite
            draw.polygon([(left, top), (right, top), (right, bottom)], fill=(0, 0, 0))
        elif cell_type == 5:  # triangle en haut à gauche
            draw.polygon([(left, top), (right, top), (left, bottom)], fill=(0, 0, 0))
        elif cell_type == 6:  # triangle en bas à gauche
            draw.polygon([(left, bottom), (left, top), (right, bottom)], fill=(0, 0, 0))


def bid_2_img(path_bid, image_scale=50, bool_no_save=True, bool_no_display_image=True):
    """Convertit un fichier BID en image."""
    with open(path_bid, 'r') as text_file:
        data = text_file.read().splitlines()
    grid = [[int(cell) for cell in row] for row in data]

    image_width = len(data[0]) * image_scale
    image_height = len(data) * image_scale

    image = Image.new('RGB', (image_width, image_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    for y in range(len(grid)):
        for x in range(len(grid[y])):
            cell = grid[y][x]
            draw_cellule(draw, x, y, cell, image_scale)

    if not bool_no_save:
        filename_img = os.path.splitext(os.path.basename(path_bid))[0]
        filename_img += f'_{int(image_width/image_scale)}x{int(image_height/image_scale)}.png'
        file_img = os.path.join('export', filename_img)
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
