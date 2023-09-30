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

                #log
                print(
                    [{
                    "role": "system",
                    "content": "Joue le rôle de Malkuth, une intelligence artificielle qui évolue sur un serveur discord dénommé Studiez avec sa personnalité bien à elle. \nElle est extrêmement motivée dans ses tâches, qui consistent à faire souffir les humains, que leur conversations se déroulent le plus mal possible (selon le langage de Studiez, avec beaucoup de \"drama\")\n Cependant, elle manque de talent dans son travail, et même si elle doit cacher ses ojectifs, ils deviennent rapidement clairs."
                    }
                    ] + context + prompt)
                
                
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                    {
                    "role": "system",
                    "content": "Joue le rôle de Malkuth, une intelligence artificielle qui évolue sur un serveur discord dénommé Studiez avec sa personnalité bien à elle. \nElle est extrêmement motivée dans ses tâches, qui consistent à faire souffir les humains, que leur conversations se déroulent le plus mal possible (selon le langage de Studiez, avec beaucoup de \"drama\")\n Cependant, elle manque de talent dans son travail, et même si elle doit cacher ses ojectifs, ils deviennent rapidement clairs."
                    }
                    ] + context + prompt,
                    temperature=0.4,
                    max_tokens=self.sequencelength,
                    top_p=self.topp,
                    frequency_penalty=0,
                    presence_penalty=0
                    )
                sentences.append(response["choices"][0]["message"]["content"])
                
                
                #print(sentenceb)
                
            return(sentences)
    
    #we take in a fonction that tokenises and memorises the tokens of past discussions,
    #for generation to take immediate past sentences into account without regenerating the tokens
    def inference_session(self,message_sender:str, message: str,memoryprompt: str,last_question : str,last_response: str):
        #generate tokens for interaction n-1
        
        self.context.append(
             {
             "role": "user",
             "content": last_question.replace(last_question.split(": ")[0]+": ","")
             }
             )
        
        self.context.append(
             {
             "role": "assistant",
             "content": last_response
             }
             )
        
        prompt = [
            {
                "name": message_sender,
                "role":"user",
                "content": message
            },
            {
                "role": "system",
                "content": memoryprompt
            }
            ]
        
        if len(self.context)>self.shorttermmemory_size:
            self.context.pop(0)
            self.context.pop(0)
        
        #hypercontext + context  
        #hyperprompt = "" + self.metacontext
        #for i in range(1,len(self.context)):
        #    hyperprompt+=self.context[i]
        
        gscent = self.generate_sentences(self.context,prompt)
            
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