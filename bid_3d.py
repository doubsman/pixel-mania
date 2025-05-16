import ttkbootstrap as ttk
from tkinter import ttk as ttk2
from tkinter import filedialog
from PIL import ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from class_bid_3d import Bid3D
from class_carrousel import BidCarrousel
import numpy as np
import os

class Bid3DApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Mania - BID 3D Editor")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Initialisation sans passer root
        self.editor = Bid3D()
        self.edge_colors = {
            "White": (0.7, 0.7, 0.7, 1.0),
            "Black": (0.0, 0.0, 0.0, 1.0)
        }
        self.black_height_var = ttk.DoubleVar(value=0.50)
        self.white_height_var = ttk.DoubleVar(value=0.45)
        self.setup_ui()
        
    def setup_ui(self):
        icon = ImageTk.PhotoImage(file=os.path.join('ico', 'carre.png'))
        self.root.iconphoto(False, icon)
        # Création de l'interface graphique
        # Frame principale
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Frame de contrôle (gauche)
        control_frame = ttk.Frame(main_frame)  # Changé de LabelFrame à Frame
        control_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        # Définir une largeur fixe pour tous les widgets
        widget_width = 15
        
        # Bouton Ouvrir avec largeur fixe
        open_button = ttk.Button(control_frame, text="Open BID", 
                               bootstyle="outline", 
                               command=self.open_bid,
                               width=widget_width)
        open_button.pack(pady=5)
        
        open_carrousel_button = ttk.Button(control_frame, text="Mosaïc BID", 
                               bootstyle="outline", 
                               command=self.open_carousselbid,
                               width=widget_width)
        open_carrousel_button.pack(pady=5)

        # Frame pour les contrôles de hauteur
        ttk.Label(control_frame, text="Height black:").pack(pady=(10,0))
        black_scale = ttk.Scale(
            control_frame,
            from_=0,
            to=2,
            variable=self.black_height_var,
            orient="horizontal",
            command=lambda _: self.on_height_changed()
        )
        black_scale.pack(pady=5, fill='x', padx=5)
        
        ttk.Label(control_frame, text="Height white:").pack(pady=(10,0))
        white_scale = ttk.Scale(
            control_frame,
            from_=0,
            to=2,
            variable=self.white_height_var,
            orient="horizontal",
            command=lambda _: self.on_height_changed()
        )
        white_scale.pack(pady=5, fill='x', padx=5)

        # Combobox pour les élévations
        ttk.Label(control_frame, text="Elevation:").pack(pady=(10,0))
        self.elevation_combo = ttk2.Combobox(control_frame, 
                                           values=list(self.editor.elevation_templates.keys()),
                                           state='readonly',
                                           width=widget_width)
        self.elevation_combo.set("Plat")
        self.elevation_combo.pack(pady=5)
        self.elevation_combo.bind('<<ComboboxSelected>>', self.update_3d_view)

        # Combobox pour les contours
        ttk.Label(control_frame, text="Contours:").pack(pady=(10,0))
        self.edge_combo = ttk2.Combobox(control_frame, 
                                       values=list(self.edge_colors.keys()),
                                       state='readonly',
                                       width=widget_width)
        self.edge_combo.set("White")
        self.edge_combo.pack(pady=5)
        self.edge_combo.bind('<<ComboboxSelected>>', self.update_3d_view)

        # Checkbox pour afficher/masquer les cellules blanches
        self.show_white_var = ttk.BooleanVar(value=True)
        show_white_check = ttk.Checkbutton(
            control_frame, 
            text="display White",
            variable=self.show_white_var,
            command=self.update_3d_view,
            width=widget_width
        )
        show_white_check.pack(pady=5)

        # Bouton Exporter avec largeur fixe
        export_button = ttk.Button(control_frame, text="Exporter STL", 
                                 bootstyle="outline", 
                                 command=self.export_stl,
                                 width=widget_width)
        export_button.pack(pady=5)

        # Frame pour la vue 3D
        view_frame = ttk.Frame(main_frame)
        view_frame.pack(side='right', fill='both', expand=True)
        
        # Création de la figure 3D
        self.fig = plt.Figure(figsize=(8, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_axis_off()
        self.canvas = FigureCanvasTkAgg(self.fig, view_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def open_bid(self):
        file_path = filedialog.askopenfilename(
            title="Ouvrir fichier BID",
            filetypes=[("Fichiers BID", "*.bidz"), ("Fichiers BID shape", "*.bid"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            self.editor.load_bidfile(file_path)
            self.update_3d_view()

    def open_carousselbid(self, event=None):
        # make modal window
        dialog = ttk.Toplevel(self.root)
        dialog.title("Open Bid File")
        icon = ImageTk.PhotoImage(file=os.path.join('ico', 'carre.png'))
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
            file_path = bid_file
            self.editor.load_bidfile(file_path)
            self.update_3d_view()
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

    def export_stl(self):
        file_path = filedialog.asksaveasfilename(
            title="Exporter en STL",
            defaultextension=".stl",
            filetypes=[("Fichier STL", "*.stl")]
        )
        if file_path:
            # Update heights before exporting
            self.editor.black_cell_height = self.black_height_var.get()
            self.editor.white_cell_height = self.white_height_var.get()
            self.editor.export_stl(file_path, self.elevation_combo.get())

    def update_3d_view(self, event=None):
        self.ax.clear()
        
        if self.editor.grid_bid is not None:
            # Pré-calculer les couleurs
            color_map = {
                0: (1.0, 1.0, 1.0),    # Blanc
                1: (0.89, 0.89, 0.89), # Gris très clair
                2: (0.75, 0.75, 0.75), # Gris clair
                3: (0.5, 0.5, 0.5),    # Gris
                4: (0.25, 0.25, 0.25), # Gris foncé
                5: (0.0, 0.0, 0.0)     # Noir
            }
            
            # Appliquer le template d'élévation actuel
            template = self.editor.elevation_templates[self.elevation_combo.get()]
            template_height, template_width = template.shape
            
            # Créer une matrice d'élévation pour toute la grille
            elevation_matrix = np.zeros((self.editor.grid_height, self.editor.grid_width))
            
            # Calculer les facteurs d'échelle pour étirer le template sur toute la grille
            scale_y = self.editor.grid_height / template_height
            scale_x = self.editor.grid_width / template_width
            
            # Appliquer le template mis à l'échelle
            for row in range(self.editor.grid_height):
                for col in range(self.editor.grid_width):
                    # Calculer les positions proportionnelles dans le template
                    template_row = int((row / scale_y) % template_height)
                    template_col = int((col / scale_x) % template_width)
                    elevation_matrix[row][col] = template[template_row][template_col]

            # Parcourir toutes les cellules
            for row in range(self.editor.grid_height):
                for col in range(self.editor.grid_width):
                    cell_type = self.editor.grid_bid[row][col]
                    if cell_type >= 0:
                        color_code = self.editor.grid_colors[row][col] if self.editor.grid_colors is not None else 0
                        y = self.editor.grid_height - 1 - row
                        
                        # Pour les cellules triangulaires
                        if 3 <= cell_type <= 6:
                            # Triangle noir
                            if color_code > 0:
                                color_rgb = color_map.get(color_code, (1.0, 1.0, 1.0))
                                base_height = self.editor.black_cell_height
                                height = (base_height * (1 + elevation_matrix[row][col])) - 0.40
                                self.editor.cell_triangle(col, y, color_rgb, self.ax, cell_type, height, 
                                                           self.edge_colors[self.edge_combo.get()])
                            
                            # Triangle blanc complémentaire si l'affichage du blanc est activé
                            if self.show_white_var.get():
                                color_rgb = (1.0, 1.0, 1.0)  # Blanc
                                base_height = self.editor.white_cell_height
                                height = (base_height * (1 + elevation_matrix[row][col])) - 0.40
                                # Inverser le type de triangle pour avoir la contrepartie
                                opposite_type = {3: 5, 4: 6, 5: 3, 6: 4}
                                self.editor.cell_triangle(col, y, color_rgb, self.ax, opposite_type[cell_type], 
                                                           height, self.edge_colors[self.edge_combo.get()])
                        
                        # Pour les cellules entières
                        elif cell_type <= 1:
                            if color_code > 0 or self.show_white_var.get():
                                color_rgb = color_map.get(color_code, (1.0, 1.0, 1.0))
                                base_height = self.editor.black_cell_height if color_code > 0 else self.editor.white_cell_height
                                height = (base_height * (1 + elevation_matrix[row][col])) - 0.40
                                self.editor.cell_entire(col, y, color_rgb, self.ax, height, self.edge_colors[self.edge_combo.get()])

            # Ajustement de la vue
            max_template_height = np.max(template)
            self.ax.set_axis_off()
            self.ax.set_xlim(0, self.editor.grid_width)
            self.ax.set_ylim(0, self.editor.grid_height)
            self.ax.set_zlim(0, self.editor.black_cell_height * (1 + max_template_height))
            self.ax.view_init(elev=30, azim=45)
            self.ax.set_box_aspect([1, 1, 0.3])
            self.fig.tight_layout(pad=0)
        
        self.canvas.draw()

    def on_height_changed(self):
        """Appelé quand les valeurs des scales changent"""
        self.editor.black_cell_height = self.black_height_var.get()
        self.editor.white_cell_height = self.white_height_var.get()
        self.update_3d_view()


if __name__ == "__main__":
    root = ttk.Window(themename="minty")
    app = Bid3DApplication(root)
    root.mainloop()