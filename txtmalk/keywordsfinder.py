# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 01:25:47 2023

@author: suric
"""

import stanza

#conversion from stanza's to spacy's syntax
class document:
    class token:
        pos_=""
        dep_=""
        lemma_=""
        def __init__(self,wor,parentdocument):
            self.parentdocument= parentdocument
            self.dep_ =wor.deprel
            self.pos_=wor.pos
            self.text=wor.text
            self.feats= wor.feats
            if self.feats != None:
                self.feats= self.feats.split('|')
            self.lemma_=wor.lemma
            self.head_=wor.head-1
            self.head=self
            self.i = wor.id-1
            self.children=[]


        def maketreeheads(self):
            self.head=self.parentdocument.tokens[self.head_]


        def maketreechildren(self):
            children = []
            for tokens in self.parentdocument.tokens:
                if tokens.head.i==self.i:
                    children.append(tokens)
     
            self.children=children


        def head(self):
            return()


    def __init__(self,sentence):
        self.sentence = sentence
        self.tokens=[]
        for wor in sentence.words: 
            self.tokens.append(self.token(wor,self))
        for mytoken in self.tokens:
            mytoken.maketreeheads()
        for mytoken in self.tokens:
            mytoken.maketreechildren()


class KeywordsFinder:
    nlp = stanza.Pipeline("fr",processors='tokenize,pos,mwt,lemma,depparse')

    #find simple keywors i.e nouns and verbs
    def keywords(self, string):  
        sentence= self.nlp.process(string)
        keywords=[]
        for sen in sentence.sentences:
            for wor in sen.words:
                if wor.pos=='NOUN' or wor.pos=='PROPN' or wor.pos=='VERB':
                    keywords.append([wor.lemma])
        return keywords


if __name__ == "__main__":
    keyfind=KeywordsFinder()
    