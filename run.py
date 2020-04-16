from src.PhotoSorter import PhotoSorter
import os

#####################
# MAIN

# init
media = PhotoSorter()

# divide media files by filetype
os.mkdir(os.path.join(os.getcwd(),'sorted','separated'))
outdir = os.path.join(os.getcwd(),'sorted','separated')
media.separate(copy=False,outdir=outdir)

# organise media files into year and months