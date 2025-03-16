import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk

class ImageViewer(ttk.Frame):
    def __init__(self, master, image, grid_spacing=50):
        super().__init__(master)
        self.master = master
        self.image = image
        self.grid_spacing = grid_spacing

        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill=BOTH, expand=True)

        self.canvas = ttk.Canvas(self.canvas_frame, width=800, height=600)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.vscrollbar = ttk.Scrollbar(self.canvas_frame, orient=VERTICAL, command=self.canvas.yview)
        self.vscrollbar.grid(row=0, column=1, sticky="ns")

        self.hscrollbar = ttk.Scrollbar(self.canvas_frame, orient=HORIZONTAL, command=self.canvas.xview)
        self.hscrollbar.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(yscrollcommand=self.vscrollbar.set, xscrollcommand=self.hscrollbar.set)

        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.move_image)

        self.photo = ImageTk.PhotoImage(self.image)

        self.canvas_image = self.canvas.create_image(0, 0, anchor=NW, image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))

        self.zoom_factor = 1.0
        self.start_x = None
        self.start_y = None

        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        self.draw_grid()

    def zoom(self, event):
        if event.delta > 0:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor /= 1.1

        new_size = (int(self.image.width * self.zoom_factor), int(self.image.height * self.zoom_factor))
        self.photo = ImageTk.PhotoImage(self.image.resize(new_size))
        self.canvas.itemconfig(self.canvas_image, image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))

        self.draw_grid()

    def start_move(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def move_image(self, event):
        if self.start_x is not None and self.start_y is not None:
            self.canvas.move(self.canvas_image, event.x - self.start_x, event.y - self.start_y)
            self.start_x = event.x
            self.start_y = event.y

    def draw_grid(self):
        self.canvas.delete("grid_line")
        width = self.image.width * self.zoom_factor
        height = self.image.height * self.zoom_factor
        scaled_grid_spacing = self.grid_spacing * self.zoom_factor

        for x in range(0, int(width), int(scaled_grid_spacing)):
            self.canvas.create_line(x, 0, x, height, dash=(4, 4), fill="gray", tags="grid_line")

        for y in range(0, int(height), int(scaled_grid_spacing)):
            self.canvas.create_line(0, y, width, y, dash=(4, 4), fill="gray", tags="grid_line")

if __name__ == "__main__":
    root = ttk.Window(themename="journal")
    root.title("Image Viewer")

    image_path = "E:\\Download\\logo_BA-removebg-preview.png"
    image = Image.open(image_path)
    grid_spacing = 50  # Remplacez par l'espacement souhaité pour les lignes de la grille
    viewer = ImageViewer(root, image, grid_spacing)
    viewer.pack(fill=BOTH, expand=True)

    root.mainloop()





# "E:\\Download\\logo_BA-removebg-preview.png"