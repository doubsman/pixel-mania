from PIL import Image, ImageDraw
import numpy as np
import math
from scipy.ndimage import center_of_mass
from bid2ascii import bid_2_ascii
import matplotlib.pyplot as plt  # Pour l'affichage des images

def classify_cell(cell_image, threshold=128, triangle_ratio=0.2):
    """Classifie une cellule en tant que carré blanc, carré noir ou triangle."""
    pixels = np.array(cell_image)
    h, w = pixels.shape

    # Calcul de la couleur moyenne des pixels de la cellule
    avg_color = np.mean(pixels)

    # On utilise un seuil fixe
    if avg_color > threshold:
        return 0  # Carré blanc
    
    black_pixels = pixels < threshold

    # On calcule le ratio de pixels noirs dans l'image
    black_ratio = np.sum(black_pixels) / (h * w)

    if black_ratio > 1 - triangle_ratio:
        return 1  # Carré noir

    if black_ratio < triangle_ratio:
        return 0  # Carré blanc
    
    # Calcule le centre de masse des pixels noirs
    center = center_of_mass(black_pixels)
    
    if np.isnan(center).any():
        return 2  # Erreur
    
    center_x = center[1]
    center_y = center[0]

    # Vérification de la position du centre de masse pour déterminer la direction du triangle
    if center_x < w / 2 and center_y < h / 2:
        return 5  # Triangle en haut à gauche
    elif center_x > w / 2 and center_y < h / 2:
        return 4  # Triangle en haut à droite
    elif center_x < w / 2 and center_y > h / 2:
        return 6  # Triangle en bas à gauche
    elif center_x > w / 2 and center_y > h / 2:
        return 3  # Triangle en bas à droite
    
    return 2  # Par défaut, retourne une erreur

def process_image(image_path, grid_width=40, grid_height=40, threshold=128, triangle_ratio=0.2):
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
    problematic_cells = []

    for row in range(grid_height):
        for col in range(grid_width):
            left = col * cell_width
            top = row * cell_height
            right = (col + 1) * cell_width
            bottom = (row + 1) * cell_height
            
            cell = image.crop((left, top, right, bottom))
            code = classify_cell(cell, threshold, triangle_ratio)
            grid_codes[row, col] = code

            # Affichage de la cellule et de son code
            #decode_img_ascii(cell)
            #plt.imshow(cell, cmap='gray')
            #plt.title(f"Code: {code}\nPosition: ({row}, {col})")
            #plt.axis('off')
            #plt.show()

            if code == -1:
                problematic_cells.append(((left, top, right, bottom), cell))

    return grid_codes, problematic_cells

def visualize_problematic_cells(image_path, problematic_cells, output_path="problematic_cells.png"):
    """Visualise les cellules problématiques sur une nouvelle image."""
    if not problematic_cells:
        print("Aucune cellule problématique à visualiser.")
        return

    try:
        image = Image.open(image_path).convert('RGB')
    except FileNotFoundError:
        print(f"Erreur : L'image à l'adresse {image_path} n'a pas été trouvée.")
        return

    draw = ImageDraw.Draw(image)
    for bbox, cell in problematic_cells:
        left, top, right, bottom = bbox
        draw.rectangle(bbox, outline="red", width=3)  # Red rectangle
        
    image.save(output_path)
    print(f"Image des cellules problématiques enregistrée dans '{output_path}'.")

if __name__ == "__main__":
    image_path = 'E:/Download/fence.jpeg'
    grid_width = 72
    grid_height = 128
    output_file = 'E:/Download/fence.bid'
    output_image = "E:/Download/fence_problematic_cells.png"
    threshold = 128
    triangle_ratio = 0.20  # Seuil qui permet de différencier les triangles des carrés

    grid_codes, problematic_cells = process_image(image_path, grid_width, grid_height, threshold, triangle_ratio)

    if grid_codes is not None:
        if problematic_cells:
            visualize_problematic_cells(image_path, problematic_cells, output_image)

        output_lines = []
        for row in grid_codes:
            row_str = ""
            for code in row:
                row_str += str(code)
            output_lines.append(row_str)
        with open(output_file, 'w') as f:
            for row in output_lines:
                f.write(row + '\n')
        bid_2_ascii(output_file)
