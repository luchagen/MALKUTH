# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 01:25:47 2023

@author: suric
"""

import stanza

#conversion from stanza's to spacy's syntax
class document:
    class token:
        pos_=""
        dep_=""
        lemma_=""
        def __init__(self,wor,parentdocument):
            self.parentdocument= parentdocument
            self.dep_ =wor.deprel
            self.pos_=wor.pos
            self.text=wor.text
            self.feats= wor.feats
            if self.feats != None:
                self.feats= self.feats.split('|')
            self.lemma_=wor.lemma
            self.head_=wor.head-1
            self.head=self
            self.i = wor.id-1
            self.children=[]
        def maketreeheads(self):
            self.head=self.parentdocument.tokens[self.head_]
        def maketreechildren(self):
            children = []
            for tokens in self.parentdocument.tokens:
                if tokens.head.i==self.i:
                    children.append(tokens)
                    
            self.children=children
            
            
        def head(self):
            return()
    def __init__(self,sentence):
        self.sentence = sentence
        self.tokens=[]
        for wor in sentence.words: 
            self.tokens.append(self.token(wor,self))
        for mytoken in self.tokens:
            mytoken.maketreeheads()
        for mytoken in self.tokens:
            mytoken.maketreechildren()
        
class KeywordsFinder:
    nlp = stanza.Pipeline("fr",processors='tokenize,pos,mwt,lemma,depparse')
    
    #find simple keywors i.e nouns and verbs
    def keywords(self, string):  
        sentence= self.nlp.process(string)
        keywords=[]
        for sen in sentence.sentences:
            for wor in sen.words:
                if wor.pos=='NOUN' or wor.pos=='PROPN' or wor.pos=='VERB':
                    keywords.append([wor.lemma])
        return keywords
    
    #parse the text into predicates
    def predicates(self, string):
        predicates=[]
        sentence = self.nlp.process(string)
        for sen in sentence.sentences:
            self.doc=document(sen)
            for token in self.doc.tokens:
                if token.pos_ in ("VERB") and token.dep_ not in ("xcomp", "conj","advcl"):
                    self.pred(token,[token.i] ,predicates,[],[],[],[],[])
                elif token.pos_ in("NOUN, PROPN,ADJ") and token.dep_ not in ("xcomp", "conj","advcl"):
                    proceed=False
                    for child in token.children:
                        if child.pos_ in("AUX") and child.dep_ in ("cop"):
                            proceed= True
                    if proceed == True:
                        self.pred(token,[token.i] ,predicates,[],[],[],[],[])
            for i in range(len(predicates)-1,-1,-1):
                for j in range (len(predicates)-1,i,-1):
                    if predicates[i]==predicates[j] :       
                        predicates.pop(j)
        return predicates
    def addobj (self,obj,child,predicates):
        groups= self.addtogroup(child, predicates)
        for item in groups :
            if obj[len(obj)-1]=="":
                obj[len(obj)-1]=item
            else: 
                obj.append(item)

    def addwhy(self,why,child,predicates):
        for grandchild in child.children:
            if (grandchild.lemma_
                    in (
                        "par"
                        "parce"
                        "car"
                        "avec"
                    )):
                groups= self.addtogroup(child , predicates)
                for item in groups :
                    if why[len(why)-1]=="":
                        why[len(why)-1]=item
                    else: 
                        why.append(item)
    
    #quand / où codés au même endroit
    def addwhere(self,where,child,predicates):
        iswhere=False
        for grandchild in child.children:
            #cases indicating a time or a place
            if (grandchild.lemma_
                    in (
                        "à",
                        "au",
                        "dessus",
                        "contre",
                        "long",
                        "parmis",
                        "parmi",
                        "autour",
                        "a",
                        "derriere",
                        "dessous",
                        "sous",
                        "cote",
                        "entre",
                        "dela",
                        "proche",
                        "en",
                        "bas",
                        "dans",
                        "interieur",
                        "pres",
                        "apres",
                        "dehors",
                        "sur",
                        "oppose",
                        "autour",
                        "travers",
                        "outside",
                        "vers",
                        "la",
                        "ici",
                        "chez",
                        "avant",
                        "de",
                        "d'",
                        "le"
                    )):
                iswhere=True
        if iswhere==True:
                groups= self.addtogroup(child, predicates)
                if where[len(where)-1]=="":
                    where.pop(len(where)-1)
                    for item in groups :
                        where.append(item)
                else:
                    for i in range(len(where)):
                        where[i]+=groups[0]
                        for j in range(1,len(groups)): 
                            where.append(where[i]+ groups[j])

    def addhow(self,how,child,predicates):
        groups= self.addtogroup(child, predicates)
        for item in groups:
            if how[len(how)-1]=="":
                how.pop(len(how)-1)
                how+=item
            else:
                how+=item

    def addsubj(self,subj,testsubj,child,predicates):
        groups= self.addtogroup(child, predicates)
        for item in groups :
            if subj[len(subj)-1]=="" or (subj==testsubj and child.head.dep_ in ("conj","xcomp","advcl")):
                for i in range(len(subj)-1,-1,-1):
                    subj.pop(i)
                subj.append(item)
            else: 
                subj.append(item)
    def pred(self,token,text ,predicates, subj=[], obj=[], where=[],how=[],why=[]):
        if subj==[]:
            subj.append("")
        testsubj=[]
        testsubj+=subj
        if obj==[]:
            obj.append("")
        if where==[]:
            where.append("")
        if how==[]:
            how.append("")
        if why==[]:
            why.append("")
        
        #head is VERB and predicate is adnominal clause
        if token.pos_ == "VERB" and token.dep_ =="acl":
            reversed = False
            for child in token.children:
                if child.dep_ in ("obl:agent"):
                    reversed = True
                    agent=child
            if reversed == True:
                self.addsubj(subj,testsubj,agent,predicates)
                self.addobj(obj,token.head,predicates)
            else:
                self.addsubj(subj,testsubj,token.head,predicates)
            
        for child in token.children:
            if child.dep_ in ("cop") and child.pos_ in ("AUX"):
                text = [child.i] + text
                if token.pos_ in ("NOUN,PROPN"):
                    self.addobj(obj,token,predicates)
                    text = [child.i]
            #add auxiliary to head
            if child.dep_ in ("aux:tense","aux:pass"):
                text = [child.i] + text
                
            #subject found
            if child.dep_ in ("nsubj","nsubj:pass"):
                self.addsubj(subj,testsubj,child,predicates)
                        
            #direct object found (COD?)
            if child.dep_ in ("obj","iobj"):
                self.addobj (obj,child,predicates)
            #adverbial modifier of head found
            if child.dep_ in ("advmod") and child.pos_ in ("ADV") and child.head.pos_ in("VERB"):
                self.addhow (how,child,predicates)
            #oblique argument: to adj(noun/adj predicate) => obj , to verb => (COI?)
            if child.dep_ in ("obl:arg"):
                if child.head.pos_ == "ADJ":
                    self.addobj (obj,child,predicates)
                elif child.head.pos_ == "VERB":
                    self.addwhere(where,child,predicates)
                    self.addwhy(why,child,predicates)
            
            #oblique modifier (nominal adjuncts in french?)
            if child.dep_ in ("obl:mod"):
                self.addwhere(where,child,predicates)
                self.addwhy(why,child,predicates)
            #linked predicates ("Je mange mes frites et bois mon soda")
            if child.dep_ in ("xcomp") and (  child.pos_ in("NOUN","PROPN") or ( child.pos_ == "VERB" and len([ft for ft in child.feats if ft=='VerbForm=Inf'])!=0)):
                self.addobj(obj,child,predicates)
            if child.dep_ in ("conj","xcomp","advcl") and child.pos_ == "VERB" and len([ft for ft in child.feats if ft=='VerbForm=Inf'])==0:
                conjsubj=[]
                for otherchild in token.children:
                    if otherchild.dep_ == "nsubj": 
                        groups= self.addtogroup(otherchild, predicates)
                        for item in groups :
                            conjsubj.append(item)
                self.pred(child,[child.i], predicates,conjsubj,[],[],[],[])
                
            #phrases être - adj ("je suis un humain" > "humain = verb") 
            if child.dep_ in ("conj","xcomp","advcl") and child.pos_ in ("PROPN","NOUN") :
                proceed=False
                for grandchild in child.children:
                    if grandchild.pos_ in("AUX") and grandchild.dep_ in ("cop"):
                        proceed= True
                if proceed == True:
                    conjsubj=[]
                    for otherchild in token.children:
                        if otherchild.dep_ == "nsubj": 
                            groups= self.addtogroup(otherchild, predicates)
                            for item in groups :
                                conjsubj.append(item)
                    self.pred(child,[child.i], predicates,conjsubj,[],[],[],[])
                    
        # print(subj)
        # print(text)
        # print(obj)
        # print(where)
        # print(how)
        for i in range(len(subj)):
            for j in range(len(obj)):
                for k in range (len(where)):
                    for l in range(len(why)):
                            tsubj=""
                            tobj=""
                            twhere=""
                            twhy=""
                            thow=""
                            if isinstance(text[len(text)-1],int):
                                text.sort()
                                thead=[(self.doc.tokens[text[mm]].text,self.doc.tokens[text[mm]].lemma_) for mm in range(len(text))]
                            else:
                                thead=text
                            if subj[i] != "":
                                subj[i].sort()
                                tsubj= [(self.doc.tokens[subj[i][ii]].text,self.doc.tokens[subj[i][ii]].lemma_) for ii in range(len(subj[i]))]
                            if obj[j] != "":
                                obj[j].sort()
                                tobj= [(self.doc.tokens[obj[j][jj]].text,self.doc.tokens[obj[j][jj]].lemma_) for jj in range(len(obj[j]))]
                            if where[k] != "":
                                where[k].sort()
                                twhere= [(self.doc.tokens[where[k][kk]].text,self.doc.tokens[where[k][kk]].lemma_) for kk in range(len(where[k]))]
                            if why[l] !="":
                                why[l].sort()
                                twhy= [(self.doc.tokens[why[l][ll]].text,self.doc.tokens[why[l][ll]].lemma_) for ll in range(len(why[l]))]
                            if how[0] != "":
                                how.sort()
                                thow= [(self.doc.tokens[how[hh]].text,self.doc.tokens[how[hh]].lemma_) for hh in range(len(how))]
                            predicates.append(
                            {
                            
                            "subj":subj[i],
                            "subj_":tsubj,
                            "head":text,
                            "head_":thead,
                            "obj":obj[j],
                            "obj_":tobj,
                            "where":where,
                            "where_":twhere,
                            "why":why[l],
                            "why_":twhy,
                            "how":how,
                            "how_":thow
                            }
                            )
    
    #we recursively add words of the same group to an information                        
    def addtogroup(self,token,predicates):
        group=[[token.i]]
        for child in token.children:
            if child.dep_ in ("conj") and child.pos_ not in ("VERB"):
                if len([tok for tok in child.children if tok.pos_ in ("AUX" ) and tok.dep_ in ("cop")])==0:
                    group+= self.recaddtogroup(child,predicates,[])
            if child.dep_ in ("amod"):
                self.pred(child,[("est","être"), (child.text,child.lemma_)],predicates,self.recaddtogroup(token,predicates,["amod"]),[],[],[],[])
            if child.dep_ in ("appos"):
                for grandchild in child.children:
                    if grandchild.dep_ in ("amod"):
                        obj = []
                        obj1=self.recaddtogroup(child,predicates,["amod"])
                        obj2=self.recaddtogroup(grandchild,predicates,[])
                        for item1 in obj1:
                            for item2 in obj2:
                                obj.append(item1 + item2)
                        self.pred(grandchild,[("est","être")],predicates,self.recaddtogroup(token,predicates,["appos"]),obj,[],[],[])
            if token.dep_ in ("obl:mod","obl:arg") and child.dep_ in ("case"):
                rec=self.recaddtogroup(child,predicates,[])
                tempgroup=[]
                for item1 in rec:
                    for item2 in group:
                        tempgroup.append(item2  + item1)
                group= tempgroup
                
            if child.dep_ in ("nmod","amod","flat:name", "advmod","nummod","det","fixed","obl:arg","obl:mod",'dep','mark','expl:comp','acl','cop',"flat:foreign") and child.pos_ not in ("VERB","AUX","SCONJ","ADV"):
                rec=self.recaddtogroup(child,predicates,[])
                tempgroup=[]
                for item1 in rec:
                    for item2 in group:
                        tempgroup.append(item2 + item1)
                group= tempgroup
        return(group)
    def recaddtogroup(self,token, predicates, ignore):
        group=[[token.i]]
        for child in token.children :
            if child.dep_ not in ignore:
                if child.dep_ in ("conj"):
                    if len([tok for tok in child.children if tok.pos_ in ("AUX" ) and tok.dep_ in ("cop")])==0:
                        group+= self.recaddtogroup(child,predicates,[])
                if child.dep_ in ("amod"):
                    self.pred(child,[("est","être"), (child.text,child.lemma_)],predicates,self.recaddtogroup(token,predicates,["amod"]),[],[],[],[])
                if child.dep_ in ("appos"):
                    for grandchild in child.children:
                        if grandchild.dep_ in ("amod"):
                            obj = []
                            obj1=self.recaddtogroup(child,predicates,["amod"])
                            obj2=self.recaddtogroup(grandchild,predicates,[])
                            for item1 in obj1:
                                for item2 in obj2:
                                    obj.append(item1 + item2)
                            self.pred(grandchild,[("est","être")],predicates,self.recaddtogroup(token,predicates,["appos"]),obj,[],[],[])
                if token.dep_ in ("obl:mod","obl:arg","conj") and child.dep_ in ("case"):
                    rec=self.recaddtogroup(child,predicates,[])
                    tempgroup=[]
                    for item1 in rec:
                        for item2 in group:
                            tempgroup.append(item2  + item1)
                    group= tempgroup
                    
                if child.dep_ in ("nmod","flat:name","amod", "advmod","nummod","det","fixed","obl:arg","obl:mod",'dep','mark','expl:comp','acl','cop',"flat:foreign") and child.pos_ not in ("VERB","AUX","SCONJ","ADV"):
                    rec=self.recaddtogroup(child,predicates,[])
                    tempgroup=[]
                    for item1 in rec:
                        for item2 in group:
                            tempgroup.append(item2  + item1)
                    group= tempgroup
        return(group)



if __name__ == "__main__":
    keyfind=KeywordsFinder()
    predicates=keyfind.predicates("Comment t'appelles-tu ?")

    