# MALKUTH
discord bot powered by Bloom-Petals with memory augmentation powered by large-camembert-sentence and stanford-nlp

#getting started
-required python packages:
transformers
sentence-transformers
scipy
stanza
scikit-image
petals
numba
tqdm
numpy

-download and place large-camembert-sentence (https://huggingface.co/dangvantuan/sentence-camembert-large) into ./sentence directory
(either manually or via transformers-model.save)

note: seam-carving is a patented algorithm , thus not present in the repository. The expected method should follow the algorithm as presented by Karthik Karanth here:
https://karthikkaranth.me/blog/implementing-seam-carving-with-python/
