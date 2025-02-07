import argparse


def ascii_2_bid(path_ascii, output_file=None):
    charts_ascii=[{'motifs' : "▩   X ◤ ◣ ◢ ◥ ", 'width_cellule' : 2},
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
            if motifs_ascii.find(car) != -1:
                if car == '  ':
                    ascii_art += '1'
                else:
                    ascii_art += str(int(motifs_ascii.find(car)/2))
        print(ascii_art)
        if len(ascii_art.strip()) !=0:
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
    path_ascii = args.path_ascii
    path_bid = args.path_bid
    path_ascii='fence.ascii'
    ascii_2_bid(path_ascii, path_bid)