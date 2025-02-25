import ttkbootstrap as ttk
from tkinter import filedialog
from tkinter.messagebox import showerror, askyesno
from tkinter import colorchooser
from PIL import Image, ImageOps, ImageTk, ImageFilter, ImageGrab
from bid_class import BidFile
import numpy as np

class ImageEditorApp(BidFile):
    def __init__(self, root):
        BidFile.__init__(self)
        self.root = root
        self.root.title("Image Editor")
        self.root.geometry("1024x1024")
        self.root.resizable(width=False, height=False)

        self.WIDTH = 1024-200
        self.HEIGHT = 1024-30
        self.file_path = ""
        self.pen_size = 3
        self.pen_color = "black"
        self.bool_grid = False

        self.grid_bid_backup = None
        self.grid_sel_cells = None

        self.grid_x = 0
        self.grid_y = 0

        self.current_select_shape = 0
        self.current_select_color = 0

        self.initialize_ui()

    def initialize_ui(self):
        # Set the window icon
        icon = ImageTk.PhotoImage(file='png/carre.png')
        self.root.iconphoto(False, icon)

        # The left frame to contain the 4 buttons
        left_frame = ttk.Frame(self.root, width=200, height=600)
        left_frame['borderwidth'] = 5
        left_frame.pack(side="left", fill="y")

        image_icon = ttk.PhotoImage(file='ico/open.png').subsample(12,12)
        image_button = ttk.Button(left_frame, image=image_icon, bootstyle="light", command=self.open_image)
        image_button.image = image_icon
        image_button.pack(pady=5)

        color_icon = ttk.PhotoImage(file='ico/draw.png').subsample(12,12)
        color_button = ttk.Button(left_frame, image=color_icon, bootstyle="light", command=self.mode_draw)
        color_button.image = color_icon
        color_button.pack(pady=5)

        select_icon = ttk.PhotoImage(file='ico/select.png').subsample(12,12)
        select_button = ttk.Button(left_frame, image=select_icon, bootstyle="light", command=self.mode_select)
        select_button.image = select_icon
        select_button.pack(pady=5)

        grid_icon = ttk.PhotoImage(file='ico/grid.png').subsample(12,12)
        grid_button = ttk.Button(left_frame, image=grid_icon, bootstyle="light", command=self.draw_grid)
        grid_button.image = grid_icon
        grid_button.pack(pady=5)

        color_icon = ttk.PhotoImage(file='ico/invent.png')
        self.palet = ttk.Canvas(left_frame, width=50, height=500)
        self.palet.create_image(0, 0, anchor="nw", image=color_icon)
        self.palet.image = color_icon
        self.palet.pack()
        self.palet.bind("<Button-1>", self.select_color)
        self.palet.create_rectangle(0, 0, 50, 50, fill="", outline="red", width=2, tags="cell_color")

        save_icon = ttk.PhotoImage(file='ico/save.png').subsample(12,12)
        save_button = ttk.Button(left_frame, image=save_icon, bootstyle="light", command=self.save_image)
        save_button.image = save_icon
        save_button.pack(pady=5)

        # The right canvas for displaying the image
        self.canvas = ttk.Canvas(self.root, width=self.WIDTH, height=self.HEIGHT)
        self.canvas.pack()
        self.canvas.bind("<Motion>", self.update_coords)

        self.coord_label = ttk.Label(self.root, text="Coords: (0, 0)")
        self.coord_label.pack(side="bottom")

    def open_image(self):
        self.file_path = filedialog.askopenfilename(title="Open Bid File", filetypes=[("Bid Files", "*.bid")])
        if self.file_path:
            imagebid = self.load_bidfile(self.file_path, self.WIDTH)
            image = ImageTk.PhotoImage(imagebid)
            self.canvas.create_image(0, 0, anchor="nw", image=image)
            self.canvas.image = image
            self.grid_bid_backup = self.grid_bid
            self.grid_sel_cells = np.zeros((self.grid_height, self.grid_width), dtype=int)

    def save_image(self):
        pass

    def select_color(self, event):
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
        print(self.current_select_shape,self.current_select_color)

    def update_coords(self, event):
        self.coord_label
        self.grid_x = int(event.x / self.image_scale) 
        self.grid_y = int(event.y / self.image_scale)
        self.coord_label.config(text=f"Coords: ({self.grid_x+1}, {self.grid_y+1})")

    def mode_draw(self):
        self.canvas.bind("<Button-1>", self.draw_cellules)

    def draw_cellules(self, event):
        self.grid_bid[self.grid_y][self.grid_x] = self.current_select_shape
        self.grid_colors[self.grid_y][self.grid_x] = self.current_select_color
        self.draw_cellule(self.grid_x, self.grid_y, self.current_select_shape, self.current_select_color)
        image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=image)
        self.canvas.image = image
        if self.bool_grid:
            self.bool_grid = False
            self.draw_grid()

    def mode_select(self):
        self.canvas.bind("<Button-1>", self.select_cellules)

    def select_cellules(self, event):
        if self.grid_sel_cells[self.grid_y, self.grid_x] == 1:
            self.grid_sel_cells[self.grid_y, self.grid_x] = 0
            self.canvas.delete(f"cell_select{self.grid_x}_{self.grid_y}")
        elif self.grid_sel_cells[self.grid_y, self.grid_x] == 0:
            self.grid_sel_cells[self.grid_y, self.grid_x] = 1
            x1, y1 = (self.grid_x * self.image_scale), (self.grid_y * self.image_scale)
            x2, y2 = ((self.grid_x+1) * self.image_scale), ((self.grid_y+1) * self.image_scale)
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="red", width=2, tags=f"cell_select{self.grid_x}_{self.grid_y}")

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

    def change_color(self):
        self.pen_color = colorchooser.askcolor(title="Select Pen Color")[1]


if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    app = ImageEditorApp(root)
    root.mainloop()
