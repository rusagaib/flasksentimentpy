import pandas as pd
import numpy as np

# convert list formated string to list
import ast

def convert_text_list(texts):
    texts = ast.literal_eval(texts)
    return [text for text in texts]

# =========================================================
# Proses perhitungan tf

def calc_TF(document):
    # Menghitung banyaknya jumlah term dalam satu dokumen kemudian
    # diincrementkan dalam variabel dictionary TF_dict
    TF_dict = {}
    for term in document:
        if term in TF_dict:
            TF_dict[term] += 1
        else:
            TF_dict[term] = 1
    return TF_dict

# =======================================================
def calc_DF(tfDict):
    count_DF = {}
    # Looping pada tiap tf_dict kemudian dari tiap term jumlah dari tf ditampung dalam
    # dictionary and diincrement kan ke dalam variabel dictionary (Count_DF)
    for document in tfDict:
        for term in document:
            if term in count_DF:
                count_DF[term] += 1
            else:
                count_DF[term] = 1
    return count_DF

# =======================================================
# Perhitungan IDF menggunakan jumlah seluruh n dokumen dan seluruh nilai panda
# variabel dictionari DF
def calc_IDF(__n_document, __DF):
    IDF_Dict = {}
    # Untuk tiap term yang ada di dictionari DF dilakukan perhitungan IDF
    for term in __DF:
        IDF_Dict[term] = np.log10(__n_document / __DF[term])
    return IDF_Dict
