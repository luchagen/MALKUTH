# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 00:24:53 2023

@author: suric
"""
import seamcarving
import requests # request img from web
import shutil # save img locally
import imageio.v3 as iio
from skimage import transform, util
from PIL import Image
import numpy as np

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
        img = iio.imread(file)
        
        ratio=256/img.shape[0]
        img=transform.rescale(img,ratio ,channel_axis=2)
        
        if isinstance(img[0][0][0],float):
            img=(img * 255).astype(np.uint8)
        scale=strength
        out = seamcarving.crop_c(img, scale)
        
        iio.imwrite("./img/temp.png", out)
        img = iio.imread("./img/temp.png")
        
        scale=strength
        out = seamcarving.crop_r(img, scale)
        
        out=transform.rescale(out,(1/ratio)*(1/scale) ,channel_axis=2)
        if isinstance(out[0][0][0],float):
            out=(out * 255).astype(np.uint8)
        iio.imwrite("./img/temp.png", out)
        f = open("./img/temp.png", "rb")
        return f