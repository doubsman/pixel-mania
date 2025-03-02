import tkinter as tk
from tkinter import filedialog, messagebox
from class_bid_imp import ImageProcessor

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image to BID Converter")

        self.path_image = tk.StringVar()
        self.grid_width = tk.IntVar(value=48)
        self.grid_height = tk.IntVar(value=48)
        self.triangle_ratio = tk.DoubleVar(value=0.30)
        self.threshold = tk.IntVar(value=128)
        self.display_cells = tk.BooleanVar(value=False)
        self.display_cells_scale_reduce = tk.IntVar(value=10)
        self.no_save_bid = tk.BooleanVar(value=True)
        self.model_ascii = tk.IntVar(value=1)
        self.no_save_ascii = tk.BooleanVar(value=True)

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Image Path:").grid(row=0, column=0, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.path_image, width=50).grid(row=0, column=1, columnspan=2)
        tk.Button(self.root, text="Browse", command=self.browse_image).grid(row=0, column=3)

        tk.Label(self.root, text="Grid Width:").grid(row=1, column=0, sticky=tk.W)
        tk.Scale(self.root, from_=10, to=100, orient=tk.HORIZONTAL, variable=self.grid_width, command=self.update_parameters).grid(row=1, column=1)

        tk.Label(self.root, text="Grid Height:").grid(row=2, column=0, sticky=tk.W)
        tk.Scale(self.root, from_=10, to=100, orient=tk.HORIZONTAL, variable=self.grid_height, command=self.update_parameters).grid(row=2, column=1)

        tk.Label(self.root, text="Triangle Ratio:").grid(row=3, column=0, sticky=tk.W)
        tk.Scale(self.root, from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, variable=self.triangle_ratio, command=self.update_parameters).grid(row=3, column=1)

        tk.Label(self.root, text="Threshold:").grid(row=4, column=0, sticky=tk.W)
        tk.Scale(self.root, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.threshold, command=self.update_parameters).grid(row=4, column=1)

        tk.Checkbutton(self.root, text="Display Cells", variable=self.display_cells, command=self.update_parameters).grid(row=5, column=0, columnspan=2, sticky=tk.W)

        tk.Label(self.root, text="Display Cells Scale Reduce:").grid(row=6, column=0, sticky=tk.W)
        tk.Scale(self.root, from_=1, to=20, orient=tk.HORIZONTAL, variable=self.display_cells_scale_reduce, command=self.update_parameters).grid(row=6, column=1)

        tk.Checkbutton(self.root, text="No Save BID", variable=self.no_save_bid, command=self.update_parameters).grid(row=7, column=0, columnspan=2, sticky=tk.W)

        tk.Label(self.root, text="Model ASCII:").grid(row=8, column=0, sticky=tk.W)
        tk.Scale(self.root, from_=1, to=4, orient=tk.HORIZONTAL, variable=self.model_ascii, command=self.update_parameters).grid(row=8, column=1)

        tk.Checkbutton(self.root, text="No Save ASCII", variable=self.no_save_ascii, command=self.update_parameters).grid(row=9, column=0, columnspan=2, sticky=tk.W)

        self.result_label = tk.Label(self.root, text="")
        self.result_label.grid(row=10, column=0, columnspan=2)

        self.ascii_text = tk.Text(self.root, wrap=tk.WORD, height=40, width=120, font=("Consolas", 8))
        self.ascii_text.grid(row=11, column=0, columnspan=4)

    def browse_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.path_image.set(file_path)
            self.update_parameters()

    def update_parameters(self, event=None):
        try:
            processor = ImageProcessor(
                path_image=self.path_image.get(),
                grid_width=self.grid_width.get(),
                grid_height=self.grid_height.get(),
                triangle_ratio=self.triangle_ratio.get(),
                threshold=self.threshold.get(),
                display_cells=self.display_cells.get(),
                display_cells_scale_reduce=self.display_cells_scale_reduce.get(),
                no_save_bid=self.no_save_bid.get(),
                model_ascii=self.model_ascii.get(),
                no_save_ascii=self.no_save_ascii.get()
            )
            ascii_codes = processor.process_image()
            self.display_ascii(ascii_codes)
            self.result_label.config(text="Processing complete!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_ascii(self, ascii_codes):
        self.ascii_text.delete(1.0, tk.END)
        for row in ascii_codes:
            self.ascii_text.insert(tk.END, ''.join(row) + '\n')

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()
