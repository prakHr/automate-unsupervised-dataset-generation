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
import hyperopt
import time
import multiprocessing 
from mpire import WorkerPool
from pprint import pprint
from transformers import logging
logging.set_verbosity_error()
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch
from sklearn.model_selection import train_test_split
from hpsklearn import HyperoptEstimator, any_classifier, svc, svc_linear, svc_rbf, svc_poly, svc_sigmoid, liblinear_svc
from hpsklearn import knn, ada_boost, gradient_boosting,random_forest,extra_trees,decision_tree,sgd,xgboost_classification
from hpsklearn import multinomial_nb,gaussian_nb,passive_aggressive,linear_discriminant_analysis,quadratic_discriminant_analysis
from hpsklearn import rbm,colkmeans,one_vs_rest,one_vs_one,output_code
from hyperopt import tpe
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import BertTokenizer, BertModel
import torch
from sklearn.model_selection import train_test_split
from hyperopt import tpe
from hpsklearn import HyperoptEstimator, ada_boost, extra_trees, gaussian_nb, decision_tree
from hpsklearn import quadratic_discriminant_analysis, passive_aggressive, sgd, svc_linear, svc
from hpsklearn import xgboost_classification, gradient_boosting, random_forest, knn, linear_discriminant_analysis
import languagemodels as lm
from nltk.corpus import wordnet
from transformers import pipeline

num_cores = max(multiprocessing.cpu_count()//2,1)

unmasker = pipeline("fill-mask", model="bert-base-uncased",framework="pt")
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
model = BertModel.from_pretrained('bert-base-uncased')

def preprocess_texts(texts):
    inputs = tokenizer(texts, return_tensors='pt', padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)

    sentence_embeddings = outputs.last_hidden_state[:, 0, :]
    sentence_embeddings_np = sentence_embeddings.numpy()
    return sentence_embeddings_np

def train_models(name,classifier,X_train, X_test, y_train, y_test,max_evals=10,trial_timeout=120):
    try:
        estim = HyperoptEstimator(
            classifier=classifier(name),
            algo=tpe.suggest,
            max_evals=max_evals,
            trial_timeout=trial_timeout
        )

        estim.fit(X_train, y_train)

        # Collect results
        my_dict = {
            "best_model": estim.best_model(),
            "best_score": estim.score(X_test, y_test)
        }
        return my_dict
    except Exception as e:
        return {
            "error":str(e)
        }
def apply_ml_example(labelled_dataset,test_size=0.2,max_evals=10,trial_timeout=120):
    
    available_classifier_dict = {
        'AdaBoostClassifier': ada_boost,
        'ExtraTreeClassifier': extra_trees,
        'GaussianNB': gaussian_nb,
    }

    # Extract texts and labels, convert labels to strings
    texts = [labelled_data['texts'][0] for labelled_data in labelled_dataset]
    labels_str = [labelled_data['labels'][0] for labelled_data in labelled_dataset]  # Convert labels to strings
    
    labels_str = list(set(labels_str))
    mapping = {}
    for i in range(len(labels_str)):
        mapping[labels_str[i]] = i
    labels = [mapping[labelled_data['labels'][0]] for labelled_data in labelled_dataset]  #
    X = preprocess_texts(texts)

    X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=test_size)

    results = []
    meta_task = []
    for i, (name, classifier) in enumerate(list(available_classifier_dict.items())):
        my_dict = {}
        my_dict["name"] = name
        my_dict["classifier"] = classifier
        my_dict["X_train"] = X_train
        my_dict["X_test"] = X_test
        my_dict["y_train"] = y_train
        my_dict["y_test"] = y_test
        
        meta_task.append(my_dict)

    for my_dict in meta_task:
        name,classifier=my_dict["name"],my_dict["classifier"]
        results.append(train_models(name,classifier,X_train, X_test, y_train, y_test,max_evals,trial_timeout))
                
    return {"labelled_dataset": labelled_dataset, "results": results}




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

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    framework="pt"
)

def tag_dataset(texts, labels, inference_size):

    text = texts[0]

    result = classifier(
        text,
        candidate_labels=labels
    )

    predicted_label = result["labels"][0]

    return {
        "texts": texts,
        "labels": predicted_label
    }


def parallel_scraping(query,num_page,labels,test_size=0.2,max_evals=10,trial_timeout=120,inference_size="2gb"):
    # Load tokenizer and model
    num_labels = len(labels)  # Example for custom labels: Spam, Not Spam, Promotional
    model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=num_labels)  # Adjust num_labels
    syn = get_synonyms(query,num_page)
    new_urls = [{"query":syn[i]} for i in range(num_page)]
    with WorkerPool(n_jobs=num_cores) as pool:
        descriptions = pool.map(get_descriptions, new_urls, progress_bar=False)
    # Define the number of labels for your task
    
    descriptions = [{"texts":[descriptions[i]],"labels":labels,"inference_size":inference_size} for i in range(len(descriptions)) if descriptions[i]!=""]
    
    with WorkerPool(n_jobs=num_cores) as pool:
        labelled_dataset = pool.map(tag_dataset, descriptions, progress_bar=False)
    return apply_ml_example(labelled_dataset,test_size=test_size,max_evals=max_evals,trial_timeout=trial_timeout)

# if __name__=="__main__":
#     query = "Artificial Intelligence"
#     num_page = 3
#     labels = ["spam","not Spam"]
#     inference_size = "2gb"
#     results = parallel_scraping(query,num_page,labels,inference_size = inference_size)
#     print(results)

    