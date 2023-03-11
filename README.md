<h2>MALKUTH</h2>
discord bot powered by Bloom-Petals with memory augmentation powered by large-camembert-sentence and stanford-nlp


This branch in particular is powered by a local, significantly smaller version of bloom. 


You can change the model version depending on what your processing capabilities can handle in sentencegenerator.py (see https://huggingface.co/models?other=bloom)
<h6>getting started</h6>


You need a cuda enabled graphics card for the code to run as is. If that's not your case, delete every mention of .cuda() in sentencegenerator.py
> required python packages:
>  - transformers
>  - sentence-transformers
>  - scipy
>  - stanza
>  - scikit-image
>  - numba
>  - tqdm
>  - numpy

-download and place large-camembert-sentence (https://huggingface.co/dangvantuan/sentence-camembert-large) into ./sentence directory
(either manually or via transformers.model.save)

seam-carving algorithm as presented by Karthik Karanth here:
https://karthikkaranth.me/blog/implementing-seam-carving-with-python/


Main file for discord interaction is bot.py 

