# MALKUTH
discord bot powered by Bloom-Petals with memory augmentation powered by large-camembert-sentence and stanford-nlp

#getting started
-required python packages:
transformers
sentence-transformers
scipy
stanza
scikit-image
petals #NOT COMPATIBLE WITH WINDOWS DISTRIBUTIONS
numba
tqdm
numpy

-download and place large-camembert-sentence (https://huggingface.co/dangvantuan/sentence-camembert-large) into ./sentence directory
(either manually or via transformers-model.save)

seam-carving algorithm as presented by Karthik Karanth here:
https://karthikkaranth.me/blog/implementing-seam-carving-with-python/


Main file for discord interaction is bot.py 

