import numpy as np


class Action:
    def __init__(self, grid_bid, grid_colors, grid_clipboard, grid_sel_cells):
        self.grid_bid = grid_bid
        self.grid_colors = grid_colors
        self.grid_clipboard = grid_clipboard
        self.grid_sel_cells = grid_sel_cells

class ActionState():
    def __init__(self):
        self.history = []
        
    def save_actionstate(self, grid_bid, grid_colors, grid_clipboard, grid_sel_cells):
        """Sauvegarde l'état actuel dans l'historique."""
        action = Action(
            np.copy(grid_bid),
            np.copy(grid_colors),
            np.copy(grid_clipboard),
            np.copy(grid_sel_cells)
        )
        self.history.append(action)
    
    def restore_actionstate(self):
        if self.history:
            return self.history.pop()
        else:
            return None
            