import argparse


def decode_bidfile_ascii(file_model, model_ascii=1):
    with open(file_model) as text_file:
        lines = text_file.readlines()
    if model_ascii == 1:
        chart_ascii="▩   X ◤ ◣ ◢ ◥ "
        witch_scale = 2
    elif model_ascii == 2:
        chart_ascii="▉ X▛▙▟▜"
        witch_scale = 1
    elif model_ascii == 3:
        chart_ascii="▉▉  XX▛▘▙▖▗▟▝▜"
        witch_scale = 2
    elif model_ascii == 4:
        chart_ascii="▉   XX▛ ▙ ▟ ▜ "
        witch_scale = 2
    print('┌' + '─' * (len(lines[0])*witch_scale) + '┐')
    for line in lines:
        print('│ ', end="")
        for car in line:
            if car != "\n":
                print(chart_ascii[int(car)*witch_scale:int(car)*witch_scale + (1*witch_scale)], end="")
        print(' │')
    print('└' + '─' * (len(lines[0])*witch_scale) + '┘')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='path image')
    parser.add_argument('--path_file', action="store", dest='path_file')
    parser.add_argument('--model_ascii', action="store", dest='model_ascii', default=1)
    args = parser.parse_args()
    path_file = args.path_file
    model_ascii = int(args.model_ascii)
    decode_bidfile_ascii(path_file, model_ascii)