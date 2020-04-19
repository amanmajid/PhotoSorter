# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 18:49:59 2020

@author: amanm
"""

from tqdm import tqdm
import filetype
import os
import shutil
import pandas
import numpy
import time
import datetime
import PIL.Image
import PIL.ExifTags
from moviepy.editor import VideoFileClip

class PhotoSorter():

    def __init__(self):
        '''Init class'''
        # get current dir path
        self.curdir     = os.getcwd()
        # get raw input dir path
        self.rawdir     = os.path.join(self.curdir,'raw')
        # get output dir path
        self.outdir     = os.path.join(os.getcwd(),'sorted')
        # get list of subdirs
        self.subdirs    = [i for i,j,k in os.walk(self.rawdir)]

    def gather(self,copy=False,outdir=None,separate=True):
        '''
        Function to gather photos and videos into one folder

        Arguments:

        *copy* : boolean, default False
            Choice to copy or move files. Copying is much slower.

        *outdir* : str, default None
            Path to output directory where files are gathered.

        *separate* : boolean, default True
            Separate photos and videos into separate directories
        '''

        # output dir if None
        if outdir==None:
            outdir=self.outdir
        #check/make output folder
        if separate==True:
            ipath=os.path.join(outdir,'Photos')
            if os.path.isdir(ipath)==False:
                os.mkdir(ipath)

            #check/make Video folder
            ipath=os.path.join(outdir,'Videos')
            if os.path.isdir(ipath)==False:
                os.mkdir(ipath)
        else:
            ipath=os.path.join(outdir,'Collection')
            if os.path.isdir(ipath)==False:
                os.mkdir(ipath)

        # loop files and separate
        if separate==True:
            pic_count = 0
            vid_count = 0
            pbar = tqdm(self.subdirs)
            for idir in pbar:
                pbar.set_description('Separating photos and videos')
                os.chdir(idir)
                files = [f for f in os.listdir('.') if os.path.isfile(f)]
                for file in files:
                    k = filetype.guess(file)
                    try:
                        if k.MIME.split('/')[0]=='image':
                            cur_fpath = os.path.join(idir,file)
                            out_fpath = os.path.join(outdir,'Photos',''.join(['IMG_',str(pic_count),'.',k.extension]))
                            if copy==False:
                                shutil.move(cur_fpath, out_fpath)
                            elif copy==True:
                                shutil.copy2(cur_fpath, out_fpath)
                            pic_count = pic_count + 1

                        elif k.MIME.split('/')[0]=='video':
                            cur_fpath = os.path.join(idir,file)
                            out_fpath = os.path.join(outdir,'Videos',''.join(['VID_',str(vid_count),'.',k.extension]))
                            if copy==False:
                                shutil.move(cur_fpath, out_fpath)
                            elif copy==True:
                                shutil.copy2(cur_fpath, out_fpath)
                            vid_count = vid_count + 1
                    except:
                        pass
        # gather
        elif separate==False:
            pic_count = 0
            vid_count = 0
            pbar = tqdm(self.subdirs)
            for idir in pbar:
                pbar.set_description('Collecting photos and videos')
                os.chdir(idir)
                files = [f for f in os.listdir('.') if os.path.isfile(f)]
                for file in files:
                    k = filetype.guess(file)
                    try:
                        if k.MIME.split('/')[0]=='image':
                            cur_fpath = os.path.join(idir,file)
                            out_fpath = os.path.join(outdir,'Collection',''.join(['IMG_',str(pic_count),'.',k.extension]))
                            if copy==False:
                                shutil.move(cur_fpath, out_fpath)
                            elif copy==True:
                                shutil.copy2(cur_fpath, out_fpath)
                            pic_count = pic_count + 1

                        elif k.MIME.split('/')[0]=='video':
                            cur_fpath = os.path.join(idir,file)
                            out_fpath = os.path.join(outdir,'Collection',''.join(['VID_',str(vid_count),'.',k.extension]))
                            if copy==False:
                                shutil.move(cur_fpath, out_fpath)
                            elif copy==True:
                                shutil.copy2(cur_fpath, out_fpath)
                            vid_count = vid_count + 1
                    except:
                        pass
        # restore dir
        os.chdir(self.curdir)

    def drop_duplicates(self,path):
        '''
        Function to delete duplicate photos

        Arguments:
        *path* : str
            Path to directory containing files
        '''

        os.chdir(path)
        # get files in dir
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        files_before = len(files)
        # build-up pandas dataframe of file metadata
        name = []
        size = []
        make = []
        model = []
        duration = []
        pbar = tqdm(files)
        for file in pbar:
            pbar.set_description('Gathering metadata')
            name.append(file)
            size.append(os.stat(file).st_size)
            # determine filetype
            k = filetype.guess(file)
            if k.MIME.split('/')[0]=='image':
                try:
                    img = PIL.Image.open(file)
                    exif = {PIL.ExifTags.TAGS[k]: v
                            for k, v in img._getexif().items()
                            if k in PIL.ExifTags.TAGS}
                    make.append(exif['Make'])
                    model.append(exif['Model'])
                    duration.append('N/A')
                except:
                    img = PIL.Image.open(file)
                    make.append('N/A')
                    model.append('N/A')
                    duration.append('N/A')
            elif k.MIME.split('/')[0]=='video':
                clip = VideoFileClip(file)
                duration.append(clip.duration)
                clip.close()
                make.append('N/A')
                model.append('N/A')

        metadata = pandas.DataFrame({'Filename' :name,
                                     'Filesize' :size,
                                     'Make'     :make,
                                     'Model'    :model,
                                     'Duration' :duration})

        # sort by filesize
        metadata = metadata.sort_values(by='Filesize').reset_index(drop=True)
        # get names of files to delete
        duplicates = metadata[~metadata.Filename.isin(\
                              metadata.drop_duplicates(\
                              subset=['Filesize','Make','Model','Duration'],
                              keep='first').Filename)].Filename.to_list()
        files_after = len(duplicates)
        # delete duplicates
        pbar = tqdm(duplicates)
        for file in pbar:
            pbar.set_description('Deleting files')
            os.remove(file)

        print('Deleted ' + str(files_after) + ' from a total of ' + str(files_before) + ' files')

    def purge_live_photos(self,path,len_param=2.0,exception=None):
        '''
        Function to delete 'live photos' from directory. A live photo
        is stored as a very short video and so is usually not needed.

        Arguments:
        *path* : str
            Path to directory with media files

        *len_param* : float, default 2.0
            Length below which videos are deleted (seconds)

        *exception* : str, default None
            Files containing the exception will not be interpreted. This can
            save computation time. For instance, if the directory contains
            images with 'IMG_' in the title, this can be passed in as an
            exception.

        '''
        os.chdir(path)
        # get files in dir
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        files_before = len(files)
        files = [x for x in files if exception not in x]
        # loop files
        pbr = tqdm(files)
        for file in pbr:
            pbr.set_description('Removing short videos')
            k = filetype.guess(file)
            if k.MIME.split('/')[0]=='video':
                clip = VideoFileClip(os.path.join(os.getcwd(),file))
                if clip.duration < 2:
                    clip.close()
                    os.remove(file)

        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        files_after = len(files)
        files_deleted = files_after - files_before
        print('Deleted ' + str(files_after) + ' from a total of ' + str(files_before) + ' files')

    def organise(self,path,device=False):
        '''
        Function to organise media files into folders by year and month

        Arguments:
        *path* : str
            Path to directory with media files

        *device* : bool, default False
            If True, subfolders will be created within each month's
            folder to indicate which camera the photo was taken on.
        '''

        os.chdir(path)
        # get files in dir
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        #create dict for month
        months = {1:'1-Jan',2:'2-Feb',3:'3-Mar',4:'4-Apr',
                  5:'5-May',6:'6-Jun',7:'7-Jul',8:'8-Aug',
                  9:'9-Sep',10:'10-Oct',11:'11-Nov',12:'12-Dec'}
        # loop files
        pbr = tqdm(files)
        for file in pbr:
            pbr.set_description('Organising files')
            img = PIL.Image.open(file)
            try:
                exif = {PIL.ExifTags.TAGS[k]: v
                        for k, v in img._getexif().items()
                        if k in PIL.ExifTags.TAGS}

                img_date = exif['DateTimeOriginal'].split(':')
                img_year = str(img_date[0])
                img_month = str(months[int(img_date[1])])
                img_device = exif['Model']
            except:
                img_date = datetime.datetime.strptime(time.ctime(os.path.getmtime(file)),"%a %b %d %H:%M:%S %Y")
                img_year = str(img_date.year)
                img_month = str(months[img_date.month])
                img_device = 'Other'

            img.close()
            if device==False:
                #check/make folder for year
                ipath=os.path.join(os.getcwd(),img_year)
                if os.path.isdir(ipath)==False:
                    os.mkdir(ipath)
                #check/make folder for month
                ipath=os.path.join(os.getcwd(),img_year,img_month)
                if os.path.isdir(ipath)==False:
                    os.mkdir(ipath)
                # move file
                cur_fpath = os.path.join(os.getcwd(),file)
                out_fpath = os.path.join(os.getcwd(),img_year,img_month,file)
                shutil.move(cur_fpath, out_fpath)
            elif device==True:
                #check/make folder for year
                ipath=os.path.join(os.getcwd(),img_year)
                if os.path.isdir(ipath)==False:
                    os.mkdir(ipath)
                #check/make folder for month
                ipath=os.path.join(os.getcwd(),img_year,img_month,img_device)
                if os.path.isdir(ipath)==False:
                    os.mkdir(ipath)
                # move file
                cur_fpath = os.path.join(os.getcwd(),file)
                out_fpath = os.path.join(os.getcwd(),img_year,img_month,img_device,file)
                shutil.move(cur_fpath, out_fpath)

    def drop_duplicates2(self,path):
        '''
        A second function to drop duplicate. Works only for photos.
        Computation is based on the 'date created' field of a photo.

        Arguments:
        *path* : str
            Path to directory containing files
        '''

        os.chdir(path)
        # get files in dir
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        files_before = len(files)
        # build-up pandas dataframe of file metadata
        name = []
        time = []
        pbar = tqdm(files)
        for file in pbar:
            pbar.set_description('Gathering metadata')
            # determine filetype
            k = filetype.guess(file)
            if k.MIME.split('/')[0]=='image':
                try:
                    img = PIL.Image.open(file)
                    exif = {PIL.ExifTags.TAGS[k]: v
                            for k, v in img._getexif().items()
                            if k in PIL.ExifTags.TAGS}
                    d = exif['DateTimeOriginal']
                    dd = d.split(' ')[0].split(':')
                    tt = d.split(' ')[1].split(':')
                    t = datetime.datetime(int(dd[0]),int(dd[1]),int(dd[2]),
                                          int(tt[0]),int(tt[1]),int(tt[2]))
                    time.append(t)
                    name.append(file)
                    img.close()
                except:
                    img = PIL.Image.open(file)
                    name.append(file)
                    time.append(numpy.nan)
                    img.close()

        time = [pandas.Timestamp(i) for i in time]
        metadata = pandas.DataFrame({'Filename' :name,
                                     'Time'     :time})

        # sort by time
        metadata = metadata.sort_values(by='Time').reset_index(drop=True)
        # get names of files to delete
        duplicates = metadata[~metadata.Filename.isin(\
                              metadata.drop_duplicates(\
                              subset=['Time'],
                              keep='first').Filename)].Filename.to_list()
        files_after = len(duplicates)
        # delete duplicates
        pbar = tqdm(duplicates)
        for file in pbar:
            pbar.set_description('Deleting files')
            os.remove(file)

        print('Deleted ' + str(files_after) + ' from a total of ' + str(files_before) + ' files')
