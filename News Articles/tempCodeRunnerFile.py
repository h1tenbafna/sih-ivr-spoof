import os
import random
import string
from nltk import word_tokenize
from nltk import FreqDist
from collections import defaultdict
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
import pickle

stop_words=set(stopwords.words('english'))
stop_words.add('said')
stop_words.add('mr')

BASE_DIR= 'C:/Users/keval/Downloads/BBC News Summary/News Articles'
LABELS=['business','entertainment','politics','sport','tech']

def create_data_set():
    with open('data.txt','w',encoding='utf8') as outfile:
         for label in LABELS:
            dir='%s/%s' % (BASE_DIR,label)
            for filename in os.listdir(dir):
                fullfilename='%s/%s' % (dir,filename)
                print(fullfilename)
                with open(fullfilename,'rb') as file:
                    text = file.read().decode(errors='replace').replace('\n','')
                    outfile.write('%s\t%s\t%s\n' % (label,filename,text))


def setup_docs():
     docs=[]#(label,text)
     with open('data.txt','r',encoding='utf8')as datafile:
         for row in datafile:
             parts = row.split('\t')
             doc = (parts[0],parts[2].strip())
             docs.append(doc)
     return docs



def clean_text(text):
    #remove punctuation
    text=text.translate(str.maketrans('','',string.punctuation))
    #convert to lower case
    text=text.lower()
    return text

def get_tokens(text):
    #get individual words
    tokens = word_tokenize(text)
    #remove common words that are useless
    tokens=[t for t in tokens if not t in stop_words]
    return tokens


def print_frequency_dist(docs):
    tokens=defaultdict(list)
    #lets makeagiant list of all the words for each category
    for doc in docs:
        doc_label = doc[0]
        doc_text = clean_text(doc[1])
        doc_tokens = get_tokens(doc_text)
        tokens[doc_label].extend(doc_tokens)
        #doc_text=clean_text(doc[1])
        #doc_tokens=get_tokens(doc_text)
        #tokens[doc_label].extend(doc_tokens)
    for category_label,category_tokens in tokens.items():
        print(category_label)
        fd=FreqDist(category_tokens)
        print(fd.most_common(20))

def get_splits(docs):
    #scramble docs
    random.shuffle(docs)
    X_train=[]#training documents
    y_train=[]#corresponding training labels
    X_test=[]#test documents
    y_test=[]#correspoding test label
    pivot = int(.80 * len(docs))
    for i in range(0,pivot):
         X_train.append(docs[i][1])
         y_train.append(docs[i][0])