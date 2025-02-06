import argparse


def bid_2_ascii(path_bid, model_ascii=1, output_file=None):
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

    if output_file is not None:
        with open(output_file, 'w',encoding='utf-8') as f:
            for row in output_lines:
               f.write(row + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='bid to ascii consol')
    parser.add_argument('--path_bid', action="store", dest='path_bid')
    parser.add_argument('--model_ascii', action="store", dest='model_ascii', default=1)
    parser.add_argument('--path_save', action="store", dest='path_save', default=None)
    args = parser.parse_args()
    path_bid = args.path_bid
    path_save = args.path_save
    model_ascii = int(args.model_ascii)
    bid_2_ascii(path_bid, model_ascii, path_save)