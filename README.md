<h2>MALKUTH</h2>
discord bot made for the Studiez server. Malkuth is designed with the aim of saving and changing with a server or server cluster's history (for the moment message interactions with the bot, posted images,...).
As such, Malkuth should be self-hosted.


For features that do not concern the current implemented ones (Causal generation with a language model with txtmalk, and image handling with imagemalk), consider looking at the discord.py documentation: https://discordpy.readthedocs.io/
Please refer to each cog (subfolder) for the already implemented features.


You can change the sentencegenerator to sentencegeneratorlocal for a local, significantly smaller version of bloom (which you can also run on windows). 
You can change the model version depending on what your processing capabilities can handle in sentencegenerator.py (see https://huggingface.co/models?other=bloom)


<h6>getting started</h6>


To make use of gpu power, you need an Nvidia card with Cuda enabled. If that's your case, simply add .cuda() after every tokenization as well as after the language model instanciation in sentencegenerator.py
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

