from flask import Flask, request, render_template, session, redirect, url_for
from flaskext.mysql import MySQL
from flask_wtf.csrf import CSRFProtect, CSRFError
from pymysql.cursors import DictCursor
from werkzeug.utils import secure_filename
import os

from config_db import *
# from pwd_hash import validate_pass, cry_pwd
from pwd_hash import validate_pass

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from form import DocumentUploadForm as docup
from form import LoginUserForm as logusr
from testku import text_preprocesing
from preprocesing_text import remove_number
from tf_idf import *
from naive_bayes import *
from genplot import *

# development
assets_dir = assets_dir
# static_folder = os.path.join('static')
# assets_dir = os.path.join('assets')
# resource_dir = os.path.join('resource')
# production
# static_folder = os.path.join('static')
# assets_dir = os.path.join('assets')
# resource_dir = os.path.join('resource')

app = Flask(__name__)

# declare variabel dari config_db.py
database_username = database_username
database_password = database_password
database_ip       = database_ip
database_name     = database_name
secret_key        = secret_key
environment       = env
# server_name       = server_name

# config
app.config['SECRET_KEY'] = secret_key
app.config['FLASK_ENV'] = environment
app.config['UPLOAD_FOLDER'] = assets_dir
# app.config['SERVER_NAME'] = server_name

app.config['MYSQL_DATABASE_USER'] = database_username
app.config['MYSQL_DATABASE_PASSWORD'] = database_password
app.config['MYSQL_DATABASE_DB'] = database_name
app.config['MYSQL_DATABASE_HOST'] = database_ip
app.config['MYSQL_DATABASE_CHARSET'] = "utf8mb4"

app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(hours=3)
# app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=2)
# app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=180)

app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_SECURE=True,
    REMEMBER_COOKIE_HTTPONLY = True,
    SESSION_COOKIE_SAMESITE='Lax',
)
# SESSION_PERMANENT=True

app.config['UPLOAD_EXTENSIONS'] = ['.xlsx']

# inisialisasi variabel instan pada konfigurasi
csrf = CSRFProtect(app)
mysql = MySQL(cursorclass=DictCursor)

# peggunaan instan diterapkan global
csrf.init_app(app)
mysql.init_app(app)

# error handling untuk page 404 dan 500
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    return render_template('500.html'), 400

# route halaman
@app.route('/')
@app.route('/index')
def index():
    if 'loggedin' in session:
        return render_template('index_sentimen.html', username=session['username'])
    return render_template('index.html', title='Login')
    # return redirect('/dashboard/login')
    # return redirect(url_for('login'), code=302)

@app.route('/dashboard/login', methods=['POST','GET'])
def login():

    msg=''
    form = logusr()

    if form.validate_on_submit():
    # if request.method == 'POST' and 'username' in request.form and 'password' in request.form:

        # username = request.form['username']
        # password = cry_pwd(request.form['password'])

        # username = request.form.get("username")
        # password = cry_pwd(request.form.get("password"))
        # validasi_username = form.validate_username(form.username.data)
        # if validasi_username != "valid":
        #     msg=validasi_username
        #     return render_template('index.html', msg=msg, form=form)
        # else:

        _username = form.clean_username(form.username.data)
        _password = form.password.data

        # print(_username)

        query = """select id,username,password from pengguna where username = %s"""
        # query = """select * from pengguna where username = %s"""
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(query, (_username, ))
        data = cursor.fetchone()
        conn.close()

        if data:
            session.pop('loggedin', None)
            session.pop('id', None)
            session.pop('username', None)
            if (validate_pass(str(_password), str(data.get('password'))) == "sukses" ):
                session['loggedin'] = True
                session['id'] = data['id']
                session['username'] = data['username']
                session.permanent = True
                # return redirect(url_for('home'))
                return render_template('index_sentimen.html', username=session['username'])
            else:
                msg = 'Password Salah!'
        else:
            msg = 'Password/Username Salah!'
    return render_template('index.html', msg=msg, form=form)

@app.route('/dashboard/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.clear()
    # Redirect to login page
    # return redirect(url_for('index'))
    # return redirect('/dashboard/login')
    return render_template('index.html')


# route halaman utama
@app.route('/dashboard')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        # return render_template('home.html', username=session['username'])
        return render_template('index_sentimen.html', username=session['username'])
    # User is not loggedin redirect to login page
    # return redirect(url_for('index'))
    return render_template('index.html')

# route halaman about
@app.route('/about')
def about():
    if 'loggedin' in session:
        # User is loggedin show them the home page
        # return render_template('home.html', username=session['username'])
        return render_template('about.html', username=session['username'])
    # User is not loggedin redirect to login page
    # return redirect(url_for('index'))
    # return render_template("about.html")
    return render_template('index.html')

# route sentimen untuk input satuan dari pengguna
# pada testing input manual ini diggunakan dataset 520 dari dataset yang telah dipre-processing
@app.route('/sentimen', methods=['GET','POST'])
def index_sentimen():
    if 'loggedin' in session:

        # data diambil dari database MySQL
        query = """select * from dataset_procesed"""
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        #
        if data:
            df = pd.DataFrame(data)
            # print(df.head())
            df["tweet_list"] = df["tweet_tokens_stemmed"].apply(convert_text_list)
            df["TF_dict"] = df['tweet_list'].apply(calc_TF)

            DF = calc_DF(df["TF_dict"])
            n_document = len(df)
            IDF = calc_IDF(n_document, DF)
            # print(IDF)

            df_kamusdata = pd.DataFrame(list(IDF.items()),columns = ['term','tf'])

            gk = df.groupby('label')
            n_dok = gk.size()
            # print(n_dok)

            df_kamusdata_pos = gk.get_group(1)
            # print(df_kamusdata_pos)
            DF_pos = calc_DF(df_kamusdata_pos["TF_dict"])
            IDF_pos = calc_IDF(n_document, DF_pos)
            df_kamusdata_posnya = pd.DataFrame(list(DF_pos.items()),columns = ['term','tf'])
            df_kamusdata_posnya["idf"] = pd.DataFrame(list(IDF_pos.values()),columns = ['idf'])
            df_kamusdata_posnya["tf_idf_dict"] = df_kamusdata_posnya.tf * df_kamusdata_posnya.idf
            # df_kamusdata_posnya["TF-IDF_dict"].sum()

            df_kamusdata_neg = gk.get_group(0)
            # print(df_kamusdata_neg)
            DF_neg = calc_DF(df_kamusdata_neg["TF_dict"])
            IDF_neg = calc_IDF(n_document, DF_neg)
            df_kamusdata_negnya = pd.DataFrame(list(DF_neg.items()),columns = ['term','tf'])
            df_kamusdata_negnya["idf"] = pd.DataFrame(list(IDF_neg.values()),columns = ['idf'])
            df_kamusdata_negnya["tf_idf_dict"] = df_kamusdata_negnya.tf * df_kamusdata_negnya.idf
            # print(df_kamusdata_negnya.head())
            # df_kamusdata_negnya["TF-IDF_dict"].sum()
        else:
            msg = 'Dataset masih Kosong!'

        if request.method == 'POST':

            response = request.form.get('sentimen')
            response = re.sub(r'[^\w]', ' ', remove_number(response))

            if len(response.strip()) == 0:
                return render_template("index_sentimen.html", score_pos="kosong",  score_neg="kosong", prediksi_nb="kosong", prediksi="kosong", sentimen=False, username=session['username'])
            elif len(response) != 0:

                sentimen=None
                dictme=None
                dictme = {'username':'input','term':response}
                sentimen = pd.DataFrame([dictme])

                pre=text_preprocesing(sentimen['term'], "satuan") # <--- satuan
                unique_term = list(set(pre[0]))
                # # print("unique termnya-------")
                # print(unique_term)
                if len(unique_term) == 0:
                    return render_template("index_sentimen.html", score_pos="kosong",  score_neg="kosong", prediksi_nb="kosong", prediksi="kosong", sentimen=False, username=session['username'])


                prediksi_nb=naive_bayes_once("satuan", unique_term, df_kamusdata_posnya , df_kamusdata_negnya, df_kamusdata)

                score_posneg = score_probnb(prediksi_nb, n_dok.sum(), n_dok[1], n_dok[0])


                if score_posneg["Negatif"] > score_posneg["Positif"]:
                    label_prediksi="Negatif"
                elif score_posneg["Negatif"] < score_posneg["Positif"]:
                    label_prediksi="Positif"
                else:
                    label_prediksi="Sentimen tidak diketahui"

                _uid=session['id']

                if (add_loghistory(response, label_prediksi, _uid) == True):
                    return render_template("index_sentimen.html", username=session['username'], score_pos=score_posneg["Positif"],  score_neg=score_posneg["Negatif"], prediksi_nb=[prediksi_nb.to_html(classes='table', header="true")], prediksi=label_prediksi, sentimen=' '.join(map(str, sentimen['term'].values)))

    # return redirect(url_for('index'))
    return render_template('index.html')


def add_loghistory(sentimen, hasil_label, idusr):
    conn = mysql.connect()
    cursor = conn.cursor()

    # Insert data_preproces
    query = """INSERT INTO
                log_riwayat_testing (
                    datetime,
                    sentimen,
                    hasil_sentimen,
                    user_id)
            VALUES(%s, %s, %s, %s);"""

    now=datetime.now().strftime('%Y-%m-%d %H-%M-%S')

    cursor.execute(query, (now, sentimen, hasil_label, idusr, ))
    conn.commit()
    conn.close()
    return True


# route untuk halaman history
@app.route('/history',methods=['GET'])
def history():
    if 'loggedin' in session:
        _data_history = load_riwayat_testing()
        # print(_data_history)
        if (_data_history != False):
            return render_template('log_history.html',
                                    username=session['username'],
                                    datahistory=_data_history,
                                    msg="sukses")
            # return render_template('log_history.html', username=session['username'], datahistory=_data_history.to_html(classes="table"), msg="sukses")
        else:
            return render_template('log_history.html', username=session['username'], msg=False)

    # return redirect(url_for('index'))
    return render_template('index.html')


def load_riwayat_testing():
    query = """SELECT id, datetime, sentimen, hasil_sentimen, validasi_sentimen FROM log_riwayat_testing"""
    # conn = mysql.connect()
    cursor = mysql.get_db().cursor()
    # cursor = conn.cursor()
    # cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    # data = cursor.fetchone()
    # conn.close()
    cursor.close()
    if data:
        return data
    else:
        return False

# route untuk update log_historty untuk (validasi label)
# @app.route('/history/opt/<string:validasi_sentimen>/<int:i')
@app.route('/history/edit', methods=['POST'])
def edit_histori():
    if 'loggedin' in session:
        id=request.form.get('my_id')
        validasi_sentimen=request.form.get('option')
        # print(type(id))
        # print(id)
        # print(validasi_sentimen)
        msg=''
        try:
            query = "UPDATE log_riwayat_testing SET validasi_sentimen = %s WHERE id = %s" % (validasi_sentimen, int(id))
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            conn.close()
        except Exception as e:
            print(e)

        return redirect(url_for('history',msg="sukses"))

    # return redirect(url_for('index'))
    return render_template('index.html')


# route untuk clear semua loghistory
@app.route('/history/clear-log', methods=['POST'])
def clear_loghistory():
    if 'loggedin' in session:
        query = """DELETE FROM log_riwayat_testing"""
        # print(query)
        query_reset_id = """TRUNCATE TABLE log_riwayat_testing"""
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.execute(query_reset_id)
        conn.commit()
        conn.close()
        return redirect(url_for('history', msg="sukses"))

    # return redirect(url_for('index'))
    return render_template('index.html')


# route untuk halaman dataset
# @app.route('/dataset', methods=['GET', 'POST'])
@app.route('/dataset')
def dataset():
    if 'loggedin' in session:

        _dr=load_dataset_raw()
        _dp=load_dataset_processed()

        if (_dr.empty == True or _dp.empty == True):
            return render_template('dataset.html', username=session['username'])
        else:
            return render_template('dataset.html', username=session['username'], dr=_dr.to_html(classes="table"), dp=_dp.to_html(classes="table"), msg="sukses")

    # return redirect(url_for('index'))
    return render_template('index.html')


def load_dataset_raw():
    query = """SELECT username, tweets, label FROM dataset_raw"""
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    # data = cursor.fetchone()
    conn.close()
    if data:
        df = pd.DataFrame(data, columns=['username','tweets','label'])
        # df.columns = data.keys()
        return df
    else:
        return False

def load_dataset_processed():
    query = """SELECT tweet_tokens_stemmed, label FROM dataset_procesed"""
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    # data = cursor.fetchone()
    conn.close()
    if data:
        df = pd.DataFrame(data, columns=['label','tweet_tokens_stemmed'])
        # df.columns = data.keys()
        return df
    else:
        return False

# route untuk halaman kamus-data
# @app.route('/dataset/')
@app.route('/dataset/kamus-data', methods=['GET','POST'])
def kamusdata():
    if 'loggedin' in session:
        msg=''

        # inisialisasi data
        _df_kamusdata = load_kamus()
        _df_kamusdata_posnya = load_kamus_pos()
        _df_kamusdata_negnya = load_kamus_neg()

        msg='kamus done..'

        # print(_df_kamusdata)
        # print(df_kamusdata_posnya)
        # print(df_kamusdata_negnya)

        # cek if kamus data kosong? (OR)
        if ( _df_kamusdata.empty == True or _df_kamusdata_posnya.empty == True or _df_kamusdata_negnya.empty == True):
            return render_template('kamus_data.html', username=session['username'])

        else:
            return render_template('kamus_data.html',
                                    username=session['username'],
                                    df_kamusdata= _df_kamusdata.to_html(classes="table"),
                                    df_kamusdata_pos= _df_kamusdata_posnya.to_html(classes="table"),
                                    df_kamusdata_neg= _df_kamusdata_negnya.to_html(classes="table"),
                                    msg=msg)

    # User is not loggedin redirect to login page
    # return redirect(url_for('index'))
    return render_template('index.html')


def load_kamus():
    # query = """SELECT term, df, idf FROM kamus_data_all"""
    query = """SELECT term, df, idf FROM kamus_data_all"""
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    if data:
        df = pd.DataFrame(data, columns=['term','df','idf'])
        return df
    else:
        return False

def load_kamus_pos():
    query = """SELECT term, tf, idf, tf_idf_dict FROM kamus_positif"""
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    if data:
        df = pd.DataFrame(data, columns=['term','tf','idf','tf_idf_dict'])
        return df
    else:
        return False


def load_kamus_neg():
    query = """SELECT term, tf, idf, tf_idf_dict FROM kamus_negatif"""
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(query)
    cursor.commit()
    data = cursor.fetchall()
    # data = cursor.fetchone()
    conn.close()
    if data:
        df = pd.DataFrame(data, columns=['term','tf','idf','tf_idf_dict'])
        # print(df.head())
        # df.columns = data.keys()
        return df
    else:
        return False

# route untuk halaman data training dan testing
# @app.route('/dataset/')
@app.route('/dataset/train-testing', methods=['GET','POST'])
def train_tes():
    if 'loggedin' in session:
        # msg=""

        # Buata kursor koneksi ke mysql
        # conn = mysql.connect()
        # cursor = conn.cursor()

        # load dataset
        _train = load_train()
        _test = load_tes()

        # print(_train)
        # print(_test)

        msg="traintest done.."

        if ( _train.empty == True or _test.empty == True ):
            return render_template('train_tes.html', username=session['username'])

        else:
            # conn.close()
            return render_template('train_tes.html',
                                    username=session['username'],
                                    train= _train.to_html(classes="table"),
                                    test= _test.to_html(classes="table"),
                                    msg=msg)

    # User is not loggedin redirect to login page
    # return redirect(url_for('index'))
    return render_template('index.html')


def load_train():
    query = """SELECT label, tweet_tokens_stemmed as tweet_list FROM dataset_training"""
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(query)
    cursor.commit()
    data = cursor.fetchall()
    # data = cursor.fetchone()
    conn.close()
    if data:
        df = pd.DataFrame(data, columns=['label','tweet_list'])
        # print("\n inside load train()")
        # print(df.head())
        # df.columns = data.keys()
        return df
    else:
        return False

def load_tes():
    query = """SELECT label, tweet_tokens_stemmed as tweet_list FROM dataset_tes"""
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(query)
    cursor.commit()
    data = cursor.fetchall()
    # data = cursor.fetchone()
    conn.close()
    if data:
        df = pd.DataFrame(data, columns=['label','tweet_list'])
        # print(df.head())
        # df.columns = data.keys()
        return df
    else:
        return False

# route untuk halaman uji testing
# @app.route('/dataset/')
@app.route('/dataset/uji-testing', methods=['GET','POST'])
def testing():
    if 'loggedin' in session:

        msg=""
        # train = pd.DataFrame(load_train(), columns=["label","tweet_tokens_stemmed"])
        # test = pd.DataFrame(load_tes(), columns=["label","tweet_tokens_stemmed"])

        # load data
        _dataset = load_dataset_processed()
        _train = load_train()
        _test = load_tes()
        _kamusdata = load_kamus_all()
        _kamusdata_pos = load_kamus_pos()
        _kamusdata_neg = load_kamus_neg()

        if (_dataset.empty == True or _train.empty == True or _test.empty == True or _kamusdata.empty == True or _kamusdata_neg.empty == True or _kamusdata_pos.empty == True):
            return render_template('uji_testing.html', username=session['username'])

        else:
            dataset = pd.DataFrame(_dataset, columns=["label"])
            train = pd.DataFrame(_train, columns=["label","tweet_list"])
            test = pd.DataFrame(_test, columns=["label","tweet_list"])
            df_kamusdata = pd.DataFrame(_kamusdata, columns=["term","df","idf"])
            df_kamusdata_posnya = pd.DataFrame(_kamusdata_pos, columns=['term','tf','idf','tf_idf_dict'])
            df_kamusdata_negnya = pd.DataFrame(_kamusdata_neg, columns=['term','tf','idf','tf_idf_dict'])

            # dict_kamus_pos = df_kamusdata_pos[['term','tf_idf_dict']].to_dict()

            # print("train")
            # print(train.head())
            # print("tes")
            # print(test.head())
            # print("kamus data")
            # print(df_kamusdata.head())
            # print("kamus data Positif")
            # print(df_kamusdata_posnya.head())
            # print("kamus data Negatif")
            # print(df_kamusdata_negnya.head())

            # train["tweet_list"] = train["tweet_tokens_stemmed"].astype(str).apply(convert_text_list)
            # test["tweet_list"] = test["tweet_tokens_stemmed"].astype(str).apply(convert_text_list)

            datahasil = {}
            datahasil = naive_bayes(test, train, df_kamusdata_posnya, df_kamusdata_negnya, df_kamusdata)
            # print(datahasil.head())

            show = pd.DataFrame(datahasil)

            show['Label_Prediksi'] = show['Label_Prediksi'].replace({'Negatif': 0, 'Positif':1})

            show["label_asal"]=[x for x in test["label"]]
            # print(show)

            df_matrik = pd.DataFrame(show, columns=['label_asal','Label_Prediksi'])
            # print(df_matrik)
            # df_matrik = pd.DataFrame(show, columns=['y_Actual','y_Predicted'])

            confusion_matrix = pd.crosstab(df_matrik['label_asal'], df_matrik['Label_Prediksi'], rownames=['Actual'], colnames=['Predicted'])
            # print(confusion_matrix)

            # buat visualisasi data
            diagram_dataset_pie=piechart(dataset)
            kemunculan_kata=barchart(df_kamusdata[["term","df"]])
            # kemunculan_kata=barchart(df_kamusdata[["term","df"]])
            # word_cloud_neg=get_wordcloud(df_kamusdata_negnya)
            word_cloud_pos=get_wordcloud(dict(df_kamusdata_posnya[['term','tf_idf_dict']].values))
            word_cloud_neg=get_wordcloud(dict(df_kamusdata_negnya[['term','tf_idf_dict']].values))


            msg="test done.."

            return render_template('uji_testing.html',
                                    username=session['username'],
                                    show=show.to_html(classes="table"),
                                    confusion_matrix=confusion_matrix.to_html(classes="table"),
                                    akurasi=round(akurasi(confusion_matrix), 2) * 100,
                                    barJSON=kemunculan_kata,
                                    pieJSON=diagram_dataset_pie,
                                    img_data_pos=word_cloud_pos,
                                    img_data_neg=word_cloud_neg,
                                    msg=msg)

    # User is not loggedin redirect to login page
    # return redirect(url_for('index'))
    return render_template('index.html')


def load_dataset_proces():
    query = """SELECT label FROM dataset_procesed"""
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    # data = cursor.fetchone()
    conn.close()
    if data:
        df = pd.DataFrame(data, columns=['label'])
        # print("\n inside load train()")
        # print(df.head())
        # df.columns = data.keys()
        return df
    else:
        return False

def load_train():
    query = """SELECT label, tweet_tokens_stemmed as tweet_list FROM dataset_training"""
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    # data = cursor.fetchone()
    conn.close()
    if data:
        df = pd.DataFrame(data, columns=['label','tweet_list'])
        # print("\n inside load train()")
        # print(df.head())
        # df.columns = data.keys()
        return df
    else:
        return False

def load_tes():
    query = """SELECT label, tweet_tokens_stemmed as tweet_list FROM dataset_tes"""
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    # data = cursor.fetchone()
    conn.close()
    if data:
        df = pd.DataFrame(data, columns=['label','tweet_list'])
        # print(df.head())
        # df.columns = data.keys()
        return df
    else:
        return False

def load_kamus_all():
    query = """SELECT term, df, idf FROM kamus_data_all"""
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    # data = cursor.fetchone()
    conn.close()
    if data:
        df = pd.DataFrame(data, columns=['term','df','idf'])
        # print(df.head())
        # df.columns = data.keys()
        return df
    else:
        return False

def load_kamus_pos():
    query = """SELECT term, tf, idf, tf_idf_dict FROM kamus_positif"""
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    # data = cursor.fetchone()
    conn.close()
    if data:
        df = pd.DataFrame(data, columns=['term','tf','idf','tf_idf_dict'])
        # print(df.head())
        # df.columns = data.keys()
        return df
    else:
        return False


def load_kamus_neg():
    query = """SELECT term, tf, idf, tf_idf_dict FROM kamus_negatif"""
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    # data = cursor.fetchone()
    conn.close()
    if data:
        df = pd.DataFrame(data, columns=['term','tf','idf','tf_idf_dict'])
        # print(df.head())
        # df.columns = data.keys()
        return df
    else:
        return False


# route untuk halaman upload dataset (.xlsx)
# @app.route('/dataset/')
# @app.route('/dataset/inputdataset')
@app.route('/dataset/inputdataset', methods=['GET','POST'])
def input_dataset():
    if 'loggedin' in session:

        username = session.get('username')
        # password = cry_pwd(request.form.get("password"))

        query = """select username,password from pengguna where username = %s"""
        # query = """select * from pengguna where username = %s"""
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(query, (username, ))
        data = cursor.fetchone()
        conn.close()

        if data:
            form = docup()
            msg=''

            if form.validate_on_submit():

                d = form.document.data

                docname = secure_filename(d.filename)

                # save file document di server
                d.save( os.path.join(app.config['UPLOAD_FOLDER'], docname))
                # d.save( str(app.config['UPLOAD_FOLDER']), docname )
                print("upload sukses")

                # print(str(app.config['UPLOAD_FOLDER']+'/'+docname))

                # _dataFileUrl = r""+str(app.config['UPLOAD_FOLDER'])+"/"+docname
                # print(_dataFileUrl)

                # ef = pd.read_excel(app.config['UPLOAD_FOLDER']+'/'+docname)
                # print(ef.head())
                # ef = pd.read_excel(app.config['UPLOAD_FOLDER']+"\\"+docname, sep=",")

                data_path = os.path.join(app.config['UPLOAD_FOLDER'], docname)


                ef = pd.read_excel(data_path)
                filename_raw = pd.DataFrame(ef, columns=['username','tweets','label'])

                # print(filename_raw)

                if(load_kedb(filename_raw, len(filename_raw)) == "sukses"):

                    filename_raw['label'] = filename_raw['label'].replace({'negatif': 0, 'positif':1})

                    # preprocess mulai
                    filename_raw["tweet_tokens_stemmed"] = text_preprocesing(filename_raw, "data-520")
                    # filename_raw["tweet_list"] = filename_raw["tweet_tokens_stemmed"].apply(convert_text_list)
                    # pre["tweet_list"] = pre["tweet_tokens_stemmed"].astype(str).apply(convert_text_list)

                    filename_raw["tweet_list"] = filename_raw["tweet_tokens_stemmed"].astype(str).apply(convert_text_list)
                    # bagi dataset train & testing
                    train = filename_raw.sample(frac=0.8, random_state=100)
                    # train = filename_raw.sample(frac=0.8)
                    test = filename_raw[~filename_raw.index.isin(train.index)]

                    # Pembobotan tf-idf train
                    train["TF_dict"] = train['tweet_list'].apply(calc_TF)
                    DF = calc_DF(train["TF_dict"])
                    # print(len(DF))
                    n_document = len(train)
                    IDF = calc_IDF(n_document, DF)

                    df_kamusdata = pd.DataFrame(list(IDF.items()),columns = ['term','idf'])
                    df_kamusdata['df'] = pd.DataFrame(list(DF.values()), columns = ['df'])
                    # print(df_kamusdata['idf'].head())
                    # print(df_kamusdata.head())
                    # df_kamusdata['idf'].sum()

                    gk = train.groupby('label')
                    n_dok = gk.size()
                    # print(n_dok)

                    df_kamusdata_pos = gk.get_group(1)
                    DF_pos = calc_DF(df_kamusdata_pos["TF_dict"])
                    IDF_pos = calc_IDF(n_document, DF_pos)
                    df_kamusdata_posnya = pd.DataFrame(list(DF_pos.items()),columns = ['term','tf'])
                    df_kamusdata_posnya["idf"] = pd.DataFrame(list(IDF_pos.values()),columns = ['idf'])
                    df_kamusdata_posnya["TF-IDF_dict"] = df_kamusdata_posnya.tf * df_kamusdata_posnya.idf
                    # df_kamusdata_posnya["TF-IDF_dict"].sum()

                    df_kamusdata_neg = gk.get_group(0)
                    DF_neg = calc_DF(df_kamusdata_neg["TF_dict"])
                    IDF_neg = calc_IDF(n_document, DF_neg)
                    df_kamusdata_negnya = pd.DataFrame(list(DF_neg.items()),columns = ['term','tf'])
                    df_kamusdata_negnya["idf"] = pd.DataFrame(list(IDF_neg.values()),columns = ['idf'])
                    df_kamusdata_negnya["TF-IDF_dict"] = df_kamusdata_negnya.tf * df_kamusdata_negnya.idf
                    # df_kamusdata_negnya["TF-IDF_dict"].sum()

                    # prepare table insert (delete)
                    pre_loaddata('dataset_procesed')
                    pre_loaddata('dataset_training')
                    pre_loaddata('dataset_tes')
                    pre_loaddata('kamus_data_all')
                    pre_loaddata('kamus_positif')
                    pre_loaddata('kamus_negatif')

                    conn = mysql.connect()
                    cursor = conn.cursor()

                    # Insert data_preproces
                    query = """INSERT INTO
                                dataset_procesed (
                                    label,
                                    tweet_tokens_stemmed)
                            VALUES(%s, "%s");"""

                    i=0
                    while i < len(filename_raw):
                        cursor.execute(query, (filename_raw['label'].iloc[i], filename_raw['tweet_tokens_stemmed'].iloc[i]))
                        conn.commit()
                        i+=1

                    # Insert data Training & Testing
                    # Insert data_preproces
                    query = """INSERT INTO
                                dataset_tes (
                                    label,
                                    tweet_tokens_stemmed)
                            VALUES(%s, "%s");"""

                    i=0
                    while i < len(test):
                        cursor.execute(query, (test['label'].iloc[i], test['tweet_list'].iloc[i]))
                        conn.commit()
                        i+=1


                    # Insert data Training & Testing
                    # Insert data_preproces
                    query = """INSERT INTO
                                dataset_training (
                                    label,
                                    tweet_tokens_stemmed)
                            VALUES(%s, "%s");"""

                    i=0
                    while i < len(train):
                        cursor.execute(query, (train['label'].iloc[i], train['tweet_list'].iloc[i]))
                        conn.commit()
                        i+=1



                    # Insert kamus_data_all
                    query = """INSERT INTO
                                kamus_data_all (
                                    term,
                                    df,
                                    idf)
                            VALUES(%s, %s, %s);"""

                    i=0
                    while i < len(df_kamusdata):
                        cursor.execute(query, ( df_kamusdata['term'][i], df_kamusdata['df'][i], df_kamusdata['idf'][i], ))
                        conn.commit()
                        i+=1


                    # Insert kamus_positif
                    query = """INSERT INTO
                                kamus_positif (
                                    term,
                                    tf,
                                    idf,
                                    tf_idf_dict)
                            VALUES(%s, %s ,%s ,%s);"""

                    conn = mysql.connect()
                    cursor = conn.cursor()

                    i=0
                    while i < len(df_kamusdata_posnya):
                        cursor.execute(query, (df_kamusdata_posnya['term'][i], df_kamusdata_posnya['tf'][i], df_kamusdata_posnya['idf'][i], df_kamusdata_posnya['TF-IDF_dict'][i], ))
                        conn.commit()
                        i+=1


                    # Insert kamus_negatif
                    query = """INSERT INTO
                                kamus_negatif (
                                    term,
                                    tf,
                                    idf,
                                    tf_idf_dict)
                            VALUES(%s ,%s ,%s,%s);"""

                    conn = mysql.connect()
                    cursor = conn.cursor()

                    i=0
                    while i < len(df_kamusdata_negnya):
                        cursor.execute(query, (df_kamusdata_negnya['term'][i], df_kamusdata_negnya['tf'][i], df_kamusdata_negnya['idf'][i], df_kamusdata_negnya['TF-IDF_dict'][i], ))
                        conn.commit()
                        i+=1

                    conn.close()

                    msg="Data berhasil ditambahkan.."

                return redirect(url_for('dataset', username=session['username'], msg=msg))

        return render_template('dataset_upload.html', username=session['username'], form=form, msg=msg)

    # return redirect(url_for('index'))
    return render_template('index.html')


def pre_loaddata(table):
    query = "DELETE FROM `{}`;".format(table)
    # print(query)
    query_reset_id = "TRUNCATE TABLE `{}`;".format(table)
    conn = mysql.connect()
    cursor = conn.cursor()
    # cursor.execute(query, query_reset_id)
    # cursor.execute(query, (table, ))
    # print(query, format(table,))

    # cursor.execute(query, (table,))
    cursor.execute(query)
    conn.commit()
    cursor.execute(query_reset_id)
    conn.commit()
    conn.close()
    return True

def load_kedb(data, jumTot):
    temp_dat=pd.DataFrame(data, columns=["username","tweets","label"])
    # print('inside function....')
    # print(dump)
    dataset_raw='dataset_raw'
    if(pre_loaddata(dataset_raw)==True):
        query = """INSERT INTO
                    dataset_raw (
                        username,
                        tweets,
                        label)
                VALUES (%s,%s,%s);"""

        conn = mysql.connect()
        cursor = conn.cursor()

        i=0
        while i < jumTot:
            cursor.execute(query, (temp_dat['username'][i], str(temp_dat['tweets'][i]), temp_dat['label'][i], ))
            conn.commit()
            i+=1

        conn.close()
        return "sukses"
    else:
        return "gagal"
    # return True


if __name__ == '__main__':
    # app.run(debug = True)
    app.run()
    # app.run(host=os.getenv('IP', 'localhost'),
    #         port=int(os.getenv('PORT', 5000)),
    #         threaded=True)
