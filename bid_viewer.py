import os
import tkinter as tk
from PIL import ImageTk
from class_carrousel import BidCarrousel

class BidViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bid File Viewer")
        self.root.geometry("1290x1290")
        icon = ImageTk.PhotoImage(file=os.path.join('ico', 'carre.png'))
        self.root.iconphoto(False, icon)
        # Configure the window expansion
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create carrousel with no callback (standalone mode)
        self.carrousel = BidCarrousel(self.root, callback=None, thumbnail_size=480)
        self.carrousel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Define a minimum size for the window
        self.root.minsize(1290, 1290)
        
        # Add keyboard shortcuts
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen')))
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    viewer = BidViewer()
    viewer.run()