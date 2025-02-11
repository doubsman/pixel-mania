import argparse
from PIL import Image


def img_2_ascii(image_path, grid_width=1, grid_height=1, width_cellule=2, scale=1):
    image = Image.open(image_path)
    width, height = image.size
    
    if scale != 1:
        width = int(width * scale)
        height = int(height * scale)
        image = image.resize((width, height), Image.Resampling.BICUBIC)
    
    cell_width = int(width / grid_width)
    cell_height = int(height / grid_height)
    
    for row in range(grid_height):
        out_lines = [''] * (cell_height + 2)
        for col in range(grid_width):
            left = col * cell_width
            top = row * cell_height
            right = (col + 1) * cell_width
            bottom = (row + 1) * cell_height
            cell = image.crop((left, top, right, bottom))
            decode_image_ascii(cell, out_lines, width_cellule)
        print('\n'.join(out_lines))


def decode_image_ascii(image, out_lines, width_cellule=2):
    image = image.convert("RGB")
    width, height = image.size
    
    out_lines[0] += '┌' + '─' * ((width * width_cellule)+2) + '┐'
    for y in range(height):
        ascii_line = ''
        for x in range(width):
            r, g, b = image.getpixel((x, y))
            ansi_color = f"\033[38;2;{r};{g};{b}m"
            ascii_line += f"{ansi_color}" +"█" * width_cellule
        ascii_line += "\033[0m"
        out_lines[y+1] += f'│ {ascii_line} │'
    out_lines[y+2] += '└' + '─' * ((width * width_cellule)+2) + '┘'
    
    return out_lines


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Image to ASCII')
    parser.add_argument('--path_image', action="store", dest='path_image', default='chevalier.png')
    parser.add_argument('--grid_width', action="store", dest='grid_width', type=int, default=1)
    parser.add_argument('--grid_height', action="store", dest='grid_height', type=int, default=1)
    parser.add_argument('--width_cellule', action="store", dest='width_cellule', type=int, default=2) 
    parser.add_argument('--scale', action="store", dest='scale', type=float, default=1) 
    args = parser.parse_args()
    img_2_ascii(args.path_image, args.grid_width, args.grid_height, args.width_cellule, args.scale)