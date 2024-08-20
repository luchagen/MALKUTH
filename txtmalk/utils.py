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
