# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 01:23:45 2023

@author: suric
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.generation import stopping_criteria
from transformers.generation import logits_process
from typing import Iterable, List

#new transformers criterium for stopping generation when encountering tokens we count as stopwords.
class StopWordCriteria(stopping_criteria.StoppingCriteria):
    def __init__(self, stoptokens):
        self.stoptokens = stoptokens
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        return input_ids[-1][-1] in self.stoptokens



#We appy constraints to prevent the model from overly repeating itself 
class NoRepeatNGramWMemLogitsProcessor(logits_process.LogitsProcessor):
    r"""
    Copied from Transformers (generation.logits_process, see NoRepeatNgramLogitsProcessor)
    [`LogitsProcessor`] that enforces no repetition of n-grams. See
    [Fairseq](https://github.com/pytorch/fairseq/blob/a07cb6f40480928c9e0548b737aadd36ee66ac76/fairseq/sequence_generator.py#L345).
    Args:
        ngram_size (`int`):
            All ngrams of size `ngram_size` can only occur once.
    """

    def __init__(self, ngram_size: int,usedngrams:dict, min_logits: float = -1e8):
        if not isinstance(ngram_size, int) or ngram_size <= 0:
            raise ValueError(f"`ngram_size` has to be a strictly positive integer, but is {ngram_size}")
        self.ngram_size = ngram_size
        self.min_logits = min_logits
        self.usedngrams = usedngrams
        
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        num_batch_hypotheses = scores.shape[0]
        cur_len = input_ids.shape[-1]
        banned_batch_tokens = self._calc_banned_ngram_tokens(self.ngram_size, input_ids, num_batch_hypotheses, cur_len)
        
        
        for i, banned_tokens in enumerate(banned_batch_tokens):
            scores[i, banned_tokens] = -float("inf")

        return scores


    def _get_generated_ngrams(self,banned_ngrams, prev_input_ids, ngram_size, cur_len):
        # Before decoding the next token, prevent decoding of ngrams that have already appeared
        start_idx = cur_len + 1 - ngram_size
        ngram_idx = tuple(prev_input_ids[start_idx:cur_len].tolist())
        return banned_ngrams.get(ngram_idx, [])


    def _calc_banned_ngram_tokens(
        self, ngram_size: int, prev_input_ids: torch.Tensor, num_hypos: int, cur_len: int,
    ) -> List[Iterable[int]]:
        """Copied from fairseq for no_repeat_ngram in beam_search"""
        if cur_len + 1 < ngram_size:
            # return no banned tokens if we haven't generated no_repeat_ngram_size tokens yet
            return [[] for _ in range(num_hypos)]

        banned_tokens = [
            self._get_generated_ngrams(self.usedngrams, prev_input_ids[hypo_idx], ngram_size, cur_len)
            for hypo_idx in range(num_hypos)
        ]
        return banned_tokens
    
   

    
class SentenceGenerator():
    tokenizer = AutoTokenizer.from_pretrained("bigscience/bloom-1b7",cache_dir="./models")
    model = AutoModelForCausalLM.from_pretrained("bigscience/bloom-1b7",cache_dir="./models")
    #proposed values (for small LMs)
    sentencesperquery=10
    sequencelength=25
    topp=0.9
    topk=3
    shorttermmemory_size=20
    # stoptokens= [17,503,4,1926,34,2040] #?!. end of message detection tokens.
    # stopcriteria= generation_stopping_criteria.StoppingCriteriaList()
    # stopcriteria.append(StopWordCriteria(stoptokens))
    stoptokens =[] #end of message detection tokens.
    metacontext=tokenizer("Malkuth, une intelligence artificielle, échange avec des humains par messagerie électronique instantanée. ", return_tensors="pt")["input_ids"]
    context=[] #old messages stored as tokens
    memquottoken=[] #token that delimit memories, for use in a repetition constraint
    
    
    def __init__(self, sentencesperquery:int,sequencelength:int,shorttermmemory_size:int,topp:float,topk:int):
        self.sentencesperquery=sentencesperquery #number of sentences generated for memory-based choice
        self.sequencelength=sequencelength #max length of a response in tokens
        self.topp=topp #top p sampling 
        self.topk=topk #top k sampling (not used)
        self.shorttermmemory_size=shorttermmemory_size #size of the memory of the inference session in number of messages
        self.trigramlists=[] #trigrams that have already be done 
        #We autodetect the end of message detection tokens
        a= self.tokenizer(" ?",return_tensors="pt")["input_ids"]
        self.stoptokens.append(a[-1][-1])
        a= self.tokenizer("?",return_tensors="pt")["input_ids"]
        self.stoptokens.append(a[-1][-1])
        a= self.tokenizer("keter?",return_tensors="pt")["input_ids"]
        self.stoptokens.append(a[-1][-1])
        a= self.tokenizer(" !",return_tensors="pt")["input_ids"]
        self.stoptokens.append(a[-1][-1])
        a= self.tokenizer("!",return_tensors="pt")["input_ids"]
        self.stoptokens.append(a[-1][-1])
        a= self.tokenizer("keter!",return_tensors="pt")["input_ids"]
        self.stoptokens.append(a[-1][-1])
        a= self.tokenizer(" .",return_tensors="pt")["input_ids"]
        self.stoptokens.append(a[-1][-1])
        a= self.tokenizer(".",return_tensors="pt")["input_ids"]
        self.stoptokens.append(a[-1][-1])
        a= self.tokenizer("keter.",return_tensors="pt")["input_ids"]
        self.stoptokens.append(a[-1][-1])
        
        
        self.stopcriteria = stopping_criteria.StoppingCriteriaList()
        self.stopcriteria.append(StopWordCriteria(self.stoptokens))
        
    def generate_sentences(self,context,prompt: str,usedtrigrams: dict,usedquadrigrams:dict):
            inpts = self.tokenizer(prompt, return_tensors="pt")["input_ids"]
            inputs=torch.cat((context, inpts), 1) #add inpts to context to run inference
            sentences=[]
            
            logitsprocessors = logits_process.LogitsProcessorList()
            logitsprocessors.append(NoRepeatNGramWMemLogitsProcessor(3,usedtrigrams))
            logitsprocessors.append(NoRepeatNGramWMemLogitsProcessor(4,usedquadrigrams))
            
            tokenout = self.model.generate(inputs, max_length=len(inputs[0])+self.sequencelength,do_sample=True,top_p=self.topp,num_return_sequences =self.sentencesperquery,temperature=0.7,no_repeat_ngram_size=3,logits_processor=logitsprocessors,stopping_criteria=self.stopcriteria,eos_token_id=2)
            
            for i in range(len(tokenout)):
                sentence=self.tokenizer.decode(tokenout[i][len(context[0]):])
                sentenceb=prompt
                j=len(prompt)
                
                #The sentence generation has a tendency to add unnecessary quotes,
                #and to generate a full dialogue rather than just one response, so we used to add delimiters.
                #we keep those in case the model refuses to stop generation when constrained to do it (petals).
                #(note , perhaps the end of sentence delimiters might sometimes cut the answer too short)
                while j< len(sentence):
                    if sentence[j]=='«'or sentence[j] == '»' or sentence[j] =='"':
                        sentenceb+=''
                    elif sentence[j]=='.'or sentence[j]=='!'or sentence[j]=='?':
                        sentenceb+=sentence[j]
                        j=len(sentence)
                    else:
                        sentenceb+=sentence[j]
                    j+=1
                sentences.append(sentenceb)
                
                
                #print(sentenceb)
                
            return sentences
    
    #we take in a fonction that tokenises and memorises the tokens of past discussions,
    #for generation to take immediate past sentences into account without regenerating the tokens
    def inference_session(self,prompt: str,last_question : str,last_response: str):
        #generate tokens for interaction n-1
        self.context.append(self.tokenizer(last_question+ " \n" +last_response+" \n", return_tensors="pt")["input_ids"])
        if len(self.context)>self.shorttermmemory_size:
            self.context.pop(0)
        
        newtrigrams=self._get_ngrams(3, self.tokenizer(last_response, return_tensors="pt")["input_ids"][0])
        self.trigramlists.append(newtrigrams)
        if len(self.trigramlists) > self.shorttermmemory_size :
            self.trigramlists.pop(0)
        
        newquadrigrams=self._get_ngrams(4, self.tokenizer(last_question, return_tensors="pt")["input_ids"][0])
        self.quadrigramlists.append(newquadrigrams)
        if len(self.quadrigramlists) > self.shorttermmemory_size :
            self.quadrigramlists.pop(0)
            
        #hypercontext + context  
        hyperprompt = torch.cat((self.context[0],self.metacontext),1)
        for i in range(1,len(self.context)):
            hyperprompt=torch.cat((hyperprompt, self.context[i]), 1)
       
        usedtrigrams={}
        for trigrams in self.trigramlists:
            usedtrigrams.update(trigrams)
        
        usedquadrigrams={}
        for quadrigrams in self.quadrigramlists:
            usedquadrigrams.update(quadrigrams)
        
        gscent = self.generate_sentences(hyperprompt,prompt,usedtrigrams,usedquadrigrams)
            
            
        return gscent
    
    def free_text_gen(self,prompt):
        #place the burden of indicating context on the user, no memory whatsoever
        inputs = self.tokenizer(prompt, return_tensors="pt")["input_ids"]
        tokenout = self.model.generate(inputs, max_length=len(inputs[0])+self.sequencelength,do_sample=True,top_p=self.topp,temperature=0.7,no_repeat_ngram_size=3)
        sentence=self.tokenizer.decode(tokenout[0])
        return sentence[(len(prompt)-1):]
    
    def _get_ngrams(self,ngram_size: int, gen_output_ids: torch.Tensor):
        gen_tokens = gen_output_ids.tolist()
        generated_ngram = {}
        for ngram in zip(*[gen_tokens[i:] for i in range(ngram_size)]):
                prev_ngram_tuple = tuple(ngram[:-1])
                generated_ngram[prev_ngram_tuple] = generated_ngram.get(prev_ngram_tuple, []) + [ngram[-1]]
        return generated_ngram

    def wipeshorttermmemory(self):
        self.context = []