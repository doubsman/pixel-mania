from PIL import Image, ImageEnhance
import argparse
import os
from bid2ascii import bid_2_ascii


def encode_bidfile(file_model, width_result, height_result, model_ascii, display_ascii):
    image = Image.open(file_model).convert("L")
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    filename_img = os.path.splitext(os.path.basename(file_model))[0] + '.bid'
    file_bid =  os.path.join('bid', filename_img)
    width, height = image.size
    width_scale = int(width/width_result)
    height_scale = int(height/height_result)
    image = image.resize((int(width/width_scale), int(height/height_scale)), Image.Resampling.LANCZOS)
    
    threshold = 128  # Seuil N&B
    binary_data = []
    for y in range(image.height):
        row = []
        for x in range(image.width):
            pixel = image.getpixel((x, y))
            row.append(1 if pixel < threshold else 0)
        binary_data.append(row)
    
    with open(file_bid, "w") as f:
        for row in binary_data:
            f.write("".join(map(str, row)) + "\n")

    if display_ascii:
        bid_2_ascii(file_bid, model_ascii)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='path image')
    parser.add_argument('--path_file', action="store", dest='path_file', default='test.jpeg')
    parser.add_argument('--width_result', action="store", dest='width_result')
    parser.add_argument('--height_result', action="store", dest='height_result')
    parser.add_argument('--display_ascii', action="store", type=bool, dest='display_ascii', default=False)
    parser.add_argument('--model_ascii', action="store", dest='model_ascii', default=1)
    args = parser.parse_args()
    path_file = args.path_file
    width_result = int(args.width_result)
    height_result = int(args.height_result)
    model_ascii = int(args.model_ascii)
    display_ascii = int(args.display_ascii)
    encode_bidfile(path_file, width_result, height_result, model_ascii, display_ascii)