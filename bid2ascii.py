import argparse
import os
import numpy as np


GRAY_SCALE = {
    0: (255, 255, 255),  # Blanc
    1: (192, 192, 192),  # Gris très clair
    2: (128, 128, 128),  # Gris clair
    3: (64, 64, 64),     # Gris foncé
    4: (32, 32, 32),     # Gris très foncé
    5: (0, 0, 0)         # Noir
}
CHARTS_ASCII = [
    {'motifs' : "▩   X ▮◤ ◣ ◢ ◥ ", 'width_cellule' : 2},
    {'motifs' : "▉ X▛▙▟▜", 'width_cellule' : 1},
    {'motifs' : "▉▉▉▉XX▛▘▙▖▗▟▝▜", 'width_cellule' : 2},
    {'motifs' : "▉   XX▛ ▙ ▟ ▜ ", 'width_cellule' : 2}
]


def bid_2_ascii(path_bid, model_ascii=1, bool_no_save=True):
    # shape
    grid_shapes = np.loadtxt(path_bid, dtype=str)
    width = len(str(grid_shapes[0]))
    height = grid_shapes.size
    
    model_ascii=3

    # ascii
    chart_ascii = CHARTS_ASCII[model_ascii - 1]
    motifs_ascii = chart_ascii['motifs']
    width_cellule = chart_ascii['width_cellule']
    grid_ascii = np.empty(height, dtype=object)

    # colors
    path_color = path_bid.replace('.bid','.color')
    if os.path.isfile(path_color):
        grid_colors = np.loadtxt(path_color, dtype=str)
    else:
        grid_colors = np.zeros((height, width), dtype=int)
    
    output_lines = []
    print('┌' + '─' * (2 + width*width_cellule) + '┐')
    for row in range(height):
        backup_line = ''
        display_line = ''
        for column in range(width):
            color_indice = int(grid_colors[row][column])
            color_rgb = GRAY_SCALE[color_indice]
            color_ascii = f"\033[38;2;{color_rgb[0]};{color_rgb[1]};{color_rgb[2]}m"
            carac = int(grid_shapes[row][column])
            carac_ascii = motifs_ascii[carac*width_cellule:carac*width_cellule + (1*width_cellule)]
            backup_line += carac_ascii
            display_line += color_ascii + carac_ascii
        display_line += "\033[0m"
        print(f'│ {display_line} │')
        output_lines.append(backup_line)
        grid_ascii[row] = backup_line
    print('└' + '─' * (2 + len(str(grid_shapes[0]))*width_cellule) + '┘')

    if not bool_no_save:
        filename_ascii = os.path.splitext(os.path.basename(path_bid))[0] + '.ascii'
        path_ascii = os.path.join('bid', filename_ascii)
        np.savetxt(path_ascii, grid_ascii, fmt='%s', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='bid to ascii consol')
    parser.add_argument('--path_bid', action="store", dest='path_bid')
    parser.add_argument('--model_ascii', action="store", dest='model_ascii', type=int, default=1)
    parser.add_argument('--no_save', action="store_true", dest='no_save')
    args = parser.parse_args()
    bid_2_ascii(args.path_bid, args.model_ascii, args.no_save)