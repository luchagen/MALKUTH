# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 18:26:28 2023

@author: suric
"""
import sqlite3 as sl
import beliefcomparator
import belief
import sentencegenerator
import keywordsfinder
import json 
import utils

class malkuth:
    MEMORY =  sl.connect('MEMORY.db', check_same_thread=False)
    kwfinder=keywordsfinder.KeywordsFinder()
    beefcomp=beliefcomparator.BeliefComparator(kwfinder)
    writememory=False
    lastquestion=""
    lastresponse=""
    last_video=""
    last_activated=""
    
    def __init__(self,sentencesperquery: int,sequencelength: int,topp:float,topk:int,shorttermmemory_size:int,writememory:bool):
        self.writememory=writememory
        self.scentgen=sentencegenerator.SentenceGenerator(sentencesperquery, sequencelength,shorttermmemory_size,topp,topk)
        
    def generate_response(self,message,messagesender):
        #get keywords from prompt message
        messagekw=self.kwfinder.keywords(message)
        
        #parse predicates from prompt message 
        messagepred= self.kwfinder.predicates(message)
        
        
        #get pointers to memories(beliefs) linked to keywords
        datapointers=[]
        for kw in messagekw:
            dtpointer=self.MEMORY.execute("SELECT (pointer) FROM KEYWORDSPOINTERS WHERE keyword == ?",kw).fetchall()
            datapointers+=dtpointer
        datapointers=list(set(datapointers))
        #get predicates and beliefs linked to memories
        memorypred= []
        beliefs=[]
            
        for ptr in datapointers:
            blf=self.MEMORY.execute("SELECT * FROM BELIEFS WHERE id==?",ptr).fetchall()
            beliefs.append((blf[0][1], blf[0][2]))
            memorysentencestr=self.MEMORY.execute("SELECT predicate FROM PREDICATES WHERE id==?",ptr).fetchall()
            memorysentencepred=[]
            for pred in memorysentencestr:
                memorysentencepred+=json.loads(pred[0])
            memorypred.append(memorysentencepred)
        
        #find most activated memories
        activated = [0 for i in range(len(beliefs))]
        memoryprompt=' \nMalkuth pense : "'
        for pred in messagepred:
            activations=[]
            for i in range(len(memorypred)):
                activations+= utils.getactivations(memorypred[i], pred,i)
            maxactivation=0
            if len(activations)!=0:    
                maxactivation=max(activations)[0]-2.0
            for i in range(len(activations)):
                if activations[i][0]>=2.0 and activations[i][0]-2.0 >= maxactivation-0.5:
                    activated[activations[i][1]]=1
        
        tobeaddedbeliefs=[]
        for i in range(len(beliefs)):
            if activated[i]==1:
                tobeaddedbeliefs.append(beliefs[i][0])
        tobeaddedbeliefs= list(set(tobeaddedbeliefs))
        for i in range(min(len(tobeaddedbeliefs),4)):
                memoryprompt+=  " \n" + tobeaddedbeliefs[i]
        

        if memoryprompt ==' \nMalkuth pense ": ':
            memoryprompt=""
        else:
            memoryprompt+='"'
        self.last_activated=memoryprompt
        #generate responses to prompt
        prompt=messagesender+": "+message+memoryprompt+" \nMalkuth:"
        generatedsentences=self.scentgen.inference_session(prompt,self.lastquestion,self.lastresponse)
        
        
        testsentences=[]
        for sen in generatedsentences:
            
            #get keywords from generated response
            gsentenceskw=self.kwfinder.keywords(sen)
            keywordspointers=[]
            keywordspointers+=datapointers # add prompt message pointers to each response
            
            #get pointers to memories(beliefs) linked to keywords
            for kw in gsentenceskw:
                dtpointer=self.MEMORY.execute("SELECT (pointer) FROM KEYWORDSPOINTERS WHERE keyword == ?",kw).fetchall()
                keywordspointers+=dtpointer
            keywordspointers=list(set(keywordspointers))
            #fetch beliefs corresponding to pointers
            beliefs=[]
            for ptr in keywordspointers:
                blf=self.MEMORY.execute("SELECT * FROM BELIEFS WHERE id==?",ptr).fetchall()
                beliefs.append(belief.Belief(blf[0][1], blf[0][2]))
            
                
            #for each generated sentence, the belief comparator will receive (the sentence, the list of beliefs to test the sentence against)
            testsentences.append((sen,beliefs))
        chosensentence=self.beefcomp.mostbelievable(testsentences)
        chosenresponse=chosensentence[0][len(prompt):]
        
        self.lastquestion=""
        self.lastresponse=""
        self.lastquestion+=messagesender+": "+message
        self.lastresponse+=chosensentence[0][len(prompt):] #save the current Q/A for preserving its tensors into the sentence generator context
        
        #save to MEMORY database
        if self.writememory == True:
            chosensentencekw=self.kwfinder.keywords(chosenresponse)
            sentencepred= json.dumps(self.kwfinder.predicates(chosenresponse)+messagepred)
            self.MEMORY.execute("INSERT INTO PREDICATES (predicate) values(?)",[sentencepred])
            self.MEMORY.execute("INSERT INTO BELIEFS (belief, strength) values(?,?)",(chosenresponse,chosensentence[1]))

            pointer=self.MEMORY.execute("select seq from sqlite_sequence where name='BELIEFS'").fetchall()
            pointers=[]
            for kw in chosensentencekw:
                 pointers.append((pointer[0][0],kw[0]))
            for kw in messagekw:
                pointers.append((pointer[0][0],kw[0]))
            qry="INSERT INTO KEYWORDSPOINTERS (pointer,keyword) values(?,?)"
            self.MEMORY.executemany(qry,pointers)
            self.MEMORY.commit()
            
        return chosenresponse,chosensentence[1],self.last_activated
    
    def freeprompt(self,prompt):
        return self.scentgen.free_text_gen(prompt)
        
    def program(self, questions: str, answer: str):
        sentencekw=self.kwfinder.keywords(answer)+self.kwfinder.keywords(questions)
        chosensentencepred= json.dumps(self.kwfinder.predicates(answer)+self.kwfinder.predicates(questions))
        self.MEMORY.execute("INSERT INTO PREDICATES (predicate) values(?)",[chosensentencepred])
        self.MEMORY.execute("INSERT INTO BELIEFS (belief, strength) values(?,?)",(answer,1.0))
    
        pointer=self.MEMORY.execute("select seq from sqlite_sequence where name='BELIEFS'").fetchall()
        pointers=[]
        for kw in sentencekw:
            pointers.append((pointer[0][0],kw[0]))
         
        qry="INSERT INTO KEYWORDSPOINTERS (pointer,keyword) values(?,?)"
        self.MEMORY.executemany(qry,pointers)
        self.MEMORY.commit()