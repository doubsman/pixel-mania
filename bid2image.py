import argparse
from PIL import Image, ImageDraw
import os
from bid2ascii import decode_bidfile_ascii


def draw_cellule(draw, x, y, cell_type, image_size):
    if image_size == 1:
        # Dessiner les formes différemment lorsque image_size est égal à 1
        if cell_type == 0:  # carré blanc
            draw.point((x, y), fill=(255, 255, 255))
        elif cell_type == 1:  # carré noir
            draw.point((x, y), fill=(0, 0, 0))
        elif cell_type == 3:  # triangle en bas à droite
            draw.point((x, y+1), fill=(0, 0, 0))
        elif cell_type == 4:  # triangle en haut à droite
            draw.point((x+1, y), fill=(0, 0, 0))
        elif cell_type == 5:  # triangle en haut à gauche
            draw.point((x, y), fill=(0, 0, 0))
        elif cell_type == 6:  # triangle en bas à gauche
            draw.point((x, y+1), fill=(0, 0, 0))
    else:
        if cell_type == 0:  # carré blanc
            draw.rectangle((x*image_size, y*image_size, (x+1)*image_size, (y+1)*image_size), fill=(255, 255, 255), outline=(0, 0, 0))
        elif cell_type == 1:  # carré noir
            draw.rectangle((x*image_size, y*image_size, (x+1)*image_size, (y+1)*image_size), fill=(0, 0, 0), outline=(0, 0, 0))
        elif cell_type == 3:  # triangle en bas à droite
            draw.polygon([(x*image_size, (y+1)*image_size), ((x+1)*image_size, (y+1)*image_size), ((x+1)*image_size, y*image_size)], fill=(0, 0, 0))
        elif cell_type == 4:  # triangle en haut à droite
            draw.polygon([(x*image_size, y*image_size), ((x+1)*image_size, y*image_size), ((x+1)*image_size, (y+1)*image_size)], fill=(0, 0, 0))
        elif cell_type == 5:  # triangle en haut à gauche
            draw.polygon([(x*image_size, y*image_size), ((x+1)*image_size, y*image_size), (x*image_size, (y+1)*image_size)], fill=(0, 0, 0))
        elif cell_type == 6:  # triangle en bas à gauche
            draw.polygon([(x*image_size, (y+1)*image_size), (x*image_size, y*image_size), ((x+1)*image_size, (y+1)*image_size)], fill=(0, 0, 0))


def decode_bidfile_image(file_model, image_scale=100, model_ascii=1, display_image=True):
    with open(file_model, 'r') as text_file:
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

    filename_img = os.path.splitext(os.path.basename(file_model))[0]
    filename_img += f'_{image_width}x{image_height}.png'
    file_img = os.path.join('export', filename_img)
    image.save(file_img)
    if display_image:
        decode_bidfile_ascii(file_model, model_ascii)
        image.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='path image')
    parser.add_argument('--path_file', action="store", dest='path_file')
    parser.add_argument('--image_scale', action="store", dest='image_scale', default=100)
    parser.add_argument('--model_ascii', action="store", dest='model_ascii', default=1)
    args = parser.parse_args()
    path_file = args.path_file
    image_scale = int(args.image_scale)
    model_ascii = int(args.model_ascii)
    decode_bidfile_image(path_file, image_scale, model_ascii)
