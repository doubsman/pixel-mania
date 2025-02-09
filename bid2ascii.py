import argparse
import os

def bid_2_ascii(path_bid, model_ascii=1, bool_no_save=True):
    charts_ascii=[{'motifs' : "▩   X ◤ ◣ ◢ ◥ ", 'width_cellule' : 2},
                  {'motifs' : "▉ X▛▙▟▜", 'width_cellule' : 1},
                  {'motifs' : "▉▉  XX▛▘▙▖▗▟▝▜", 'width_cellule' : 2},
                  {'motifs' : "▉   XX▛ ▙ ▟ ▜ ", 'width_cellule' : 2}]
    chart_ascii = charts_ascii[model_ascii - 1]
    motifs_ascii = chart_ascii['motifs']
    width_cellule = chart_ascii['width_cellule']

    with open(path_bid) as text_file:
        lines = text_file.readlines()

    output_lines = []
    print('┌' + '─' * (len(lines[0])*width_cellule) + '┐')
    for line in lines:
        ascii_art = ''
        for car in line:
            if car != "\n":
                ascii_art += motifs_ascii[int(car)*width_cellule:int(car)*width_cellule + (1*width_cellule)]
        print(f'│ {ascii_art} │')
        output_lines.append(ascii_art)
    print('└' + '─' * (len(lines[0])*width_cellule) + '┘')

    if not bool_no_save:
        filename_ascii = os.path.splitext(os.path.basename(path_bid))[0] + '.txt'
        path_ascii = os.path.join('ascii', filename_ascii)
        with open(path_ascii, 'w', encoding='utf-8') as f:
            for row in output_lines:
               f.write(row + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='bid to ascii consol')
    parser.add_argument('--path_bid', action="store", dest='path_bid')
    parser.add_argument('--model_ascii', action="store", dest='model_ascii', type=int, default=1)
    parser.add_argument('--no_save', action="store_true", dest='no_save')
    args = parser.parse_args()
    bid_2_ascii(args.path_bid, args.model_ascii, args.no_save)