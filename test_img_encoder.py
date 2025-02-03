from PIL import Image
import numpy as np
import math
from scipy.ndimage import center_of_mass
from bid2ascii import decode_bidfile_ascii

def classify_cell(cell_image, threshold=128):
    """Classifie une cellule en tant que carré blanc, carré noir ou triangle."""
    pixels = np.array(cell_image)
    h, w = pixels.shape
    
    # Calcul de la couleur moyenne des pixels de la cellule
    avg_color = np.mean(pixels)

    # On utilise un seuil dynamique par rapport à la moyenne de la cellule
    if avg_color > threshold + 20:
        return 0  # Carré blanc
    elif avg_color < threshold - 20:
        return 1  # Carré noir
    else: # Sinon, on cherche des triangles
        
        # On utilise la même méthode que dans la réponse précédente mais avec un seuil adapté
        black_pixels = pixels < threshold - 20

        # Si très peu de pixels noirs on considère un carré blanc
        if np.sum(black_pixels) < h * w * 0.01:
          return 0

        # Si beaucoup de pixels noirs on considère un carré noir
        if np.sum(black_pixels) > h * w * 0.99:
          return 1

        # Calcule le centre de masse
        center = center_of_mass(black_pixels)
        
        if np.isnan(center).any():
            return -1 # Erreur
        
        center_x = center[1]
        center_y = center[0]
        

        if center_x < w / 2 and center_y < h / 2:
            return 5 # Triangle en haut à gauche
        elif center_x > w / 2 and center_y < h / 2:
            return 4 # Triangle en haut à droite
        elif center_x < w / 2 and center_y > h / 2:
           return 6 # Triangle en bas à gauche
        elif center_x > w / 2 and center_y > h / 2:
            return 3 # Triangle en bas à droite
        
        return 2

def process_image(image_path, grid_width=40, grid_height=40):
    """Traite l'image, la divise en grille et la classifie."""
    try:
      image = Image.open(image_path).convert('L')
    except FileNotFoundError:
        print(f"Erreur : L'image à l'adresse {image_path} n'a pas été trouvée.")
        return None
    width, height = image.size
    cell_width = math.floor(width / grid_width)
    cell_height = math.floor(height / grid_height)

    grid_codes = np.zeros((grid_height, grid_width), dtype=int)

    for row in range(grid_height):
        for col in range(grid_width):
            left = col * cell_width
            top = row * cell_height
            right = (col + 1) * cell_width
            bottom = (row + 1) * cell_height
            
            cell = image.crop((left, top, right, bottom))
            grid_codes[row, col] = classify_cell(cell)
            
    return grid_codes

if __name__ == "__main__":
    image_path = "E:/Download/grill.jpeg"
    bid_path=  'test.bid'
    grid_width = 42
    grid_height = 42
    grid_codes = process_image(image_path, grid_width, grid_height)
    if grid_codes is not None:
        output_lines = []
        for row in grid_codes:
            row_str = ""
            for code in row:
                row_str += str(code)
            output_lines.append(row_str)
        with open(bid_path, 'w') as f:
            for row in output_lines:
               f.write(row + '\n')
        decode_bidfile_ascii(bid_path)
