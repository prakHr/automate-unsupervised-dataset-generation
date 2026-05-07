import os
import warnings
import logging
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("tensorflow").setLevel(logging.ERROR)
logging.basicConfig(level=logging.ERROR)
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
import inspect
from inspect import getargspec
import numpy as np
import sklearn
import time
import multiprocessing 
from mpire import WorkerPool
from pprint import pprint
from nltk.corpus import wordnet
from transformers import pipeline
import languagemodels as lm

num_cores = max(multiprocessing.cpu_count()//2,1)

unmasker = pipeline("fill-mask", model="bert-base-uncased",framework="pt")


def get_synonyms(query, num_query=10):
    x = "".join(list(query))
    prompt = f"Another word for {x} is [MASK]."

    results = unmasker(prompt, top_k=num_query)

    synonyms = []
    seen = set()

    for r in results:
        word = r["token_str"].strip()
        # Keep only clean alphabetic words
        if word.isalpha() and word.lower() not in seen:
            seen.add(word.lower())
            synonyms.append(word)

    return synonyms


def get_descriptions(query: str):
    description = lm.get_wiki(query)
    return description




def parallel_scraping(query,num_page):
    # Load tokenizer and model
    syn = get_synonyms(query,num_page)
    new_urls = [{"query":syn[i]} for i in range(num_page)]
    with WorkerPool(n_jobs=num_cores) as pool:
        descriptions = pool.map(get_descriptions, new_urls, progress_bar=False)
    # Define the number of labels for your task
    descriptions = [{"texts":[descriptions[i]]} for i in range(len(descriptions)) if descriptions[i]!=""]
    return descriptions



if __name__ == "__main__":
    query = "Artificial Intelligence"
    num_page = 1
    rv = parallel_scraping(query,num_page)
    pprint(rv)

    
    
