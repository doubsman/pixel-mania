import ttkbootstrap as ttk
from tkinter import filedialog, Frame
from tkinter.messagebox import askyesno
from PIL import ImageTk, Image
import numpy as np
import os
import subprocess
from pynput.keyboard import Key, Controller, Listener
from class_bid import BidFile
from class_cells import Cells
from class_action import ActionState
from class_ascii import ImageASCII, BidASCII
from class_consol import CmdTerminal
import sys
import logging
from class_carrousel import SymbolCarrousel
from class_carrousel import BidCarrousel

# Logging configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        
        # If path already contains 'ico', don't add it again
        if relative_path.startswith(('ico/', 'ico\\')):
            full_path = os.path.join(base_path, relative_path)
        else:
            full_path = os.path.join(base_path, relative_path)
        
        logger.debug(f"Resource path requested: {relative_path}")
        logger.debug(f"Base path: {base_path}")
        logger.debug(f"Full path: {full_path}")
        
        # Check if file exists
        if not os.path.exists(full_path):
            logger.error(f"Resource not found: {full_path}")
            # Try to find the file in current directory
            alt_path = os.path.join(os.getcwd(), relative_path)
            if os.path.exists(alt_path):
                logger.debug(f"Resource found in current directory: {alt_path}")
                return alt_path
            # List available files in base directory
            logger.debug(f"Files in {base_path}:")
            for root, dirs, files in os.walk(base_path):
                for item in dirs + files:
                    logger.debug(f"  {os.path.join(root, item)}")
        
        return full_path
    except Exception as e:
        logger.error(f"Error in resource_path: {str(e)}")
        return relative_path

class ImageEditorApp(BidFile, ActionState):
    def __init__(self, root):
        BidFile.__init__(self)
        ActionState.__init__(self)
        self.root = root
        self.tittle = "Image Bid Editor v1.00beta"
        self.root.title(self.tittle)
        self.root.geometry("1700x1520")
        self.root.resizable(width=False, height=False)
        
        # Intercept window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.WIDTH = 1700-200-100
        self.HEIGHT = 1520-20-100
        self.file_path = ""
        # Canvas Grid Mode
        self.bool_grid = True
        # Backup BID necessary
        self.bool_backup = False
        # Selection
        self.grid_sel_cells = []
        # Clipboard
        self.grid_clipboard = []
        self.clipboard = Cells()
        # Current cursor position (x,y)
        self.grid_x = 1
        self.grid_y = 1
        # UI options
        self.grid_width_option = ttk.IntVar(value=0)
        self.grid_height_option = ttk.IntVar(value=0)
        # Palette selection
        self.current_select_shape = 1
        self.current_select_color = 5
        # Area selection mode
        self.selection_start = None
        self.selection_end = None
        self.selection_rect = None
        # Selection ADD mode
        self.bool_mode_add_selection = False
        # Paste Cells mode
        self.bool_paste_mode = False
        # Pasted Image ID
        self.image_over_id = 0
        # Default image scale
        self.image_scale_default = 1
        # Collect events until released
        listener = Listener(on_press=self.on_press)
        listener.start()
        self.controler = Controller()
        
        # Environment logging
        logger.debug(f"Python executable: {sys.executable}")
        logger.debug(f"Current working directory: {os.getcwd()}")
        logger.debug(f"MEIPASS: {getattr(sys, '_MEIPASS', 'Not running in PyInstaller')}")
        
        # Check if ico directory exists
        ico_path = resource_path('ico')
        if not os.path.exists(ico_path):
            print(f"Warning: ico directory not found at {ico_path}")
            print(f"Current directory: {os.getcwd()}")
            print(f"Available files: {os.listdir('.')}")
        
        self.initialize_ui()

    def initialize_ui(self):
        icon = ImageTk.PhotoImage(file=resource_path(os.path.join('ico', 'carre.png')))
        self.root.iconphoto(False, icon)

        # The left frame to contain the buttons
        left_frame = ttk.Frame(self.root)
        left_frame['borderwidth'] = 5
        left_frame.pack(side="left", fill="y")

        left_frame2 = ttk.Frame(self.root)
        left_frame2['borderwidth'] = 5
        left_frame2.pack(side="left", fill="y")

        # Width frame
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=5)
        width_frame = ttk.Frame(left_frame)
        width_frame.pack()
        ttk.Button(width_frame, text="-", command=lambda: self.change_size('width', -2), bootstyle="outline", width=0).pack(side="left", padx=0, pady=0)
        self.grid_width_label = ttk.Label(width_frame, text="48")
        self.grid_width_label.pack(side="left", padx=2, pady=0)
        ttk.Button(width_frame, text="+", command=lambda: self.change_size('width', 2), bootstyle="outline", width=0).pack(side="left", padx=0, pady=0)
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=5)

        # Frame for height
        ttk.Separator(left_frame2, orient='horizontal').pack(fill='x', pady=5)
        height_frame = ttk.Frame(left_frame2)
        height_frame.pack()
        ttk.Button(height_frame, text="-", command=lambda: self.change_size('height', -2), bootstyle="outline", width=0).pack(side="left", padx=0, pady=0)
        self.grid_height_label = ttk.Label(height_frame, text="48")
        self.grid_height_label.pack(side="left", padx=2, pady=0)
        ttk.Button(height_frame, text="+", command=lambda: self.change_size('height', 2), bootstyle="outline", width=0).pack(side="left", padx=0, pady=0)
        ttk.Separator(left_frame2, orient='horizontal').pack(fill='x', pady=5)

        opencar_button = self.create_button(left_frame, 'ico/openbid.png', self.open_carousselbid, "open")
        open_button = self.create_button(left_frame, 'ico/open.png', self.open_bid, "open")
        save_button = self.create_button(left_frame, 'ico/save.png', self.save_bid, "Save bid")
        saveas_button = self.create_button(left_frame, 'ico/saveas.png', self.saveas_bid, "Save bid")
        new_button = self.create_button(left_frame, 'ico/plus.png', self.create_bid, "New")
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=4)
        copy_button = self.create_button(left_frame, 'ico/copy.png', self.copy_cells, "Copy")
        cut_button = self.create_button(left_frame, 'ico/cut.png', lambda: self.copy_cells(True), "Cut")
        paste_button = self.create_button(left_frame, 'ico/paste.png', self.paste_cells, "Cut")
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=4)
        grid_button = self.create_button(left_frame, 'ico/grid.png', self.draw_grill, "Grid")
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=4)
        save_image_button = self.create_button(left_frame, 'ico/photo.png', self.save_image, "Save Image")
        ascii_button = self.create_button(left_frame, 'ico/ascii.png', self.display_console_bid, "Save ASCII")
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=6)
        imageascii_button = self.create_button(left_frame, 'ico/terminalimg.png', self.display_console_image, "Image ASCII")
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=4)
        folder_button = self.create_button(left_frame, 'ico/open.png', self.open_folder, "Open Folder")

        undo_button = self.create_button(left_frame2, 'ico/undo.png', self.undo_action, "Cancel")
        select_button = self.create_button(left_frame2, 'ico/selection.png', self.mode_select, "Cell Selecion")
        area_button = self.create_button(left_frame2, 'ico/square.png', self.mode_area, "Area Selecion")
        magic_button = self.create_button(left_frame2, 'ico/magic.png', self.mode_magicselect, "Magic Selecion")

        color_icon = ttk.PhotoImage(file='ico/invent.png')
        self.palet = ttk.Canvas(left_frame2, width=50, height=500, bg='#E0E0E0')
        self.palet.create_image(0, 0, anchor="nw", image=color_icon)
        self.palet.image = color_icon
        self.palet.pack(pady=5)
        self.palet.bind("<Button-1>", self.select_palet)
        self.palet.create_rectangle(0, 250, 50, 300, fill="", outline="red", width=2, tags="cell_color")
        
        filpv_button = self.create_button(left_frame2, 'ico/flip-v.png', self.flipv_cells, "Flip V")
        filph_button = self.create_button(left_frame2, 'ico/flip-h.png', self.fliph_cells, "Flip H")
        rotate_l_button = self.create_button(left_frame2, 'ico/rotate-left.png', self.rotate_l_cells, "Flip V")
        rotate_r_button = self.create_button(left_frame2, 'ico/rotate-right.png', self.rotate_r_cells, "Flip H")
        inverse_button = self.create_button(left_frame2, 'ico/inverser.png', self.inverse_colors, "Inverse Colors")
        fill_button = self.create_button(left_frame2, 'ico/fill.png', self.fill_cells, "Fill Selecion")
        
        self.mode_copy = ttk.Label(left_frame2, text="SUB (✖)", foreground="blue")
        self.mode_copy.pack(side="bottom")

        self.thumbnail_canvas = ttk.Canvas(left_frame2, width=80, height=80, border=2, relief="sunken", bg='#E0E0E0')
        self.thumbnail_canvas.pack(side="bottom", fill="y")
        self.thumbnail_canvas.pack_propagate(False)

        self.coord_label = ttk.Label(left_frame, text="(00, 00)")
        self.coord_label.pack(side="bottom")

        save_symbol = self.create_button(left_frame, 'ico/save.png', self.save_grid_clipboard, "Save Symbol", 'bottom', 25)
        load_symbol = self.create_button(left_frame, 'ico/open.png', self.open_grid_clipboard, "Load Symbol", 'bottom', 25)
        init_symbol = self.create_button(left_frame, 'ico/cross.png', self.clear_grid_clipboard, "Reset Symbol", 'bottom', 25)

        # The right canvas for displaying the image
        self.outercanvas = ttk.Canvas(self.root, width=self.WIDTH + 100, height=self.HEIGHT + 100, bg='#E0E0E0')
        self.outercanvas.pack(expand="y", fill="y")

        # Create a frame to contain the canvas and scrollbars
        self.canvas_frame = Frame(self.outercanvas)
        self.outercanvas.create_window(50, 50, window=self.canvas_frame, anchor="nw")

        # Create the scrollbars
        self.v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical")
        self.h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient="horizontal")
        self.canvas = ttk.Canvas(self.canvas_frame, width=self.WIDTH, height=self.HEIGHT,
                           bg='#E0E0E0',
                           border=2, relief="sunken",
                           xscrollcommand=self.h_scrollbar.set,
                           yscrollcommand=self.v_scrollbar.set)

        # Configure scrollbars
        self.v_scrollbar.config(command=self.canvas.yview)
        self.h_scrollbar.config(command=self.canvas.xview)

        # Place canvas first
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Configure scrollbars to be placed correctly
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure resizing
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Bind mouse wheel events for scrolling
        self.canvas.bind("<Control-MouseWheel>", self.zoom)  # Zoom with Ctrl+Wheel
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Vertical scroll
        self.canvas.bind("<Shift-MouseWheel>", self.on_shift_mousewheel)  # Horizontal scroll
        self.canvas.bind("<Button-4>", self.zoom)
        self.canvas.bind("<Button-5>", self.zoom)
        self.canvas.bind("<Motion>", self.update_coords_cells)

        self.create_bid()
        self.refresh_thumbnail()

    def create_button(self, parent, image_path, command, text="", side='top', subsample=12, pady=5):
        image = ttk.PhotoImage(file=resource_path(os.path.join('ico', os.path.basename(image_path)))).subsample(subsample, subsample)
        button = ttk.Button(parent, image=image, bootstyle="outline", command=command, text=text)
        button.image = image
        button.pack(pady=pady, side=side)
        return button

    def open_bid(self):
        bid_path = filedialog.askopenfilename(title="Open Bid File", filetypes=[("Bid Files", "*.bid")], initialdir="wrk")
        if bid_path != '':
            self.save_bid()
            self.file_path = bid_path
            self.root.title(f'{self.tittle} [{self.file_path}]')  
            self.load_bidfile(self.file_path, self.WIDTH, self.HEIGHT)
            self.init_bid()      

    def open_carousselbid(self):
        # make modal window
        dialog = ttk.Toplevel(self.root)
        dialog.title("Open Bid File")
        icon = ImageTk.PhotoImage(file=resource_path(os.path.join('ico', 'carre.png')))
        dialog.iconphoto(False, icon)
        dialog.geometry("733x567")
        dialog.transient(self.root)  # make the window modal
        dialog.grab_set()  # force focus on this window
        dialog.resizable(width=False, height=True)
        # Configure the window expansion
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)
        
        # create carrousel
        def on_bid_selected(bid_file):
            self.save_bid()
            self.file_path = bid_file
            self.root.title(f'{self.tittle} [{self.file_path}]')  
            self.load_bidfile(self.file_path, self.WIDTH, self.HEIGHT)
            self.init_bid()
            dialog.destroy()
            
        carrousel = BidCarrousel(dialog, callback=on_bid_selected)
        carrousel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Position the window next to the mouse
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        
        # Get the mouse position
        mouse_x = self.root.winfo_pointerx()
        mouse_y = self.root.winfo_pointery()
        
        # Calculate the window position
        x = mouse_x + 20  # 20 pixels to the right of the mouse
        y = mouse_y - height // 2  # Centered vertically relative to the mouse
        
        # Ensure the window stays within the screen boundaries
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        if x + width > screen_width:
            x = mouse_x - width - 20  # Place to the left of the mouse if not enough space on the right
        if y < 0:
            y = 0  # Align to the top if not enough space above
        if y + height > screen_height:
            y = screen_height - height  # Align to the bottom if not enough space below
            
        dialog.geometry(f'+{x}+{y}')
        
        # Define a minimum size for the window
        dialog.minsize(733,567)
        
        # Wait for the window to be closed
        dialog.wait_window()

    def create_bid(self):
        self.save_bid()
        self.root.title(f'{self.tittle} : [NEW]')
        self.file_path = ''
        self.new_bid(self.WIDTH, self.HEIGHT)
        self.init_bid()
    
    def init_bid(self):
        witdth, height = self.image.size
        self.canvas.config(width=witdth, height=height)
        self.clipboard.image_scale = self.image_scale
        self.image_scale_default = self.image_scale
        self.grid_sel_cells = np.zeros((self.grid_height, self.grid_width), dtype=int)
        self.grid_width_label.config(text=str(self.grid_width))
        self.grid_height_label.config(text=str(self.grid_height))
        self.grid_width_option.set(self.grid_width)
        self.grid_height_option.set(self.grid_height)
        self.canvas.config(scrollregion=None)
        self.canvas.update_idletasks()
        self.v_scrollbar.grid_remove()
        self.h_scrollbar.grid_remove()
        
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
        # make modal window
        dialog = ttk.Toplevel(self.root)
        dialog.title("Load Symbol")
        icon = ImageTk.PhotoImage(file=resource_path(os.path.join('ico', 'carre.png')))
        dialog.iconphoto(False, icon)
        dialog.geometry("772x280")
        dialog.resizable(width=False, height=False)
        dialog.transient(self.root)  # modal windows
        dialog.grab_set()  # force focus on this window
        
        # create carrousel
        def on_symbol_selected(symbol):
            self.grid_clipboard = symbol
            self.clipboard.insert_symbol(symbol)  # Update clipboard with new symbol
            self.refresh_thumbnail()
            self.paste_cells()
            dialog.destroy()
            
        carrousel = SymbolCarrousel(dialog, callback=on_symbol_selected)
        
        # Position the window next to the mouse
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        
        # Get the mouse position
        mouse_x = self.root.winfo_pointerx()
        mouse_y = self.root.winfo_pointery()
        
        # Calculate the window position
        x = mouse_x + 20  # 20 pixels to the right of the mouse
        y = mouse_y - height // 2  # Centered vertically relative to the mouse
        
        # Ensure the window stays within the screen boundaries
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        if x + width > screen_width:
            x = mouse_x - width - 20  # Place to the left of the mouse if not enough space on the right
        if y < 0:
            y = 0  # Align to the top if not enough space above
        if y + height > screen_height:
            y = screen_height - height  # Align to the bottom if not enough space below
            
        dialog.geometry(f'+{x}+{y}')
        
        # Wait for the window to be closed
        dialog.wait_window()

    def save_grid_clipboard(self):
        if hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            number = 1
            path_symbol = os.path.join('sym', f'symbol{number:03d}.sym')
            while os.path.isfile(path_symbol):
                number += 1
                path_symbol = os.path.join('sym', f'symbol{number:03d}.sym')
            np.savetxt(path_symbol, self.grid_clipboard, fmt='%i', delimiter=";")

    def clear_grid_clipboard(self):
        if hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            self.grid_clipboard = []
            self.refresh_thumbnail()

    def display_console_bid(self):
        file_ascii = self.file_path.replace('.bid','.ascii')
        bid_ascii = BidASCII(self.grid_bid, self.grid_colors, 1, file_ascii)
        
        # Calculate width in characters
        # For ASCII model 1, each cell is 2 characters wide
        # Plus ANSI color control characters (about 20 characters per cell)
        width_cellule = 2
        width_chars = 2 + self.grid_width * (width_cellule + 20) + 2  # +2 for vertical borders
        
        # Calculate height in characters
        height_chars = self.grid_height + 2  # +2 for horizontal borders
        
        # Limit dimensions to CmdTerminal maximums
        width_chars = min(width_chars, 150)  # Maximum 150 characters wide
        height_chars = min(height_chars, 50)  # Maximum 50 lines
        
        CmdTerminal(width_chars, height_chars, texte=bid_ascii.display_result).run()

    def display_console_image(self):
        # Create ASCII image with appropriate parameters
        image_ascii = ImageASCII(self.image,1,1,2,0.1)
        
        # Get image dimensions
        width, height = self.image.size
        
        # Calculate required dimensions based on content
        # For each image pixel, we have 2 characters (width_cellule=2)
        # Plus 4 for vertical borders and spaces (2 on each side)
        width_chars = width * 2 + 4
        
        # Height = number of image lines + 2 for horizontal borders
        height_chars = height + 2
        
        # Limit dimensions to CmdTerminal maximums
        width_chars = min(width_chars, 150)  # Maximum 150 characters wide
        height_chars = min(height_chars, 50)  # Maximum 50 lines
        
        CmdTerminal(width_chars, height_chars, texte=image_ascii.display_result).run()

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

    def zoom(self, event):
        old_scale = self.image_scale
        if event.num == 4 or event.delta > 0:
            self.image_scale += 10
        elif event.num == 5 or event.delta < 0:
            self.image_scale -= 10
        if self.image_scale < self.image_scale_default:
            self.image_scale = self.image_scale_default
        zoom_factor = self.image_scale / old_scale
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        self.draw_bidfile()
        self.refresh_image()
        new_x = (canvas_x * zoom_factor - event.x) / (self.grid_width * self.image_scale)
        new_y = (canvas_y * zoom_factor - event.y) / (self.grid_height * self.image_scale)
        self.canvas.xview_moveto(new_x)
        self.canvas.yview_moveto(new_y)

    def on_mousewheel(self, event):
        """Handle vertical scrolling"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_shift_mousewheel(self, event):
        """Handle horizontal scrolling"""
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def refresh_image(self):
        tk_image = ImageTk.PhotoImage(self.image)
        # Delete old image
        self.canvas.delete("all")
        # Create new image
        self.canvas.create_image(0, 0, anchor=ttk.NW, image=tk_image)
        self.canvas.image = tk_image
        self.outercanvas.configure(bg='#E0E0E0')
        
        # Update scroll region
        image_width = self.grid_width * self.image_scale
        image_height = self.grid_height * self.image_scale
        self.canvas.config(scrollregion=(0, 0, image_width, image_height))

        if image_width > self.canvas.winfo_width() or image_height > self.canvas.winfo_height():
            self.v_scrollbar.grid(row=0, column=1, sticky="ns")
            self.h_scrollbar.grid(row=1, column=0, sticky="ew")
            self.canvas.bind("<MouseWheel>", self.on_mousewheel)
            self.canvas.bind("<Shift-MouseWheel>", self.on_shift_mousewheel)
        else:
            self.v_scrollbar.grid_remove()
            self.h_scrollbar.grid_remove()
            self.canvas.unbind("<MouseWheel>")
            self.canvas.unbind("<Shift-MouseWheel>")
        
        # Redraw selected cells
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid_sel_cells[y, x] == 1:
                    x1, y1 = (x * self.image_scale), (y * self.image_scale)
                    x2, y2 = ((x+1) * self.image_scale), ((y+1) * self.image_scale)
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="red", width=2, dash=(4,4), tags=['cell_select', f"cell_select{x}_{y}"])
        
        # Redraw grid if necessary
        if self.bool_grid:
            self.canvas.delete('grid_line_w')
            self.canvas.delete('grid_line_h')
            self.bool_grid = False
            self.draw_grill()

    def center_image_on_canvas(self, canvas, image):
        photo = ImageTk.PhotoImage(image)
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        x = (canvas_width - image.width) // 2
        y = (canvas_height - image.height) // 2
        canvas.delete("all")
        canvas.create_image(x, y, anchor="nw", image=photo)
        canvas.image = photo

    def refresh_thumbnail(self, dimension=80):
        if hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            # Get image with transparency (handled by Cells)
            thumbnail = self.clipboard.symbol_image
            
            # Resize image
            ratio = thumbnail.width / thumbnail.height
            if ratio > 1:
                new_width = dimension
                new_height = int(dimension / ratio)
            else:
                new_height = dimension
                new_width = int(dimension * ratio)
            thumbnail = thumbnail.resize((new_width, new_height), Image.LANCZOS)
            
            # Configure canvas to support transparency
            self.thumbnail_canvas.configure(bg='#E0E0E0')
            self.center_image_on_canvas(self.thumbnail_canvas, thumbnail)
        else:
            image = Image.open(resource_path(os.path.join('ico', 'empty.png')))
            image = image.resize((84, 84), Image.LANCZOS)
            self.center_image_on_canvas(self.thumbnail_canvas, image)

    def change_size(self, dimension, delta):
        """Change the size of the grid by incrementing or decrementing"""
        if dimension == 'width':
            current = int(self.grid_width_label.cget("text"))
            new_size = current + delta
            if new_size % 2 != 0:
                new_size += 1
            if 5 <= new_size <= 96:
                self.grid_width_label.config(text=str(new_size))
                self.update_grid_size(new_size, None)
        else:  # height
            current = int(self.grid_height_label.cget("text"))
            new_size = current + delta
            if new_size % 2 != 0:
                new_size += 1
            if 5 <= new_size <= 96:
                self.grid_height_label.config(text=str(new_size))
                self.update_grid_size(None, new_size)

    def update_grid_size(self, new_width=None, new_height=None):
        """Update the size of the grid"""
        if self.file_path == '':
            self.new_bid(self.WIDTH, self.HEIGHT, new_width or self.grid_width, new_height or self.grid_height)
            self.init_bid()
        else:
            self.change_bid_size(self.WIDTH, self.HEIGHT, new_width or self.grid_width, new_height or self.grid_height)
            self.init_bid()
        self.grid_sel_cells = np.zeros((self.grid_height, self.grid_width), dtype=int)

    def update_coords_cells(self, event):
        # Get canvas coordinates considering scroll position
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Calculate grid position
        self.grid_x = int(canvas_x / self.image_scale)
        self.grid_y = int(canvas_y / self.image_scale)
        
        if self.grid_y >= self.grid_height:
            self.grid_y = self.grid_height-1
        if self.grid_x >= self.grid_width:
            self.grid_x = self.grid_width-1
        self.coord_label.config(text=f"({self.grid_x+1:02d}, {self.grid_y+1:02d})")

        if self.bool_paste_mode and len(self.grid_clipboard) > 0:
            # Determine the position to paste the cells
            grid_clipboard_x = int((self.clipboard.max_x - self.clipboard.min_x)/2)
            grid_clipboard_y = int((self.clipboard.max_y - self.clipboard.min_y)/2)
            
            # Calculate position considering scroll
            x1 = (self.grid_x - grid_clipboard_x) * self.image_scale
            y1 = (self.grid_y - grid_clipboard_y) * self.image_scale
            
            self.clipboard.image_scale = self.image_scale
            self.clipboard.draw_cells()
            overview_tk = ImageTk.PhotoImage(self.clipboard.symbol_image)
            if self.image_over_id != 0:
                self.canvas.delete(self.image_over_id)
            self.image_over_id = self.canvas.create_image(x1, y1, anchor="nw", image=overview_tk)
            self.canvas.image_sur = overview_tk

    def mode_draw(self):
        self.bool_paste_mode = False
        if self.image_over_id !=0:
            self.canvas.delete(self.image_over_id)
            self.image_over_id = 0
        self.grid_sel_cells = np.zeros((self.grid_height, self.grid_width), dtype=int)
        self.canvas.delete("cell_select")
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
        """Start the selection rectangle."""
        if not self.bool_mode_add_selection:
            self.grid_sel_cells = np.zeros((self.grid_height, self.grid_width), dtype=int)
            self.canvas.delete("cell_select")
        self.bool_paste_mode = False
        self.selection_start = (event.x, event.y)
        self.selection_end = (event.x, event.y)
        outline_color = "green" if self.bool_mode_add_selection else "blue"
        self.selection_rect = self.canvas.create_rectangle(
            self.selection_start[0], self.selection_start[1],
            self.selection_end[0], self.selection_end[1],
            outline=outline_color, dash=(4, 4), tags="selection_rect"
        )

    def update_selection(self, event):
        """Grow the selection rectangle."""
        self.selection_end = (event.x, event.y)
        self.canvas.coords(
            self.selection_rect,
            self.selection_start[0], self.selection_start[1],
            self.selection_end[0], self.selection_end[1]
        )

    def end_selection(self, event):
        """End the selection rectangle."""
        self.selection_end = (event.x, event.y)
        self.update_selected_cells()
        self.canvas.delete("selection_rect")

    def update_selected_cells(self):
        """Update the selected cells."""
        start_x = min(self.selection_start[0], self.selection_end[0]) // self.image_scale
        start_y = min(self.selection_start[1], self.selection_end[1]) // self.image_scale
        end_x = max(self.selection_start[0], self.selection_end[0]) // self.image_scale
        end_y = max(self.selection_start[1], self.selection_end[1]) // self.image_scale

        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                self.grid_sel_cells[y, x] = 1
                x1, y1 = (x * self.image_scale), (y * self.image_scale)
                x2, y2 = ((x+1) * self.image_scale), ((y+1) * self.image_scale)
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="red", width=2, dash=(4,4), tags=['cell_select', f"cell_select{x}_{y}"])

    def mode_select(self):
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<Button-1>", self.select_cellules)
        self.bool_paste_mode = False
        if not self.bool_mode_add_selection:
            self.controler.press(Key.insert)
        if self.image_over_id !=0:
            self.canvas.delete(self.image_over_id)
            self.image_over_id = 0

    def select_cellules(self, event):
        if not self.bool_mode_add_selection:
            self.grid_sel_cells = np.zeros((self.grid_height, self.grid_width), dtype=int)
            self.canvas.delete("cell_select")
        if self.grid_sel_cells[self.grid_y, self.grid_x] == 1:
            if not self.bool_mode_add_selection:
                self.grid_sel_cells[self.grid_y, self.grid_x] = 0
                self.canvas.delete(f"cell_select{self.grid_x}_{self.grid_y}")
        else:
            self.grid_sel_cells[self.grid_y, self.grid_x] = 1
            x1, y1 = (self.grid_x * self.image_scale), (self.grid_y * self.image_scale)
            x2, y2 = ((self.grid_x+1) * self.image_scale), ((self.grid_y+1) * self.image_scale)
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="red", width=2, dash=(4,4), tags=['cell_select', f"cell_select{self.grid_x}_{self.grid_y}"])

    def mode_magicselect(self):
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<Button-1>", self.magic_select_cellules)
        self.bool_paste_mode = False
        if not self.bool_mode_add_selection:
            self.controler.press(Key.insert)
        if self.image_over_id != 0:
            self.canvas.delete(self.image_over_id)
            self.image_over_id = 0

    def magic_select_cellules(self, event):
        if not self.bool_mode_add_selection:
            self.grid_sel_cells = np.zeros((self.grid_height, self.grid_width), dtype=int)
            self.canvas.delete("cell_select")
        grid_x = self.grid_x
        grid_y = self.grid_y
        # Get the color of the clicked cell
        cell_color = self.grid_colors[grid_y, grid_x]
        self.select_adjacent_cells(grid_x, grid_y, cell_color)
        self.update_magic_selection()

    def select_adjacent_cells(self, x, y, color):
        # Check if cell is within grid boundaries
        if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height:
            return
        # Check if cell is already selected
        if self.grid_sel_cells[y, x] == 1:
            return
        # Check if cell has the same color
        if self.grid_colors[y, x] != color:
            return
        # Select the cell
        self.grid_sel_cells[y, x] = 1
        
        # Check adjacent cells
        self.select_adjacent_cells(x, y - 1, color)  # Up
        self.select_adjacent_cells(x, y + 1, color)  # Down
        self.select_adjacent_cells(x - 1, y, color)  # Left
        self.select_adjacent_cells(x + 1, y, color)  # Right

    def update_magic_selection(self):
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid_sel_cells[y, x] == 1:
                    x1, y1 = (x * self.image_scale), (y * self.image_scale)
                    x2, y2 = ((x+1) * self.image_scale), ((y+1) * self.image_scale)
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="red", width=2, dash=(4,4), tags=['cell_select', f"cell_select{x}_{y}"])

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

        self.grid_clipboard = selected_cells
        self.clipboard.insert_symbol(self.grid_clipboard)
        self.refresh_thumbnail()
        self.canvas.delete(f"cell_select")
        self.grid_sel_cells = np.zeros((self.grid_height, self.grid_width), dtype=int)

    def paste_cells(self):
        if hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            # Paste mode activated
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
        if len(self.canvas.gettags("cell_select")) > 0:
            self.save_state()
            if self.flipv_grid():
                self.refresh_image()
        elif hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            self.grid_clipboard = self.clipboard.flipv_cells()
            self.refresh_thumbnail()

    def fliph_cells(self):
        if len(self.canvas.gettags("cell_select")) > 0:
            self.save_state()
            if self.fliph_grid():
                self.refresh_image()
        elif hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            self.grid_clipboard = self.clipboard.fliph_cells()
            self.refresh_thumbnail()

    def rotate_l_cells(self):
        if len(self.canvas.gettags("cell_select")) > 0:
            self.save_state()
            if self.rotate_l_grid():
                self.refresh_image()
        elif hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            self.grid_clipboard = self.clipboard.rotate_l_cells()
            self.refresh_thumbnail()
    
    def rotate_r_cells(self):
        if len(self.canvas.gettags("cell_select")) > 0:
            self.save_state()
            if self.rotate_r_grid():
                self.refresh_image()
        elif hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            self.grid_clipboard = self.clipboard.rotate_r_cells()
            self.refresh_thumbnail()

    def inverse_colors(self):
        if len(self.canvas.gettags("cell_select")) > 0:
            self.save_state()
            if self.inverse_grid():
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

    def draw_grill(self):
        if not self.bool_grid:
            width_image = self.grid_width * self.image_scale
            height_image = self.grid_height * self.image_scale
            # Draw vertical lines
            for x in range(0, self.grid_width + 1):
                line_x = x * self.image_scale
                if x % 5 == 0:
                    width = 2
                else:
                    width = 1
                self.canvas.create_line(line_x, -1, line_x, height_image + 1, 
                                         fill='gray', width=width, dash=(2,2), tags='grid_line_w')
            # Draw horizontal lines
            for y in range(0, self.grid_height + 1):
                line_y = y * self.image_scale
                if y % 5 == 0:
                    width=2
                else:
                    width=1
                self.canvas.create_line(-1, line_y, width_image + 1, line_y, 
                                         fill='gray', width=width, dash=(2,2), tags='grid_line_h')
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
        if key == Key.insert:
            self.bool_mode_add_selection = not self.bool_mode_add_selection
            if self.bool_mode_add_selection:
                self.mode_copy.config(text="ADD (✚)", foreground="green")
                self.canvas.config(cursor="plus")
            else:
                self.mode_copy.config(text="SUB (✖)", foreground="blue")
                self.canvas.config(cursor="")
        
    def on_closing(self):
        if self.bool_backup:
            if askyesno("Save", "There are unsaved changes. Do you want to save before quitting?"):
                self.save_bid()
        self.root.destroy()

if __name__ == "__main__":
    root = ttk.Window(themename="minty")
    app = ImageEditorApp(root)
    root.mainloop()