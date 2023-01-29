# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 01:25:47 2023

@author: suric
"""

import stanza

class KeywordsFinder:
    nlp = stanza.Pipeline("fr",processors='tokenize,pos,lemma')
    
    def keywords(self, string):  
        sentence= self.nlp.process(string)
        keywords=[]
        for sen in sentence.sentences:
            for wor in sen.words:
                if wor.pos=='NOUN' or wor.pos=='PROPN':
                    keywords.append([wor.lemma])
        return keywords

