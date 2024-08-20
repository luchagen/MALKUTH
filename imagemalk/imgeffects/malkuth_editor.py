# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 00:24:53 2023

@author: suric
"""
import imageio.v3 as iio
import numpy as np
from skimage import transform
from imagemalk.imgeffects import seamcarving

class MagickEditor:
    '''Provides tools for editing images.'''

    def rescale(self,img, ratio):
        ''' rescale image using the provided ratio.'''
        img=transform.rescale(img,ratio ,channel_axis=2)
        if isinstance(img[0][0][0],float):
            img=(img * 255).astype(np.uint8)
        return img


    def magick(self,file: str,strength:float):
        '''apply distortion using two seam_carving compressions.'''
        img = iio.imread(file)

        #standardize the image size for predictable, fast results
        ratio_standardize=256/img.shape[0]
        img=self.rescale(img,ratio_standardize)

        out = seamcarving.crop_c(img, strength)

        iio.imwrite("./img/temp.png", out)
        img = iio.imread("./img/temp.png")

        out = seamcarving.crop_r(img, strength)

        #restore the original file size
        ratio_restore=1/(ratio_standardize * min(1,strength))
        out=self.rescale(img,ratio_restore)

        iio.imwrite("./img/temp.png", out)
        f = open("./img/temp.png", "rb")
        return f
