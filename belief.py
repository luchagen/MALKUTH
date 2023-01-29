# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 01:00:09 2023

@author: suric
"""

class Belief:
    belief_sentence=""
    belief_strength=0.0
    def __init__(self, sentence,belief_strength: float):
        self.belief_sentence=sentence
        self.belief_strength=belief_strength
    def getsentence(self):
        return self.belief_sentence
    
    def getstrength(self):
        return self.belief_strength