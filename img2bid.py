import cv2
import numpy as np
import argparse
from bid2ascii import decode_bidfile_ascii


def detect_pattern(cell):
    h, w = cell.shape
    
    # Calcul du pourcentage de pixels noirs
    black_percentage = np.sum(cell < 127) / (h * w)
    
    # Si presque tout est noir -> code 1
    if black_percentage > 0.85:
        return '1'
    
    # Si presque tout est blanc -> code 0
    if black_percentage < 0.15:
        return '0'
    
    # Analyse des bords pour les triangles
    border = w // 4
    left = np.mean(cell[:, :border] < 127)
    right = np.mean(cell[:, -border:] < 127)
    top = np.mean(cell[:border, :] < 127)
    bottom = np.mean(cell[-border:, :] < 127)
    
    # Seuils pour la détection des triangles
    threshold = 0.5
    
    # Détection de l'orientation du triangle
    if left > threshold and right < threshold:
        return '6'  # Triangle pointant vers la gauche
    elif left < threshold and right > threshold:
        return '5'  # Triangle pointant vers la droite
    elif top > threshold and bottom < threshold:
        return '4'  # Triangle pointant vers le haut
    elif top < threshold and bottom > threshold:
        return '3'  # Triangle pointant vers le bas
        
    return '0'  # Par défaut


def encode_bidfile(image_path, bid_path, grid_w, grid_h, model_ascii, display_ascii):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.equalizeHist(img)
    
    height, width = img.shape
    cell_h = height // grid_h
    cell_w = width // grid_w
    
    # Redimensionnement
    new_height = cell_h * grid_h
    new_width = cell_w * grid_w
    img = cv2.resize(img, (new_width, new_height))
    
    # Prétraitement
    img = cv2.GaussianBlur(img, (3,3), 0)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Détection des motifs
    pattern = []
    for y in range(grid_h):
        row = ''
        for x in range(grid_w):
            cell = img[y*cell_h:(y+1)*cell_h, x*cell_w:(x+1)*cell_w]
            pattern_code = detect_pattern(cell)
            row += pattern_code
        pattern.append(row)
    
    with open(bid_path, 'w') as f:
        for row in pattern:
            f.write(row + '\n')

    if display_ascii:
        decode_bidfile_ascii(bid_path, model_ascii)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='path image')
    parser.add_argument('--path_img', action="store", dest='path_img', default='test.jpeg')
    parser.add_argument('--path_bid', action="store", dest='path_bid', default='test.bid')
    parser.add_argument('--width_result', action="store", dest='width_result')
    parser.add_argument('--height_result', action="store", dest='height_result')
    parser.add_argument('--display_ascii', action="store", type=bool, dest='display_ascii', default=True)
    parser.add_argument('--model_ascii', action="store", dest='model_ascii', default=1)
    args = parser.parse_args()
    path_img = args.path_img
    path_bid = args.path_bid
    width_result = int(args.width_result)
    height_result = int(args.height_result)
    model_ascii = int(args.model_ascii)
    display_ascii = int(args.display_ascii)
    encode_bidfile(path_img, path_bid, width_result, height_result, model_ascii, display_ascii)

