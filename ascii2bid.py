import argparse


def ascii_2_bid(path_ascii, output_file=None):
    charts_ascii=[{'motifs' : "▩ X◤◣◢◥", 'width_cellule' : 2},
                  {'motifs' : "▉ X▛▙▟▜", 'width_cellule' : 1},
                  {'motifs' : "▉▉  XX▛▘▙▖▗▟▝▜", 'width_cellule' : 2},
                  {'motifs' : "▉   XX▛ ▙ ▟ ▜ ", 'width_cellule' : 2}]
 
    chart_ascii = charts_ascii[0]
    motifs_ascii = chart_ascii['motifs']
    width_cellule = chart_ascii['width_cellule']

    with open(path_ascii, encoding='utf-8') as text_file:
        lines = text_file.readlines()

    output_lines = []
    for line in lines:
        ascii_art = ''
        for cell in range(2, len(line)-2, width_cellule):
            car = line[cell:cell + width_cellule]
            if car == ' '*width_cellule:
                ascii_art += '1'
            elif motifs_ascii.find(car.strip()) != -1:
                ascii_art += str(motifs_ascii.find(car.strip()))
        if ascii_art != '':
            output_lines.append(ascii_art)

    if output_file is not None:
        with open(output_file, 'w', encoding='utf-8') as f:
            for row in output_lines:
               f.write(row + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='bid to ascii consol')
    parser.add_argument('--path_ascii', action="store", dest='path_ascii')
    parser.add_argument('--path_bid', action="store", dest='path_bid', default=None)
    args = parser.parse_args()
    ascii_2_bid(args.path_ascii, args.path_bid)