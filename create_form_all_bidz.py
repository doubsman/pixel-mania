import os
from datetime import datetime
from class_bid_3d import Bid3D

def convert_all_bidz_to_stl():
    # Chemin du répertoire bid
    bid_dir = "bid"
    
    # Créer un éditeur 3D
    editor = Bid3D()
    
    # Parcourir tous les fichiers .bidz
    for filename in os.listdir(bid_dir):
        if filename.endswith(".bidz"):
            bidz_path = os.path.join(bid_dir, filename)
            stl_path = os.path.join(bid_dir, filename.replace(".bidz", ".stl"))
            
            # Récupérer la date du fichier bidz
            bidz_time = os.path.getmtime(bidz_path)
            
            print(f"Conversion de {filename}...")
            
            # Charger et convertir le fichier
            editor.load_bidfile(bidz_path)
            editor.export_stl(stl_path)
            
            # Appliquer la même date au fichier STL
            os.utime(stl_path, (bidz_time, bidz_time))
            
            print(f"Terminé : {filename}")

if __name__ == "__main__":
    convert_all_bidz_to_stl()