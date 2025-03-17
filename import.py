import ttkbootstrap as ttk
from tkinter import filedialog, messagebox, Entry
from PIL import ImageTk, Image
from class_bid_imp import ImageProcessor
from class_bid import BidFile
import numpy as np

class ImageProcessorApp:
    def __init__(self, root):
        self.class_ImageProcessor = ImageProcessor()
        self.class_BidFile = BidFile()
        self.root = root
        self.path_image = None
        self.title = "Image to BID Converter"
        self.grid_width = ttk.IntVar(value=48)
        self.grid_height = ttk.IntVar(value=48)
        self.triangle_ratio = ttk.DoubleVar(value=0.30)
        self.threshold = ttk.IntVar(value=128)
        self.display_cells = ttk.BooleanVar(value=False)
        self.display_cells_scale_reduce = ttk.IntVar(value=10)
        self.model_ascii = ttk.IntVar(value=1)
        self.sync_grid_dimensions = ttk.BooleanVar(value=True)
        self.root.title(self.title)

        self.initialize_ui()

    def initialize_ui(self):
        # Set the window icon
        icon = ImageTk.PhotoImage(file='ico/carre.png')
        self.root.iconphoto(False, icon)

        # Create a frame for the options
        options_frame = ttk.Frame(self.root, width=250)
        options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        # Create a frame for the canvas
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Configure the grid to expand the canvas frame
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Add widgets to the options frame
        self.add_option(options_frame, "Grid Width:", self.grid_width, 1, 1, 200, self.update_grid_width)
        self.add_option(options_frame, "Grid Height:", self.grid_height, 3, 1, 200, self.update_grid_height)
        ttk.Checkbutton(options_frame, text="Sync Grid Dimensions", variable=self.sync_grid_dimensions).grid(row=5, column=0, columnspan=2, sticky=ttk.W, padx=10, pady=5)
        self.add_option(options_frame, "Triangle Ratio:", self.triangle_ratio, 6, 0.0, 1.0, self.update_parameters)
        self.add_option(options_frame, "Threshold:", self.threshold, 8, 0, 256, self.update_parameters)
        ttk.Checkbutton(options_frame, text="Display Cells", variable=self.display_cells, command=self.update_parameters).grid(row=10, column=0, columnspan=2, sticky=ttk.W, padx=10, pady=5)
        self.add_option(options_frame, "Display Cells Scale Reduce:", self.display_cells_scale_reduce, 11, 1, 50, self.update_parameters)
        self.add_option(options_frame, "Model ASCII:", self.model_ascii, 14, 1, 4, self.update_parameters)

        ttk.Button(options_frame, text="Reset to Default", command=self.reset_to_default).grid(row=17, column=0, columnspan=3, padx=10, pady=5)
        ttk.Button(options_frame, text="Load Image...", command=self.browse_image).grid(row=18, column=0, columnspan=2, padx=10, pady=5)
        ttk.Button(options_frame, text="Save bid file...", command=self.class_ImageProcessor.save_bid).grid(row=19, column=0, columnspan=2, padx=10, pady=5)
        ttk.Button(options_frame, text="Save image file...", command=self.browse_image).grid(row=20, column=0, columnspan=2, padx=10, pady=5)
        ttk.Button(options_frame, text="Save ASCII file...", command=self.class_ImageProcessor.save_ascii).grid(row=21, column=0, columnspan=2, padx=10, pady=5)

        # Add the canvas to the canvas frame
        self.canvas = ttk.Canvas(canvas_frame, width=1024, height=1024, border=2)
        self.canvas.pack(expand=True, fill="both")

    def add_option(self, frame, label_text, variable, row, min_val, max_val, update_command):
        ttk.Label(frame, text=label_text).grid(row=row, column=0, sticky=ttk.W, padx=10, pady=5)
        entry = ttk.Entry(frame, textvariable=variable, width=10)
        entry.grid(row=row, column=1, sticky=ttk.W, padx=10, pady=5)
        entry.bind("<Return>", update_command)
        ttk.Scale(frame, from_=min_val, to=max_val, orient=ttk.HORIZONTAL, variable=variable, command=update_command, length=200).grid(row=row+1, column=0, columnspan=2, padx=10, pady=5)

    def browse_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.path_image = file_path
            self.root.title(f'{self.title} [{self.path_image}]')
            self.update_parameters()

    def update_grid_width(self, event=None):
        value = int(self.grid_width.get())
        self.grid_width.set(value)
        if self.sync_grid_dimensions.get():
            self.grid_height.set(value)
        self.update_parameters()

    def update_grid_height(self, event=None):
        value = int(self.grid_height.get())
        self.grid_height.set(value)
        if self.sync_grid_dimensions.get():
            self.grid_width.set(value)
        self.update_parameters()

    def update_parameters(self, event=None):
        if self.path_image:
            try:
                cells_bid = self.class_ImageProcessor.process_image(
                    path_image=self.path_image,
                    grid_width=self.grid_width.get(),
                    grid_height=self.grid_height.get(),
                    triangle_ratio=self.triangle_ratio.get(),
                    threshold=self.threshold.get(),
                    display_cells=self.display_cells.get(),
                    display_cells_scale_reduce=self.display_cells_scale_reduce.get(),
                    model_ascii=self.model_ascii.get()
                )
                # Convertir la liste de tuples en grilles 2D
                grid_bid = np.zeros((self.grid_height.get(), self.grid_width.get()), dtype=int)
                grid_colors = np.zeros((self.grid_height.get(), self.grid_width.get()), dtype=int)
                for x, y, shape, color in cells_bid:
                    grid_bid[y, x] = shape
                    grid_colors[y, x] = color
                
                self.class_BidFile.grid_bid = grid_bid
                self.class_BidFile.grid_colors = grid_colors
                self.class_BidFile.grid_width = self.grid_width.get()
                self.class_BidFile.grid_height = self.grid_height.get()
                self.class_BidFile.image_scale = 20
                self.class_BidFile.draw_bidfile()
                
                # Obtenir les dimensions du canvas
                canvas_width = max(1, self.canvas.winfo_width())
                canvas_height = max(1, self.canvas.winfo_height())
                
                # Obtenir les dimensions de l'image
                image_width = max(1, self.class_BidFile.image.width)
                image_height = max(1, self.class_BidFile.image.height)
                
                # Calculer l'échelle pour que l'image s'adapte au canvas
                scale_x = canvas_width / image_width
                scale_y = canvas_height / image_height
                scale = min(scale_x, scale_y)
                
                # Redimensionner l'image
                new_width = max(1, int(image_width * scale))
                new_height = max(1, int(image_height * scale))
                resized_image = self.class_BidFile.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convertir en PhotoImage et afficher
                image = ImageTk.PhotoImage(resized_image)
                
                # Effacer le canvas et centrer l'image
                self.canvas.delete("all")
                x = (canvas_width - new_width) // 2
                y = (canvas_height - new_height) // 2
                self.canvas.create_image(x, y, anchor="nw", image=image)
                self.canvas.image = image  # Garder une référence
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def reset_to_default(self):
        self.grid_width.set(48)
        self.grid_height.set(48)
        self.triangle_ratio.set(0.30)
        self.threshold.set(128)
        self.display_cells.set(False)
        self.display_cells_scale_reduce.set(10)
        self.model_ascii.set(1)
        self.sync_grid_dimensions.set(False)
        self.update_parameters()

if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    app = ImageProcessorApp(root)
    root.mainloop()
