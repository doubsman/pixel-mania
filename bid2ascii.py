import argparse
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


def bid_2_ascii(path_bid, model_ascii=1, bool_no_save=True):
    # shape
    grid_shapes = np.loadtxt(path_bid, dtype=str)
    try:
        width = len(str(grid_shapes[0]))
        height = grid_shapes.size
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

    # colors
    path_color = path_bid.replace('.bid','.color')
    bool_color = os.path.isfile(path_color)
    if bool_color:
        grid_colors = np.loadtxt(path_color, dtype=str)

    
    output_lines = []
    print('┌' + '─' * (2 + width*width_cellule) + '┐')
    for row in range(height):
        backup_line = ''
        display_line = ''
        for column in range(width):
            carac = int(grid_shapes[row][column])
            if bool_color:
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
    print('└' + '─' * (2 + len(str(grid_shapes[0]))*width_cellule) + '┘')

    if not bool_no_save:
        filename_ascii = os.path.splitext(os.path.basename(path_bid))[0] + '.ascii'
        path_ascii = os.path.join('wrk', filename_ascii)
        np.savetxt(path_ascii, grid_ascii, fmt='%s', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='bid to ascii consol')
    parser.add_argument('--path_bid', action="store", dest='path_bid')
    parser.add_argument('--model_ascii', action="store", dest='model_ascii', type=int, default=1)
    parser.add_argument('--no_save', action="store_true", dest='no_save')
    args = parser.parse_args()
    bid_2_ascii(args.path_bid, args.model_ascii, args.no_save)