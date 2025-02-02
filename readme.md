# convert image to bid file
python .\image2bid.py --path_file source/zigzag.png --width_result 57 --height_result 57 --display_ascii True

# convert bid file to image
python .\bid2image.py --path_file bid/zigzag.bid --image_scale 10