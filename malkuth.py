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
import http.client
import json 


class malkuth:
    MEMORY =  sl.connect('MEMORY.db')
    kwfinder=keywordsfinder.KeywordsFinder()
    beefcomp=beliefcomparator.BeliefComparator()
    writememory=False
    lastresponse=""
    last_video=""
    
    def __init__(self,sentencesperquery: int,sequencelength: int,topp:float,topk:int,shorttermmemory_size:int,writememory:bool):
        self.writememory=writememory
        self.scentgen=sentencegenerator.SentenceGenerator(sentencesperquery, sequencelength,shorttermmemory_size,topp,topk)
        
    def generate_response(self,message,messagesender):
        #get keywords from prompt message
        messagekw=self.kwfinder.keywords(message)
        
        #get pointers to memories(beliefs) linked to keywords
        datapointers=[]
        for kw in messagekw:
            dtpointer=self.MEMORY.execute("SELECT (pointer) FROM KEYWORDSPOINTERS WHERE keyword == ?",kw).fetchall()
            datapointers+=dtpointer
       
        #generate responses tp prompt
        prompt=messagesender+": "+message+" Malkuth:"
        generatedsentences=self.scentgen.inference_session(prompt,self.lastresponse)
        
        
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
            
            #fetch beliefs corresponding to pointers
            beliefs=[]
            for ptr in keywordspointers:
                blf=self.MEMORY.execute("SELECT * FROM BELIEFS WHERE id==?",ptr).fetchall()
                beliefs.append(belief.belief(blf[0][1], blf[0][2]))
                
            #for each generated sentence, the belief comparator will receive (the sentence, the list of beliefs to test the sentence against)
            testsentences.append((sen,beliefs))
        chosensentence=self.beefcomp.mostbelievable(testsentences)
        chosenresponse=chosensentence[0][len(prompt):]
        
        self.lastresponse=""
        self.lastresponse+=chosensentence[0] #save the current Q/A for preserving its tensors into the sentence generator context
        
        #save to MEMORY database
        if self.writememory == True:
            chosensentencekw=self.kwfinder.keywords(chosenresponse)
            self.MEMORY.execute("INSERT INTO BELIEFS (belief, strength) values(?,?)",chosensentence)
            pointer=self.MEMORY.execute("select seq from sqlite_sequence where name='BELIEFS'").fetchall()
            pointers=[]
            for kw in chosensentencekw:
                 pointers.append((pointer[0][0],kw[0]))
            for kw in messagekw:
                pointers.append((pointer[0][0],kw[0]))
            qry="INSERT INTO KEYWORDSPOINTERS (pointer,keyword) values(?,?)"
            self.MEMORY.executemany(qry,pointers)
            self.MEMORY.commit()
            
        return chosenresponse,chosensentence[1]
    
    def youtube_video(self,link=""):
        conn = http.client.HTTPSConnection("yt-api.p.rapidapi.com")
        if link=="":
            keywords=self.MEMORY.execute("select (keyword) from KEYWORDSPOINTERS").fetchall()
            keywords=keywords[(len(keywords)-min(5,len(keywords))):]
            rsrch=b""
            for kw in keywords:
                rsrch+=kw[0].encode("ascii","ignore")
                rsrch+=b"%20"
            research=b'/search?query='+rsrch+b'&pretty=1'
            headers = {
                'X-RapidAPI-Key': "112b6ebd1bmsh65242a7d696060ap1d04ecjsn61318ebf35da",
                'X-RapidAPI-Host': "yt-api.p.rapidapi.com"
            }
            
            conn.request("GET", research.decode("ascii"), headers=headers)
            
            res = conn.getresponse()
            data = res.read()
            jsonised=json.loads(data)
            self.last_video=jsonised["data"][0]
            return("https://youtu.be/"+jsonised["data"][0]["videoId"]+self.scentgen.free_text_gen(jsonised["data"][0]["title"]))
        
            
        else:
            while link.find("/")!=-1:
                link=link[link.find("/")+1:]
            headers = {
                'X-RapidAPI-Key': "112b6ebd1bmsh65242a7d696060ap1d04ecjsn61318ebf35da",
                'X-RapidAPI-Host': "yt-api.p.rapidapi.com"
            }
            conn.request("GET", "/video?id="+link, headers=headers)
            res = conn.getresponse()
            data = res.read()
            jsonised=json.loads(data)
            self.last_video=jsonised
            return ("https://youtu.be/"+jsonised["id"]+self.scentgen.free_text_gen(jsonised["title"]))
    
    def on_my_mind(self):
        keywords=self.MEMORY.execute("select (keyword) from KEYWORDSPOINTERS").fetchall()
        keywords=keywords[(len(keywords)-min(5,len(keywords))):]
        resp="Je suis en ce moment en train de penser à :"
        for kw in keywords:
            resp+=kw[0]
        return resp
    
    def freeprompt(self,prompt):
        return self.scentgen.free_text_gen(prompt)