import os
import numpy as np
from PIL import Image, ImageDraw
from class_cells import Cells


class BidFile(Cells):
    def __init__(self):
        Cells.__init__(self)
        self.path_bid = None
        self.grid_bid = None
        self.path_color = None
        self.grid_colors = None
        self.bool_color = True
        self.grid_width = 0
        self.grid_height = 0
        self.image = None
        self.draw = None
        self.grid_sel_cells = None

    def load_bidfile(self, path_bid, image_with=None, image_height=None):
        self.path_bid = path_bid
        self.grid_bid = np.genfromtxt(self.path_bid, delimiter=1, dtype=int, ndmin=2)
        self.grid_width = len(self.grid_bid[0])
        self.grid_height = int(self.grid_bid.size / self.grid_width)
        if image_with is not None and image_height is not None:
            self.define_scale(image_with, image_height, self.grid_width, self.grid_height)
        # colors
        self.path_color = self.path_bid.replace('.bid','.color')
        self.bool_color = os.path.isfile(self.path_color)
        if self.bool_color:
            self.grid_colors = np.genfromtxt(self.path_color, delimiter=1, dtype=int, ndmin=2)
        else:
            self.grid_colors = np.zeros((self.grid_height, self.grid_width), dtype=int)
            #browse self.grid_bid and define colors, set value=5 (black) if shape <>0
            for row in range(self.grid_height):
                for column in range(self.grid_width):
                    if self.grid_bid[row][column] > 0:
                        self.grid_colors[row][column] = 5
            
    
        self.draw_bidfile()
        return self.image

    def new_bid(self, image_with=None, image_height=None, grid_width=48, grid_height=48):
        self.bool_color = True
        self.grid_height = grid_height
        self.grid_width = grid_width
        if image_with is not None and image_height is not None:
            self.define_scale(image_with, image_height, self.grid_width, self.grid_height)
        self.grid_bid = np.zeros((self.grid_height, self.grid_width), dtype=int)
        self.grid_colors = np.zeros((self.grid_height, self.grid_width), dtype=int)
        self.draw_bidfile()
        return self.image

    def change_bid_size(self, image_with, image_height, grid_width, grid_height):
        """Change the size of the bid file with parameter validation"""
        # Validate parameters
        if not isinstance(grid_width, int) or not isinstance(grid_height, int):
            raise TypeError("Grid dimensions must be integers")
        if grid_width < 1 or grid_height < 1:
            raise ValueError("Grid dimensions must be positive")
        if grid_width > 96 or grid_height > 96:
            raise ValueError("Grid dimensions cannot exceed 96")
        if not isinstance(image_with, (int, float)) or not isinstance(image_height, (int, float)):
            raise TypeError("Image dimensions must be numbers")
        if image_with <= 0 or image_height <= 0:
            raise ValueError("Image dimensions must be positive")

        # Store original dimensions for potential rollback
        original_width = self.grid_width
        original_height = self.grid_height

        try:
            if grid_width < self.grid_width or grid_height < self.grid_height:
                self.reduce_grid(grid_width, grid_height)
            if grid_width > self.grid_width or grid_height > self.grid_height:
                self.extend_grid(grid_width, grid_height)
            
            self.grid_height = grid_height
            self.grid_width = grid_width
            self.define_scale(image_with, image_height, self.grid_width, self.grid_height)
            self.draw_bidfile()
        except Exception as e:
            # Rollback on error
            self.grid_width = original_width
            self.grid_height = original_height
            raise RuntimeError(f"Failed to change bid size: {str(e)}")

    def extend_grid(self, grid_width, grid_height):
        """Extend the grid with optimized memory management"""
        # Calculate padding dimensions
        extend_rows = int((grid_height - self.grid_height) // 2)
        extend_columns = int((grid_width - self.grid_width) // 2)
        
        # Create new arrays with the correct dimensions directly
        new_bid = np.zeros((grid_height, grid_width), dtype=int)
        new_colors = np.zeros((grid_height, grid_width), dtype=int)
        
        # Copy existing data to the center of the new arrays
        new_bid[extend_rows:extend_rows + self.grid_height, 
               extend_columns:extend_columns + self.grid_width] = self.grid_bid
        new_colors[extend_rows:extend_rows + self.grid_height, 
                  extend_columns:extend_columns + self.grid_width] = self.grid_colors
        
        # Update references
        self.grid_bid = new_bid
        self.grid_colors = new_colors

    def reduce_grid(self, grid_width, grid_height):
        reduce_rows = (self.grid_height - grid_height) // 2
        reduce_columns = (self.grid_width - grid_width) // 2
        start_row = reduce_rows
        end_row = self.grid_height - reduce_rows
        start_col = reduce_columns
        end_col = self.grid_width - reduce_columns
        self.grid_bid = self.grid_bid[start_row:end_row, start_col:end_col]
        self.grid_colors = self.grid_colors[start_row:end_row, start_col:end_col]

    def draw_bidfile(self, bool_outline=False):
        """Draw the bid file with optimized performance"""
        # Create image with white background
        self.image = Image.new('RGB', (self.grid_width * self.image_scale, self.grid_height * self.image_scale), color=(255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)
        
        # Pre-calculate colors for better performance
        colors = [self.get_color(i) for i in range(6)]
        
        # Create numpy arrays for faster access
        bid_array = np.array(self.grid_bid)
        colors_array = np.array(self.grid_colors)
        
        # Process cells in batches for better performance
        for row in range(self.grid_height):
            for column in range(self.grid_width):
                cell = bid_array[row, column]
                if self.bool_color:
                    color_indice = colors_array[row, column]
                    # plain square if color: compatibility old version
                    if cell == 0 and color_indice > 0:
                        cell = 1
                else:
                    # not greys
                    color_indice = 0 if cell == 0 else 5
                    colors_array[row, column] = color_indice
                
                # Get pre-calculated color
                color = colors[color_indice]
                
                # Calculate cell position
                x1 = column * self.image_scale
                y1 = row * self.image_scale
                x2 = (column + 1) * self.image_scale
                y2 = (row + 1) * self.image_scale
                
                # Draw cell based on shape
                if cell == 0:  # Empty cell
                    if bool_outline:
                        self.draw.rectangle([x1, y1, x2, y2], outline='gray')
                elif cell == 1:  # Square
                    self.draw.rectangle([x1, y1, x2, y2], fill=color)
                    if bool_outline:
                        self.draw.rectangle([x1, y1, x2, y2], outline='gray')
                elif cell == 2:  # X
                    self.draw.rectangle([x1, y1, x2, y2], fill=color)
                    self.draw.line([x1, y1, x2, y2], fill='white', width=2)
                    self.draw.line([x2, y1, x1, y2], fill='white', width=2)
                    if bool_outline:
                        self.draw.rectangle([x1, y1, x2, y2], outline='gray')
                else:  # Triangles
                    points = self.get_triangle_points(x1, y1, x2, y2, cell)
                    self.draw.polygon(points, fill=color)
                    if bool_outline:
                        self.draw.polygon(points, outline='gray')

    def save_bidfile(self, path_bid):
        if not path_bid.endswith(".bid"):
            self.path_bid = path_bid + '.bid'
        else:
            self.path_bid = path_bid
        np.savetxt(self.path_bid, self.grid_bid, fmt='%i', delimiter="")
        path_color = self.path_bid.replace('.bid','.color')
        np.savetxt(path_color, self.grid_colors, fmt='%i', delimiter="")

    def save_imagefile(self, path_image, image_scale=50, bool_outline=True):
        if not path_image.endswith(".png"):
            path_image = path_image + '.png'
        backup_scale = self.image_scale
        self.image_scale = image_scale
        self.draw_bidfile(bool_outline=bool_outline)
        self.image.save(path_image)
        self.image_scale = backup_scale
        self.draw_bidfile()

    def load_combined_file(self, path_combined):
        data = np.load(path_combined)
        self.grid_bid = data['grid_bid']
        self.grid_colors = data['grid_colors']
        image_array = data['image']
        self.image = Image.fromarray(image_array)
        self.draw = ImageDraw.Draw(self.image)

    def save_combined_file(self, path_combined):
        image_array = np.array(self.image)
        np.savez(path_combined, grid_bid=self.grid_bid, grid_colors=self.grid_colors, image=image_array)

    def rotate_l_grid(self):
        """Rotate selected cells 90° counterclockwise"""
        if self.grid_sel_cells is not None and np.any(self.grid_sel_cells):
            # Get selection bounds using the helper method
            min_x, max_x, min_y, max_y = self._get_selection_bounds()
            if min_x is None:
                return False
                
            # Calculate center of selection using float division and round
            center_x = round((min_x + max_x) / 2)
            center_y = round((min_y + max_y) / 2)
            
            # Create a temporary copy of selected cells
            temp_cells = []
            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    if self.grid_sel_cells[y, x] == 1:
                        temp_cells.append((x, y, self.grid_bid[y, x], self.grid_colors[y, x]))
            
            # Clear selected cells first
            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    if self.grid_sel_cells[y, x] == 1:
                        self.grid_bid[y, x] = 0
                        self.grid_colors[y, x] = 0
                        self.grid_sel_cells[y, x] = 0
            
            # Calculate new positions after rotation
            for x, y, shape, color in temp_cells:
                # Calculate relative position from center
                rel_x = x - center_x
                rel_y = y - center_y
                
                # Rotate 90° counterclockwise
                new_x = round(center_x + rel_y)
                new_y = round(center_y - rel_x)
                
                # Rotate triangle shapes
                if shape == 3:
                    new_shape = 4
                elif shape == 4:
                    new_shape = 5
                elif shape == 5:
                    new_shape = 6
                elif shape == 6:
                    new_shape = 3
                else:
                    new_shape = shape
                
                # Update grid if within bounds
                if 0 <= new_x < self.grid_width and 0 <= new_y < self.grid_height:
                    self.grid_bid[new_y, new_x] = new_shape
                    self.grid_colors[new_y, new_x] = color
                    self.grid_sel_cells[new_y, new_x] = 1
            
            # Redraw
            self.draw_bidfile()
            return True
        return False

    def rotate_r_grid(self):
        """Rotate selected cells 90° clockwise"""
        if self.grid_sel_cells is not None and np.any(self.grid_sel_cells):
            # Get selection bounds using the helper method
            min_x, max_x, min_y, max_y = self._get_selection_bounds()
            if min_x is None:
                return False
                
            # Calculate center of selection using float division and round
            center_x = round((min_x + max_x) / 2)
            center_y = round((min_y + max_y) / 2)
            
            # Create a temporary copy of selected cells
            temp_cells = []
            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    if self.grid_sel_cells[y, x] == 1:
                        temp_cells.append((x, y, self.grid_bid[y, x], self.grid_colors[y, x]))
            
            # Clear selected cells first
            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    if self.grid_sel_cells[y, x] == 1:
                        self.grid_bid[y, x] = 0
                        self.grid_colors[y, x] = 0
                        self.grid_sel_cells[y, x] = 0
            
            # Calculate new positions after rotation
            for x, y, shape, color in temp_cells:
                # Calculate relative position from center
                rel_x = x - center_x
                rel_y = y - center_y
                
                # Rotate 90° clockwise
                new_x = round(center_x - rel_y)
                new_y = round(center_y + rel_x)
                
                # Rotate triangle shapes
                if shape == 3:
                    new_shape = 6
                elif shape == 4:
                    new_shape = 3
                elif shape == 5:
                    new_shape = 4
                elif shape == 6:
                    new_shape = 5
                else:
                    new_shape = shape
                
                # Update grid if within bounds
                if 0 <= new_x < self.grid_width and 0 <= new_y < self.grid_height:
                    self.grid_bid[new_y, new_x] = new_shape
                    self.grid_colors[new_y, new_x] = color
                    self.grid_sel_cells[new_y, new_x] = 1
            
            # Redraw
            self.draw_bidfile()
            return True
        return False

    def flipv_grid(self):
        """Flip selected cells vertically"""
        if self.grid_sel_cells is not None and np.any(self.grid_sel_cells):
            # Trouver les limites de la sélection
            selected_x = [x for x in range(self.grid_width) for y in range(self.grid_height) if self.grid_sel_cells[y, x] == 1]
            selected_y = [y for x in range(self.grid_width) for y in range(self.grid_height) if self.grid_sel_cells[y, x] == 1]
            min_x = min(selected_x)
            max_x = max(selected_x)
            min_y = min(selected_y)
            max_y = max(selected_y)
            
            # Créer une liste temporaire des cellules sélectionnées
            temp_cells = []
            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    if self.grid_sel_cells[y, x] == 1:
                        temp_cells.append((x, y, self.grid_bid[y, x], self.grid_colors[y, x]))
                        # Effacer la cellule d'origine
                        self.grid_bid[y, x] = 0
                        self.grid_colors[y, x] = 0
            
            # Calculer les nouvelles positions après retournement vertical
            flipped_cells = []
            for cell in temp_cells:
                x, y, shape, color = cell
                # Calculer les coordonnées relatives au centre de la sélection
                rel_x = x - min_x
                rel_y = y - min_y
                
                # Retournement vertical
                new_x = min_x + rel_x
                new_y = max_y - rel_y
                
                # Retournement des formes de triangle
                if shape == 3:
                    new_shape = 4
                elif shape == 4:
                    new_shape = 3
                elif shape == 5:
                    new_shape = 6
                elif shape == 6:
                    new_shape = 5
                else:
                    new_shape = shape
                
                flipped_cells.append((new_x, new_y, new_shape, color))
            
            # Mettre à jour la grille avec les cellules retournées
            for x, y, shape, color in flipped_cells:
                if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                    self.grid_bid[y, x] = shape
                    self.grid_colors[y, x] = color
            
            # Redessiner
            self.draw_bidfile()
            return True
        return False

    def fliph_grid(self):
        """Flip selected cells horizontally"""
        if self.grid_sel_cells is not None and np.any(self.grid_sel_cells):
            # Trouver les limites de la sélection
            selected_x = [x for x in range(self.grid_width) for y in range(self.grid_height) if self.grid_sel_cells[y, x] == 1]
            selected_y = [y for x in range(self.grid_width) for y in range(self.grid_height) if self.grid_sel_cells[y, x] == 1]
            min_x = min(selected_x)
            max_x = max(selected_x)
            min_y = min(selected_y)
            max_y = max(selected_y)
            
            # Créer une liste temporaire des cellules sélectionnées
            temp_cells = []
            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    if self.grid_sel_cells[y, x] == 1:
                        temp_cells.append((x, y, self.grid_bid[y, x], self.grid_colors[y, x]))
                        # Effacer la cellule d'origine
                        self.grid_bid[y, x] = 0
                        self.grid_colors[y, x] = 0
            
            # Calculer les nouvelles positions après retournement horizontal
            flipped_cells = []
            for cell in temp_cells:
                x, y, shape, color = cell
                # Calculer les coordonnées relatives au centre de la sélection
                rel_x = x - min_x
                rel_y = y - min_y
                
                # Retournement horizontal
                new_x = max_x - rel_x
                new_y = min_y + rel_y
                
                # Retournement des formes de triangle
                if shape == 3:
                    new_shape = 6
                elif shape == 4:
                    new_shape = 5
                elif shape == 5:
                    new_shape = 4
                elif shape == 6:
                    new_shape = 3
                else:
                    new_shape = shape
                
                flipped_cells.append((new_x, new_y, new_shape, color))
            
            # Mettre à jour la grille avec les cellules retournées
            for x, y, shape, color in flipped_cells:
                if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                    self.grid_bid[y, x] = shape
                    self.grid_colors[y, x] = color
            
            # Redessiner
            self.draw_bidfile()
            return True
        return False

    def _get_selection_bounds(self):
        """Helper method to get selection boundaries"""
        if self.grid_sel_cells is None or not np.any(self.grid_sel_cells):
            return None, None, None, None
        selected_indices = np.where(self.grid_sel_cells == 1)
        if len(selected_indices[0]) == 0:
            return None, None, None, None
        return (np.min(selected_indices[1]), np.max(selected_indices[1]), 
                np.min(selected_indices[0]), np.max(selected_indices[0]))

    def inverse_grid(self):
        """Inverse selected cells"""
        if self.grid_sel_cells is not None and np.any(self.grid_sel_cells):
            # Utiliser numpy pour une meilleure performance
            selected_indices = np.where(self.grid_sel_cells == 1)
            for y, x in zip(*selected_indices):
                shape, color_indice = self.inverse_cell(self.grid_bid[y, x], self.grid_colors[y, x])
                self.grid_bid[y, x] = shape
                self.grid_colors[y, x] = color_indice
            
            # Redessiner
            self.draw_bidfile()
            return True
        return False

    def get_triangle_points(self, x1, y1, x2, y2, cell_type):
        """Get the points for drawing different types of triangles"""
        if cell_type == 3:  # Bottom right triangle
            return [(x1, y2), (x2, y2), (x2, y1)]
        elif cell_type == 4:  # Top right triangle
            return [(x1, y1), (x2, y1), (x2, y2)]
        elif cell_type == 5:  # Top left triangle
            return [(x1, y1), (x2, y1), (x1, y2)]
        elif cell_type == 6:  # Bottom left triangle
            return [(x1, y2), (x1, y1), (x2, y2)]
        return []  # Return empty list for invalid cell type

if __name__ == '__main__':
    Myclass = BidFile()
    image = Myclass.load_bidfile('bid/balls.bid')
    image.show()