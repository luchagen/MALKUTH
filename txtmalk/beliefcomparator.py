# -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 23:02:44 2023

@author: suric
"""
import logging
import txtmalk.utils as utils
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

class BeliefComparator:
    '''
    The goal of this class is to be able to provide a decision 
    on which sentence should be picked amongst a list of generated sentences.
    It works using memories we check against every candidate,
    in order to pick the most adequate.
    '''
    modelsentence =  SentenceTransformer("./sentence")
    _logger=logging.getLogger(__name__)
    _logger.setLevel(20)
    _logger.addHandler(
        logging.FileHandler(filename='belief_comparator.log', encoding='utf-8', mode='w')
        )

    def __init__(self,keywordsfindersub):
        self.keywordsfindersub=keywordsfindersub

    def parse_beliefs(self,memories):
        '''
        get quantifiers from a list of beliefs using:
        - sentence transformer for making a vector
        - our own parser for parsing predicates
        - the already present strength of each belief
        '''
        beliefs = []
        for memory in memories:
            vector = self.modelsentence.encode([memory.getsentence()])[0]
            belief_strength = memory.getstrength()
            beliefs.append(
                {'vector':vector,
                 'belief_strength':belief_strength
                })
        return beliefs

    def parse_sentences(self,sentences):
        '''
        get quantifiers from sentence propositions using:
        - sentence transformer for making a vector
        - our own parser for parsing predicates
        '''
        parsed_sentences=[]
        for sentence in sentences:
            vector =self.modelsentence.encode([sentence[0]])[0]
            parsed_sentences.append({'vector':vector,'sentence':sentence})
        return parsed_sentences


    def cosine_similarity(self,beliefs,sentence):
        '''
        We calculate simularity of the sentences 
        using cosine similarity with the vectors provided by camembert-sentence
        '''
        cosim=0
        nbr_beliefs= len(beliefs)
        for j in range(nbr_beliefs):
            cosim+=(1-cosine(sentence['vector'],beliefs[j]['vector']))*beliefs[j]['belief_strength']
        if nbr_beliefs!=0:
            cosim=cosim/nbr_beliefs
        return cosim

    def choose_sentence(self,sentences,memories,minimum_similarity=0):
        '''
        choosing wich sentence to say ,based on the memories raised by all possible choices
        '''
        beliefs = self.parse_beliefs(memories)
        parsed_sentences = self.parse_sentences(sentences)

        for parsed_sentence in parsed_sentences:


            cosine_similarity = self.cosine_similarity(beliefs,parsed_sentence)

            if cosine_similarity > minimum_similarity:
                choosen_sentence=parsed_sentence['sentence']
                minimum_similarity=cosine_similarity

        self._logger.info('Choice : %s' ,str((choosen_sentence,minimum_similarity)))
        return choosen_sentence,minimum_similarity
    