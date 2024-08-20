# -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 23:02:44 2023

@author: suric
"""

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
            predicates = self.keywordsfindersub.predicates(memory.getsentence())
            beliefs.append(
                {'vector':vector,
                 'belief_strength':belief_strength,
                 'predicates':predicates})
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
            predicates=self.keywordsfindersub.predicates(sentence[0])
            parsed_sentences.append({'vector':vector,'predicates':predicates,'sentence':sentence})
        return parsed_sentences

    def predicate_similarity(self,beliefs,sentence):
        '''we calculate simularity of a sentence to memories based on their predicates'''
        nbr_predicates= len(sentence['predicates'])
        predicates_similarity=[0 for i in range(nbr_predicates)]
        for i in range(nbr_predicates):
            activations=[]

            for index, belief in enumerate(beliefs):
                activations+=utils.getactivations(
                    belief['predicates'],
                    sentence['predicates'][i],
                    index,belief['belief_strength']
                    )

            nbract=len(activations)
            for activation in activations:
                predicates_similarity[i]+=activation[0]*beliefs[activation[1]]/(nbract*10)

        similarity=0
        if len(predicates_similarity)!=0:
            similarity=sum(predicates_similarity)/len(predicates_similarity)
        return similarity

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

            predicate_similarity = self.predicate_similarity(beliefs,parsed_sentence)
            cosine_similarity = self.cosine_similarity(beliefs,parsed_sentence)

            computed_similarity = predicate_similarity + cosine_similarity

            if computed_similarity > minimum_similarity:
                choosen_sentence=parsed_sentence['sentence']
                minimum_similarity=computed_similarity

        return choosen_sentence,minimum_similarity
    