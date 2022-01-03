from math import log, sqrt
import pandas as pd
import numpy as np
import re
from testku import select_unique as unique
from tf_idf import *


# perhitungan akurasi menggunakan confusion_matrix
def akurasi(confusion_matrix):
    return (confusion_matrix.iloc[0][0]+confusion_matrix.iloc[1][1]) / (confusion_matrix.iloc[0][0]+confusion_matrix.iloc[0][1]+confusion_matrix.iloc[1][0]+confusion_matrix.iloc[1][1])

# perhitungan posterior probability
def score_probnb(data, n_dok, n_jumpos, n_jumneg):
    # perkalian semua score di dataframe
    score_tot_neg =  np.prod(np.array(data["negatif"]))
    score_tot_pos =  np.prod(np.array(data["positif"]))

    # print(score_tot_neg)
    # print("{:.7f}".format(score_tot_neg))
    # print(score_tot_pos)
    # print("{:.7f}".format(score_tot_pos))

    # perhitungan prior probability untuk label positif dan negatif
    # jum_positif/jum_dokumen dan jum_negatif/jum_dokumen

    # perhitungan posterior probability
    # perhitungan score positif = jum_positif/jum_dokumen x score_pos1 x score_pos2 x ... x n_score_pos
    # perhitungan score negatif = jum_negatif/jum_dokumen x score_neg1 x score_neg2 x ... x n_score_neg

    # hasil variabel skor disini merupakan hasil dari perhitungan posterior probability
    score={
        "Positif": (n_jumpos/n_dok) * score_tot_pos,
        "Negatif": (n_jumneg/n_dok) * score_tot_neg
        # formating ke decimal contoh: (8 / 14) x 0.005807 x 0.005807
        # harusnya hasilnya 0.00001926928 atau 1.92692851×10^−5
        # saat di python otomatis menjadi bilangan komplek 3.371725658015813e-05
        # maka digunakan formating menggunakan "{:.7f}".format(number) menjadi 0.0000193
        # sumber https://www.kite.com/python/answers/how-to-suppress-scientific-notation-in-python
        # "Positif": "{:.20f}".format((n_jumpos/n_dok) * score_tot_pos),
        # "Negatif": "{:.20f}".format((n_jumneg/n_dok) * score_tot_neg)
    }
    return score

# hitung conditional probability
def hitung_bayes(found,n_tfidf,n_totaltfidf,total_idf):
    if found == "true":
        return ((n_tfidf+1) / ((n_totaltfidf)+total_idf))
    elif found == "false":
        return ( 1 / ((n_totaltfidf)+total_idf))


def naive_bayes(test, train, kamus_pos, kamus_neg, idf_all):
    print("proses naive bayes (many)")

    # data train
    df_train = pd.DataFrame(train, columns=["label","tweet_list"])
    # print(df_train)

    # data tes
    df_files = pd.DataFrame(test, columns=["label","tweet_list"])
    # print(df_files)

    df_files['tweet_list'] = df_files['tweet_list'].apply(ast.literal_eval).tolist()
    df_files['unique_term'] = df_files['tweet_list'].apply(unique)
    # print(df_files['unique_term'])

    ds_kamus_pos = pd.DataFrame(kamus_pos, columns=["term", "tf_idf_dict"])
    ds_kamus_neg = pd.DataFrame(kamus_neg, columns=["term", "tf_idf_dict"])
    ds_kamus_all = pd.DataFrame(idf_all, columns=["term", "idf"])
    jml_idf_all = ds_kamus_all["idf"].sum()

    gk = df_train.groupby('label')
    n_dok = gk.size()

    # negatif = 0 dan positif = 1
    n_dok, n_jumpos, n_jumneg = n_dok.sum(), n_dok[1], n_dok[0]

    datahasil={}

    x = 0
    while x < len(df_files):
        n_label_prediksi={}
        n_hasil_nb = naive_bayes_once("satuan", df_files['unique_term'].iloc[x], ds_kamus_pos , ds_kamus_neg, ds_kamus_all)
        # print(n_hasil_nb)
        n_score_nb = score_probnb(n_hasil_nb, n_dok, n_jumpos, n_jumneg)
        # print(n_score_nb)

        if n_score_nb["Negatif"] > n_score_nb["Positif"]:
            n_label_prediksi[x]="Negatif"
        else:
            n_label_prediksi[x]="Positif"

        datahasil[x] = {
            "Negatif": n_score_nb["Negatif"],
            "Positif": n_score_nb["Positif"],
            "Label_Prediksi": n_label_prediksi[x]
        }

        n_hasil_nb = None
        n_score_nb = None
        n_label_prediksi = None
        x+=1

    # print(len(datahasil.keys()))
    datahasil_final=pd.DataFrame(columns=["Negatif","Positif","Label_Prediksi"])
    x=0
    while x < len(datahasil.keys()):
        datahasil_final.loc[x] = datahasil[x]["Negatif"], datahasil[x]["Positif"], datahasil[x]["Label_Prediksi"]
        x+=1
    return datahasil_final


def naive_bayes_once(mode, files, kamus_pos, kamus_neg, idf_all):
    # read dataset
    df_files = pd.DataFrame(files, columns=["term"])
    ds_kamus_pos = pd.DataFrame(kamus_pos, columns=["term", "tf_idf_dict"])
    ds_kamus_neg = pd.DataFrame(kamus_neg, columns=["term", "tf_idf_dict"])
    ds_kamus_all = pd.DataFrame(idf_all, columns=["term", "idf"])

    jml_idf_all = ds_kamus_all["idf"].sum()

    if mode == "satuan":
        positif, negatif = {}, {}

        for j,term in enumerate(df_files["term"]):
            # Positif
            for i,kata in enumerate(ds_kamus_pos['term']):
                if term == kata:
                    positif[term] = hitung_bayes("true", ds_kamus_pos["tf_idf_dict"][i], ds_kamus_pos["tf_idf_dict"].sum(), jml_idf_all)
                    break
                elif term != kata :
                    positif[term] = hitung_bayes("false", 0, ds_kamus_pos["tf_idf_dict"].sum(), jml_idf_all)

            # Negatif
            for i,kata in enumerate(ds_kamus_neg['term']):
                if term == kata:
                    negatif[term] = hitung_bayes("true", ds_kamus_neg["tf_idf_dict"][i], ds_kamus_neg["tf_idf_dict"].sum(), jml_idf_all)
                    break
                elif term != kata :
                    negatif[term] = hitung_bayes("false", 0, ds_kamus_neg["tf_idf_dict"].sum(), jml_idf_all)

        df_files["negatif"] = df_files["term"].map(negatif)
        df_files["positif"] = df_files["term"].map(positif)

    else:
        print("data kosong!!")
        pass

    return df_files
