import numpy as np


class Action:
    def __init__(self, grid_bid, grid_colors, grid_clipboard, grid_sel_cells, grid_width, grid_height):
        self.grid_bid = grid_bid
        self.grid_colors = grid_colors
        self.grid_clipboard = grid_clipboard
        self.grid_sel_cells = grid_sel_cells
        self.grid_width = grid_width
        self.grid_height = grid_height

class ActionState():
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []
        
    def save_actionstate(self, grid_bid, grid_colors, grid_clipboard, grid_sel_cells, grid_width, grid_height):
        """Sauvegarde l'état actuel dans l'historique."""
        action = Action(
            np.copy(grid_bid),
            np.copy(grid_colors),
            np.copy(grid_clipboard),
            np.copy(grid_sel_cells),
            grid_width,
            grid_height
        )
        self.undo_stack.append(action)
        self.redo_stack.clear()
    
    def undo_actionstate(self):
        if self.undo_stack:
            action = self.undo_stack.pop()
            self.redo_stack.append(action)
            return action
        else:
            return None

    def redo_actionstate(self):
        if self.redo_stack:
            action = self.redo_stack.pop()
            self.undo_stack.append(action)
            return action
        else:
            return None
            