______________________________________________________________
# Bid 2 Image
.\bid2img.py --path_bid bid/fence5.bid --no_display_image

# Bid 2 Ascii
.\bid2ascii.py --path_bid bid/fence5.bid

# Bid 2 Graph
.\bid2graph.py --path_bid bid/fence5.bid


______________________________________________________________
# Image 2 Bid
.\img2bid.py --path_image source/fence.jpeg --grid_width 40 --grid_height 40 --no_display_image
.\img2bid.py --path_image E:\\Download\\test.png --grid_width 11 --grid_height 11 --no_save_bid --no_save_ascii --display_cells --display_cells_scale_reduce 10

# Image 2 Ascii
.\img2ascii.py --path_image png/chevalier.png --grid_width 4 --grid_height 4
.\img2ascii.py --path_image export/fence.png --grid_width 40 --grid_height 40
.\img2ascii.py --path_image png/carre.png --grid_width 4 --grid_height 4 --scale 0.5


______________________________________________________________
# Ascii 2 Bid
.\ascii2bid.py --path_ascii export/fence.ascii --path_bid export/fence5.bid


______________________________________________________________
# create EXE Windows from editor
pyinstaller --noconfirm --onefile --windowed ./editor.py