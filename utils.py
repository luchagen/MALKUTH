# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 21:22:27 2023

@author: suric
"""
from collections import Counter
import math

def predicatestosentences(predicates):
    sentences=[]
    for pred in predicates:
        sen=""
        for word in pred["subj_"]:
            sen+= " " + word[0]
        for word in pred["head_"]:
            sen+= " " + word[0]
        for word in pred["how_"]:
            sen+= " " + word[0]
        for word in pred["obj_"]:
            sen+= " " + word[0]
        for word in pred["why_"]:
            sen+= " " + word[0]
        for word in pred["where_"]:
            sen+= " " + word[0]
        sentences.append(sen)
    return sentences

def lemmascount(predicatepart):
    lemmas=[]
    for item in predicatepart:
        lemmas.append(item[0])
    return Counter(lemmas)

# cosine similarity
def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
    sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

def getactivations(predicatesmem,predicatetest,i):
    activations=[]
    for pred in predicatesmem:
        activation=0.0
        activation+=get_cosine(lemmascount(pred["subj_"]),lemmascount(predicatetest["subj_"]))
        activation+=get_cosine(lemmascount(pred["head_"]),lemmascount(predicatetest["head_"]))
        
        activation+=get_cosine(lemmascount(pred["obj_"]),lemmascount(predicatetest["obj_"]))
        activation+=get_cosine(lemmascount(pred["obj_"]),lemmascount(predicatetest["how_"]))/2
        activation+=get_cosine(lemmascount(pred["obj_"]),lemmascount(predicatetest["why_"]))/2
        activation+=get_cosine(lemmascount(pred["obj_"]),lemmascount(predicatetest["where_"]))/2
        
        activation+=get_cosine(lemmascount(pred["how_"]),lemmascount(predicatetest["how_"]))
        activation+=get_cosine(lemmascount(pred["how_"]),lemmascount(predicatetest["why_"]))/2
        activation+=get_cosine(lemmascount(pred["how_"]),lemmascount(predicatetest["where_"]))/2
        activation+=get_cosine(lemmascount(pred["how_"]),lemmascount(predicatetest["obj_"]))/2
        
        activation+=get_cosine(lemmascount(pred["why_"]),lemmascount(predicatetest["why_"]))
        activation+=get_cosine(lemmascount(pred["why_"]),lemmascount(predicatetest["how_"]))/2
        activation+=get_cosine(lemmascount(pred["why_"]),lemmascount(predicatetest["where_"]))/2
        activation+=get_cosine(lemmascount(pred["why_"]),lemmascount(predicatetest["obj_"]))/2
        
        activation+=get_cosine(lemmascount(pred["where_"]),lemmascount(predicatetest["where_"]))
        activation+=get_cosine(lemmascount(pred["where_"]),lemmascount(predicatetest["obj_"]))/2
        activation+=get_cosine(lemmascount(pred["where_"]),lemmascount(predicatetest["how_"]))/2
        activation+=get_cosine(lemmascount(pred["where_"]),lemmascount(predicatetest["why_"]))/2
        activations.append((activation,i))
    if activations==[]:
        activations.append((0,i))
    return activations
        
        
        
    