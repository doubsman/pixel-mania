import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from class_cells import Cells
import numpy as np
from class_bid import BidFile
import threading
import queue
import time

class SymbolCarrousel:
    def __init__(self, parent, sym_dir='sym', thumbnail_size=80, callback=None):
        self.parent = parent
        self.sym_dir = sym_dir
        self.thumbnail_size = thumbnail_size
        self.current_index = 0
        self.symbol_files = []
        self.thumbnails = []
        self.cells = Cells()
        self.callback = callback  # Callback function for the click
        
        # Create the main container
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame for the navigation buttons
        self.nav_frame = ttk.Frame(self.frame)
        self.nav_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Create the navigation buttons
        self.left_button = ttk.Button(self.nav_frame, text="←", command=self.scroll_left)
        self.left_button.pack(side=tk.LEFT, padx=5)
        
        self.right_button = ttk.Button(self.nav_frame, text="→", command=self.scroll_right)
        self.right_button.pack(side=tk.RIGHT, padx=5)
        
        # Create the canvas for the thumbnails
        self.canvas = tk.Canvas(self.frame, bg='#E0E0E0', height=230)  # Increased height for 2 lines
        self.canvas.pack(side=tk.TOP, fill=tk.X)
        
        # Create the horizontal scrollbar
        self.scrollbar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configure the canvas
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
        
        # Create the frame for the thumbnails
        self.thumbnails_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.thumbnails_frame, anchor=tk.NW)
        
        # Load the symbols
        self.load_symbols()
        
        # Configure the resizing
        self.thumbnails_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Bind the horizontal scrolling events
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)
        
        # Bind the events of clicking on the scrollbar
        self.scrollbar.bind('<Button-1>', self.on_scrollbar_click)
        self.scrollbar.bind('<B1-Motion>', self.on_scrollbar_drag)
        
        # Force the update of the scroll region after a short delay
        self.parent.after(100, self.update_scroll_region)
        
    def scroll_left(self):
        """Scroll to the left"""
        self.canvas.xview_scroll(-1, "pages")
        
    def scroll_right(self):
        """Scroll to the right"""
        self.canvas.xview_scroll(1, "pages")
        
    def on_scrollbar_click(self, event):
        """Handle the click on the scrollbar"""
        # Calculate the relative position of the click
        rel_pos = event.x / self.scrollbar.winfo_width()
        # Set the scroll position
        self.canvas.xview_moveto(rel_pos)
        
    def on_scrollbar_drag(self, event):
        """Handle the dragging on the scrollbar"""
        # Calculate the relative position of the cursor
        rel_pos = event.x / self.scrollbar.winfo_width()
        # Set the scroll position
        self.canvas.xview_moveto(rel_pos)
        
    def update_scroll_region(self):
        """Force the update of the scroll region"""
        # Update the scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Force the frame to take the necessary width
        bbox = self.thumbnails_frame.winfo_reqwidth()
        self.canvas.itemconfig(self.canvas_window, width=max(bbox, self.canvas.winfo_width()))
        
    def _on_shift_mousewheel(self, event):
        if self.canvas.winfo_exists():
            self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        
    def load_symbols(self):
        """Load all .sym files in the directory"""
        if not os.path.exists(self.sym_dir):
            os.makedirs(self.sym_dir)
            
        # Get all .sym files with their modification date
        self.symbol_files = []
        for f in os.listdir(self.sym_dir):
            if f.endswith('.sym'):
                path = os.path.join(self.sym_dir, f)
                mtime = os.path.getmtime(path)
                self.symbol_files.append((f, mtime))
        
        # Sort by modification date (most recent first)
        self.symbol_files.sort(key=lambda x: x[1], reverse=True)
        self.symbol_files = [f[0] for f in self.symbol_files]  # Keep only the file names
        
        # Update the window title with the number of elements
        self.parent.title(f"Load Symbol [{len(self.symbol_files)}]")
        
        # Create the thumbnails
        for sym_file in self.symbol_files:
            self.create_thumbnail(sym_file)
            
    def create_thumbnail(self, sym_file):
        """Create a thumbnail for a .sym file"""
        # Load the symbol
        self.cells.load_symbol(os.path.join(self.sym_dir, sym_file))
        
        # Get the image with transparency
        thumbnail = self.cells.symbol_image
        
        # Resize the image
        ratio = thumbnail.width / thumbnail.height
        if ratio > 1:
            new_width = self.thumbnail_size
            new_height = int(self.thumbnail_size / ratio)
        else:
            new_height = self.thumbnail_size
            new_width = int(self.thumbnail_size * ratio)
        thumbnail = thumbnail.resize((new_width, new_height), Image.LANCZOS)
        
        # Create the frame for the thumbnail
        thumb_frame = ttk.Frame(self.thumbnails_frame)
        
        # Calculate the position (row and column)
        index = len(self.thumbnails)
        row = index // (len(self.symbol_files) // 2 + 1)  # Division to determine the row
        col = index % (len(self.symbol_files) // 2 + 1)   # Modulo to determine the column
        
        # Place the frame in the grid
        thumb_frame.grid(row=row, column=col, padx=5, pady=5)
        
        # Create a canvas for the image with a light gray background
        canvas = tk.Canvas(thumb_frame, width=new_width, height=new_height, bg='#E0E0E0', highlightthickness=0)
        canvas.pack()
        
        # Create a light gray rectangle for the background
        canvas.create_rectangle(0, 0, new_width, new_height, fill='#E0E0E0')
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(thumbnail)
        
        # Calculate the central position
        x = (new_width - thumbnail.width) // 2
        y = (new_height - thumbnail.height) // 2
        
        # Display the image on the canvas with transparency
        canvas.create_image(x, y, anchor=tk.NW, image=photo)
        canvas.image = photo  # Keep a reference
        
        # Create the label for the file name
        name_label = ttk.Label(thumb_frame, text=sym_file)
        name_label.pack()
        
        # Add the binding for the left click
        canvas.bind('<Button-1>', lambda e, f=sym_file: self.on_thumbnail_click(f))
        name_label.bind('<Button-1>', lambda e, f=sym_file: self.on_thumbnail_click(f))
        
        # Add the binding for the right click
        canvas.bind('<Button-3>', lambda e, f=sym_file: self.show_context_menu(e, f))
        name_label.bind('<Button-3>', lambda e, f=sym_file: self.show_context_menu(e, f))
        
        # Store the thumbnail
        self.thumbnails.append((thumb_frame, photo))
        
    def on_frame_configure(self, event=None):
        """Configure the scroll region of the canvas"""
        # Update the scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Force the frame to take the necessary width
        bbox = self.thumbnails_frame.winfo_reqwidth()
        self.canvas.itemconfig(self.canvas_window, width=max(bbox, self.canvas.winfo_width()))
        
    def on_canvas_configure(self, event):
        """Configure the width of the inner frame when the canvas is resized"""
        # Update the width of the inner frame
        bbox = self.thumbnails_frame.winfo_reqwidth()
        self.canvas.itemconfig(self.canvas_window, width=max(bbox, event.width))
        
    def on_thumbnail_click(self, sym_file):
        """Handle the click on a thumbnail"""
        # Load the symbol
        self.cells.load_symbol(os.path.join(self.sym_dir, sym_file))
        
        # Call the callback function if it exists
        if self.callback:
            self.callback(self.cells.symbol)
        
    def get_selected_symbol(self):
        """Return the selected .sym file"""
        if 0 <= self.current_index < len(self.symbol_files):
            return os.path.join(self.sym_dir, self.symbol_files[self.current_index])
        return None

    def show_context_menu(self, event, sym_file):
        """Show the context menu for the symbol deletion"""
        # Create the context menu
        menu = tk.Menu(self.parent, tearoff=0)
        menu.add_command(label="Delete", command=lambda: self.delete_symbol(sym_file))
        
        # Display the menu at the click position
        menu.post(event.x_root, event.y_root)
        
    def delete_symbol(self, sym_file):
        """Delete the selected symbol"""
        # Full path of the file
        file_path = os.path.join(self.sym_dir, sym_file)
        
        # Delete the file
        try:
            os.remove(file_path)
            
            # Update the list of files
            self.symbol_files.remove(sym_file)
            
            # Delete the thumbnail
            for thumb_frame, photo in self.thumbnails:
                if thumb_frame.winfo_children()[1].cget("text") == sym_file:
                    thumb_frame.destroy()
                    self.thumbnails.remove((thumb_frame, photo))
                    break
            
            # Rearrange the remaining thumbnails
            for index, (thumb_frame, photo) in enumerate(self.thumbnails):
                # Calculate the new position
                row = index // (len(self.symbol_files) // 2 + 1)
                col = index % (len(self.symbol_files) // 2 + 1)
                # Update the position in the grid
                thumb_frame.grid(row=row, column=col, padx=5, pady=5)
            
            # Update the title with the new number of elements
            self.parent.title(f"Load Symbol [{len(self.symbol_files)}]")
            
            # Force the update of the scroll region
            self.update_scroll_region()
            
        except Exception as e:
            print(f"Error deleting file {sym_file}: {e}")

class BidCarrousel(ttk.Frame):
    def __init__(self, parent, bid_dir="bid", callback=None):
        super().__init__(parent)
        
        self.parent = parent
        self.bid_dir = bid_dir
        self.thumbnails = []
        self.callback = callback
        self.thumbnail_size = 150
        self.loading_queue = queue.Queue()
        self.is_loading = False
        self.all_bid_files = []  # Store all bid files
        self.filtered_bid_files = []  # Store filtered bid files
        self.loader_thread = None  # Store the loader thread reference
        self.no_files_label = None  # Store reference to the no files label
        
        # Create the main container
        self.frame = ttk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the search frame
        self.search_frame = ttk.Frame(self.frame)
        self.search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Create the search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_files)  # Call filter_files when text changes
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create the canvas for the thumbnails
        self.canvas = tk.Canvas(self.frame, bg='#E0E0E0')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create the vertical scrollbar
        self.scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure the canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Create the frame for the thumbnails
        self.thumbnails_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.thumbnails_frame, anchor=tk.NW)
        
        # Load the .bid files
        self.load_bids()
        
        # Configure the resizing
        self.thumbnails_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Bind the vertical scrolling events
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Start the thumbnail loading thread
        self.start_thumbnail_loader()
        
        # Force the update of the scroll region after a short delay
        self.parent.after(100, self.update_scroll_region)
        
        # Bind the window closing event
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def stop_thumbnail_loader(self):
        """Stop the thumbnail loading thread and clear the queue"""
        if self.is_loading:
            self.is_loading = False
            # Clear the queue
            while not self.loading_queue.empty():
                try:
                    self.loading_queue.get_nowait()
                except queue.Empty:
                    break
            # Wait for the thread to finish
            if self.loader_thread and self.loader_thread.is_alive():
                self.loader_thread.join(timeout=1.0)

    def start_thumbnail_loader(self):
        """Start the thumbnail loading thread"""
        self.stop_thumbnail_loader()  # Stop any existing loader
        self.is_loading = True
        self.loader_thread = threading.Thread(target=self.thumbnail_loader_worker)
        self.loader_thread.daemon = True
        self.loader_thread.start()
        
    def filter_files(self, *args):
        """Filter files based on search text"""
        search_text = self.search_var.get().lower()
        
        # Stop current loading and clear thumbnails
        self.stop_thumbnail_loader()
        
        # Clear existing thumbnails
        for thumb_frame, photo in self.thumbnails:
            thumb_frame.destroy()
        self.thumbnails.clear()
        
        # Remove existing no_files_label if it exists
        if self.no_files_label:
            self.no_files_label.destroy()
            self.no_files_label = None
        
        # Filter files
        self.filtered_bid_files = [f for f in self.all_bid_files if search_text in f.lower()]
        
        # Update the window title with the number of filtered elements
        self.parent.title(f"Open Bid File [{len(self.filtered_bid_files)}]")
        
        if not self.filtered_bid_files:
            # Display a message if no files match the search
            self.no_files_label = ttk.Label(self.thumbnails_frame, 
                                          text="No matching .bid files found",
                                          font=('Arial', 12))
            self.no_files_label.grid(row=0, column=0, pady=20)
            self.thumbnails_frame.grid_columnconfigure(0, weight=1)
            return
            
        # Add filtered files to the loading queue
        for bid_file in self.filtered_bid_files:
            self.loading_queue.put(bid_file)
            
        # Restart the thumbnail loader
        self.start_thumbnail_loader()
            
        # Update the scroll region
        self.update_scroll_region()

    def load_bids(self):
        """Charge tous les fichiers .bid du dossier"""
        if not os.path.exists(self.bid_dir):
            os.makedirs(self.bid_dir)
            
        # Get all .bid files with their modification date
        self.all_bid_files = []
        for f in os.listdir(self.bid_dir):
            if f.endswith('.bid'):
                path = os.path.join(self.bid_dir, f)
                mtime = os.path.getmtime(path)
                self.all_bid_files.append((f, mtime))
        
        # Sort by modification date (most recent first)
        self.all_bid_files.sort(key=lambda x: x[1], reverse=True)
        self.all_bid_files = [f[0] for f in self.all_bid_files]
        
        # Initialize filtered files with all files
        self.filtered_bid_files = self.all_bid_files.copy()
        
        # Update the window title with the number of elements
        self.parent.title(f"Open Bid File [{len(self.all_bid_files)}]")
        
        # Remove existing no_files_label if it exists
        if self.no_files_label:
            self.no_files_label.destroy()
            self.no_files_label = None
        
        if not self.all_bid_files:
            # Display a message if no files are found
            self.no_files_label = ttk.Label(self.thumbnails_frame, 
                                          text="No .bid files found in the 'bid' directory",
                                          font=('Arial', 12))
            self.no_files_label.grid(row=0, column=0, pady=20)
            self.thumbnails_frame.grid_columnconfigure(0, weight=1)
            return
            
        # Add files to the loading queue
        for bid_file in self.filtered_bid_files:
            self.loading_queue.put(bid_file)
            
    def thumbnail_loader_worker(self):
        """Worker thread to load thumbnails asynchronously"""
        while self.is_loading:
            try:
                # Get a task from the queue
                bid_file = self.loading_queue.get(timeout=0.1)
                if not self.is_loading:  # Check again after getting the task
                    break
                self.create_thumbnail(bid_file)
                self.loading_queue.task_done()
                # Small delay to avoid overloading the CPU
                time.sleep(0.1)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in thumbnail loader: {e}")
                break
            
    def create_thumbnail(self, bid_file):
        """Create a thumbnail for a .bid file"""
        # drauw bid_file to thumbnail
        my_bid = BidFile()
        thumbnail = my_bid.load_bidfile(os.path.join(self.bid_dir, bid_file))
            
        # Resize the image
        ratio = thumbnail.width / thumbnail.height
        if ratio > 1:
            new_width = self.thumbnail_size
            new_height = int(self.thumbnail_size / ratio)
        else:
            new_height = self.thumbnail_size
            new_width = int(self.thumbnail_size * ratio)
        thumbnail = thumbnail.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(thumbnail)
        
        # Create the frame for the thumbnail
        thumb_frame = ttk.Frame(self.thumbnails_frame)
        
        # Calculate the position (row and column)
        index = len(self.thumbnails)
        row = index // 8  # 8 thumbnails per row
        col = index % 8
        
        # Place the frame in the grid
        thumb_frame.grid(row=row, column=col, padx=2, pady=2)  # Reduced padding for better spacing
        
        # Create the label for the image
        label = ttk.Label(thumb_frame, image=photo)
        label.image = photo  # Keep a reference
        label.pack()
        
        # Create the label for the file name with a smaller font size
        name_label = ttk.Label(thumb_frame, text=bid_file, wraplength=self.thumbnail_size - 10, font=('Arial', 8))
        name_label.pack()
        
        # Add the binding for the click
        label.bind('<Button-1>', lambda e, f=os.path.join(self.bid_dir, bid_file): self.on_click(f))
        name_label.bind('<Button-1>', lambda e, f=os.path.join(self.bid_dir, bid_file): self.on_click(f))
        
        # Stocker la vignette
        self.thumbnails.append((thumb_frame, photo))
        
        # Update the scroll region
        self.parent.after(100, self.update_scroll_region)
        
    def on_frame_configure(self, event=None):
        """Configure the scroll region of the canvas"""
        # Update the scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Forcer le frame à prendre toute la largeur nécessaire
        bbox = self.thumbnails_frame.winfo_reqwidth()
        self.canvas.itemconfig(self.canvas_window, width=max(bbox, self.canvas.winfo_width()))
        
    def on_canvas_configure(self, event):
        """Configure the width of the inner frame when the canvas is resized"""
        # Update the width of the inner frame
        bbox = self.thumbnails_frame.winfo_reqwidth()
        self.canvas.itemconfig(self.canvas_window, width=max(bbox, event.width))
        
    def on_click(self, bid_file):
        """Handle the click on a thumbnail"""
        # Stop the loading thread before closing
        self.is_loading = False
        if self.callback:
            self.callback(bid_file)
            
    def _on_mousewheel(self, event):
        """Handle the vertical scrolling"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
    def update_scroll_region(self):
        """Force the update of the scroll region"""
        # Update the scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Forcer le frame à prendre toute la largeur nécessaire
        bbox = self.thumbnails_frame.winfo_reqwidth()
        self.canvas.itemconfig(self.canvas_window, width=max(bbox, self.canvas.winfo_width()))
        
    def on_closing(self):
        """Handle window closing"""
        # Stop the loading thread
        self.stop_thumbnail_loader()
        # Clean the bindings
        self.canvas.unbind_all("<MouseWheel>")
        # Destroy the window
        self.parent.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    root.title("load Symbol")
    root.geometry("500x280")  # Increased height for the navigation buttons
    
    def on_symbol_selected(symbol):
        print("Selected symbol:", symbol)
    
    carrousel = SymbolCarrousel(root, callback=on_symbol_selected)
    root.mainloop() 