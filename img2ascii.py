import argparse
from PIL import Image
import math
import numpy as np


def img_2_ascii(image_path, grid_width=1, grid_height=1):
    image = Image.open(image_path).convert('L')
    width, height = image.size
    cell_width = math.floor(width / grid_width)
    cell_height = math.floor(height / grid_height)
    
    for row in range(grid_height):
        for col in range(grid_width):
            left = col * cell_width
            top = row * cell_height
            right = (col + 1) * cell_width
            bottom = (row + 1) * cell_height
            cell = image.crop((left, top, right, bottom))

    decode_image_ascii(cell)
            

def decode_image_ascii(image, width_cellule=2, output_lines = []):
    img = image
    img = img.convert("RGB")

    width, height = img.size
    
    print('┌' + '─' * ((width * width_cellule)+2) + '┐')
    for y in range(height):
        ascii_art = ''
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            ansi_color = f"\033[38;2;{r};{g};{b}m"
            ascii_art += f"{ansi_color}" +"▉" * width_cellule
        ascii_art += "\033[0m"
        print(f'│ {ascii_art} │')
        if len(output_lines) >= height:
            output_lines[x] += ascii_art
        output_lines.append(ascii_art)
    print('└' + '─' * ((width * width_cellule)+2) + '┘')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='path image')
    parser.add_argument('--path_file', action="store", dest='path_file')
    parser.add_argument('--width_result', action="store", dest='width_result',default=1)
    parser.add_argument('--height_result', action="store", dest='height_result',default=1)    
    args = parser.parse_args()
    path_file = args.path_file
    width_result = int(args.width_result)
    height_result = int(args.height_result)
    img_2_ascii(path_file, width_result, height_result)