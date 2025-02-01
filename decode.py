import argparse
from PIL import Image, ImageDraw
import os

def draw_cellule(draw, x, y, cell_type, image_size):
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

    file_model_extension = (os.path.splitext(file_model))[1]
    file_bid = file_model.replace(file_model_extension, '.png')
    image.save(file_bid)
    if display_image:
        image.show()

def decode_bidfile_ascii(file_model, model_ascii):
    with open(file_model) as text_file:
        lines = text_file.readlines()
    if model_ascii == 1:
        chart_ascii="  "
    elif model_ascii == 2:
        chart_ascii=" "
    print('┌' + '─' * (len(lines[0]) + 1) + '┐')
    for line in lines:
        print('│ ', end="")
        for car in line:
            if car != "\n":
                print(chart_ascii, end="")
        print(' │')
    print('└' + '─' * (len(lines[0]) + 1) + '┘')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='path image')
    parser.add_argument('--path_file', action="store", dest='path_file')
    args = parser.parse_args()
    path_file = args.path_file
    decode_bidfile_image(path_file)
