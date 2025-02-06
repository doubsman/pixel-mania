import cv2
import numpy as np
import argparse
from bid2ascii import bid_2_ascii


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


def encode_bidfile(image_path, grid_width=1, grid_height=1, bid_path=None):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.equalizeHist(img)
    
    height, width = img.shape
    cell_h = height // grid_height
    cell_w = width // grid_width
    
    # Redimensionnement
    new_height = cell_h * grid_height
    new_width = cell_w * grid_width
    img = cv2.resize(img, (new_width, new_height))
    
    # Prétraitement
    img = cv2.GaussianBlur(img, (3,3), 0)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Détection des motifs
    pattern = []
    for y in range(grid_height):
        row = ''
        for x in range(grid_width):
            cell = img[y*cell_h:(y+1)*cell_h, x*cell_w:(x+1)*cell_w]
            pattern_code = detect_pattern(cell)
            row += pattern_code
        pattern.append(row)
    
    if bid_path is not None:
        with open(bid_path, 'w') as f:
            for row in pattern:
                f.write(row + '\n')
        bid_2_ascii(bid_path)
    else:
        print(pattern)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='path image')
    parser.add_argument('--path_img', action="store", dest='path_img', default='test.jpeg')
    parser.add_argument('--path_bid', action="store", dest='path_bid', default=None)
    parser.add_argument('--grid_width', action="store", dest='grid_width')
    parser.add_argument('--grid_height', action="store", dest='grid_height')    
    args = parser.parse_args()
    path_img = args.path_img
    path_bid = args.path_bid
    width_result = int(args.width_result)
    grid_width = int(args.grid_width)
    grid_height = int(args.grid_height)
    encode_bidfile(path_img, grid_width, grid_height, path_bid)


