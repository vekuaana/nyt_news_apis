from connection_db import MongoDBConnection
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
import logging

from api_nyt import NYTConnector
import configparser
from config import api_nyt_path
import ScrapperAppleBooks as sc

# Lists from which books are retrieved 
non_fiction_book_lists = [
    {
        'list_name': 'paperback-nonfiction',
        'start_date': '2008-06-08',
        'end_date': '2011-02-13'
    },
    {
        'list_name': 'combined-print-and-e-book-nonfiction',
        'start_date': '2011-02-20',
        'end_date': '2011-06-20'
    },
    {
        'list_name': 'hardcover-political-books',
        'start_date': '2011-07-01',
        'end_date': '2011-11-01' # error avec 2011-12-01
    },
    {
       'list_name': 'hardcover-political-books',
        'start_date': '2012-01-01',
        'end_date': '2012-03-01' 
    },
    {
        'list_name': 'combined-print-and-e-book-nonfiction',
        'start_date': '2012-04-01',
        'end_date': '2012-06-20'
    },
    {
        'list_name': 'hardcover-political-books',
        'start_date': '2012-07-01',
        'end_date': '2015-07-01' #error avec 2015-08-01
    },
    {
        'list_name': 'hardcover-political-books',
        'start_date': '2015-09-01', 
        'end_date': '2016-12-01' 
    },
    {
        'list_name': 'combined-print-and-e-book-nonfiction',
        'start_date': '2017-01-01',
        'end_date': '2024-06-18'
    }
]


class Injector_books(NYTConnector):

    def __init__(self):
        try:
            # Attempt to connect to MongoDB within a container environment
            self.db = MongoDBConnection('mongodb').conn_db
        except ServerSelectionTimeoutError:
            # Handle the case where the connection times out if we try to connect outside the container
            print("Try to connect outside the container with localhost")
            self.db = MongoDBConnection('localhost').conn_db
        except OperationFailure as of:
            print(of)

        cfg = configparser.ConfigParser()
        cfg.read(api_nyt_path)
        self.API_KEY = cfg.get('KEYS', 'key_nyt_news')

# ajuster api_nyt pour pouvoir retirer cette fonction
    def add_bestsellers_to_list(self, response, books, unique_titles):
            # Save the number of books of the entire list
            num_books = response['num_results']

            # List of the 20 first NYT bestselling books of the list requested
            books_list = response['results']['books']

            for book in books_list:
                title = book["title"]

                if title not in unique_titles:
                    applebooks_url = None  # Handle the case when no apple links are provided
                    buy_links = book.get('buy_links', [])  # Get the 'buy_links' list or an empty list if not present
                    for link in buy_links:
                        if link.get('name') == 'Apple Books':
                            applebooks_url = link.get('url')

                    new_book = {
                        "title": book["title"],
                        "author": book["author"],
                        "publisher": book["publisher"],
                        "book_uri": book["book_uri"],
                        "buy_links": applebooks_url
                    }

                    books.append(new_book)
                    unique_titles.append(title)

            return books, unique_titles
    
    def add_bestsellers_to_db(self, response):
        # List of the 20 first NYT bestselling books of the list requested
        books_list = response['results']['books']
        scraper = sc.AppleBooksScraper()

        try:
            for book in books_list:
                # Check if the book is already in the database using 'book_uri' instead of 'title'
                if not self.db['book'].find_one({'book_uri': book['book_uri']}):
                    # Initialize applebooks_url to None in case no Apple Books link is found
                    applebooks_url = None
                    # Get the 'buy_links' list or an empty list if not present
                    buy_links = book.get('buy_links', [])
                    for link in buy_links:
                        if link.get('name') == 'Apple Books':
                            applebooks_url = link.get('url')
                            try:
                                scraper.open_apple_books_link(applebooks_url)
                                book_name, author_name, genre_name, summary_text = scraper.extract_book_information()
                                book['genre'] = genre_name
                                book['abstract'] = summary_text
                            except Exception as e:
                                logging.error(f"Error extracting information from Apple Books: {e}")
                                book['genre'] = None
                                book['abstract'] = None
                            break  # Exit the loop 

                    # Create a new book entry
                    new_book = {
                        "title": book["title"],
                        "author": book["author"],
                        "publisher": book["publisher"],
                        "book_uri": book["book_uri"],
                        "buy_links": applebooks_url,
                        "genre": book['genre'],
                        "abstract": book['abstract']
                    }

                    # Insert the new book into the database
                    self.db['book'].insert_one(new_book)
                    logging.info(f"Book added to database: {new_book['title']} by {new_book['author']}")

        except Exception as e:
            logging.error(f"Error adding books to database: {e}")
            return {'status': 'error', 'message': str(e)} 

injector = Injector_books()

for idx, list in enumerate(non_fiction_book_lists):
 list_name = list['list_name']
 start_date = list['start_date']
 end_date = list['end_date']
 published_dates, books, unique_titles = injector.request_bestsellers(non_fiction_book_lists[idx]['list_name'], non_fiction_book_lists[idx]['start_date'], non_fiction_book_lists[idx]['end_date'], injector.add_bestsellers_to_list, injector.add_bestsellers_to_db)
