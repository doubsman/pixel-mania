import cv2
import numpy as np

# Charger l'image
image = cv2.imread("source/entrelas.jpeg")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Appliquer le seuillage ou binarisation
_, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

# Détection des lignes verticales et horizontales
vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 10))
horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 1))
vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)

# Combiner pour reconstituer la grille
grid = cv2.bitwise_or(vertical_lines, horizontal_lines)

# Améliorer la détection via dilatation
kernel = np.ones((3, 3), np.uint8)
grid = cv2.dilate(grid, kernel, iterations=1)

# Trouver les contours
contours, _ = cv2.findContours(grid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
rectangles = [cv2.boundingRect(contour) for contour in contours]

# Normaliser les positions des colonnes/lignes
unique_x = sorted(set([rect[0] for rect in rectangles]))
unique_y = sorted(set([rect[1] for rect in rectangles]))
threshold = 10
final_x = [unique_x[0]]
for x in unique_x[1:]:
    if x - final_x[-1] > threshold:
        final_x.append(x)

final_y = [unique_y[0]]
for y in unique_y[1:]:
    if y - final_y[-1] > threshold:
        final_y.append(y)

nb_colonnes = len(final_x)
nb_lignes = len(final_y)

print(f"Nombre de colonnes : {nb_colonnes}")
print(f"Nombre de lignes : {nb_lignes}")
