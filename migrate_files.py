import os
from class_bid import BidFile

def migrate_bid_files(source_dir="bid"):
    """
    Migre les fichiers .bid et .color vers le format .bidz
    """
    # Créer une instance de BidFile
    bid_handler = BidFile()
    
    # Parcourir tous les fichiers .bid
    for filename in os.listdir(source_dir):
        if filename.endswith('.bid'):
            print(f"Processing {filename}...")
            bid_path = os.path.join(source_dir, filename)
            color_path = bid_path.replace('.bid', '.color')
            bidz_path = bid_path.replace('.bid', '.bidz')
            ascii_path = bid_path.replace('.bid', '.ascii')
            
            original_mtime = os.path.getmtime(bid_path)
            
            # Charger le fichier bid
            bid_handler.load_bidfile(bid_path)
            
            # Sauvegarder au format .bidz
            bid_handler.save_bidfile(bidz_path)
            os.utime(bidz_path, (original_mtime, original_mtime))
            
            # Supprimer les fichiers originaux après la migration réussie
            os.remove(bid_path)
            os.remove(color_path)
            if os.path.exists(ascii_path):
                os.remove(ascii_path)

def align_bidpng_dates(source_dir="bid"):
    bid_handler = BidFile()
    for filename in os.listdir(source_dir):
        if filename.endswith('.bidz'):
            print(f"Processing {filename}...")
            bid_path = os.path.join(source_dir, filename)
            original_mtime = os.path.getmtime(bid_path)
            bid_handler.load_bidfile(bid_path)
            png_path = os.path.join(source_dir, filename.replace('.bidz', f'_{bid_handler.grid_width}x{bid_handler.grid_height}.png'))
            if not os.path.exists(png_path):
                print(f"Warning: {png_path} does not exist.")
            else:
                os.utime(png_path, (original_mtime, original_mtime))

if __name__ == "__main__":
    migrate_bid_files()
    #align_bidpng_dates()