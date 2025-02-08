# convert image to bid file
python .\image2bid.py --path_file source/zigzag.png --width_result 57 --height_result 57 --display_ascii True




______________________________________________________________
# Bid 2 Image
python .\bid2img.py --path_bid bid/fence5.bid --no_display_image

# Bid 2 Ascii
python .\bid2ascii.py --path_bid bid/fence5.bid

# Bid 2 Graph
python .\bid2graph.py --path_bid bid/fence5.bid


______________________________________________________________
# Image 2 Bid
python .\img2bid.py --path_image source/fence.jpeg --grid_width 40 --grid_height 40 --no_display_image

# Image 2 Ascii
python .\img2ascii.py --path_image chevalier.png --grid_width 4 --grid_height 4
python .\img2ascii.py --path_image export/fence.png --grid_width 40 --grid_height 40


______________________________________________________________
# Ascii 2 Bid
python .\ascii2bid.py --path_ascii export/fence.ascii --path_bid export/fence5.bid