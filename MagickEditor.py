# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 00:24:53 2023

@author: suric
"""
import seamcarving
import requests # request img from web
import shutil # save img locally
from skimage import io
from skimage import transform, util

class MagickEditor:
    def download(self,image_url: str):
        locallink=""
        locallink+=image_url
        while locallink.find("/")!=-1:
            locallink=locallink[locallink.find("/")+1:]
        file_name = "./img/"+locallink[-5:]

        res = requests.get(image_url, stream = True)

        if res.status_code == 200:
            with open(file_name,'wb') as f:
                shutil.copyfileobj(res.raw, f)
        return file_name
    
    def magick(self,image_url: str,strength:float):
        file= self.download(image_url)
        img = io.imread(file)
        img = util.img_as_float(img)
        img=transform.rescale(img, 256/img.shape[0],channel_axis=2)
        
        scale=strength
        out = seamcarving.crop_c(img, scale)
        
        io.imsave("./img/temp.png", out)
        img = io.imread("./img/temp.png")
        
        scale=strength
        out = seamcarving.crop_r(img, scale)
        io.imsave("./img/temp.png", out)
        f = open("./img/temp.png", "rb")
        return f