from src.PhotoSorter import PhotoSorter
import os

#####################
# MAIN

# init
media = PhotoSorter()

# divide media files by filetype
#os.mkdir(os.path.join(os.getcwd(),'sorted','separated'))
#outdir = os.path.join(os.getcwd(),'sorted','separated')
#media.separate(copy=False,outdir=outdir)

# find possible duplicates
path_to_photos='C:\\Users\\amanm\\Desktop\\test\\sorted\\separated\\Photos'
media.catch_duplicates(path=path_to_photos)