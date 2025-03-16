from PIL import Image
import os
import numpy as np


GRAY_SCALE_DISPLAY = {
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
    3: ['▉▉','▉▉','XX','▛▘','▙▖','▗▟','▝▜'],
    4: ['0 ','1 ','2 ','3 ','4 ','5 ','6 ']
}

class ImageASCII():
    def __init__(self, image, grid_width=1, grid_height=1, width_cellule=2, scale=1):
        width, height = image.size
        if scale != 1:
            width = int(width * scale)
            height = int(height * scale)
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        
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
                self.decode_image_ascii(cell, out_lines, width_cellule)
            print('\n'.join(out_lines))

    def decode_image_ascii(self, image, out_lines, width_cellule=2):
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

class BidASCII():
    def __init__(self, grid_shapes, grid_colors=[], model_ascii=1, path_ascii=None):
        try:
            width = len(grid_shapes[0])
            height = int(grid_shapes.size / width)
        except:
            # one line
            width = len(str(grid_shapes))
            height = 1
            tmp_shapes = np.zeros((height), dtype=f'<U{width}')
            tmp_shapes[0] = grid_shapes
            grid_shapes = tmp_shapes
        
        # ascii
        motifs_ascii = CHARTS_ASCII[model_ascii]
        width_cellule = len(motifs_ascii[0])
        grid_ascii = np.empty(height, dtype=object)
        
        output_lines = []
        print('┌' + '─' * (2 + width*width_cellule) + '┐')
        for row in range(height):
            backup_line = ''
            display_line = ''
            for column in range(width):
                carac = int(grid_shapes[row][column])
                if len(grid_colors) > 0:
                    color_indice = int(grid_colors[row][column])
                    if color_indice == 5 and carac > 1:
                        color_indice = 0
                    color_rgb = GRAY_SCALE_DISPLAY[color_indice]   
                else:
                    color_rgb = (255, 255, 255) if carac != 1 else (0, 0, 0)
                color_ascii = f"\033[38;2;{color_rgb[0]};{color_rgb[1]};{color_rgb[2]}m"
                carac_ascii = motifs_ascii[carac]
                backup_line += CHARTS_ASCII[1][carac]
                display_line += color_ascii + carac_ascii
            display_line += "\033[0m"
            print(f'│ {display_line} │')
            output_lines.append(backup_line)
            grid_ascii[row] = backup_line
        print('└' + '─' * (2 + width*width_cellule) + '┘')

        if path_ascii is not None:
            filename_ascii = os.path.splitext(os.path.basename(path_ascii))[0] + '.ascii'
            path_ascii = os.path.join('wrk', filename_ascii)
            np.savetxt(path_ascii, grid_ascii, fmt='%s', encoding='utf-8')