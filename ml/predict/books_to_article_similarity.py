import json 
import pandas as pd 
import pprint
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

def get_top_5_books_to_article(book, article_preprocessed_abstract):
    # Combine all books abstracts with the article's abstract in one dataset
    corpus_abstract = pd.DataFrame(book['abstract_preprocessed'])
    corpus_abstract.loc[-1] = article_preprocessed_abstract # add article's abstract at the end of the corpus
    corpus_abstract = corpus_abstract.reset_index(drop=True)

    # Compute Tdidf
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus_abstract['abstract_preprocessed']) # return a document-term matrix
 
    # Computation of Cosine similarity. The higher the cosim value, the more similar the elements are. 
    cosim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    cosim = pd.DataFrame(cosim)
    cosim_article = cosim.tail(1)
    # Select the last row of the cosine matrix which represents the artcile cosine values to each books summary.
    cosim_article_sort = cosim_article.iloc[-1,:].sort_values(ascending = False)

    top_5_books = cosim_article_sort[1:6]
    top_5_books = pd.DataFrame(top_5_books)
    top_5_books.columns = ['cosine']
    top_5_books = top_5_books.reset_index()
    top_5_books = pd.merge(book, top_5_books, how='inner', on='index')
    columns = ['title', 'author', 'publisher']
    top_5_books = top_5_books[columns]
    top_5_books = top_5_books.to_json(orient='records', lines=False, indent=4)
    return top_5_books

################# A Remplacer par la connexion à la DB pour accéder à books #################
os.chdir('/Users/anavekua/Documents/DataScienTest/nyt_news')
file_paths = "data/bestsellers_with_abstract_and_genre_3350.json"
with open(file_paths, 'r') as file:
        data = json.load(file)
book = pd.DataFrame(data)

# Remove N/A category and select 'Politics & Current Events'
book = book[(book['genre'] != 'N/A') & (book['genre'] == 'Politics & Current Events')]
book = book.reset_index(drop=True)
book = book.reset_index(drop = False)
book['abstract_preprocessed'] = None
col_index = book.columns.get_loc('abstract_preprocessed')

# Loop through each abstract, preprocess it, transform list in string, update the DataFrame
for index, abstract in enumerate(book['abstract']):
    abstract_preprocessed = preprocessing_abstract(abstract)
    string = ' '.join([str(item)for item in abstract_preprocessed])
    book.iloc[index, col_index] = string

################# A Remplacer par un article reçu via l'api #################
article = {
            "_id": {
                "$oid": "664c81164444e18089255a0c"
            },
            "uri": "nyt://article/cc29805e-55c9-5902-a308-50be425e9b99",
            "abstract": "Despite right-wing bluster to the contrary, there really is a war on women, and the Republicans are the aggressors.",
            "web_url": "https://takingnote.blogs.nytimes.com/2012/04/13/wars-imagined-and-real/",
            "snippet": "Despite right-wing bluster to the contrary, there really is a war on women, and the Republicans are the aggressors.",
            "lead_paragraph": "Politicians are always declaring a “war” on something. Often the conflict is entirely in their imaginations– like the War on Christmas and the War on Religion. Sometimes it’s a label designed to lend a sense of urgency to a problem they are not going to fix – like the War on Poverty and the War on Drugs.",
            "headline_main": "Wars: Imagined and Real",
            "headline_kicker": "Taking Note",
            "pub_date": "2012-04-13T17:02:30+0000",
            "document_type": "article",
            "section_name": "Opinion",
            "subsection_name": "null",
            "byline": "By Andrew Rosenthal",
            "keywords": [
                "Presidential Election of 2012",
                "Women's Rights",
                "Romney, Ann",
                "Rosen, Hilary"
            ],
            "election_year": 2012,
            "election_date": {
                "$date": "2012-11-06T00:00:00.000Z"
            }
            }

#preprocessing article
article_preprocessed_abstract = preprocessing_abstract(article['abstract'])
article_preprocessed_abstract = ' '.join([str(item)for item in article_preprocessed_abstract])

# get top 5 books
top_5_books = get_top_5_books_to_article(book, article_preprocessed_abstract)
print(top_5_books)