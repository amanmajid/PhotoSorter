from src.PhotoSorter import PhotoSorter
import os

#####################
m = PhotoSorter()

# divide by filetype
os.mkdir(os.path.join(os.getcwd(),'sorted','separated'))
outdir = os.path.join(os.getcwd(),'sorted','separated')
m.separate(copy=True,outdir=outdir)