import ttkbootstrap as ttk
from tkinter import ttk as ttk2
from tkinter import filedialog
from PIL import ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from class_bid_3d import Bid3D
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
            "Blanc": (0.7, 0.7, 0.7, 1.0),
            "Noir": (0.0, 0.0, 0.0, 1.0)
        }
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
        open_button = ttk.Button(control_frame, text="Ouvrir BID", 
                               bootstyle="outline", 
                               command=self.open_bid,
                               width=widget_width)
        open_button.pack(pady=5)
        
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
        self.edge_combo.set("Noir")
        self.edge_combo.pack(pady=5)
        self.edge_combo.bind('<<ComboboxSelected>>', self.update_3d_view)

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
            
    def export_stl(self):
        file_path = filedialog.asksaveasfilename(
            title="Exporter en STL",
            defaultextension=".stl",
            filetypes=[("Fichier STL", "*.stl")]
        )
        if file_path:
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
            elevation_matrix = np.zeros((self.editor.grid_height, self.editor.grid_width))
            
            for row in range(self.editor.grid_height):
                for col in range(self.editor.grid_width):
                    template_row = row % template.shape[0]
                    template_col = col % template.shape[1]
                    elevation_matrix[row][col] = template[template_row][template_col]
            
            # Récupérer la couleur des contours sélectionnée
            edge_color = self.edge_colors[self.edge_combo.get()]
            
            # Traitement par lots des cellules
            for row in range(self.editor.grid_height):
                for col in range(self.editor.grid_width):
                    cell_type = self.editor.grid_bid[row][col]
                    if cell_type > 0:
                        color_code = self.editor.grid_colors[row][col] if self.editor.grid_colors is not None else 0
                        color_rgb = color_map.get(color_code, (1.0, 1.0, 1.0))
                        
                        y = self.editor.grid_height - 1 - row
                        height = self.editor.black_cell_height if color_rgb != (1.0, 1.0, 1.0) else self.editor.white_cell_height
                        
                        if elevation_matrix is not None:
                            height *= (1 + elevation_matrix[row][col])
                        
                        # Utiliser les fonctions de l'éditeur avec la couleur des contours
                        if cell_type <= 1:
                            self.editor.cell_entire(col, y, color_rgb, self.ax, height, edge_color)
                        elif 3 <= cell_type <= 6:
                            self.editor.cell_triangle(col, y, color_rgb, self.ax, cell_type, height, edge_color)

            # Configuration optimisée de la vue
            self.ax.set_axis_off()
            self.ax.set_xlim(0, self.editor.grid_width)
            self.ax.set_ylim(0, self.editor.grid_height)
            self.ax.set_zlim(0, 2)
            self.ax.view_init(elev=30, azim=45)
            self.ax.set_box_aspect([1, 1, 0.3])
            self.fig.tight_layout(pad=0)
        
        self.canvas.draw()


if __name__ == "__main__":
    root = ttk.Window(themename="minty")
    app = Bid3DApplication(root)
    root.mainloop()