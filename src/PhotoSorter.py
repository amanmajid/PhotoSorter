# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 18:49:59 2020

@author: amanm
"""

from tqdm import tqdm
import filetype
import os
import shutil

class PhotoSorter():
    
    def __init__(self):
        
        # get current dir path
        self.curdir     = os.getcwd()
        # get raw input dir path
        self.rawdir     = os.path.join(self.curdir,'raw')
        # get output dir path
        self.outdir     = os.path.join(os.getcwd(),'sorted')
        # get list of subdirs
        self.subdirs    = [i for i,j,k in os.walk(self.rawdir)]
        
    def separate(self,copy=False,outdir=None):
        '''Separate pictures and videos into individual folders'''
        
        if outdir==None:
            outdir=self.outdir
        
        #check/make Audio folder
        ipath=os.path.join(outdir,'Photos')
        if os.path.isdir(ipath)==False:
            os.mkdir(ipath)
        
        #check/make Video folder
        ipath=os.path.join(outdir,'Videos')
        if os.path.isdir(ipath)==False:
            os.mkdir(ipath)
            
        # loop files and separate
        count = 0
        for i in tqdm(range(0,len(self.subdirs))):
            idir = self.subdirs[i]
            os.chdir(idir)
            files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for file in files:
                k = filetype.guess(file)
                try:
                    if k.MIME.split('/')[0]=='image':
                        cur_fpath = os.path.join(idir,file)
                        out_fpath = os.path.join(outdir,'Photos',''.join(['pic_',str(count),'.',k.extension]))
                        if copy==False:
                            shutil.move(cur_fpath, out_fpath)
                        elif copy==True:
                            shutil.copy2(cur_fpath, out_fpath)
                    elif k.MIME.split('/')[0]=='video':
                        cur_fpath = os.path.join(idir,file)
                        out_fpath = os.path.join(outdir,'Videos',''.join(['vid_',str(count),'.',k.extension]))
                        if copy==False:
                            shutil.move(cur_fpath, out_fpath)
                        elif copy==True:
                            shutil.copy2(cur_fpath, out_fpath)
                except:
                    pass
                count = count + 1
        
        # restore dir
        os.chdir(self.curdir)