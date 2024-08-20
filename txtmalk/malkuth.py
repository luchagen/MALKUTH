# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 18:26:28 2023

@author: suric
"""
import sqlite3 as sl
import http.client
import json
import logging
from txtmalk import keywordsfinder,beliefcomparator,sentencegeneratorapi,belief
import parameters

class malkuth:
    MEMORY =  sl.connect('MEMORY.db', check_same_thread=False)
    kwfinder=keywordsfinder.KeywordsFinder()
    beefcomp=beliefcomparator.BeliefComparator(kwfinder)
    writememory=False
    lastquestion=""
    lastresponse=""
    last_video=""
    last_activated=""
    _logger=logging.getLogger(__name__)
    _logger.setLevel(20)
    _logger.addHandler(
        logging.FileHandler(filename='malkuth.log', encoding='utf-8', mode='w')
        )


    def __init__(self,sentencesperquery: int,sequencelength: int,topp:float,topk:int,shorttermmemory_size:int,writememory:bool):
        self.writememory=writememory
        self.scentgen=sentencegeneratorapi.SentenceGenerator(sentencesperquery, sequencelength,shorttermmemory_size,topp,topk)


    def generate_response(self,message : str ,messagesender : str ,server='',channel = ''):
        """Handles Malkuth generating a text response to a message.

        Args:
            message (str): Message Malkuth has to respond to.
            messagesender (str): Individual who sent the message
            server (str, optional): _description_. Defaults to ''.
            channel (str, optional): _description_. Defaults to ''.

        """        #get memories activated by prompt message
        beliefs=self.get_beliefs_from_sentence(message)

        memoryprompt= self.build_memory_prompt(beliefs)
        system_prompt = [self.get_system_prompt(server,channel)] + memoryprompt

        #generate responses to prompt
        prompt={'messagesender' : messagesender, 'message' : message }
        generatedsentences=self.scentgen.inference_session(system_prompt,
                                prompt,self.lastquestion,self.lastresponse)

        #get keywords from generated response
        for sentence in generatedsentences:
            beliefs += self.get_beliefs_from_sentence(sentence)

        #for each generated sentence, the belief comparator will receive (the sentence, the list of beliefs to test the sentence against)
        chosensentence=self.beefcomp.choose_sentence(generatedsentences,beliefs)
        chosenresponse=chosensentence[0]

        self.lastquestion=prompt
        self.lastresponse=chosensentence[0] #save the current Q/A for preserving its tensors into the sentence generator context

        #save to MEMORY database
        if self.writememory is True:
            chosensentencekw=self.kwfinder.keywords(chosenresponse)
            self.save_belief(chosensentencekw , chosenresponse , chosensentence[1])

        self._logger.info(chosenresponse)
        return chosenresponse,chosensentence[1],self.last_activated

    def get_beliefs_from_sentence(self, sentence):
        #get keywords from prompt message
        keywords=self.kwfinder.keywords(sentence)

        beliefs=[]
        #get pointers to memories(beliefs) linked to keywords
        keywordspointers=[]
        for kw in keywords:
            dtpointer=self.MEMORY.execute("SELECT (pointer) FROM KEYWORDSPOINTERS WHERE keyword == ?",kw).fetchall()
            keywordspointers+=dtpointer
        keywordspointers=list(set(keywordspointers))
        #fetch beliefs corresponding to pointers

        for ptr in keywordspointers:
            blf=self.MEMORY.execute("SELECT * FROM BELIEFS WHERE id==?",ptr).fetchall()
            beliefs.append(belief.Belief(blf[0][1], blf[0][2]))

        return beliefs


    def build_memory_prompt(self,beliefs):
        """Build the memory prompt to send to the Language model,
        depending on the beliefs fetched with fetch_memories.
        We only send a certain number (4).

        Args:
            beliefs (_type_): One belief to be stated to Malkuth as a directive.
        """
        memoryprompts=[]

        beliefs= list(set(beliefs))
        for i in range(min(len(beliefs),4)):
            memoryprompts.append(' \nMalkuth pense : "' + beliefs[i].getsentence())

        self.last_activated=memoryprompts
        return memoryprompts


    def save_belief(self,keywords , sentence : str , belief_strength : float):
        """Save a belief into the belief database.

        Args:
            keywords : list of keywords (lemmas) as returned by kwfinder.keywords
            sentence (str): This is the sentence Malkuth has to associate to the keywords.
            belief_strength (int): This is the overall strength of the belief, used for weight calculation 
        """

        self.MEMORY.execute("INSERT INTO BELIEFS (belief, strength) values(?,?)",(sentence,belief_strength))
        pointer=self.MEMORY.execute("select seq from sqlite_sequence where name='BELIEFS'").fetchall()

        pointers=[]
        for kw in keywords:
            pointers.append((pointer[0][0],kw[0]))
        qry="INSERT INTO KEYWORDSPOINTERS (pointer,keyword) values(?,?)"
        self.MEMORY.executemany(qry,pointers)
        self.MEMORY.commit()


    def freeprompt(self,prompt):
        return self.scentgen.free_text_gen(prompt)
        
    def program(self, questions: str, answer: str):
        sentencekw=self.kwfinder.keywords(answer)+self.kwfinder.keywords(questions)
        self.save_belief(sentencekw, answer, 1.0 )


    def wipeshorttermmemory(self):
        self.scentgen.wipeshorttermmemory()
        self.lastquestion =""
        self.lastresponse =""


    def new_system_prompt(self,server: str ,channel: str, prompt: str):
        '''Insert a new system prompt for the channel
        so that malkuth knows how behave there'''
        existence_check=self.MEMORY.execute(
        f"SELECT id FROM CHANNELS WHERE server='{server}' AND channel='{channel}'"
        ).fetchall()
        self._logger.info(str((server,channel,prompt,existence_check)))

        try:
            if existence_check:
                self._logger.info('Overwriting existing system prompt')
                self.MEMORY.execute(
                "UPDATE CHANNELS set system_prompt = ? WHERE server=? AND channel=?",
                (prompt,server,channel)
                )

            else :
                self.MEMORY.execute(
                "INSERT INTO CHANNELS(server,channel,system_prompt) VALUES (?,?,?)",
                (server,channel,prompt)
                )

            self.MEMORY.commit()

        except Exception as e:
            self.MEMORY.rollback()
            raise e from e


    def get_system_prompt(self,server: str ,channel: str):
        '''Get the system prompt for the channel
        so that malkuth knows how behave there'''
        system_prompt=self.MEMORY.execute(
        f"SELECT system_prompt FROM CHANNELS WHERE server='{server}' AND channel='{channel}'"
        ).fetchall()

        if system_prompt and system_prompt[0]:
            self._logger.info(str((server,channel,system_prompt[0][0])))
            return system_prompt[0][0]

        self._logger.info('No system prompt found for %s %s', server, channel)
        return '''Malkuth, une intelligence artificielle,
                échange avec des humains, par messagerie électronique instantanée,
                sur un serveur discord dénommé Studiez. \n'''


    async def youtube_video(self,link=""):
        conn = http.client.HTTPSConnection("yt-api.p.rapidapi.com")
        if link=="":
            rsrch=b""
            if self.lastresponse!=None:
                rsrch+=self.lastresponse.encode("ascii","ignore")
            research=b'/search?query='+rsrch+b'&pretty=1'
            headers = {
                'X-RapidAPI-Key': parameters.youtube_api_key,
                'X-RapidAPI-Host': "yt-api.p.rapidapi.com"
            }
            
            conn.request("GET", research.decode("ascii"), headers=headers)
            
            res = conn.getresponse()
            data = res.read()
            jsonised=json.loads(data)
            return("https://youtu.be/"+jsonised["data"][0]["videoId"]+self.scentgen.free_text_gen(jsonised["data"][0]["title"]))
        
            
        else:
            while link.find("/")!=-1:
                link=link[link.find("/")+1:]
            headers = {
                'X-RapidAPI-Key': parameters.youtube_api_key,
                'X-RapidAPI-Host': "yt-api.p.rapidapi.com"
            }
            conn.request("GET", "/video?id="+link, headers=headers)
            res = conn.getresponse()
            data = res.read()
            jsonised=json.loads(data)
            return ("https://youtu.be/"+jsonised["id"]+self.scentgen.free_text_gen(jsonised["title"]))