# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 01:23:45 2023

@author: suric
"""

import torch
from transformers import BloomTokenizerFast 
from petals import DistributedBloomForCausalLM



class SentenceGenerator():
    MODEL_NAME = "bigscience/bloomz-petals"
    tokenizer = BloomTokenizerFast.from_pretrained(MODEL_NAME)
    model = DistributedBloomForCausalLM.from_pretrained(MODEL_NAME)
    sentencesperquery=0
    sequencelength=25
    topp=0.9
    topk=3
    metacontext=tokenizer("Malkuth, le premier général de l'armée de Sirus, échange avec des humains par messagerie électronique instantanée. ", return_tensors="pt")["input_ids"]
    context=[]
    shorttermmemory_size=20
    
    def __init__(self, sentencesperquery:int,sequencelength:int,shorttermmemory_size:int,topp:float,topk:int):
        self.sentencesperquery=sentencesperquery #number of sentences generated for memory-based choice
        self.sequencelength=sequencelength #max length of a response in tokens
        self.topp=topp #top p sampling 
        self.topk=topk #top k sampling
        self.shorttermmemory_size=shorttermmemory_size #size of the memory of the inference session in number of messages
        
    def generate_sentences(self,context,prompt: str):
            inpts = self.tokenizer(prompt, return_tensors="pt")["input_ids"]
            inputs=torch.cat((context, inpts), 1)
            sentences=[]
            for i in range(self.sentencesperquery):
                tokenout = self.model.generate(inputs, max_length=len(inputs[0])+self.sequencelength,do_sample=True,top_p=self.topp,early_stopping=True,temperature=0.7,no_repeat_ngram_size=3)
                sentence=self.tokenizer.decode(tokenout[0][len(context[0]):])
                sentenceb=prompt
                j=len(prompt)-1
                while j< len(sentence):
                    if sentence[j]=='«'or sentence[j] == '»':
                        sentenceb+=''
                    elif sentence[j]=='.'or sentence[j]=='!'or sentence[j]=='?':
                        sentenceb+=sentence[j]
                        j=len(sentence)
                    else:
                        sentenceb+=sentence[j]
                    j+=1
                sentences.append(sentenceb)
                print(sentenceb)
            return(sentences)
    
    def inference_session(self,prompt: str,last_response: str):
        self.context.append(self.tokenizer(last_response+" \n ", return_tensors="pt")["input_ids"])
        if len(self.context)>self.shorttermmemory_size:
            self.context.pop(0)
        hyperprompt = torch.cat((self.context[0],self.metacontext),1)
        for i in range(1,len(self.context)):
            hyperprompt=torch.cat((hyperprompt, self.context[i]), 1)
        gscent = self.generate_sentences(hyperprompt,prompt)
        return gscent
    
    def free_text_gen(self,prompt):
        inputs = self.tokenizer(prompt, return_tensors="pt")["input_ids"]
        tokenout = self.model.generate(inputs, max_length=len(inputs[0])+self.sequencelength,do_sample=True,top_p=self.topp,temperature=0.7,no_repeat_ngram_size=3)
        sentence=self.tokenizer.decode(tokenout[0])
        return sentence
        