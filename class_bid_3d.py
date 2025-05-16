from tkinter import filedialog
import numpy as np
from stl import mesh
from class_bid import BidFile
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

class Bid3D(BidFile):
    def __init__(self):
        super().__init__()
        self.grid_bid = None
        self.grid_colors = None
        self.grid_width = 0
        self.grid_height = 0
        
        # Paramètres de hauteur (valeurs par défaut)
        self.white_cell_height = 0.45
        self.black_cell_height = 0.50
        
        # Templates d'élévation
        self.elevation_templates = {
            "Plat": np.zeros((8, 8)),  # Uniformiser la taille à 8x8
            "Pyramide": np.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 2, 2, 2, 2, 1, 0],
                [0, 1, 2, 3, 3, 2, 1, 0],
                [0, 1, 2, 3, 3, 2, 1, 0],
                [0, 1, 2, 2, 2, 2, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ]),
            "Colline": np.array([
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 2, 2, 2, 2, 1, 0],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [0, 1, 2, 2, 2, 2, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0]
            ]),
            "Montagne": np.array([
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 2, 3, 3, 2, 1, 0],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 3, 4, 5, 5, 4, 3, 1],
                [1, 3, 4, 5, 5, 4, 3, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [0, 1, 2, 3, 3, 2, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0]
            ]),
            "Vallée": np.array([
                [5, 4, 3, 2, 2, 3, 4, 5],
                [4, 3, 2, 1, 1, 2, 3, 4],
                [3, 2, 1, 0, 0, 1, 2, 3],
                [2, 1, 0, 0, 0, 0, 1, 2],
                [2, 1, 0, 0, 0, 0, 1, 2],
                [3, 2, 1, 0, 0, 1, 2, 3],
                [4, 3, 2, 1, 1, 2, 3, 4],
                [5, 4, 3, 2, 2, 3, 4, 5]
            ]),
            "Cratère": np.array([
                [3, 3, 3, 3, 3, 3, 3, 3],
                [3, 2, 2, 2, 2, 2, 2, 3],
                [3, 2, 1, 1, 1, 1, 2, 3],
                [3, 2, 1, 0, 0, 1, 2, 3],
                [3, 2, 1, 0, 0, 1, 2, 3],
                [3, 2, 1, 1, 1, 1, 2, 3],
                [3, 2, 2, 2, 2, 2, 2, 3],
                [3, 3, 3, 3, 3, 3, 3, 3]
            ]),
            "Vagues": np.array([
                [0, 1, 2, 3, 0, 1, 2, 3],
                [1, 2, 3, 2, 1, 2, 3, 2],
                [2, 3, 2, 1, 2, 3, 2, 1],
                [3, 2, 1, 0, 3, 2, 1, 0],
                [0, 1, 2, 3, 0, 1, 2, 3],
                [1, 2, 3, 2, 1, 2, 3, 2],
                [2, 3, 2, 1, 2, 3, 2, 1],
                [3, 2, 1, 0, 3, 2, 1, 0]
            ]),
            "Escalier": np.array([
                [0, 0, 1, 1, 2, 2, 3, 3],
                [0, 0, 1, 1, 2, 2, 3, 3],
                [1, 1, 2, 2, 3, 3, 4, 4],
                [1, 1, 2, 2, 3, 3, 4, 4],
                [2, 2, 3, 3, 4, 4, 5, 5],
                [2, 2, 3, 3, 4, 4, 5, 5],
                [3, 3, 4, 4, 5, 5, 6, 6],
                [3, 3, 4, 4, 5, 5, 6, 6]
            ])
        }
        
        # Définition des triangles
        self.triangle_defs = {
            3: { # Triangle bas-droite
                'color': [[1, 0, 0], [0, 0, 0], [1, 1, 0]],
                'white': [[0, 1, 0], [1, 1, 0], [0, 0, 0]]
            },
            4: { # Triangle haut-droite
                'color': [[1, 1, 0], [1, 0, 0], [0, 1, 0]],
                'white': [[0, 0, 0], [0, 1, 0], [1, 0, 0]]
            },
            5: { # Triangle haut-gauche
                'color': [[0, 1, 0], [1, 1, 0], [0, 0, 0]],
                'white': [[1, 0, 0], [0, 0, 0], [1, 1, 0]]
            },
            6: { # Triangle bas-gauche
                'color': [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
                'white': [[1, 0, 0], [1, 1, 0], [0, 1, 0]]
            }
        }

    def cell_heightmap(self, row, col, elevation_name="Plat"):
        """Calcule la hauteur d'une cellule en fonction du template d'élévation"""
        template = self.elevation_templates[elevation_name]
        template_height, template_width = template.shape
        grid_center_row = self.grid_height // 2
        grid_center_col = self.grid_width // 2
        
        # Calcul des positions relatives au centre
        rel_row = row - (grid_center_row - template_height // 2)
        rel_col = col - (grid_center_col - template_width // 2)
        
        # Application du modulo pour répétition
        template_row = rel_row % template_height
        template_col = rel_col % template_width
        
        return template[template_row][template_col]

    def export_stl(self, file_path, elevation_name="Plat"):
        """Exporte uniquement les parties noires du modèle 3D au format STL"""
        if self.grid_bid is None:
            return False

        # Appliquer le template d'élévation comme dans update_3d_view
        template = self.elevation_templates[elevation_name]
        template_height, template_width = template.shape
        
        # Créer une matrice d'élévation pour toute la grille
        elevation_matrix = np.zeros((self.grid_height, self.grid_width))
        
        # Calculer les facteurs d'échelle pour étirer le template sur toute la grille
        scale_y = self.grid_height / template_height
        scale_x = self.grid_width / template_width
        
        # Appliquer le template mis à l'échelle
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                # Calculer les positions proportionnelles dans le template
                template_row = int((row / scale_y) % template_height)
                template_col = int((col / scale_x) % template_width)
                elevation_matrix[row][col] = template[template_row][template_col]

        # Collecter tous les triangles du modèle
        vertices = []
        faces = []
        vertex_count = 0
        
        # Parcourir toutes les cellules
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                cell_type = self.grid_bid[row][col]
                if cell_type >= 0:
                    y = self.grid_height - 1 - row
                    color_code = self.grid_colors[row][col] if self.grid_colors is not None else 0
                    
                    # Ne traiter que les cellules noires (color_code > 0)
                    if color_code > 0:
                        # Calculer la hauteur avec le template mis à l'échelle
                        base_height = self.black_cell_height
                        height = base_height * (1 + elevation_matrix[row][col])
                        
                        if cell_type <= 1:
                            # Pour les cubes noirs
                            cube_vertices = [
                                [col, y, 0], [col+1, y, 0], [col+1, y+1, 0], [col, y+1, 0],
                                [col, y, height], [col+1, y, height], [col+1, y+1, height], [col, y+1, height]
                            ]
                            cube_faces = [
                                [0, 2, 1], [0, 3, 2],  # base
                                [4, 5, 6], [4, 6, 7],  # haut
                                [0, 1, 5], [0, 5, 4],  # avant
                                [1, 2, 6], [1, 6, 5],  # droite
                                [2, 3, 7], [2, 7, 6],  # arrière
                                [3, 0, 4], [3, 4, 7]   # gauche
                            ]
                            
                            for vertex in cube_vertices:
                                vertices.append(vertex)
                            for face in cube_faces:
                                faces.append([f + vertex_count for f in face])
                            vertex_count += len(cube_vertices)
                        
                        elif 3 <= cell_type <= 6:
                            # Pour les triangles noirs
                            triangle_data = self.triangle_defs[cell_type]
                            color_vertices = [[col + v[0], y + v[1], v[2]] for v in triangle_data['color']]
                            
                            # Créer le prisme triangulaire
                            prism_vertices = []
                            prism_vertices.extend(color_vertices)
                            prism_vertices.extend([[v[0], v[1], height] for v in color_vertices])
                            
                            for vertex in prism_vertices:
                                vertices.append(vertex)
                            
                            # Faces du prisme triangulaire
                            base_faces = [
                                [0, 1, 2],      # base
                                [3, 4, 5],      # haut
                                [0, 1, 4], [0, 4, 3],  # côté 1
                                [1, 2, 5], [1, 5, 4],  # côté 2
                                [2, 0, 3], [2, 3, 5]   # côté 3
                            ]
                            
                            for face in base_faces:
                                faces.append([f + vertex_count for f in face])
                            vertex_count += len(prism_vertices)
        
        if len(vertices) > 0:
            # Créer le mesh STL
            vertices = np.array(vertices)
            faces = np.array(faces)
            
            # Créer le mesh final
            model = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
            for i, f in enumerate(faces):
                for j in range(3):
                    model.vectors[i][j] = vertices[f[j],:]
            
            # Sauvegarder le fichier STL
            model.save(file_path)

    def cell_triangle(self, x, y, color, ax, shape, height=1.0, edge_color=(0.7, 0.7, 0.7, 1.0)):
        """Draw a triangle cell with custom edge color"""
        current_triangle = {
            'color': [[x + p[0], y + p[1], p[2]] for p in self.triangle_defs[shape]['color']],
            'white': [[x + p[0], y + p[1], p[2]] for p in self.triangle_defs[shape]['white']]
        }
        
        if shape not in self.triangle_defs:
            return
            
        def create_prism(base_points, h):
            faces = []
            top_points = [[p[0], p[1], h] for p in base_points]
            faces.append(base_points)  # base
            faces.append(top_points)   # top
            
            # Side faces
            for i in range(3):
                j = (i + 1) % 3
                face = [base_points[i], base_points[j], top_points[j], top_points[i]]
                faces.append(face)
            return faces

        # Create and draw colored triangle
        color_faces = create_prism(current_triangle['color'], height)
        
        for face in color_faces:
            ax.add_collection3d(Poly3DCollection(
                [face], 
                facecolors=color + (1.0,),
                linewidths=1,
                edgecolors=edge_color,
                zsort='min'
            ))

    def cell_entire(self, x, y, color, ax, height=1.0, edge_color=(0.7, 0.7, 0.7, 1.0)):
        """Draw a full cell with custom edge color"""
        vertices = [
            [x, y, 0], [x+1, y, 0], [x+1, y+1, 0], [x, y+1, 0],  # base
            [x, y, height], [x+1, y, height], [x+1, y+1, height], [x, y+1, height]  # top
        ]
        
        faces = [
            [vertices[0], vertices[1], vertices[2], vertices[3]],  # bottom
            [vertices[4], vertices[5], vertices[6], vertices[7]],  # top
            [vertices[0], vertices[1], vertices[5], vertices[4]],  # front
            [vertices[1], vertices[2], vertices[6], vertices[5]],  # right
            [vertices[2], vertices[3], vertices[7], vertices[6]],  # back
            [vertices[3], vertices[0], vertices[4], vertices[7]]   # left
        ]

        collection = Poly3DCollection(faces, zsort='min')
        collection.set_facecolor(color)
        collection.set_edgecolor(edge_color)
        ax.add_collection3d(collection)

    def open_bid(self):
        """Ouvre un fichier BID"""
        file_path = filedialog.askopenfilename(
            title="Ouvrir fichier BID",
            filetypes=[("Fichiers BID", "*.bidz"), ("Fichiers BID shape", "*.bid"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            self.load_bidfile(file_path)
            self.update_3d_view()


