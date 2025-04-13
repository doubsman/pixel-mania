import ttkbootstrap as ttk
from tkinter import filedialog, Frame
from tkinter.messagebox import askyesno
from PIL import ImageTk, Image
import numpy as np
import os
import subprocess
import sys
import logging
from pynput.keyboard import Key, Controller, Listener
from class_bid import BidFile
from class_cells import Cells
from class_action import ActionState, Action
from class_ascii import ImageASCII, BidASCII
from class_consol import CmdTerminal
from class_carrousel import SymbolCarrousel, BidCarrousel
from class_splashscreen import SplashScreen

VERSION='1.02'

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
        self.tittle = f"Pixel Mania : Bid Editor v{VERSION}"
        
        # Configure main window first
        self.root.title(self.tittle)
        self.root.geometry("1820x1560")
        self.root.resizable(width=True, height=True)
        self.root.minsize(1820, 1560)  # Taille minimale
        
        # Intercept window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Bind keyboard shortcuts
        self.root.bind("<Control-m>", self.open_carousselbid)
        self.root.bind("<Control-o>", self.open_bid)
        self.root.bind("<Control-s>", self.save_bid)
        self.root.bind("<Control-z>", self.undo_action)
        self.root.bind("<Control-c>", lambda event: self.copy_cells(False))
        self.root.bind("<Control-x>", lambda event: self.copy_cells(True))
        self.root.bind("<Control-v>", self.paste_cells)
        self.root.bind("<Control-g>", self.draw_grill)
        self.root.bind("<Control-a>", self.select_all_cells)
        self.root.bind("<Delete>", self.delete_cells)
        self.root.bind("<F11>", self.toggle_fullscreen)

        self.with_zonecanvas = 1820-250-100
        self.height_zonecanvas = 1560-20-100
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
        listener = Listener(on_press=self.on_press, on_release=self.on_release)
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
        
        # Initialize UI
        self.initialize_ui()
        
        # Create and show splash screen after UI is initialized
        self.splash = SplashScreen(self.root, self.tittle)
        
        # Schedule splash screen destruction
        self.root.after(2000, self.destroy_splash)
        
    def initialize_ui(self):
        icon = ImageTk.PhotoImage(file=resource_path(os.path.join('ico', 'carre.png')))
        self.root.iconphoto(False, icon)

        # The left frame to contain the buttons
        left_frame = ttk.Frame(self.root, width=100)
        left_frame['borderwidth'] = 5
        left_frame.pack(side="left", fill="y")

        width_frame = ttk.Frame(left_frame)
        width_frame.pack()
        ttk.Button(width_frame, text="-", command=lambda: self.change_size('width', -2), bootstyle="outline", width=2, padding=0).pack(side="left", padx=0, pady=5)
        self.grid_width_label = ttk.Label(width_frame, text="48", font=('TkDefaultFont', 12, 'bold'))
        self.grid_width_label.pack(side="left", padx=2, pady=0)
        ttk.Button(width_frame, text="+", command=lambda: self.change_size('width', 2), bootstyle="outline", width=2, padding=0).pack(side="left", padx=0, pady=5)

        height_frame = ttk.Frame(left_frame)
        height_frame.pack()
        ttk.Button(height_frame, text="-", command=lambda: self.change_size('height', -2), bootstyle="outline", width=2, padding=0).pack(side="left", padx=0, pady=5)
        self.grid_height_label = ttk.Label(height_frame, text="48", font=('TkDefaultFont', 12, 'bold'))
        self.grid_height_label.pack(side="left", padx=2, pady=0)
        ttk.Button(height_frame, text="+", command=lambda: self.change_size('height', 2), bootstyle="outline", width=2, padding=0).pack(side="left", padx=0, pady=5)
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=4)

        new_button = self.create_button(left_frame, 'ico/plus.png', self.create_bid, "New")
        opengal_button = self.create_button(left_frame, 'ico/opengal.png', self.open_carousselbid, "open")
        open_button = self.create_button(left_frame, 'ico/openbid.png', self.open_bid, "open")
        self.save_button = self.create_button(left_frame, 'ico/save.png', self.save_bid, "Save bid")
        self.saveas_button = self.create_button(left_frame, 'ico/saveas.png', self.saveas_bid, "Save bid")
        self.save_image_button = self.create_button(left_frame, 'ico/photo.png', self.save_image, "Save Image")
        ascii_button = self.create_button(left_frame, 'ico/ascii.png', self.display_console_bid, "Save ASCII")
        grid_button = self.create_button(left_frame, 'ico/grid.png', self.draw_grill, "Grid", "bottom")
        folder_button = self.create_button(left_frame, 'ico/openfolder.png', self.open_folder, "Open Folder", "bottom")
        imageascii_button = self.create_button(left_frame, 'ico/terminalimg.png', self.display_console_image, "Image ASCII", "bottom")

        left_frame2 = ttk.Frame(self.root, width=100)
        left_frame2['borderwidth'] = 5
        left_frame2.pack(side="left", fill="y")

        self.undo_button = self.create_button(left_frame2, 'ico/undo.png', self.undo_action, "Cancel")
        select_button = self.create_button(left_frame2, 'ico/selection.png', self.mode_select, "Cell Selecion")
        area_button = self.create_button(left_frame2, 'ico/square.png', self.mode_area, "Area Selecion")
        lasso_button = self.create_button(left_frame2, 'ico/lasso.png', self.mode_lasso, "Lasso Selecion")
        magic_button = self.create_button(left_frame2, 'ico/magic.png', self.mode_magicselect, "Magic Selecion")
        self.copy_button = self.create_button(left_frame2, 'ico/copy.png', self.copy_cells, "Copy")
        self.cut_button = self.create_button(left_frame2, 'ico/cut.png', lambda: self.copy_cells(True), "Cut")
        self.paste_button = self.create_button(left_frame2, 'ico/paste.png', self.paste_cells, "Cut")
        self.fill_button = self.create_button(left_frame2, 'ico/fill.png', self.fill_cells, "Fill Selecion")
        self.grad_button = self.create_button(left_frame2, 'ico/gradient.png', self.gradient_cells, "Gradient Selecion")
        self.inverse_button = self.create_button(left_frame2, 'ico/inverser.png', self.inverse_colors, "Inverse Colors")
        self.filpv_button = self.create_button(left_frame2, 'ico/flip-v.png', self.flipv_cells, "Flip V")
        self.filph_button = self.create_button(left_frame2, 'ico/flip-h.png', self.fliph_cells, "Flip H")
        self.rotate_r_button = self.create_button(left_frame2, 'ico/rotate-right.png', self.rotate_r_cells, "Rotate Right 90°")
        self.rotate_l_button = self.create_button(left_frame2, 'ico/rotate-left.png', self.rotate_l_cells, "Rotate Left 90°")
        
        save_symbol = self.create_button(left_frame2, 'ico/save.png', self.save_grid_clipboard, "Save Symbol", 'bottom', 25)
        load_symbol = self.create_button(left_frame2, 'ico/open.png', self.open_grid_clipboard, "Load Symbol", 'bottom', 25)

        self.mode_copy = ttk.Label(left_frame2)
        self.mode_copy.pack(side="bottom")

        left_frame3 = ttk.Frame(self.root, width=100)
        left_frame3['borderwidth'] = 5
        left_frame3.pack(side="left", fill="y")

        self.redo_button = self.create_button(left_frame3, 'ico/redo.png', self.redo_action, "Retreive Cancel")
        drawline_button = self.create_button(left_frame3, 'ico/line.png', self.draw_line, "Draw Line")
        rectangle_button = self.create_button(left_frame3, 'ico/rectangle.png', self.draw_rectangle, "Draw Rectangle")
        circle_button = self.create_button(left_frame3, 'ico/circle.png', self.draw_circle, "Draw Circle")

        color_icon = ttk.PhotoImage(file='ico/invent.png')
        self.palet = ttk.Canvas(left_frame3, width=50, height=500, bg='#E0E0E0')
        self.palet.create_image(0, 0, anchor="nw", image=color_icon)
        self.palet.image = color_icon
        self.palet.pack(pady=5)
        self.palet.bind("<Button-1>", self.select_palet)
        self.palet.create_rectangle(0, 250, 50, 300, fill="", outline="red", width=2, tags="cell_color")
        
        self.thumbnail_canvas = ttk.Canvas(left_frame3, width=80, height=80, border=2, relief="sunken", bg='#E0E0E0')
        self.thumbnail_canvas.pack(side="bottom", fill="y", padx=0)
        self.thumbnail_canvas.pack_propagate(False)

        self.size_clipboard_label = ttk.Label(left_frame3, text="", font=('TkDefaultFont', 12, 'bold'))
        self.size_clipboard_label.pack(side="bottom")

        # The right canvas for displaying the image
        self.outercanvas = ttk.Canvas(self.root, bg='#E0E0E0')
        self.outercanvas.pack(expand=True, fill="both")

        # Create zoom control frame in top right corner
        style = ttk.Style()
        style.configure('Zoom.TFrame', background='#E0E0E0')
        style.configure('Zoom.Horizontal.TScale', background='#E0E0E0', troughcolor='#E0E0E0')
        zoom_frame = ttk.Frame(self.outercanvas, style='Zoom.TFrame')
        self.zoom_frame_id = self.outercanvas.create_window(
            self.outercanvas.winfo_reqwidth() - 200, 10,  # Position initiale
            window=zoom_frame,
            anchor="ne"
        )

        # Add zoom icon
        style = ttk.Style()
        style.configure('Custom.Horizontal.TScale', background='#E0E0E0')
        zoom_icon = ttk.PhotoImage(file=resource_path(os.path.join('ico', 'zoom.png'))).subsample(24, 24)
        zoom_label = ttk.Label(zoom_frame, image=zoom_icon, background='#E0E0E0')
        zoom_label.image = zoom_icon
        zoom_label.pack(side="left", padx=5)

        # Add zoom scale
        self.zoom_scale = ttk.Scale(
            zoom_frame,
            from_=0,
            to=100,
            orient="horizontal",
            length=150,
            value=0,
            command=self.on_zoom_scale,
            style='Custom.Horizontal.TScale')

        self.zoom_scale.pack(side="left", padx=5)

        # Create a frame to contain the canvas and scrollbars
        self.canvas_frame = Frame(self.outercanvas)
        
        # Create window initially at (0,0)
        self.window_id = self.outercanvas.create_window(0, 0, window=self.canvas_frame, anchor="nw")
        
        # Update position after window is created
        self.root.after(100, self.update_window_position)

        # Create the scrollbars
        self.v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical")
        self.h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient="horizontal")
        self.canvas = ttk.Canvas(self.canvas_frame,
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

        # Bind window resize event
        self.root.bind("<Configure>", self.on_window_resize)

        # Create coordinates label on outercanvas
        self.coord_label = ttk.Label(self.outercanvas, text="[00, 00]", background='#E0E0E0', font=('TkDefaultFont', 12, 'bold'))
        self.coord_label_id = self.outercanvas.create_window(10, 10, window=self.coord_label, anchor="nw")

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

    def open_bid(self, event=None):
        bid_path = filedialog.askopenfilename(title="Open Bid File", filetypes=[("Bid Files", "*.bid")], initialdir="wrk")
        if bid_path != '':
            self.save_bid()
            self.file_path = bid_path
            self.root.title(f'{self.tittle} [{self.file_path}]')  
            self.load_bidfile(self.file_path, self.with_zonecanvas, self.height_zonecanvas)
            self.init_bid()      

    def open_carousselbid(self, event=None):
        # make modal window
        dialog = ttk.Toplevel(self.root)
        dialog.title("Open Bid File")
        icon = ImageTk.PhotoImage(file=resource_path(os.path.join('ico', 'carre.png')))
        dialog.iconphoto(False, icon)
        dialog.geometry("1290x1290")
        dialog.transient(self.root)  # make the window modal
        dialog.grab_set()  # force focus on this window
        dialog.resizable(width=True, height=True)
        dialog.bind('<F11>', lambda e: dialog.attributes('-fullscreen', not dialog.attributes('-fullscreen')))
        dialog.bind('<Escape>', lambda e: dialog.attributes('-fullscreen', False))
        # Configure the window expansion
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)
        
        # create carrousel
        def on_bid_selected(bid_file):
            self.save_bid()
            self.file_path = bid_file
            self.root.title(f'{self.tittle} [{self.file_path}]')  
            self.load_bidfile(self.file_path, self.with_zonecanvas, self.height_zonecanvas)
            self.init_bid()
            dialog.destroy()
            
        carrousel = BidCarrousel(dialog, callback=on_bid_selected)
        carrousel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Position the window next to the mouse
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        
        # Get the main window position
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        
        # Calculate the window position
        x = main_x + 20  # 20 pixels to the right of the main window
        y = main_y  # Same height as main window
        
        # Ensure the window stays within the screen boundaries
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        if x + width > screen_width:
            x = main_x - width - 20  # Place to the left of the main window if not enough space on the right
        if y < 0:
            y = 0  # Align to the top if not enough space above
        if y + height > screen_height:
            y = screen_height - height  # Align to the bottom if not enough space below
            
        dialog.geometry(f'+{x}+{y}')
        
        # Define a minimum size for the window
        dialog.minsize(1290,1290)

        # Wait for the window to be closed
        dialog.wait_window()

    def create_bid(self):
        self.save_bid()
        self.root.title(f'{self.tittle} : [NEW]')
        self.file_path = ''
        self.new_bid(self.with_zonecanvas, self.height_zonecanvas)
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

    def save_bid(self, event=None):
        if self.file_path == '':
            self.saveas_bid()
        elif self.bool_backup:
            self.write_bid()

    def saveas_bid(self):
        if self.bool_backup or self.file_path != '':
            self.file_path = filedialog.asksaveasfilename(title="Save Bid File", filetypes=[("Bid Files", "*.bid")])
            if self.file_path != '':
                if not self.file_path.endswith('.bid'):
                    self.file_path += '.bid'
                # Check if file already exists
                if os.path.isfile(self.file_path):
                    # Ask for confirmation to overwrite
                    overwrite = askyesno("Overwrite File", f"The file '{self.file_path}' already exists. Do you want to overwrite it?")
                    if not overwrite:
                        return
            self.write_bid()
    
    def write_bid(self):
        if self.file_path != '':
            self.save_bidfile(self.file_path)
            self.file_path = self.path_bid
            self.root.title(f'{self.tittle} [{self.file_path}]')
            self.bool_backup = False
            self.update_buttons_state()

    def save_image(self):
        if self.file_path == '':
            file_img = filedialog.asksaveasfilename(title="Save PNG File", filetypes=[("PNG Image Files", "*.png")])
        else:
            file_img = self.file_path.replace('.bid',f'_{self.grid_width}x{self.grid_height}.png')
        self.save_imagefile(file_img, bool_outline=self.bool_grid)

    def open_folder(self):
        if self.file_path != '':
            open_path = os.path.dirname(self.file_path).replace('/','\\')
        else:
            open_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'bid')
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
        
        # Cacher la fenêtre initialement
        dialog.withdraw()
        
        # create carrousel
        def on_symbol_selected(symbol):
            self.grid_clipboard = symbol
            self.clipboard.insert_symbol(symbol)  # Update clipboard with new symbol
            self.refresh_thumbnail()
            self.paste_cells()
            #self.update_buttons_state()
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
        
        # Afficher la fenêtre une fois positionnée
        dialog.deiconify()
        
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
            # Limit maximum zoom to 5x the default scale
            if self.image_scale < self.image_scale_default * 5:
                self.image_scale += 10
        elif event.num == 5 or event.delta < 0:
            self.image_scale -= 10

        # Limit minimum Zoom
        if self.image_scale < self.image_scale_default:
            self.image_scale = self.image_scale_default
        # Limit maximum Zoom
        elif self.image_scale > self.image_scale_default * 5:
            self.image_scale = self.image_scale_default * 5

        zoom_factor = self.image_scale / old_scale
        
        # Update zoom scale to match current zoom level
        scale_value = ((self.image_scale / self.image_scale_default) - 1) / 5 * 100
        self.zoom_scale.set(scale_value)

        # Save current cursor position
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Update image size and grid
        self.draw_bidfile()
        self.refresh_image()
        
        # Update scroll region
        image_width = self.grid_width * self.image_scale
        image_height = self.grid_height * self.image_scale
        self.canvas.config(scrollregion=(0, 0, image_width, image_height))
        
        # Calculate new view position to center on cursor
        new_x = (canvas_x * zoom_factor - event.x) / image_width
        new_y = (canvas_y * zoom_factor - event.y) / image_height
        
        # Apply new zoom and position
        self.canvas.xview_moveto(new_x)
        self.canvas.yview_moveto(new_y)
        
        # Redraw the grid with the new scale
        if self.bool_grid:
            self.draw_grill(change=False)

    def on_zoom_scale(self, value):
        try:
            value = float(value)
            # Calculate new scale: 0=default scale, 100=5x default scale
            new_scale = int(self.image_scale_default * (1 + (value/100) * 4))
            old_scale = self.image_scale
            self.image_scale = new_scale
            
            # Update image with new scale
            self.draw_bidfile()
            self.refresh_image()
            
            # Update scroll region
            image_width = self.grid_width * self.image_scale
            image_height = self.grid_height * self.image_scale
            self.canvas.config(scrollregion=(0, 0, image_width, image_height))
            
            # Redraw grid if necessary
            if self.bool_grid:
                self.draw_grill(change=False)
        except ValueError:
            pass

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
        
        # Redraw selected cells if necessary
        if np.any(self.grid_sel_cells == 1):
            for y in range(self.grid_height):
                for x in range(self.grid_width):
                    if self.grid_sel_cells[y, x] == 1:
                        x1, y1 = (x * self.image_scale), (y * self.image_scale)
                        x2, y2 = ((x+1) * self.image_scale), ((y+1) * self.image_scale)
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="red", width=2, dash=(4,4), tags=['cell_select', f"cell_select{x}_{y}"])

        # Enable/disable buttons based on selection and clipboard content
        self.update_buttons_state()
        
        # Redraw grid if necessary
        self.draw_grill(change=False)

    def update_buttons_state(self):
        """Update the state of buttons."""
        if np.any(self.grid_sel_cells == 1):
            # Enable buttons when cells are selected
            self.copy_button.config(state=ttk.NORMAL)
            self.cut_button.config(state=ttk.NORMAL)
            self.grad_button.config(state=ttk.NORMAL)
            self.fill_button.config(state=ttk.NORMAL)
        else:
            # Disable buttons when no cells are selected
            self.copy_button.config(state=ttk.DISABLED)
            self.cut_button.config(state=ttk.DISABLED)
            self.grad_button.config(state=ttk.DISABLED)
            self.fill_button.config(state=ttk.DISABLED)

        if hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            self.paste_button.config(state=ttk.NORMAL)
        else:
            self.paste_button.config(state=ttk.DISABLED)
        
        if self.bool_backup:
            self.save_button.config(state=ttk.NORMAL)
            self.saveas_button.config(state=ttk.NORMAL)
        else:
            self.save_button.config(state=ttk.DISABLED)
            self.saveas_button.config(state=ttk.DISABLED)

        if self.file_path != '':
            self.save_image_button.config(state=ttk.NORMAL)
        else:
            self.save_image_button.config(state=ttk.DISABLED)

        if self.undo_stack:
            self.undo_button.config(state=ttk.NORMAL)
        else:
            self.undo_button.config(state=ttk.DISABLED)
        if self.redo_stack:
            self.redo_button.config(state=ttk.NORMAL)
        else:
            self.redo_button.config(state=ttk.DISABLED)
        
        if not len(self.canvas.gettags("cell_select")) > 0 and \
            not (hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0):
            self.inverse_button.config(state=ttk.DISABLED)
            self.filpv_button.config(state=ttk.DISABLED)
            self.filph_button.config(state=ttk.DISABLED)
            self.rotate_r_button.config(state=ttk.DISABLED)
            self.rotate_l_button.config(state=ttk.DISABLED)
        else:
            self.inverse_button.config(state=ttk.NORMAL)
            self.filpv_button.config(state=ttk.NORMAL)
            self.filph_button.config(state=ttk.NORMAL)
            self.rotate_r_button.config(state=ttk.NORMAL)
            self.rotate_l_button.config(state=ttk.NORMAL)

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
        self.update_buttons_state()

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
        if self.file_path == '' and not self.bool_backup:
            self.new_bid(self.with_zonecanvas, self.height_zonecanvas, new_width or self.grid_width, new_height or self.grid_height)
            self.init_bid()
        else:
            self.change_bid_size(self.with_zonecanvas, self.height_zonecanvas, new_width or self.grid_width, new_height or self.grid_height)
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
        if self.grid_y < 0:
            self.grid_y = 0
        if self.grid_x < 0:
            self.grid_x = 0
                
        self.coord_label.config(text=f"[{self.grid_x+1:02d}, {self.grid_y+1:02d}]")

        # Update the position of the image overlay
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
        self.grid_bid[self.grid_y][self.grid_x] = self.current_select_shape
        self.grid_colors[self.grid_y][self.grid_x] = self.current_select_color
        self.draw_cell(self.grid_x, self.grid_y, self.current_select_shape, self.current_select_color)
        self.refresh_image()

    def draw_line(self):
        """Enable line drawing mode"""
        self.bool_paste_mode = False
        if self.image_over_id != 0:
            self.canvas.delete(self.image_over_id)
            self.image_over_id = 0
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<ButtonPress-1>", self.start_line)
        self.canvas.bind("<B1-Motion>", self.update_line)
        self.canvas.bind("<ButtonRelease-1>", self.end_line)

    def start_line(self, event):
        """Start drawing a line"""
        self.selection_start = (event.x, event.y)
        self.selection_end = (event.x, event.y)
        self.selection_rect = self.canvas.create_line(
            self.selection_start[0], self.selection_start[1],
            self.selection_end[0], self.selection_end[1],
            fill="blue", dash=(4, 4), tags="selection_rect"
        )

    def update_line(self, event):
        """Update the line while drawing"""
        self.selection_end = (event.x, event.y)
        self.canvas.coords(
            self.selection_rect,
            self.selection_start[0], self.selection_start[1],
            self.selection_end[0], self.selection_end[1]
        )

    def end_line(self, event):
        """Finish drawing the line and apply it to the grid"""
        self.selection_end = (event.x, event.y)
        self.save_state()
        
        # Get grid coordinates for start and end points
        start_x = int(self.selection_start[0] / self.image_scale)
        start_y = int(self.selection_start[1] / self.image_scale)
        end_x = int(self.selection_end[0] / self.image_scale)
        end_y = int(self.selection_end[1] / self.image_scale)
        
        # Use Bresenham's algorithm to draw the line
        dx = abs(end_x - start_x)
        dy = abs(end_y - start_y)
        x, y = start_x, start_y
        n = 1 + dx + dy
        x_inc = 1 if end_x > start_x else -1
        y_inc = 1 if end_y > start_y else -1
        error = dx - dy
        dx *= 2
        dy *= 2

        for _ in range(n):
            if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                self.grid_bid[y, x] = self.current_select_shape
                self.grid_colors[y, x] = self.current_select_color
                self.draw_cell(x, y, self.current_select_shape, self.current_select_color)
            
            if error > 0:
                x += x_inc
                error -= dy
            else:
                y += y_inc
                error += dx

        # Refresh the image and remove the selection line
        self.refresh_image()
        self.canvas.delete("selection_rect")

    def draw_rectangle(self):
        self.bool_paste_mode = False
        if self.image_over_id !=0:
            self.canvas.delete(self.image_over_id)
            self.image_over_id = 0
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<ButtonPress-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-1>", self.end_selection_rectangle)
    
    def end_selection_rectangle(self, event):
        """End the selection rectangle and draw the rectangle."""
        self.selection_end = (event.x, event.y)
        # Get the grid coordinates for start and end points
        start_x = min(self.selection_start[0], self.selection_end[0]) // self.image_scale
        start_y = min(self.selection_start[1], self.selection_end[1]) // self.image_scale
        end_x = max(self.selection_start[0], self.selection_end[0]) // self.image_scale
        end_y = max(self.selection_start[1], self.selection_end[1]) // self.image_scale
        # Save state for undo
        self.save_state()
        # Draw the rectangle
        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                # Only draw on the edges for a rectangle
                if (x == start_x or x == end_x or y == start_y or y == end_y):
                    self.grid_bid[y, x] = self.current_select_shape
                    self.grid_colors[y, x] = self.current_select_color
                    self.draw_cell(x, y, self.current_select_shape, self.current_select_color)
        # Reset coordinates display
        self.coord_label.config(text=f"[{self.grid_x+1:02d}, {self.grid_y+1:02d}]")
        # Refresh the image
        self.refresh_image()
        # Remove the selection rectangle
        self.canvas.delete("selection_rect")

    def draw_circle(self):
        """Enable circle drawing mode"""
        self.bool_paste_mode = False
        if self.image_over_id != 0:
            self.canvas.delete(self.image_over_id)
            self.image_over_id = 0
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<ButtonPress-1>", self.start_circle)
        self.canvas.bind("<B1-Motion>", self.update_circle)
        self.canvas.bind("<ButtonRelease-1>", self.end_circle)

    def start_circle(self, event):
        """Start drawing a circle"""
        self.selection_start = (event.x, event.y)
        self.selection_end = (event.x, event.y)
        # Create a temporary circle (oval) that will be updated while drawing
        self.selection_rect = self.canvas.create_oval(
            self.selection_start[0], self.selection_start[1],
            self.selection_end[0], self.selection_end[1],
            outline="blue", dash=(4, 4), tags="selection_rect"
        )

    def update_circle(self, event):
        """Update the circle while drawing"""
        self.selection_end = (event.x, event.y)
        # Calculate the radius based on the distance between start and current point
        radius = ((self.selection_end[0] - self.selection_start[0])**2 + 
                 (self.selection_end[1] - self.selection_start[1])**2)**0.5
        # Update the circle coordinates
        self.canvas.coords(
            self.selection_rect,
            self.selection_start[0] - radius, self.selection_start[1] - radius,
            self.selection_start[0] + radius, self.selection_start[1] + radius
        )

    def end_circle(self, event):
        """Finish drawing the circle and apply it to the grid"""
        self.selection_end = (event.x, event.y)
        self.save_state()
        
        # Get center point and radius in grid coordinates
        center_x = int(self.selection_start[0] / self.image_scale)
        center_y = int(self.selection_start[1] / self.image_scale)
        radius = int(((self.selection_end[0] - self.selection_start[0])**2 + 
                     (self.selection_end[1] - self.selection_start[1])**2)**0.5 / self.image_scale)
        
        # Draw the circle using Bresenham's circle algorithm
        x = radius
        y = 0
        err = 0
        
        while x >= y:
            # Draw 8 points for each iteration (symmetry of a circle)
            points = [
                (center_x + x, center_y + y),
                (center_x + y, center_y + x),
                (center_x - y, center_y + x),
                (center_x - x, center_y + y),
                (center_x - x, center_y - y),
                (center_x - y, center_y - x),
                (center_x + y, center_y - x),
                (center_x + x, center_y - y)
            ]
            
            # Draw all points that are within the grid bounds
            for px, py in points:
                if 0 <= px < self.grid_width and 0 <= py < self.grid_height:
                    self.grid_bid[py, px] = self.current_select_shape
                    self.grid_colors[py, px] = self.current_select_color
                    self.draw_cell(px, py, self.current_select_shape, self.current_select_color)
            
            if err <= 0:
                y += 1
                err += 2*y + 1
            if err > 0:
                x -= 1
                err -= 2*x + 1
        
        # Refresh the image and remove the selection circle
        self.refresh_image()
        self.canvas.delete("selection_rect")

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
        # Calculate rectangle dimensions in grid cells
        start_x = min(self.selection_start[0], self.selection_end[0]) // self.image_scale
        start_y = min(self.selection_start[1], self.selection_end[1]) // self.image_scale
        end_x = max(self.selection_start[0], self.selection_end[0]) // self.image_scale
        end_y = max(self.selection_start[1], self.selection_end[1]) // self.image_scale
        width = end_x - start_x + 1
        height = end_y - start_y + 1
        
        # Update coordinates label with dimensions
        self.coord_label.config(text=f"[{self.grid_x+1:02d}, {self.grid_y+1:02d}] [{width:02d}x{height:02d}]")

    def end_selection(self, event):
        """End the selection rectangle."""
        self.selection_end = (event.x, event.y)
        self.update_selected_cells()
        self.canvas.delete("selection_rect")
         # Reset coordinates display
        self.coord_label.config(text=f"[{self.grid_x+1:02d}, {self.grid_y+1:02d}]")

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
        self.update_buttons_state()

    def mode_lasso(self):
        self.bool_paste_mode = False
        if self.image_over_id !=0:
            self.canvas.delete(self.image_over_id)
            self.image_over_id = 0
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<ButtonPress-1>", self.start_lasso)
        self.canvas.bind("<B1-Motion>", self.update_lasso)
        self.canvas.bind("<ButtonRelease-1>", self.end_lasso)
    
    def start_lasso(self, event):   
        """Start the lasso selection."""
        if not self.bool_mode_add_selection:
            self.grid_sel_cells = np.zeros((self.grid_height, self.grid_width), dtype=int)
            self.canvas.delete("cell_select")
        self.bool_paste_mode = False
        self.selection_start = (event.x, event.y)
        self.selection_end = (event.x, event.y)
        outline_color = "green" if self.bool_mode_add_selection else "blue"
        self.selection_rect = self.canvas.create_polygon(
            self.selection_start[0], self.selection_start[1],
            outline=outline_color, fill="", dash=(4, 4), tags="selection_rect"
        )
        self.canvas.bind("<Motion>", self.update_lasso)
        self.canvas.bind("<Leave>", self.end_lasso)
    
    def update_lasso(self, event):
        """Update the lasso selection."""
        self.selection_end = (event.x, event.y)
        coords = self.canvas.coords(self.selection_rect)
        coords.append(event.x)
        coords.append(event.y)
        self.canvas.coords(self.selection_rect, *coords)
        self.canvas.bind("<Motion>", self.update_lasso)
        self.canvas.bind("<Leave>", self.end_lasso)

    def end_lasso(self, event):
        """End the lasso selection."""
        self.selection_end = (event.x, event.y)
        coords = self.canvas.coords(self.selection_rect)
        # Get the polygon points
        polygon_points = [(coords[i], coords[i+1]) for i in range(0, len(coords), 2)]
        # Check if each cell is inside the polygon
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                cell_center = ((x + 0.5) * self.image_scale, (y + 0.5) * self.image_scale)
                if self.is_point_in_polygon(cell_center, polygon_points):
                    self.grid_sel_cells[y, x] = 1
                    x1, y1 = (x * self.image_scale), (y * self.image_scale)
                    x2, y2 = ((x+1) * self.image_scale), ((y+1) * self.image_scale)
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="red", width=2, dash=(4,4), tags=['cell_select', f"cell_select{x}_{y}"])
        self.update_buttons_state()
        self.canvas.delete("selection_rect")
    
    def is_point_in_polygon(self, point, polygon):
        """Check if a point is inside a polygon using the ray-casting algorithm."""
        x, y = point
        inside = False
        n = len(polygon)
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside
    
    def mode_select(self):
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<Button-1>", self.select_cellules)
        self.bool_paste_mode = False
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
        else:
            self.grid_sel_cells[self.grid_y, self.grid_x] = 1
            x1, y1 = (self.grid_x * self.image_scale), (self.grid_y * self.image_scale)
            x2, y2 = ((self.grid_x+1) * self.image_scale), ((self.grid_y+1) * self.image_scale)
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="red", width=2, dash=(4,4), tags=['cell_select', f"cell_select{self.grid_x}_{self.grid_y}"])
        self.update_buttons_state()

    def mode_magicselect(self):
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<Button-1>", self.magic_select_cellules)
        self.bool_paste_mode = False
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
        
        # Check adjacent cells (including diagonals)
        self.select_adjacent_cells(x, y - 1, color)      # Up
        self.select_adjacent_cells(x, y + 1, color)      # Down
        self.select_adjacent_cells(x - 1, y, color)      # Left
        self.select_adjacent_cells(x + 1, y, color)      # Right
        #self.select_adjacent_cells(x - 1, y - 1, color)  # Up-Left
        #self.select_adjacent_cells(x + 1, y - 1, color)  # Up-Right
        #self.select_adjacent_cells(x - 1, y + 1, color)  # Down-Left
        #self.select_adjacent_cells(x + 1, y + 1, color)  # Down-Right

    def update_magic_selection(self):
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid_sel_cells[y, x] == 1:
                    x1, y1 = (x * self.image_scale), (y * self.image_scale)
                    x2, y2 = ((x+1) * self.image_scale), ((y+1) * self.image_scale)
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="red", width=2, dash=(4,4), tags=['cell_select', f"cell_select{x}_{y}"])
        self.update_buttons_state()

    def delete_cells(self, event=None):
        """Delete selected cells."""
        self.save_state()        
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid_sel_cells[y, x] == 1:
                    self.draw_cell(x, y, 0, 0)
                    self.grid_bid[y][x] = 0
                    self.grid_colors[y][x] = 0
        self.refresh_image()
        self.canvas.delete(f"cell_select")
        self.grid_sel_cells = np.zeros((self.grid_height, self.grid_width), dtype=int)
        # Update buttons state to reflect the selection
        self.update_buttons_state()

    def select_all_cells(self, event=None):
        """Select all cells in the grid."""
        # Reset existing selection
        self.grid_sel_cells = np.ones((self.grid_height, self.grid_width), dtype=int)
        self.canvas.delete("cell_select")
        
        # Create selection rectangles for all cells
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                x1, y1 = (x * self.image_scale), (y * self.image_scale)
                x2, y2 = ((x+1) * self.image_scale), ((y+1) * self.image_scale)
                self.canvas.create_rectangle(
                    x1, y1, x2, y2, 
                    fill="", 
                    outline="red", 
                    width=2, 
                    dash=(4,4), 
                    tags=['cell_select', f"cell_select{x}_{y}"]
                )
        # Update buttons state to reflect the selection
        self.update_buttons_state()

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
        self.update_buttons_state()

        # Update size label
        if len(self.grid_clipboard) > 0:
            min_x = min(x for x, _, _, _ in self.grid_clipboard)
            max_x = max(x for x, _, _, _ in self.grid_clipboard)
            min_y = min(y for _, y, _, _ in self.grid_clipboard)
            max_y = max(y for _, y, _, _ in self.grid_clipboard)
            width = max_x - min_x + 1
            height = max_y - min_y + 1
            self.size_clipboard_label.config(text=f"{width:02d} x {height:02d}")
        else:
            self.size_clipboard_label.config(text="")

    def paste_cells(self, event=None):
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
            if self.inverse_grid():
                self.refresh_image()
                self.save_state()
        elif hasattr(self, 'grid_clipboard') and len(self.grid_clipboard) > 0:
            self.grid_clipboard = self.clipboard.inverse_colors()
            self.refresh_thumbnail()

    def fill_cells(self):
        if len(self.canvas.gettags("cell_select")) > 0:
            for y in range(self.grid_height):
                for x in range(self.grid_width):
                    if self.grid_sel_cells[y, x] == 1:
                        self.grid_colors[y, x] = self.current_select_color
                        self.grid_bid[y, x] = self.current_select_shape
                        self.draw_cell(x, y, self.grid_bid[y, x], self.grid_colors[y, x], False)
            self.refresh_image()
            self.save_state()

    def gradient_cells(self):
        if len(self.canvas.gettags("cell_select")) > 0:
            min_x, max_x, min_y, max_y = self._get_selection_bounds()
            width = (max_x - min_x + 1)
            for y in range(self.grid_height):
                for x in range(self.grid_width):
                    if self.grid_sel_cells[y, x] == 1:
                        color_value = int((x - min_x) / width * 6)
                        self.grid_bid[y, x] = 1
                        self.grid_colors[y, x] = color_value
                        self.draw_cell(x, y, self.grid_bid[y, x], self.grid_colors[y, x], False)
            self.refresh_image()
            self.save_state()

    def draw_grill(self, event=None, change=True):
        if change:
            self.bool_grid = not self.bool_grid

        if self.bool_grid:
            self.canvas.delete('grid_line_w')
            self.canvas.delete('grid_line_h')

            # Drawing vertical lines
            for x in range(0, self.grid_width + 1):
                line_x = x * self.image_scale
                if x % 5 == 0:
                    width = 2
                else:
                    width = 1
                self.canvas.create_line(line_x, -1, line_x, self.grid_height * self.image_scale + 1, 
                                     fill='gray', width=width, dash=(2,2), tags='grid_line_w')
            
            # Drawing horizontal lines
            for y in range(0, self.grid_height + 1):
                line_y = y * self.image_scale
                if y % 5 == 0:
                    width = 2
                else:
                    width = 1
                self.canvas.create_line(-1, line_y, self.grid_width * self.image_scale + 1, line_y, 
                                     fill='gray', width=width, dash=(3,3), tags='grid_line_h')
        else:
            self.canvas.delete('grid_line_w')
            self.canvas.delete('grid_line_h')

    def undo_action(self, event=None):
        action = self.undo_actionstate()
        if action is not None:
            current_state = Action(
                self.grid_bid.copy(), 
                self.grid_colors.copy(), 
                self.grid_clipboard.copy(), 
                self.grid_sel_cells.copy(),
                self.grid_width,
                self.grid_height
            )
            self.retreive_action(action)
            self.redo_stack.append(current_state)

    def redo_action(self, event=None):
        self.retreive_action(self.redo_actionstate())
        self.update_buttons_state()
        self.update_grid_size()

    def retreive_action(self, action=None):
        if action is not None:
            self.grid_bid = action.grid_bid
            self.grid_colors = action.grid_colors
            self.grid_clipboard = action.grid_clipboard
            self.grid_sel_cells = action.grid_sel_cells
            self.grid_width = action.grid_width
            self.grid_height = action.grid_height
            self.draw_bidfile()
            self.refresh_image()
            self.refresh_thumbnail()
            self.update_buttons_state()
            self.update_grid_size()

    def save_state(self):
        """Save Action."""
        self.bool_backup = True
        self.save_actionstate(
            self.grid_bid, 
            self.grid_colors, 
            self.grid_clipboard, 
            self.grid_sel_cells,
            self.grid_width,
            self.grid_height
        )

    def on_press(self, key):
        if key == Key.shift:
            self.bool_mode_add_selection = True
            self.mode_copy.config(text="ADD (✚)", foreground="green")
            self.canvas.config(cursor="plus")

    def on_release(self, key):
        if key == Key.shift:
            self.bool_mode_add_selection = False
            self.mode_copy.config(text="")
            self.canvas.config(cursor="")

    def on_closing(self):
        if self.bool_backup:
            if askyesno("Save", "There are unsaved changes. Do you want to save before quitting?"):
                self.save_bid()
        self.root.destroy()

    def destroy_splash(self):
        """Destroy the splash screen if it exists"""
        if hasattr(self, 'splash'):
            self.splash.destroy()
            delattr(self, 'splash')

    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))

    def on_window_resize(self, event):
        """Handle window resize event"""
        if event.widget == self.root:
            # Add a delay before updating the interface
            if hasattr(self, '_resize_timer'):
                self.root.after_cancel(self._resize_timer)
            self._resize_timer = self.root.after(100, lambda: self._do_resize(event))

    def _do_resize(self, event):
        """Effectue la mise à jour après un délai"""
        # Update canvas size
        self.with_zonecanvas = self.root.winfo_width() - 250 - 100
        self.height_zonecanvas = self.root.winfo_height() - 20 - 100
        
        # Recalculate the default image scale based on the new window size
        self.image_scale_default = min(self.with_zonecanvas // self.grid_width, self.height_zonecanvas // self.grid_height)
        self.image_scale = min(self.with_zonecanvas // self.grid_width, self.height_zonecanvas // self.grid_height)
        
        # Update image size and scroll region
        if hasattr(self, 'image'):
            image_width = self.grid_width * self.image_scale
            image_height = self.grid_height * self.image_scale
            self.canvas.config(scrollregion=(0, 0, image_width, image_height))
            self.draw_bidfile()
            self.refresh_image()
            
            # Redraw grid if active
            if self.bool_grid:
                self.draw_grill(change=False)
        
        # Update canvas position and size
        self.update_window_position()

        # Update coordinate label position
        self.outercanvas.coords(self.coord_label_id, 10, 10)

        # Update zoom frame position
        if hasattr(self, 'zoom_frame_id'):
            self.outercanvas.coords(
                self.zoom_frame_id,
                self.outercanvas.winfo_width() - 10,
                10
            )

    def update_window_position(self):
        """Update the position of the canvas frame in the outercanvas"""
        # Calculate the size of the squares
        cell_size = min(self.with_zonecanvas // self.grid_width, self.height_zonecanvas // self.grid_height)
        
        # Calculate canvas size
        canvas_width = self.grid_width * cell_size
        canvas_height = self.grid_height * cell_size
        
        # Center canvas in outercanvas
        x = (100 + self.with_zonecanvas - canvas_width) // 2
        y = (100 + self.height_zonecanvas - canvas_height) // 2

        # Update canvas frame position and size
        self.outercanvas.coords(self.window_id, x, y)
        self.canvas_frame.config(width=canvas_width, height=canvas_height)
        
        # Update drawing canvas size
        self.canvas.config(width=canvas_width, height=canvas_height)


if __name__ == "__main__":
    root = ttk.Window(themename="minty")
    app = ImageEditorApp(root)
    root.mainloop()