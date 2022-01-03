import pandas as pd
from math import log, log10

import string
import re #regex library
import os

import nltk_config as nltkdr

import nltk

_npath=nltkdr._nltkdir()
# load nltk data from dir
nltk.data.path.append(_npath+'/resources/punkt')
nltk.data.path.append(_npath+'/resources/stopwords')

# nltk.data.path.append('/home/rusagaib/erhost/sentimenpy/app/resources/punkt')
# nltk.data.path.append('/home/rusagaib/erhost/sentimenpy/app/resources/stopwords')

# print(type(_npath+'/resources/punkt'))


# nltk.download('punkt') #<-- punkuations
# nltk.download('stopwords') #<-- stopword

from nltk.tokenize import word_tokenize
# from nltk.probability import FreqDist

from nltk.corpus import stopwords

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
# import swifter

# hapus unique simbol
def remove_tweet_special(text):
    # hapus tab, new line, ans back slice
    text = text.replace('\\t'," ").replace('\\n'," ").replace('\\u'," ").replace('\\',"")
    # hapus non ASCII (emoticon, chinese word, .etc)
    text = text.encode('ascii', 'replace').decode('ascii')
    # hapus mention, link, hashtag
    text = ' '.join(re.sub("([@#][A-Za-z0-9]+)|(\w+:\/\/\S+)", " ", text).split())
    # hapus incomplete URL
    text = re.sub('http[s]?://\S+', '', text)
    return text

#hapus number
def remove_number(text):
    return  re.sub(r"\d+", "", text)

#hapus punctuation
def remove_punctuation(text):
    return text.translate(str.maketrans("","",string.punctuation))

#hapus whitespace leading & trailing
def remove_whitespace_LT(text):
    return text.strip()

#remove multiple whitespace into single whitespace
def remove_whitespace_multiple(text):
    return re.sub('\s+',' ',text)

# remove single char
def remove_singl_char(text):
    return re.sub(r"\b[a-zA-Z]\b", "", text)

# ====================================================================
# Tokenizing
# NLTK word rokenize
def word_tokenize_wrapper(text):
    return word_tokenize(text)


# =============================================================
# remove stopword

# get stopword indonesia
list_stopwords = stopwords.words('indonesian')

# tambahkan stopword dari Sastrawi
factorysw = StopWordRemoverFactory()
list_stopwords.extend(factorysw.get_stop_words())

# Tambah stopword manual
list_stopwords.extend(['yg', 'dg', 'rt', 'dgn', 'ny', 'd', 'klo',
                       'kalo', 'amp', 'biar', 'bikin', 'bilang',
                       'gak', 'ga', 'krn', 'nya', 'nih', 'sih',
                       'si', 'tau', 'tdk', 'tuh', 'utk', 'ya',
                       'jd', 'jgn', 'sdh', 'aja', 'n', 't', 'p', 'ak',
                       'nyg', 'hehe', 'pen', 'u', 'nan', 'loh', 'rt',
                       '&amp', 'yah'])

# baca file .txt stopword dengan pandas
# txt_stopword = pd.read_csv("stopwords.txt", names= ["stopwords"], header = None)
txt_stopword = pd.read_csv(_npath+"/stopwords.txt", names= ["stopwords"], header = None)

# convert stopword string to list & append additional stopword
list_stopwords.extend(txt_stopword["stopwords"][0].split(' '))


# convert list to dictionary
list_stopwords = set(list_stopwords)

#remove stopword pada list token
def stopwords_removal(words):
    return [word for word in words if word not in list_stopwords]


# =========================================================
# Tahap Proses Normalisasi tiap kata
normalizad_word = pd.read_excel(_npath+"/normalisasi.xlsx")

normalizad_word_dict = {}

for index, row in normalizad_word.iterrows():
    if row[0] not in normalizad_word_dict:
        normalizad_word_dict[row[0]] = row[1]

def normalized_term(document):
    return [normalizad_word_dict[term] if term in normalizad_word_dict else term for term in document]

# ==========================================================
# Steamming kata

# create stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# stemmed
def stemmed_wrapper(term):
    return stemmer.stem(term)

term_dict = {}

def normalize_documents_sastrawi(dataset):
    term_dict = {}

    for document in dataset:
        # term_dict = { term for term in document if term not in term_dict term_dict[term] = ' ' }
        for term in document:
            if term not in term_dict:
                term_dict[term] = ' '

    for term in term_dict:
        term_dict[term] = stemmed_wrapper(term)

    return term_dict
