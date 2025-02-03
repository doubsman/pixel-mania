from PIL import Image
import numpy as np
import math


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
        black_pixels = np.where(pixels < threshold - 20)

        # Si très peu de pixels noirs on considère un carré blanc
        if len(black_pixels[0]) < h * w * 0.01:
          return 0

        # Si beaucoup de pixels noirs on considère un carré noir
        if len(black_pixels[0]) > h * w * 0.99:
          return 1

        # Calcule les positions min et max des pixels noirs pour déterminer l'orientation du triangle
        min_x = min(black_pixels[1]) if len(black_pixels[1]) > 0 else 0
        max_x = max(black_pixels[1]) if len(black_pixels[1]) > 0 else 0
        min_y = min(black_pixels[0]) if len(black_pixels[0]) > 0 else 0
        max_y = max(black_pixels[0]) if len(black_pixels[0]) > 0 else 0

        if min_x < w / 2 and min_y < h / 2:
            return 5 # Triangle en haut à gauche
        elif max_x > w / 2 and min_y < h / 2:
            return 4 # Triangle en haut à droite
        elif min_x < w / 2 and max_y > h / 2:
           return 6 # Triangle en bas à gauche
        elif max_x > w / 2 and max_y > h / 2:
            return 3 # Triangle en bas à droite

        return -1 # Ne devrait pas arriver


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


def display_grid_codes(grid_codes):
    """Affiche les codes de la grille avec des caractères symboliques."""
    symbol_map = {
        0: "■",  # Carré blanc
        1: "□",  # Carré noir
        3: "◣",  # Triangle en bas à droite
        4: "◤",  # Triangle en haut à droite
        5: "◥",  # Triangle en haut à gauche
        6: "◢",  # Triangle en bas à gauche
        -1: "X"  # Code d'erreur
    }
    for row in grid_codes:
        row_str = " ".join(symbol_map.get(code, "?") for code in row)
        print(row_str)

if __name__ == "__main__":
    image_path = "export/rubicon3_4000x2900.png"  # Remplacez par le chemin de votre image
    grid_width = 40
    grid_height = 29
    grid_codes = process_image(image_path, grid_width, grid_height)
    
    if grid_codes is not None:
      print("Codes de la grille :")
      display_grid_codes(grid_codes)