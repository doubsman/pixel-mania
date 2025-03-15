import ttkbootstrap as ttk
from tkinter import filedialog
from tkinter.messagebox import askyesno
from PIL import ImageTk, Image
import numpy as np
import os
import subprocess
from pynput.keyboard import Key, Controller, Listener
from class_bid import BidFile
from class_cells import Cells
from class_canvas import ManageCanvas
from class_action import ActionState


class ImageEditorApp(BidFile, ManageCanvas, ActionState):
    def __init__(self, root):
        BidFile.__init__(self)
        ActionState.__init__(self)
        self.root = root
        self.tittle = "Image Bid Editor"
        self.root.title(self.tittle)
        self.root.geometry("1700x1520")
        self.root.resizable(width=False, height=False)

        self.WIDTH = 1700-200-100
        self.HEIGHT = 1520-20-100
        self.file_path = ""
        # Mode Grill Canvas
        self.bool_grid = True
        # Backup BID necessary
        self.bool_backup = False
        # Selection
        self.grid_sel_cells = []
        # Clipboard
        self.grid_clipboard = []
        self.clipboard = Cells()
        # (x,y) Curent position cursor
        self.grid_x = 1
        self.grid_y = 1
        # Selection palette
        self.current_select_shape = 0
        self.current_select_color = 0
        # Mode selection Area 
        self.selection_start = None
        self.selection_end = None
        self.selection_rect = None
        # Mode selection ADD +
        self.bool_mode_add_selection = False
        # Mode Past Cells
        self.bool_paste_mode = False
        # Pasted Image ID
        self.image_over_id = 0
	    # Collect events until released
        listener = Listener(on_press=self.on_press)
        listener.start()
        self.controler = Controller()
        
        self.initialize_ui()

    def initialize_ui(self):
        # Set the window icon
        icon = ImageTk.PhotoImage(file='ico/carre.png')
        self.root.iconphoto(False, icon)

        # The left frame to contain the 4 buttons
        left_frame = ttk.Frame(self.root)
        left_frame['borderwidth'] = 5
        left_frame.pack(side="left", fill="y")

        left_frame2 = ttk.Frame(self.root)
        left_frame2['borderwidth'] = 5
        left_frame2.pack(side="left", fill="y")

        open_button = self.create_button(left_frame, 'ico/open.png', self.open_bid, "open")
        new_button = self.create_button(left_frame2, 'ico/plus.png', self.create_bid, "New")
        save_button = self.create_button(left_frame, 'ico/save.png', self.save_bid, "Save bid")
        saveas_button = self.create_button(left_frame2, 'ico/saveas.png', self.saveas_bid, "Save bid")
        magic_button = self.create_button(left_frame, 'ico/magic.png', self.mode_magicselect, "Select Magic")
        undo_button = self.create_button(left_frame2, 'ico/undo.png', self.undo_action, "Cancel")
        select_button = self.create_button(left_frame, 'ico/selection.png', self.mode_select, "Select Cells")
        area_button = self.create_button(left_frame2, 'ico/square.png', self.mode_area, "Select Area")
        copy_button = self.create_button(left_frame, 'ico/copy.png', self.copy_cells, "Copy")
        paste_button = self.create_button(left_frame2, 'ico/paste.png', self.paste_cells, "Cut")
        cut_button = self.create_button(left_frame, 'ico/cut.png', lambda: self.copy_cells(True), "Cut")
        filpv_button = self.create_button(left_frame, 'ico/flip-v.png', self.flipv_cells, "Flip V")
        filph_button = self.create_button(left_frame, 'ico/flip-h.png', self.fliph_cells, "Flip H")
        rotate_l_button = self.create_button(left_frame, 'ico/rotate-left.png', self.rotate_l_cells, "Flip V")
        rotate_r_button = self.create_button(left_frame, 'ico/rotate-right.png', self.rotate_r_cells, "Flip H")
        inverse_button = self.create_button(left_frame, 'ico/inverser.png', self.inverse_colors, "Grid")
        fill_button = self.create_button(left_frame, 'ico/fill.png', self.fill_cells, "Grid")
        grid_button = self.create_button(left_frame, 'ico/grid.png', self.draw_grid, "Grid")
        save_image_button = self.create_button(left_frame, 'ico/photo.png', self.save_image, "Save Image")
        folder_button = self.create_button(left_frame, 'ico/folder.png', self.open_folder, "Save Image")
        
        color_icon = ttk.PhotoImage(file='ico/invent.png')
        self.palet = ttk.Canvas(left_frame2, width=50, height=500)
        self.palet.create_image(0, 0, anchor="nw", image=color_icon)
        self.palet.image = color_icon
        self.palet.pack()
        self.palet.bind("<Button-1>", self.select_palet)
        self.palet.create_rectangle(0, 0, 50, 50, fill="", outline="red", width=2, tags="cell_color")
        
        self.mode_copy = ttk.Label(left_frame2, text="-")
        self.mode_copy.pack(side="bottom")

        self.thumbnail_canvas = ttk.Canvas(left_frame2, width=80, height=80, border=2, relief="sunken", bg='lightblue')
        self.thumbnail_canvas.pack(side="bottom", fill="y")
        self.thumbnail_canvas.pack_propagate(False)

        self.coord_label = ttk.Label(left_frame, text="(00, 00)")
        self.coord_label.pack(side="bottom")

        save_symbol = self.create_button(left_frame, 'ico/save.png', self.save_grid_clipboard, "Save Symbol", 'bottom', 25)
        load_symbol = self.create_button(left_frame, 'ico/open.png', self.open_grid_clipboard, "Save Symbol", 'bottom', 25)

        # The right canvas for displaying the image
        self.outercanvas = ttk.Canvas(self.root, width=self.WIDTH + 100, height=self.HEIGHT + 100, bg='lightblue')
        self.outercanvas.pack(expand="y", fill="y")
        self.canvas = ttk.Canvas(self.outercanvas, width=self.WIDTH, height=self.HEIGHT, border=2, relief="sunken")
        self.outercanvas.create_window(50, 50, window=self.canvas, anchor=ttk.NW)

        self.canvas.bind("<Motion>", self.update_coords_cells)
        self.root.bind("<Control-z>", self.undo_action)

        # create new bid
        self.create_bid()

    def create_button(self, parent, image_path, command, text="", side='top', subsample=12, pady=5):
        image = ttk.PhotoImage(file=image_path).subsample(subsample, subsample)
        button = ttk.Button(parent, image=image, bootstyle="outline", command=command, text=text)
        button.image = image
        button.pack(pady=pady, side=side)
        return button

    def open_bid(self):
        bid_path = filedialog.askopenfilename(title="Open Bid File", filetypes=[("Bid Files", "*.bid")])
        if bid_path != '':
            self.file_path = bid_path
            self.root.title(f'{self.tittle} [{self.file_path}]')  
            self.load_bidfile(self.file_path, self.WIDTH, self.HEIGHT)
            self.init_bid()

    def create_bid(self):
        self.root.title(f'{self.tittle} : [NEW]')
        self.file_path = ''
        self.new_bid(self.WIDTH, self.HEIGHT)
        self.init_bid()
    
    def init_bid(self):
        self.WIDTH, self.HEIGHT = self.image.size
        self.canvas.config(width=self.WIDTH, height=self.HEIGHT)
        self.clipboard.image_scale = self.image_scale
        self.grid_sel_cells = np.zeros((self.grid_height, self.grid_width), dtype=int)
        self.refresh_image()
        self.mode_draw()

    def save_bid(self):
        if self.file_path == '' and self.bool_backup:
            self.file_path = filedialog.asksaveasfilename(title="Open Bid File", filetypes=[("Bid Files", "*.bid")])
        self.write_bid()

    def saveas_bid(self):
        if self.bool_backup or self.file_path != '':
            self.file_path = filedialog.asksaveasfilename(title="Save Bid File", filetypes=[("Bid Files", "*.bid")])
            self.write_bid()
    
    def write_bid(self):
        if self.file_path != '':
            self.save_bidfile(self.file_path)
            self.file_path = self.path_bid
            self.root.title(f'{self.tittle} [{self.file_path}]')
            self.bool_backup = False

    def save_image(self):
        if self.file_path == '':
            file_img = filedialog.asksaveasfilename(title="Save PNG File", filetypes=[("PNG Image Files", "*.png")])
        else:
            file_img = self.file_path.replace('.bid',f'_{self.grid_width}x{self.grid_height}.png')
        self.save_imagefile(file_img, bool_outline=self.bool_grid)

    def open_folder(self):
        if self.file_path != '':
            open_path = os.path.dirname(self.file_path).replace('/','\\')
            subprocess.Popen(fr'explorer "{open_path}"')

    def open_grid_clipboard(self):
        path_symbol = filedialog.askopenfilename(title="Open Symbol File", filetypes=[("Symbol Files", "*.sym")], initialdir='./sym')
        if os.path.isfile(path_symbol):
            self.grid_clipboard = self.clipboard.load_symbol(path_symbol)
            self.refresh_thumbnail()
            self.paste_cells()

    def save_grid_clipboard(self):
        if hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            number = 1
            path_symbol = os.path.join('sym', f'symbol{number:03d}.sym')
            while os.path.isfile(path_symbol):
                number += 1
                path_symbol = os.path.join('sym', f'symbol{number:03d}.sym')
            np.savetxt(path_symbol, self.grid_clipboard, fmt='%i', delimiter=";")

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
        self.bool_paste_mode = False
        if self.image_over_id !=0:
            self.canvas.delete(self.image_over_id)
            self.image_over_id = 0
        self.mode_draw()

    def update_coords_cells(self, event):
        # Update position grid
        self.grid_x = int(event.x / self.image_scale) 
        self.grid_y = int(event.y / self.image_scale)
        if self.grid_y >= self.grid_height:
            self.grid_y = self.grid_height-1
        if self.grid_x >= self.grid_width:
            self.grid_x = self.grid_width-1
        self.coord_label.config(text=f"({self.grid_x+1:02d}, {self.grid_y+1:02d})")

        if self.bool_paste_mode and len(self.grid_clipboard) > 0 :
            # Determine the position to paste the cells
            grid_clipboard_x = int((self.clipboard.max_x - self.clipboard.min_x)/2)
            grid_clipboard_y = int((self.clipboard.max_y - self.clipboard.min_y)/2)
            x1 = (self.grid_x - grid_clipboard_x) * self.image_scale
            y1 = (self.grid_y - grid_clipboard_y) * self.image_scale
            overview_tk = ImageTk.PhotoImage(self.clipboard.symbol_image)
            self.image_over_id = self.canvas.create_image(x1, y1, anchor="nw", image=overview_tk)
            self.canvas.image_sur = overview_tk

    def refresh_image(self):
        image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=image)
        self.canvas.image = image
        # Draw selected cells     
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid_sel_cells[y, x] == 1:
                    x1, y1 = (x * self.image_scale), (y * self.image_scale)
                    x2, y2 = ((x+1) * self.image_scale), ((y+1) * self.image_scale)
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="red", width=2, tags=['cell_select', f"cell_select{x}_{y}"])
        if self.bool_grid:
            self.bool_grid = False
            self.draw_grid()

    def refresh_thumbnail(self, dimension = 80):
        if hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            thumbnail = self.clipboard.symbol_image
            ratio = self.clipboard.symbol_width / self.clipboard.symbol_height
            if ratio > 1:
                thumbnail = thumbnail.resize((dimension, int(dimension/ratio)), Image.LANCZOS)
            else:
                thumbnail = thumbnail.resize((int(dimension*ratio), dimension), Image.LANCZOS)
            self.center_image_on_canvas(self.thumbnail_canvas, thumbnail)

    def mode_draw(self):
        self.bool_paste_mode = False
        if self.image_over_id !=0:
            self.canvas.delete(self.image_over_id)
            self.image_over_id = 0
        #self.canvas.delete(f"cell_select")
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.bind("<Button-1>", self.draw_canvas)

    def draw_canvas(self, event):
        self.save_state()
        self.bool_backup = True
        self.grid_bid[self.grid_y][self.grid_x] = self.current_select_shape
        self.grid_colors[self.grid_y][self.grid_x] = self.current_select_color
        self.draw_cell(self.grid_x, self.grid_y, self.current_select_shape, self.current_select_color)
        self.refresh_image()

    def mode_area(self):
        self.bool_paste_mode = False
        if self.image_over_id !=0:
            self.canvas.delete(self.image_over_id)
            self.image_over_id = 0
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<ButtonPress-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-1>", self.end_selection)

    def start_selection(self, event):
        if not self.bool_mode_add_selection:
            self.canvas.delete(f"cell_select")
        self.bool_paste_mode = False
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
        self.bool_paste_mode = False
        self.bool_mode_add_selection = False
        self.controler.press(Key.ctrl_l)
        if self.image_over_id !=0:
            self.canvas.delete(self.image_over_id)
            self.image_over_id = 0

    def select_cellules(self, event):
        if not self.bool_mode_add_selection:
            self.grid_sel_cells = np.zeros((self.grid_height, self.grid_width), dtype=int)
            self.canvas.delete("cell_select")
        if self.grid_sel_cells[self.grid_y, self.grid_x] == 1:
            self.grid_sel_cells[self.grid_y, self.grid_x] = 0
            self.canvas.delete(f"cell_select{self.grid_x}_{self.grid_y}")
        elif self.grid_sel_cells[self.grid_y, self.grid_x] == 0:
            self.grid_sel_cells[self.grid_y, self.grid_x] = 1
            x1, y1 = (self.grid_x * self.image_scale), (self.grid_y * self.image_scale)
            x2, y2 = ((self.grid_x+1) * self.image_scale), ((self.grid_y+1) * self.image_scale)
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="red", width=2, tags=['cell_select', f"cell_select{self.grid_x}_{self.grid_y}"])

    def mode_magicselect(self):
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<Button-1>", self.magic_select_cellules)
        self.bool_paste_mode = False
        self.bool_mode_add_selection = False
        self.controler.press(Key.ctrl_l)
        if self.image_over_id != 0:
            self.canvas.delete(self.image_over_id)
            self.image_over_id = 0

    def magic_select_cellules(self, event):
        if not self.bool_mode_add_selection:
            self.grid_sel_cells = np.zeros((self.grid_height, self.grid_width), dtype=int)
            self.canvas.delete(f"cell_select")
        grid_x = self.grid_x
        grid_y = self.grid_y
        # Récupérer la couleur de la cellule cliquée
        cell_color = self.grid_colors[grid_y, grid_x]
        # Sélectionner les cellules de la même couleur qui sont collées à la cellule cliquée
        self.select_adjacent_cells(grid_x, grid_y, cell_color)
        # Mettre à jour l'affichage
        self.update_magic_selection()

    def select_adjacent_cells(self, x, y, color):
        # Vérifier si la cellule est dans les limites du grid
        if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height:
            return
        # Vérifier si la cellule a déjà été sélectionnée
        if self.grid_sel_cells[y, x] == 1:
            return
        # Vérifier si la cellule a la même couleur que la cellule cliquée
        if self.grid_colors[y, x] != color:
            return
        # Sélectionner la cellule
        self.grid_sel_cells[y, x] = 1
        # Sélectionner les cellules adjacentes
        self.select_adjacent_cells(x-1, y, color)
        self.select_adjacent_cells(x+1, y, color)
        self.select_adjacent_cells(x, y-1, color)
        self.select_adjacent_cells(x, y+1, color)

    def update_magic_selection(self):
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid_sel_cells[y, x] == 1:
                    x1, y1 = (x * self.image_scale), (y * self.image_scale)
                    x2, y2 = ((x+1) * self.image_scale), ((y+1) * self.image_scale)
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="red", width=2, tags=['cell_select', f"cell_select{x}_{y}"])

    def copy_cells(self, cut=False):
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.unbind("<Button-1>")

        selected_cells = []
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid_sel_cells[y, x] == 1:
                    selected_cells.append((x, y, self.grid_bid[y][x], self.grid_colors[y][x]))
                    if cut:
                        self.draw_cell(x, y, 0, 0)
                        self.grid_bid[y, x] = 0
                        self.grid_colors[y, x] = 0
        if cut:
            self.save_state()                      
            self.refresh_image()

        if not self.bool_mode_add_selection:
            self.grid_clipboard = selected_cells
        else: 
            self.grid_clipboard += selected_cells
        self.clipboard.insert_symbol(self.grid_clipboard)
        self.refresh_thumbnail()
        self.canvas.delete(f"cell_select")
        self.grid_sel_cells = np.zeros((self.grid_height, self.grid_width), dtype=int)

    def paste_cells(self):
        if hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            # mode Past Activate
            self.bool_paste_mode = True  
            self.canvas.unbind("<ButtonPress-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
            self.canvas.bind("<Button-1>", self.paste_cells_on_canvas)

    def paste_cells_on_canvas(self, event):
        if self.bool_paste_mode:
            self.save_state()
            self.bool_backup = True
            
            grid_clipboard_x = int((self.clipboard.max_x - self.clipboard.min_x)/2)
            grid_clipboard_y = int((self.clipboard.max_y - self.clipboard.min_y)/2)
            for cell in self.grid_clipboard:
                x, y, shape, color = cell
                new_x = self.grid_x + (x - self.clipboard.min_x) - grid_clipboard_x
                new_y = self.grid_y + (y - self.clipboard.min_y) - grid_clipboard_y
                if 0 <= new_x < self.grid_width and 0 <= new_y < self.grid_height:
                    self.grid_bid[new_y][new_x] = shape
                    self.grid_colors[new_y][new_x] = color
                    self.draw_cell(new_x, new_y, shape, color)
            self.refresh_image()

    def flipv_cells(self):
        if hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            self.grid_clipboard = self.clipboard.flipv_cells()
            self.refresh_thumbnail()

    def fliph_cells(self):
        if hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            self.grid_clipboard = self.clipboard.fliph_cells()
            self.refresh_thumbnail()

    def rotate_l_cells(self):
        if hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            self.grid_clipboard = self.clipboard.rotate_l_cells()
            self.refresh_thumbnail()
    
    def rotate_r_cells(self):
        if hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            self.grid_clipboard = self.clipboard.rotate_r_cells()
            self.refresh_thumbnail()

    def inverse_colors(self):
        if len(self.canvas.gettags("cell_select")) > 0:
            self.save_state()
            for y in range(self.grid_height):
                for x in range(self.grid_width):
                    if self.grid_sel_cells[y, x] == 1:
                        color_indice = self.grid_colors[y, x]
                        shape = self.grid_bid[y, x]
                        shape, color_indice = self.inverse_cell(shape, color_indice)
                        self.grid_colors[y, x] = color_indice
                        self.grid_bid[y, x] = shape
                        self.draw_cell(x, y, self.grid_bid[y, x], self.grid_colors[y, x], False)
            self.refresh_image()
        elif hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            self.grid_clipboard = self.clipboard.inverse_colors()
            self.refresh_thumbnail()

    def fill_cells(self):
        if len(self.canvas.gettags("cell_select")) > 0:
            self.save_state()
            for y in range(self.grid_height):
                for x in range(self.grid_width):
                    if self.grid_sel_cells[y, x] == 1:
                        self.grid_colors[y, x] = self.current_select_color
                        self.grid_bid[y, x] = self.current_select_shape
                        self.draw_cell(x, y, self.grid_bid[y, x], self.grid_colors[y, x], False)
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

    def undo_action(self, event=None):
        self.restore_state()

    def save_state(self):
        self.save_actionstate(self.grid_bid, self.grid_colors, self.grid_clipboard, self.grid_sel_cells)

    def restore_state(self):
        action = self.restore_actionstate()
        if action is not None:
            self.grid_bid = action.grid_bid
            self.grid_colors = action.grid_colors
            self.grid_clipboard = action.grid_clipboard
            self.grid_sel_cells = action.grid_sel_cells
            self.draw_bidfile()
            self.refresh_image()
            self.refresh_thumbnail()

    def on_press(self, key):
        if key == Key.ctrl_l or key == Key.ctrl_r:
            self.bool_mode_add_selection = not self.bool_mode_add_selection
            if self.bool_mode_add_selection:
                self.mode_copy.config(text=f"CTRL (✚)")
            else:
                self.mode_copy.config(text=f"")
        

if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    app = ImageEditorApp(root)
    root.mainloop()