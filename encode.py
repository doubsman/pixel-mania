from PIL import Image
import argparse
import os

def encode_bidfile(file_model, display_ascii=True):
    image = Image.open(file_model).convert("L")
    image = image.convert('1')
    image.show()
    image = image.resize((31, 33), Image.Resampling.BILINEAR)
    image.show()
    file_model_extension = (os.path.splitext(file_model))[1]
    file_bid = file_model.replace(file_model_extension, '.bid')

    # Binariser l'image (0 pour blanc, 1 pour noir)
    threshold = 128  # Seuil pour distinguer le noir du blanc
    binary_data = []
    for y in range(image.height):
        row = []
        for x in range(image.width):
            pixel = image.getpixel((x, y))
            if pixel < threshold:
                row.append(1)  # Noir
            else:
                row.append(0)  # Blanc
        binary_data.append(row)

    if display_ascii:
        for row in binary_data:
            print("".join(map(str, row)))

    with open(file_bid, "w") as f:
        for row in binary_data:
            f.write("".join(map(str, row)) + "\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='path image')
    parser.add_argument('--path_file', action="store", dest='path_file')
    args = parser.parse_args()
    path_file = args.path_file
    encode_bidfile(path_file)