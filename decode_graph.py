import matplotlib.pyplot as plt
import numpy as np
import argparse
from decode_ascii import decode_bidfile_ascii


def draw_cellule(ax, x, y, cell_type):
    if cell_type == 0:  # ▯ (carré blanc) ok
        ax.add_patch(plt.Rectangle((x, y), 1, 1, color="white", ec="black"))
    elif cell_type == 1:  # ▮ (carré noir) ok
        ax.add_patch(plt.Rectangle((x, y), 1, 1, color="black", ec="black"))
    elif cell_type == 3:  # ◢ (triangle en bas à droite)
        ax.fill([x, x+1, x+1], [y+1, y+1, y], color="black")
    elif cell_type == 4:  # ◥ (triangle en haut à droite)
        ax.fill([x, x+1, x+1], [y, y, y+1], color="black")
    elif cell_type == 5:  # ◤ (triangle en haut à gauche)
        ax.fill([x, x+1, x], [y, y, y+1], color="black")
    elif cell_type == 6:  # ◣ (triangle en bas à gauche)
        ax.fill([x, x, x+1], [y, y+1, y+1], color="black")


def decode_bidfile_graph(file_model, model_ascii, display_ascii=True):
    if display_ascii:
        decode_bidfile_ascii(file_model, model_ascii)
    with open(file_model, 'r') as text_file:
        data = text_file.read().splitlines()
    grid = np.array([[int(cell) for cell in row] for row in data])

    fig, ax = plt.subplots(figsize=(8, 8))
    fig.canvas.manager.set_window_title(file_model)

    for y in range(grid.shape[0]):
        for x in range(grid.shape[1]):
            cell = grid[y, x]
            draw_cellule(ax, x, y, cell)

    ax.set_xticks(np.arange(0, grid.shape[1] + 1, 1))
    ax.set_yticks(np.arange(0, grid.shape[0] + 1, 1))
    ax.grid(color="gray", linestyle="--", linewidth=0.5)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xlim(0, grid.shape[1])
    ax.set_ylim(0, grid.shape[0])
    plt.gca().invert_yaxis()
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='path image')
    parser.add_argument('--path_file', action="store", dest='path_file')
    parser.add_argument('--model_ascii', action="store", dest='model_ascii', default=1)
    args = parser.parse_args()
    path_file = args.path_file
    model_ascii = int(args.model_ascii)
    decode_bidfile_graph(path_file, model_ascii)
