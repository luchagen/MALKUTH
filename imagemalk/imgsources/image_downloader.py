# -*- coding: utf-8 -*-
"""
Created on Wen Jul  24 22:31:44 2024

@author: suric
"""
import shutil
import requests

class ImageDownloader:
    ''' Handles the downloading and storing of images from the internet.
    Should later be able to provide a means to access a library of stored downloaded images.'''

    def download(self,local_folder: str,image_url: str):
        ''' download remote image to a local folder.'''
        file_name=image_url.split("/")[-1].split("\\")[-1]
        local_path = f"./img/{local_folder}/{file_name}"

        res = requests.get(image_url, stream = True, timeout=60)

        if res.status_code == 200:
            with open(local_path,'wb') as f:
                shutil.copyfileobj(res.raw, f)
        return file_name
