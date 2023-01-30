<h2>MALKUTH</h2>
discord bot powered by Bloom-Petals with memory augmentation powered by large-camembert-sentence and stanford-nlp

<h6>getting started</h6>


> required python packages:
>  - transformers
>  - sentence-transformers
>  - scipy
>  - stanza
>  - scikit-image
>  - petals #NOT COMPATIBLE WITH WINDOWS DISTRIBUTIONS
>  - numba
>  - tqdm
>  - numpy

-download and place large-camembert-sentence (https://huggingface.co/dangvantuan/sentence-camembert-large) into ./sentence directory
(either manually or via transformers.model.save)

note: seam-carving is a patented algorithm , thus not present in the repository. The expected method should follow the algorithm as presented by Karthik Karanth here: <br>
https://karthikkaranth.me/blog/implementing-seam-carving-with-python/


Main file for discord interaction is bot.py 

