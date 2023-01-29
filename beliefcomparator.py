# -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 23:02:44 2023

@author: suric
"""

from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine



class BeliefComparator:
        modelsentence =  SentenceTransformer("./sentence")
        def mostbelievable(self,testsentences):
            sim=0
            i=0
            k=0
            sentence=testsentences[0][0]
            for testsent in testsentences:
                testsent_vec =self.modelsentence.encode([testsent[0]])[0] 
                memsentence_vec = []
                beliefs= []
                for memory in testsent[1]:
                    memsentence_vec.append(self.modelsentence.encode([memory.getsentence()])[0])
                    beliefs.append(memory.getstrength())
                    
                cosim=0
                nbr_memories= len(testsent[1])
                for j in range(nbr_memories):
                    cosim+=(1-cosine(testsent_vec,memsentence_vec[j]))*beliefs[j]
                
                if nbr_memories!=0:
                    cosim=cosim/nbr_memories
               
                if cosim > sim:
                    sentence=testsentences[i][0]
                    sim=cosim
                    k=i 
                i+=1

            if len(testsentences[k][1]) ==0:
                sim=1
            return sentence,sim
        