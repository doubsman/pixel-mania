import numpy as np

class Grid:
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid_bid = np.zeros((grid_height, grid_width))
        self.grid_colors = np.zeros((grid_height, grid_width))

    def change_dimension(self, grid_width, grid_height):
        if grid_width < self.grid_width or grid_height < self.grid_height:
            self.reduce_grid(grid_width, grid_height)
        if grid_width > self.grid_width or grid_height > self.grid_height:
            self.extend_grid(grid_width, grid_height)
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.draw_bidfile()

    def extend_grid(self, grid_width, grid_height):
        extend_rows = max(0, (grid_height - self.grid_height) // 2)
        extend_columns = max(0, (grid_width - self.grid_width) // 2)
        print(grid_width, grid_height, extend_rows, extend_columns)

        self.grid_bid = np.pad(self.grid_bid, ((extend_rows, extend_rows), (extend_columns, extend_columns)), mode='constant', constant_values=0)
        self.grid_colors = np.pad(self.grid_colors, ((extend_rows, extend_rows), (extend_columns, extend_columns)), mode='constant', constant_values=0)

    def reduce_grid(self, grid_width, grid_height):
        reduce_rows = (self.grid_height - grid_height) // 2
        reduce_columns = (self.grid_width - grid_width) // 2

        start_row = reduce_rows
        end_row = self.grid_height - reduce_rows
        start_col = reduce_columns
        end_col = self.grid_width - reduce_columns

        self.grid_bid = self.grid_bid[start_row:end_row, start_col:end_col]
        self.grid_colors = self.grid_colors[start_row:end_row, start_col:end_col]

    def draw_bidfile(self):
        # Implement your draw_bidfile method here
        pass

# Example usage
grid = Grid(5, 5)
grid.grid_bid = np.random.randint(0, 10, (5, 5))
grid.grid_colors = np.random.randint(0, 10, (5, 5))
print("Original Grid Bid:")
print(grid.grid_bid)
print("Original Grid Colors:")
print(grid.grid_colors)

grid.change_dimension(7, 7)
print("Extended Grid Bid:")
print(grid.grid_bid)
print("Extended Grid Colors:")
print(grid.grid_colors)

grid.change_dimension(3, 3)
print("Reduced Grid Bid:")
print(grid.grid_bid)
print("Reduced Grid Colors:")
print(grid.grid_colors)
