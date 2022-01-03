from preprocesing_text import *

def select_unique(text):
    return pd.Series(text).unique()

# preprosesing menggunakan fungsi yang ada pada preprocesing_text
def text_preprocesing(dataset, mode):
    if mode == "satuan":
        df = pd.DataFrame(list(dataset.items()), columns = ['username','tweets'])

        df['tweets'] = df['tweets'].astype(str)

        df['tweets'] = df['tweets'].str.lower()

        df['tweets'] = df['tweets'].apply(remove_tweet_special)

        df['tweets'] = df['tweets'].apply(remove_number)

        df['tweets'] = df['tweets'].apply(remove_punctuation)

        df['tweets'] = df['tweets'].apply(remove_whitespace_LT)

        df['tweets'] = df['tweets'].apply(remove_whitespace_multiple)

        df['tweets'] = df['tweets'].apply(remove_singl_char)

        df['tweets_tokenizing'] = df['tweets'].apply(word_tokenize_wrapper)

        df['tweet_tokens_WSW'] = df['tweets_tokenizing'].apply(stopwords_removal)

        df['tweet_normalized'] = df['tweet_tokens_WSW'].apply(normalized_term)

        term_dict = normalize_documents_sastrawi(df['tweet_normalized'])

        def get_stemmed_term(document):
            return [term_dict[term] for term in document]

        df['tweet_tokens_stemmed'] = df['tweet_normalized'].apply(get_stemmed_term)
        # df['tweet_tokens_stemmed'] = df['tweet_normalized'].swifter.apply(get_stemmed_term)

        # print(df['tweet_tokens_stemmed'])

    else:
        df = pd.DataFrame(dataset, columns=['label','tweets'])

        df['tweets'] = df['tweets'].astype(str)

        df['tweets'] = df['tweets'].str.lower()

        df['tweets'] = df['tweets'].apply(remove_tweet_special)

        df['tweets'] = df['tweets'].apply(remove_number)

        df['tweets'] = df['tweets'].apply(remove_punctuation)

        df['tweets'] = df['tweets'].apply(remove_whitespace_LT)

        df['tweets'] = df['tweets'].apply(remove_whitespace_multiple)

        df['tweets'] = df['tweets'].apply(remove_singl_char)

        df['tweets_tokenizing'] = df['tweets'].apply(word_tokenize_wrapper)

        print("please wait...")

        df['tweet_tokens_WSW'] = df['tweets_tokenizing'].apply(stopwords_removal)

        df['tweet_normalized'] = df['tweet_tokens_WSW'].apply(normalized_term)

        term_dict = normalize_documents_sastrawi(df['tweet_normalized'])

        def get_stemmed_term(document):
            return [term_dict[term] for term in document]

        df['tweet_tokens_stemmed'] = df['tweet_normalized'].apply(get_stemmed_term)
        # df['tweet_tokens_stemmed'] = df['tweet_normalized'].swifter.apply(get_stemmed_term)
        # print(df['tweet_tokens_stemmed'])

    return df['tweet_tokens_stemmed']
