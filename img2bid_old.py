import cv2
import argparse
from bid2ascii import bid_2_ascii

def detect_pattern(cell):
    # Convertit la cellule en binaire (noir/blanc)
    _, binary = cv2.threshold(cell, 127, 255, cv2.THRESH_BINARY)
    
    h, w = cell.shape
    
    # Définition plus précise des zones de détection avec des marges ajustées
    top = binary[0:h//2-h//6, w//4:3*w//4].mean()
    bottom = binary[h//2+h//6:h, w//4:3*w//4].mean()
    left = binary[h//4:3*h//4, 0:w//2-w//6].mean()
    right = binary[h//4:3*h//4, w//2+w//6:w].mean()
    center = binary[h//3:2*h//3, w//3:2*w//3].mean()
    
    # Seuils ajustés
    black_threshold = 60
    white_threshold = 190
    
    # Moyenne globale
    mean = binary.mean()
    
    # Calcul des ratios de contraste
    top_bottom_ratio = abs(top - bottom)
    left_right_ratio = abs(left - right)
    
    if mean > white_threshold:  # Carré blanc
        return '0'
    elif mean < black_threshold:  # Carré noir
        return '1'
    else:
        # Détection améliorée des triangles avec vérification des ratios
        if bottom < black_threshold and top > white_threshold and top_bottom_ratio > 100:
            return '3'  # Triangle orienté vers le bas
        elif top < black_threshold and bottom > white_threshold and top_bottom_ratio > 100:
            return '4'  # Triangle orienté vers le haut
        elif left < black_threshold and right > white_threshold and left_right_ratio > 100:
            return '5'  # Triangle orienté vers la droite
        elif right < black_threshold and left > white_threshold and left_right_ratio > 100:
            return '6'  # Triangle orienté vers la gauche
            
    return '0'  # Par défaut


def encode_bidfile(image_path, bid_path, grid_w, grid_h, model_ascii, display_ascii):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.equalizeHist(img)

    # Redim
    target_height = grid_h * 30
    target_width = grid_w * 30
    img = cv2.resize(img, (target_width, target_height))
    
    # Amélioration du contraste
    img = cv2.GaussianBlur(img, (3,3), 0)
    _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    
    # Calcul des dimensions des cellules
    cell_h = img.shape[0] // grid_h
    cell_w = img.shape[1] // grid_w
    
    # Pour chaque cellule de la grille
    pattern = []
    for y in range(grid_h):
        row = ''
        for x in range(grid_w):
            cell = img[y*cell_h:(y+1)*cell_h, x*cell_w:(x+1)*cell_w]
            pattern_code = detect_pattern(cell)
            row += pattern_code
            break
        pattern.append(row)

    with open(bid_path, 'w') as f:
        for row in pattern:
            f.write(row + '\n')

    if display_ascii:
        bid_2_ascii(bid_path, model_ascii)



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


