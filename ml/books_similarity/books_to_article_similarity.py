import json 
import pandas as pd 
import pprint
import re
import multiprocessing as mp
import numpy as np
import pandas as pd
import nltk
nltk.download('stopwords', quiet=True)
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Il reste des moodifications à apporter en fonction du format des données d'entrée

def text_cleaning(text): 
    import re 
    # Remove #1 from, for exemple, #1 NATIONAL BESTSELLER
    remove_hastag1 = re.sub(r'\#\d', '', text)
    # Remove all numbers 
    remove_numbers = re.sub(r'\d+', '', remove_hastag1)
    # Regular expression to match fully uppercase words and words containing uppercase letters
    remove_full_upper = re.sub(r'\b[A-Z]+\b', '', remove_numbers)
    # lowercasing
    lowercased_text = remove_full_upper.lower()
    # remove everything that is not a word character (including letters, digits and underscore) or a blank space. 
    remove_punctuation = re.sub(r'[^\w\s]', '', lowercased_text)
    # Remove any sequence of one or more white space by one white space. Removes white spaces at begining and end of word. It also removes '\xa0', Unicode for non-breaking space. 
    remove_white_space = re.sub(r'\s+', ' ', remove_punctuation).strip()

    return (remove_white_space)

def tokenization(text_clean):
    # Tokenization = Breaking down each text into words put in an array based on blank spaces.
    from nltk.tokenize import word_tokenize
    tokenized_text = word_tokenize(text_clean)
    return tokenized_text

def remove_stop_words(abstract_token):
# Stop Words/filtering = Removing irrelevant words
    from nltk.corpus import stopwords
    stopwords = set(stopwords.words('english'))
    stopwords_removed = [word for word in abstract_token if word not in stopwords]
    return stopwords_removed

# Stemming = Transforming words into their base form
def stemming(abstract_stop_words):
    from nltk.stem import PorterStemmer
    ps = PorterStemmer()
    stemmed_text = [ps.stem(word) for word in abstract_stop_words]
    return stemmed_text

def preprocessing_abstract(abstract):
    """
    Clean text abstract for TF-IDF computation.

    Args:
        abstract (str): abstract of the book or the article
    
    Returns:
        List: A list of words
    """
    abstract_clean = text_cleaning(abstract)
    abstract_token = tokenization(abstract_clean)
    abstract_stop_words = remove_stop_words(abstract_token) 
    abstract_stemming = stemming(abstract_stop_words)
    return abstract_stemming

def TFIDF_computation(corpus_books_article):
    """
    Return the TF-IDF matrix of the dataset combining books and the article preprocessed abstracts. 
    Args:
        corpus_books_article (dataframe): A dataframe containing books and article preprocessed abstracts

    Retuns:
        TF-IDF matrix (matrix)
    """
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus_books_article['abstract_preprocessed']) # return a document-term matrix

    # Get words 
    feature_names = vectorizer.get_feature_names_out()
    # Combine corpus with the weighted word matrix by creating 'id' index and merge
    corpus_books_article['id'] = range(0, len(corpus_books_article))
    df_tfidf_prev = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)
    df_tfidf_prev['id'] = range(0, len(df_tfidf_prev))
    df_tfidf = pd.merge(corpus_books_article, df_tfidf_prev, on='id')
    return df_tfidf

def cosine_similarity_article_to_books(tfidf_matrix):
    """
    Return the cosine similarity between the article preprocessed abstract and books abstracts. 
    Args:
        TF-IDF matrix (matrix)

    Retuns:
        A row # à modifier
    """
    # Computation of Cosine similarity. The higher the cosim value, the more similar the elements are. 
    cosim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    cosim = pd.DataFrame(cosim)
    cosim_article = cosim.tail(1)
    # Select the last row of the cosine matrix which represents the artcile cosine values to each books summary.
    cosim_artile_sort = cosim_article.iloc[-1,:].sort_values(ascending = False)
    return cosim_artile_sort

def get_top_5_books_to_article(cosim_artile_sort)
    """
    Return the top 5 books that are the most similar to an article. 
    Args:

    Retuns:

    """
    # Select the 5 books that are the most similare to the article
    top_5_books = cosim_artile_sort[1:6]
    top_5_books = pd.DataFrame(top_5_books)
    top_5_books.columns = ['cosine']
    top_5_books = top_5_books.reset_index()
    corpus_books = corpus_books.reset_index()
    # Display the top 5 most similar books to the article
    top_5_books_info = pd.merge(corpus_books, top_5_books, how='inner', on='index')
    return top_5_books_info.head(5) # a changer en json