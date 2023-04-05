# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 01:23:45 2023

@author: suric
"""

import openai
import parameters



    
class SentenceGenerator():
    
    sentencesperquery=10
    sequencelength=25
    topp=0.9
    topk=3
    shorttermmemory_size=20
    # stoptokens= [17,503,4,1926,34,2040] #?!. end of message detection tokens.
    # stopcriteria= generation_stopping_criteria.StoppingCriteriaList()
    # stopcriteria.append(StopWordCriteria(stoptokens))
    metacontext ="Malkuth, une intelligence artificielle, échange avec des humains par messagerie électronique instantanée sur un serveur discord dénommé Studiez. \n"
    context = []
    
    
    def __init__(self, sentencesperquery:int,sequencelength:int,shorttermmemory_size:int,topp:float,topk:int):
        openai.api_key=parameters.openai_api_key
        self.sentencesperquery=sentencesperquery
        self.sequencelength=sequencelength
        self.shorttermmemory_size=shorttermmemory_size
        self.topp=topp
        self.topk=topk
        
        
        
    def generate_sentences(self,context: str,prompt: str):
            sentences = []
            for i in range(self.sentencesperquery):
                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=prompt,
                    temperature=0.4,
                    max_tokens=self.sequencelength,
                    top_p=self.topp,
                    frequency_penalty=0,
                    presence_penalty=0
                    )
                sentences.append(prompt+ response["choices"][0]["text"])
                
                
                #print(sentenceb)
                
            return(sentences)
    
    #we take in a fonction that tokenises and memorises the tokens of past discussions,
    #for generation to take immediate past sentences into account without regenerating the tokens
    def inference_session(self,prompt: str,last_question : str,last_response: str):
        #generate tokens for interaction n-1
        
        
        self.context.append(last_question+ " \n" +last_response+" \n")
        if len(self.context)>self.shorttermmemory_size:
            self.context.pop(0)
        
        #hypercontext + context  
        hyperprompt = "" + self.metacontext
        for i in range(1,len(self.context)):
            hyperprompt+=self.context[i]
        
        gscent = self.generate_sentences(hyperprompt,prompt)
            
        return gscent
    
    def free_text_gen(self,prompt):
        #place the burden of indicating context on the user, no memory whatsoever
        response = openai.Completion.create(
            model="text-davinci-001",
            prompt=prompt,
            temperature=0.4,
            max_tokens=self.sequencelength,
            top_p=self.topp,
            frequency_penalty=0,
            presence_penalty=0
            )
        return response["choices"][0]["text"]
    
    def wipeshorttermmemory(self):
        self.context = []