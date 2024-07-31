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
    default_metacontext ="Malkuth, une intelligence artificielle, échange avec des humains par messagerie électronique instantanée sur un serveur discord dénommé Studiez. \n"
    context = []
    
    
    def __init__(self, sentencesperquery:int,sequencelength:int,shorttermmemory_size:int,topp:float,topk:int):
        openai.api_key=parameters.openai_api_key
        self.sentencesperquery=sentencesperquery
        self.sequencelength=sequencelength
        self.shorttermmemory_size=shorttermmemory_size
        self.topp=topp
        self.topk=topk
        
        
        
    def generate_sentences(self,system_prompt : str , prompt: str ,*context: dict):
            sentences = []
            if not system_prompt:
                system_prompt = self.default_metacontext

            for _ in range(self.sentencesperquery):
                response = openai.chat.completions.create(
                    model="gpt-4o-mini-2024-07-18",
                    messages=[
                        {
                          "role": "system",
                          "content": [
                            {
                              "type": "text",
                              "text": system_prompt
                            }
                          ]
                        }
                        ] + list(context)
                        + [self.parse_message(prompt)],
                    temperature=0.4,
                    max_tokens=self.sequencelength,
                    top_p=self.topp,
                    frequency_penalty=0,
                    presence_penalty=0
                    )
                sentences.append(prompt+ response.choices[0].message.content)
                
                
                #print(sentenceb)
                
            return(sentences)
    

    def inference_session(self,system_prompt : str,prompt: str,last_question : str,last_response: str):
        '''We handle the short term memorisation of past messages here.
        '''
        
        self.context.append(self.parse_message(last_question))
        self.context.append(self.parse_message(last_response))
        if len(self.context)>self.shorttermmemory_size:
            self.context.pop(0)

        gscent = self.generate_sentences(system_prompt,prompt, *self.context)

        return gscent


    def parse_message(self, text : str):
        '''Parse string message into open ai formatted message'''
        return {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text" : text
                }
            ]
            }  

    def free_text_gen(self,prompt, system_prompt=''):
        '''place the burden of indicating context on the user, no memory whatsoever'''
        if not system_prompt:
            system_prompt = self.default_metacontext

        response = self.client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {
                  "role": "system",
                  "content": [
                    {
                      "type": "text",
                      "text": system_prompt
                    }
                  ]
                },
                self.parse_message(prompt)
                ],
            temperature=0.4,
            max_tokens=self.sequencelength,
            top_p=self.topp,
            frequency_penalty=0,
            presence_penalty=0
            )
        return response.choices[0].message.content

    def wipeshorttermmemory(self):
        self.context = []
