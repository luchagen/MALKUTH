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

    def __init__(self, ngram_size: int, memquottoken, min_logits: float = -1e8):
        if not isinstance(ngram_size, int) or ngram_size <= 0:
            raise ValueError(f"`ngram_size` has to be a strictly positive integer, but is {ngram_size}")
        self.ngram_size = ngram_size
        self.memquottoken = memquottoken
        self.min_logits = min_logits
        self.past_tokens = None
        
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        num_batch_hypotheses = scores.shape[0]
        cur_len = input_ids.shape[-1]
        banned_batch_tokens = self._calc_banned_ngram_tokens(self.ngram_size, input_ids, num_batch_hypotheses, cur_len,self.memquottoken)

        for i, banned_tokens in enumerate(banned_batch_tokens):
            scores[i, banned_tokens] = -float("inf")

        return scores
    
    def _get_ngrams(self,ngram_size: int, prev_input_ids: torch.Tensor, num_hypos: int, memquottoken):
        generated_ngrams = [{} for _ in range(num_hypos)]
        for idx in range(num_hypos):
            gen_tokens = prev_input_ids[idx].tolist()
            gen_tokens= []
            record=True
            for item in prev_input_ids[idx]:
                if item == memquottoken and record ==True:
                    record = False
                elif item == memquottoken and record == False:
                    record = True
                if record ==True:
                    gen_tokens.append(item.item())
                
            #gen_tokens = gen_tokens.tolist()
            generated_ngram = generated_ngrams[idx]
            for ngram in zip(*[gen_tokens[i:] for i in range(ngram_size)]):
                prev_ngram_tuple = tuple(ngram[:-1])
                generated_ngram[prev_ngram_tuple] = generated_ngram.get(prev_ngram_tuple, []) + [ngram[-1]]
        return generated_ngrams


    def _get_generated_ngrams(self,banned_ngrams, prev_input_ids, ngram_size, cur_len):
        # Before decoding the next token, prevent decoding of ngrams that have already appeared
        start_idx = cur_len + 1 - ngram_size
        ngram_idx = tuple(prev_input_ids[start_idx:cur_len].tolist())
        return banned_ngrams.get(ngram_idx, [])


    def _calc_banned_ngram_tokens(
        self, ngram_size: int, prev_input_ids: torch.Tensor, num_hypos: int, cur_len: int, memquottoken
    ) -> List[Iterable[int]]:
        """Copied from fairseq for no_repeat_ngram in beam_search"""
        if cur_len + 1 < ngram_size:
            # return no banned tokens if we haven't generated no_repeat_ngram_size tokens yet
            return [[] for _ in range(num_hypos)]

        generated_ngrams = self._get_ngrams(ngram_size, prev_input_ids, num_hypos, memquottoken)

        banned_tokens = [
            self._get_generated_ngrams(generated_ngrams[hypo_idx], prev_input_ids[hypo_idx], ngram_size, cur_len)
            for hypo_idx in range(num_hypos)
        ]
        return banned_tokens
    
   

    
class SentenceGenerator():
    tokenizer = AutoTokenizer.from_pretrained("bigscience/bloom-560m",cache_dir="./models")
    model = AutoModelForCausalLM.from_pretrained("bigscience/bloom-560m",cache_dir="./models").cuda()
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
    metacontext=tokenizer("Malkuth, une intelligence artificielle, échange avec des humains par messagerie électronique instantanée. ", return_tensors="pt")["input_ids"].cuda()
    context=[] #old messages stored as tokens
    memquottoken=[] #token that delimit memories, for use in a repetition constraint
    
    
    def __init__(self, sentencesperquery:int,sequencelength:int,shorttermmemory_size:int,topp:float,topk:int):
        self.sentencesperquery=sentencesperquery #number of sentences generated for memory-based choice
        self.sequencelength=sequencelength #max length of a response in tokens
        self.topp=topp #top p sampling 
        self.topk=topk #top k sampling (not used)
        self.shorttermmemory_size=shorttermmemory_size #size of the memory of the inference session in number of messages
        
        #We autodetect the end of message detection tokens
        a= self.tokenizer(" ?",return_tensors="pt")["input_ids"].cuda()
        self.stoptokens.append(a[-1][-1])
        a= self.tokenizer("?",return_tensors="pt")["input_ids"].cuda()
        self.stoptokens.append(a[-1][-1])
        a= self.tokenizer("keter?",return_tensors="pt")["input_ids"].cuda()
        self.stoptokens.append(a[-1][-1])
        a= self.tokenizer(" !",return_tensors="pt")["input_ids"].cuda()
        self.stoptokens.append(a[-1][-1])
        a= self.tokenizer("!",return_tensors="pt")["input_ids"].cuda()
        self.stoptokens.append(a[-1][-1])
        a= self.tokenizer("keter!",return_tensors="pt")["input_ids"].cuda()
        self.stoptokens.append(a[-1][-1])
        a= self.tokenizer(" .",return_tensors="pt")["input_ids"].cuda()
        self.stoptokens.append(a[-1][-1])
        a= self.tokenizer(".",return_tensors="pt")["input_ids"].cuda()
        self.stoptokens.append(a[-1][-1])
        a= self.tokenizer("keter.",return_tensors="pt")["input_ids"].cuda()
        self.stoptokens.append(a[-1][-1])
        
        #we search for markers of a memory information
        memquot= self.tokenizer(' "',return_tensors="pt")["input_ids"].cuda()
        self.memquottoken=memquot[-1][-1]
        
        self.logitsprocessors = logits_process.LogitsProcessorList()
        self.logitsprocessors.append(NoRepeatNGramWMemLogitsProcessor(3,self.memquottoken))
        self.stopcriteria = stopping_criteria.StoppingCriteriaList()
        self.stopcriteria.append(StopWordCriteria(self.stoptokens))
        
    def generate_sentences(self,context,prompt: str):
            inpts = self.tokenizer(prompt, return_tensors="pt")["input_ids"].cuda()
            inputs=torch.cat((context, inpts), 1) #add inpts to context to run inference
            sentences=[]
            
            
            for i in range(self.sentencesperquery):
                tokenout = self.model.generate(inputs, max_length=len(inputs[0])+self.sequencelength,do_sample=True,top_p=self.topp,early_stopping=True,temperature=0.7,no_repeat_ngram_size=3,logits_processor=self.logitsprocessors,stopping_criteria=self.stopcriteria,eos_token_id=2)
                sentence=self.tokenizer.decode(tokenout[0][len(context[0]):])
                sentenceb=prompt
                j=len(prompt)
                
                #The sentence generation has a tendency to add unnecessary quotes,
                #and to generate a full dialogue rather than just one response, so we used to add delimiters.
                #we keep those in case the model refuses to stop generation wen constrained to do it (petals).
                #(note , perhaps the end of sentence delimiters might sometimes cut the answer too short)
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
                
                
                #print(sentenceb)
                
            return(sentences)
    
    #we take in a fonction that tokenises and memorises the tokens of past discussions,
    #for generation to take immediate past sentences into account without regenerating the tokens
    def inference_session(self,prompt: str,last_response: str):
        #generate tokens for interaction n-1
        self.context.append(self.tokenizer(last_response+" \n ", return_tensors="pt")["input_ids"].cuda())
        
        if len(self.context)>self.shorttermmemory_size:
            self.context.pop(0)
        
        #hypercontext + context  
        hyperprompt = torch.cat((self.context[0],self.metacontext),1)
        for i in range(1,len(self.context)):
            hyperprompt=torch.cat((hyperprompt, self.context[i]), 1)
        
        gscent = self.generate_sentences(hyperprompt,prompt)
        
        return gscent
    
    def free_text_gen(self,prompt):
        #place the burden of indicating context on the user, no memory whatsoever
        inputs = self.tokenizer(prompt, return_tensors="pt")["input_ids"].cuda()
        tokenout = self.model.generate(inputs, max_length=len(inputs[0])+self.sequencelength,do_sample=True,top_p=self.topp,temperature=0.7,no_repeat_ngram_size=3)
        sentence=self.tokenizer.decode(tokenout[0])
        return sentence[(len(prompt)-1):]
        