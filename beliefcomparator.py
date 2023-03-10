# -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 23:02:44 2023

@author: suric
"""

from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
import utils


class BeliefComparator:
        modelsentence =  SentenceTransformer("./sentence")
        def __init__(self,keywordsfindersub):
            self.keywordsfindersub=keywordsfindersub
            
            
        
        def mostbelievable(self,testsentences):
            sim=0
            l=0
            k=0
            sentence=testsentences[0][0]
            for testsent in testsentences:
                testsent_vec =self.modelsentence.encode([testsent[0]])[0] 
                testpred=self.keywordsfindersub.predicates(testsent[0])
                memsentence_vec = []
                beliefs= []
                mempred=[]
                for memory in testsent[1]:
                    memsentence_vec.append(self.modelsentence.encode([memory.getsentence()])[0])
                    beliefs.append(memory.getstrength())
                    mempred.append(self.keywordsfindersub.predicates(memory.getsentence()))
                    
                cosim=0
                nbr_memories= len(testsent[1])
                
                #we calculate simularity of the sentences based on their predicates
                predicatesim=[0 for i in range(len(testpred))]
                for i in range(len(testpred)):
                    activations=[]
                    for j in range(nbr_memories):
                        activations+=utils.getactivations(mempred[j],testpred[i],j)
                    nbract=len(activations)
                    for activation in activations:
                        predicatesim[i]+=activation[0]*beliefs[activation[1]]/(nbract*10)
                psim=0
                if len(predicatesim)!=0:
                    psim=sum(predicatesim)/len(predicatesim)

                #we calculate simularity of the sentences based on camembert-sentence
                for j in range(nbr_memories):
                    cosim+=(1-cosine(testsent_vec,memsentence_vec[j]))*beliefs[j]
                if nbr_memories!=0:
                    cosim=cosim/nbr_memories
                    cosim += psim
                if cosim > sim:
                    sentence=testsentences[l][0]
                    sim=cosim
                    k=l 
                l+=1

            if len(testsentences[k][1]) ==0:
                sim=1
            return sentence,sim
        