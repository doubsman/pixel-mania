import ttkbootstrap as ttk
from tkinter import filedialog
from tkinter.messagebox import askyesno
from PIL import ImageTk
from bid_class import BidFile
import numpy as np


class Action:
    def __init__(self, grid_bid, grid_colors, grid_sel_cells):
        self.grid_bid = grid_bid
        self.grid_colors = grid_colors
        self.grid_sel_cells = grid_sel_cells

class ImageEditorApp(BidFile):
    def __init__(self, root):
        BidFile.__init__(self)
        self.root = root
        self.tittle = "Image Bid Editor"
        self.root.title(self.tittle)
        self.root.geometry("1600x1550")
        self.root.resizable(width=False, height=False)

        self.WIDTH = 1600-100
        self.HEIGHT = 1550-30
        self.file_path = ""
        self.pen_size = 3
        self.pen_color = "black"
        self.bool_grid = True
        self.bool_backup = False

        self.grid_sel_cells = None
        self.grid_clipboard = None

        self.grid_x = 0
        self.grid_y = 0

        self.current_select_shape = 0
        self.current_select_color = 0

        self.paste_mode = False

        self.selection_start = None
        self.selection_end = None
        self.selection_rect = None
        
        self.history = []

        self.initialize_ui()

    def initialize_ui(self):
        # Set the window icon
        icon = ImageTk.PhotoImage(file='ico/carre.png')
        self.root.iconphoto(False, icon)

        # The left frame to contain the 4 buttons
        left_frame = ttk.Frame(self.root, width=200, height=600)
        left_frame['borderwidth'] = 5
        left_frame.pack(side="left", fill="y")

        open_button = self.create_button(left_frame, 'ico/open.png', self.open_bid, "open")
        new_button = self.create_button(left_frame, 'ico/plus.png', self.create_bid, "New")
        undo_button = self.create_button(left_frame, 'ico/undo.png', self.undo_action, "Cancel")

        color_icon = ttk.PhotoImage(file='ico/invent.png')
        self.palet = ttk.Canvas(left_frame, width=50, height=500)
        self.palet.create_image(0, 0, anchor="nw", image=color_icon)
        self.palet.image = color_icon
        self.palet.pack()
        self.palet.bind("<Button-1>", self.select_palet)
        self.palet.create_rectangle(0, 0, 50, 50, fill="", outline="red", width=2, tags="cell_color")

        area_button = self.create_button(left_frame, 'ico/square.png', self.mode_area, "Select Area")
        select_button = self.create_button(left_frame, 'ico/selection.png', self.mode_select, "Select Cells")
        copy_button = self.create_button(left_frame, 'ico/copy.png', self.copy_cells, "Copy")
        cut_button = self.create_button(left_frame, 'ico/cut.png', lambda: self.copy_cells(True), "Cut")
        paste_button = self.create_button(left_frame, 'ico/paste.png', self.paste_cells, "Cut")
        filpv_button = self.create_button(left_frame, 'ico/flip-v.png', self.flipv_cells, "Flip V")
        filph_button = self.create_button(left_frame, 'ico/flip-h.png', self.fliph_cells, "Flip H")
        grid_button = self.create_button(left_frame, 'ico/grid.png', self.draw_grid, "Flip H")
        save_button = self.create_button(left_frame, 'ico/save.png', self.save_bid, "Save bid")
        saveas_button = self.create_button(left_frame, 'ico/saveas.png', self.saveas_bid, "Save bid")

        # The right canvas for displaying the image
        self.canvas = ttk.Canvas(self.root, width=self.WIDTH, height=self.HEIGHT, border=2)
        self.canvas.pack()
        self.canvas.bind("<Motion>", self.update_coords)

        self.coord_label = ttk.Label(self.root, text="Coords: (0, 0)")
        self.coord_label.pack(side="bottom")

        # create new bid
        self.create_bid()

    def create_button(self, parent, image_path, command, text="", pady=5):
        image = ttk.PhotoImage(file=image_path).subsample(12, 12)
        button = ttk.Button(parent, image=image, bootstyle="outline", command=command, text=text)
        button.image = image
        button.pack(pady=pady)
        return button

    def refresh_image(self):
        image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=image)
        self.canvas.image = image
        if self.bool_grid:
            self.bool_grid = False
            self.draw_grid()

    def open_bid(self):
        self.file_path = filedialog.askopenfilename(title="Open Bid File", filetypes=[("Bid Files", "*.bid")])
        if self.file_path != '':
            self.root.title(f'{self.tittle} [{self.file_path}]')  
            self.load_bidfile(self.file_path, self.WIDTH)
            self.refresh_image()
            self.mode_draw()

    def create_bid(self):
        self.root.title(f'{self.tittle} : [NEW]')
        self.new_bid(self.WIDTH)
        self.refresh_image()
        self.mode_draw()

    def save_bid(self):
        if self.file_path == '' and self.bool_backup:
            self.file_path = filedialog.asksaveasfilename(title="Open Bid File", filetypes=[("Bid Files", "*.bid")])
        self.write_bid()

    def saveas_bid(self):
        if self.bool_backup:
            self.file_path = filedialog.asksaveasfilename(title="Open Bid File", filetypes=[("Bid Files", "*.bid")])
            self.write_bid()
    
    def write_bid(self):
        if self.file_path != '':
            self.save_bidfiles(self.file_path)
            self.file_path = self.path_bid
            self.root.title(f'{self.tittle} [{self.file_path}]')
            self.bool_backup = False

    def select_palet(self, event):
        grid_y = int(event.y / 50)
        x1, y1 = (0), (grid_y * 50)
        x2, y2 = (50), ((grid_y+1) * 50)
        self.palet.delete("cell_color")
        self.palet.create_rectangle(x1, y1, x2, y2, fill="", outline="red", width=2, tags="cell_color")
        if grid_y == 0:
            self.current_select_shape = 0
            self.current_select_color = 0
        elif grid_y > 0 and grid_y < 6:
            self.current_select_shape = 1
            self.current_select_color = grid_y
        elif grid_y > 5:
            self.current_select_shape = grid_y - 3
            self.current_select_color = 5
        self.paste_mode = False
        self.mode_draw()

    def update_coords(self, event):
        self.grid_x = int(event.x / self.image_scale) 
        self.grid_y = int(event.y / self.image_scale)
        if self.grid_y >= self.grid_height:
            self.grid_y = self.grid_height-1
        if self.grid_x >= self.grid_width:
            self.grid_x = self.grid_width-1
        self.coord_label.config(text=f"Coords: ({self.grid_x+1:02d}, {self.grid_y+1:02d})")
        if self.paste_mode:
            clipboard_cells = self.grid_clipboard
            # Déterminer la position à coller les cellules
            grid_x = int(event.x / self.image_scale)
            grid_y = int(event.y / self.image_scale)

            # Dessiner le contour temporaire
            if hasattr(self, 'temp_outline'):
                self.canvas.delete(self.temp_outline)
            min_x = min([cell[0] for cell in clipboard_cells])
            min_y = min([cell[1] for cell in clipboard_cells])
            max_x = max([cell[0] for cell in clipboard_cells])
            max_y = max([cell[1] for cell in clipboard_cells])
            width = (max_x - min_x + 1) * self.image_scale
            height = (max_y - min_y + 1) * self.image_scale
            x1 = grid_x * self.image_scale
            y1 = grid_y * self.image_scale
            self.temp_outline = self.canvas.create_rectangle(x1, y1, x1 + width, y1 + height, outline="red", dash=(4, 4), tags='cells_paste')
        else:
            self.canvas.delete("cells_paste")

    def mode_draw(self):
        self.paste_mode = False
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<Button-1>", self.draw_cellules)

    def draw_cellules(self, event):
        self.save_state()
        self.bool_backup = True
        self.grid_bid[self.grid_y][self.grid_x] = self.current_select_shape
        self.grid_colors[self.grid_y][self.grid_x] = self.current_select_color
        self.draw_cellule(self.grid_x, self.grid_y, self.current_select_shape, self.current_select_color)
        self.refresh_image()

    def mode_area(self):
        self.paste_mode = False
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<ButtonPress-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-1>", self.end_selection)

    def start_selection(self, event):
         # Réinitialiser la sélection
        self.canvas.delete(f"cell_select")
        self.paste_mode = False
        self.grid_sel_cells = np.zeros((self.grid_height, self.grid_width), dtype=int)
        self.grid_clipboard = None        
        self.selection_start = (event.x, event.y)
        self.selection_end = (event.x, event.y)
        self.selection_rect = self.canvas.create_rectangle(
            self.selection_start[0], self.selection_start[1],
            self.selection_end[0], self.selection_end[1],
            outline="blue", dash=(4, 4), tags="selection_rect"
        )

    def update_selection(self, event):
        self.selection_end = (event.x, event.y)
        self.canvas.coords(
            self.selection_rect,
            self.selection_start[0], self.selection_start[1],
            self.selection_end[0], self.selection_end[1]
        )

    def end_selection(self, event):
        self.selection_end = (event.x, event.y)
        self.update_selected_cells()
        self.canvas.delete("selection_rect")

    def update_selected_cells(self):
        start_x = min(self.selection_start[0], self.selection_end[0]) // self.image_scale
        start_y = min(self.selection_start[1], self.selection_end[1]) // self.image_scale
        end_x = max(self.selection_start[0], self.selection_end[0]) // self.image_scale
        end_y = max(self.selection_start[1], self.selection_end[1]) // self.image_scale

        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                self.grid_sel_cells[y, x] = 1
                x1, y1 = (x * self.image_scale), (y * self.image_scale)
                x2, y2 = ((x+1) * self.image_scale), ((y+1) * self.image_scale)
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="red", width=2, tags=['cell_select', f"cell_select{x}_{y}"])

    def mode_select(self):
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<Button-1>", self.select_cellules)
         # Réinitialiser la sélection
        self.canvas.delete(f"cell_select")
        self.paste_mode = False
        self.grid_sel_cells = np.zeros((self.grid_height, self.grid_width), dtype=int)
        self.grid_clipboard = None

    def select_cellules(self, event):
        if self.grid_sel_cells[self.grid_y, self.grid_x] == 1:
            self.grid_sel_cells[self.grid_y, self.grid_x] = 0
            self.canvas.delete(f"cell_select{self.grid_x}_{self.grid_y}")
        elif self.grid_sel_cells[self.grid_y, self.grid_x] == 0:
            self.grid_sel_cells[self.grid_y, self.grid_x] = 1
            x1, y1 = (self.grid_x * self.image_scale), (self.grid_y * self.image_scale)
            x2, y2 = ((self.grid_x+1) * self.image_scale), ((self.grid_y+1) * self.image_scale)
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="red", width=2, tags=['cell_select', f"cell_select{self.grid_x}_{self.grid_y}"])

    def copy_cells(self, cut=False):
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.delete(f"cell_select")
        self.grid_clipboard = []

        selected_cells = []
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid_sel_cells[y, x] == 1:
                    selected_cells.append((x, y, self.grid_bid[y][x], self.grid_colors[y][x]))
                    if cut:
                        self.draw_cellule(x, y, 0, 0)
        if cut:                        
            self.refresh_image()
        self.grid_clipboard = selected_cells

    def flipv_cells(self):
        """Flip verticale des cellules dans le presse-papiers."""
        if hasattr(self, 'grid_clipboard') and self.grid_clipboard:
            max_y = max(cell[1] for cell in self.grid_clipboard)
            min_y = min(cell[1] for cell in self.grid_clipboard)
            flips = []
            for cell in self.grid_clipboard:
                x, y, shape, color = cell
                new_y = max_y + min_y - y
                # Inverser les shapes des triangles
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
                flips.append((x, new_y, new_shape, color))
            self.grid_clipboard = flips

    def fliph_cells(self):
        """Flip horizontale des cellules dans le presse-papiers."""
        if hasattr(self, 'grid_clipboard') and self.grid_clipboard:
            max_x = max(cell[0] for cell in self.grid_clipboard)
            min_x = min(cell[0] for cell in self.grid_clipboard)
            flips = []
            for cell in self.grid_clipboard:
                x, y, shape, color = cell
                new_x = max_x + min_x - x
                # Inverser les shapes des triangles
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
                flips.append((new_x, y, new_shape, color))
            self.grid_clipboard = flips

    def paste_cells(self):
        if hasattr(self, 'grid_clipboard') and self.grid_clipboard:
            self.paste_mode = True  # Activer le mode de collage
            self.canvas.bind("<Button-1>", self.paste_cells_on_canvas)

    def paste_cells_on_canvas(self, event):
        if self.paste_mode:
            self.save_state()
            self.bool_backup = True
            clipboard_cells = self.grid_clipboard
            # Déterminer la position à coller les cellules
            grid_x = int(event.x / self.image_scale)
            grid_y = int(event.y / self.image_scale)
            
            # Coller les cellules
            min_x = min([cell[0] for cell in clipboard_cells])
            min_y = min([cell[1] for cell in clipboard_cells])
            for cell in clipboard_cells:
                x, y, shape, color = cell
                new_x = grid_x + (x - min_x)
                new_y = grid_y + (y - min_y)
                if 0 <= new_x < self.grid_width and 0 <= new_y < self.grid_height:
                    self.grid_bid[new_y][new_x] = shape
                    self.grid_colors[new_y][new_x] = color
                    self.draw_cellule(new_x, new_y, shape, color)
            self.refresh_image()

    def draw_grid(self):
        if not self.bool_grid:
            width_image = self.grid_width * self.image_scale
            height_image = self.grid_height * self.image_scale
            for line in range(0, width_image, self.image_scale):
                self.canvas.create_line([(line, 0), (line , height_image)], fill='grey', dash=(1,1), tags='grid_line_w')
            for line in range(0, height_image, self.image_scale):
                self.canvas.create_line([(0, line), (width_image, line)], fill='grey', dash=(1,1), tags='grid_line_h')
            self.bool_grid = True
        else:
            self.canvas.delete('grid_line_w')
            self.canvas.delete('grid_line_h')
            self.bool_grid = False

    def undo_action(self):
        self.restore_state()

    def save_state(self):
        """Sauvegarde l'état actuel dans l'historique."""
        action = Action(
            np.copy(self.grid_bid),
            np.copy(self.grid_colors),
            np.copy(self.grid_sel_cells)
        )
        self.history.append(action)

    def restore_state(self):
        """Restaure l'état précédent à partir de l'historique."""
        if self.history:
            action = self.history.pop()
            self.grid_bid = action.grid_bid
            self.grid_colors = action.grid_colors
            self.grid_sel_cells = action.grid_sel_cells
            self.draw_bidfile()
            self.refresh_image()

if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    app = ImageEditorApp(root)
    root.mainloop()