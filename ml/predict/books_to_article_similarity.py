import json 
import pandas as pd 
import re
import os
import multiprocessing as mp
import numpy as np
import pandas as pd
import nltk
nltk.download('stopwords', quiet=True)
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from connection_db import MongoDBConnection
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

def get_books():

    try:
            # Attempt to connect to MongoDB within a container environment
            db = MongoDBConnection('mongodb').conn_db
    except ServerSelectionTimeoutError:
            # Handle the case where the connection times out if we try to connect outside the container
            print("Try to connect outside the container with localhost")
            try:
                db = MongoDBConnection('localhost').conn_db
            except ServerSelectionTimeoutError as sste:
                print("Unable to connect to database. Make sure the tunnel is still active.")
                print(sste)
                return sste
    except OperationFailure as of:
            print(of)
            return of

    book = list(db['book'].find())
    book = pd.DataFrame(book)

    # Remove N/A category and select 'Politics & Current Events'
    book = book[(book['genre'] != 'N/A') & (book['genre'] == 'Politics & Current Events')]
    book = book.reset_index(drop=True)
    book = book.reset_index(drop = False)
    book['abstract_preprocessed'] = None

    return book

def text_cleaning(text): 
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

def get_top_3_books_to_article(abstract):

    book = get_books()
    col_index = book.columns.get_loc('abstract_preprocessed')
        # Loop through each abstract, preprocess it, transform list in string, update the DataFrame
    for index, abstract_book in enumerate(book['abstract']):
            abstract_preprocessed = preprocessing_abstract(abstract_book)
            string = ' '.join([str(item)for item in abstract_preprocessed])
            book.iloc[index, col_index] = string

    article_preprocessed_abstract = preprocessing_abstract(abstract)
    article_preprocessed_abstract = ' '.join([str(item)for item in article_preprocessed_abstract])
    article_preprocessed_abstract

        # Combine all books abstracts with the article's abstract in one dataset
    corpus_abstract = pd.DataFrame(book['abstract_preprocessed'])
    corpus_abstract.loc[-1] = article_preprocessed_abstract # add article's abstract at the end of the corpus
    corpus_abstract = corpus_abstract.reset_index(drop=True)
    corpus_abstract

        # Compute Tdidf
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus_abstract['abstract_preprocessed'])

        # Computation of Cosine similarity. The higher the cosim value, the more similar the elements are. 
    cosim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    cosim = pd.DataFrame(cosim)
    cosim_article = cosim.tail(1)
        # Select the last row of the cosine matrix which represents the artcile cosine values to each books summary.
    cosim_article_sort = cosim_article.iloc[-1,:].sort_values(ascending = False)

    top_3_books = cosim_article_sort[1:4]
    top_3_books = pd.DataFrame(top_3_books)
    top_3_books.columns = ['cosine']
    top_3_books

    top_3_books = top_3_books.reset_index()
    top_3_books = pd.merge(book, top_3_books, how='inner', on='index')
    columns = ['title', 'author', 'publisher']
    top_3_books = top_3_books[columns]
    top_3_books = top_3_books.to_json(orient='records', lines=False, indent=4)
    top_3_books

    return top_3_books


if __name__ == "__main__":
    abstract = 'President-elect Trump has vowed to cancel the Paris climate accord, jeopardizing what scientists say is a critical 3.6-degree irreversible temperature target. ract = In 1914 a room full of German schoolboys, fresh-faced and idealistic, are goaded by their schoolmaster to troop off to the ‘glorious war’. With the fire and patriotism of youth they sign up. What follows is the moving story of a young ‘unknown soldier’ experiencing the horror and disillusionment of life in the trenches.'
    books = get_top_3_books_to_article(abstract)
    print(books)


