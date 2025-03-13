import ttkbootstrap as ttk
from PIL import ImageTk

class ManageCanvas():
    def __init__(self, canvas=None):
        self.canvas = canvas

    def center_image_on_canvas(self, canvas, image):
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        image_width, image_height = image.size
        tk_image = ImageTk.PhotoImage(image)
        x_center = (canvas_width - image_width) // 2
        y_center = (canvas_height - image_height) // 2
        canvas.create_image(x_center, y_center, anchor=ttk.NW, image=tk_image)
        canvas.image = tk_image

    def center_canvas_on_canvas(self, parent_canvas, child_canvas):
        parent_width = parent_canvas.winfo_width()
        parent_height = parent_canvas.winfo_height()
        child_width = child_canvas.winfo_width()
        child_height = child_canvas.winfo_height()
        x_center = (parent_width - child_width) // 2
        y_center = (parent_height - child_height) // 2
        parent_canvas.create_window(x_center, y_center, window=child_canvas, anchor=ttk.NW)