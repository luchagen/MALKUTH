# -*- coding: utf-8 -*-
"""
Created on Tue Jul  23 23:42:04 2024

@author: suric
"""

class MessageImageFetcher:
    '''handles fetching images present in discord messages'''

    def get_message_embeds(self,message):
        """Search each embed type object in a message to see if there is a relevant image url"""
        embeds = []
        for embedcontainer in message.embeds:
            imgurl=""

            if embedcontainer.url :
                imgurl=embedcontainer.url

            if embedcontainer.thumbnail and embedcontainer.thumbnail.proxy_url:
                imgurl=embedcontainer.thumbnail.proxy_url

            if embedcontainer.image  and embedcontainer.image.proxy_url:
                imgurl=embedcontainer.image.proxy_url

            if embedcontainer.image and embedcontainer.image.url :
                imgurl=embedcontainer.image.url

            if embedcontainer.thumbnail and embedcontainer.thumbnail.url :
                imgurl=embedcontainer.thumbnail.url

            embeds.append(imgurl)
        return embeds

    def get_message_attachments(self,message):
        """returns all message attachments as urls"""
        attachments =[]
        for attachment in message.attachments :
            attachments.append(attachment.url)
        return attachments

    def filter_out_images(self,rules,images):
        '''Filter out images if they contain the elements excluded by the provided rules.'''
        filtered_images=images
        for rule in rules:
            filtered_images=[image for image in filtered_images if rule not in image]
        return filtered_images

    def get_images_from_message(self,message,*rules):
        '''fetches all images contained in a specific discord message'''
        urls=[]
        urls += self.get_message_embeds(message)
        urls += self.get_message_attachments(message)
        urls = self.filter_out_images(rules,urls)
        return urls
