# coding: utf-8

import requests
import configparser
import time
import json
import math
import datetime
import os
from datetime import datetime
import re
import logging.config
import yaml
from dotenv import load_dotenv, find_dotenv

from config import PACKAGE_ROOT
import ScrapperAppleBooks as sc


with open(PACKAGE_ROOT + os.sep + 'config_logger.yaml', 'rt') as f:
    config = yaml.safe_load(f.read())

load_dotenv(find_dotenv())

logging.config.dictConfig(config)
logger = logging.getLogger(__name__)

# Base URLs for NYT APIs
BASE_URL = "https://api.nytimes.com/svc/"
BASE_URL_NEWSWIRE = BASE_URL + "news/v3/content"
BASE_URL_BOOKS = BASE_URL + "books/v3"
BASE_URL_KW = BASE_URL + "search/v2/articlesearch.json"
BASE_URL_MOST_POPULAR = BASE_URL + "mostpopular/v2/"
BASE_URL_ARCHIVE = BASE_URL + "archive/v1/"

# Regex to clean file names by removing problematic char
CLEAN_FILE_NAME_REGEX = re.compile(r'[:.\s]')


class NYTConnector:
    """
    A class to connect to the NYT API and fetch various types of data.
    """

    def __init__(self):
        """
        Initializes the NYTConnector by reading the API key from a configuration file.
        """
        self.API_KEY = os.getenv('NYT_API_KEY')

    def request_times_newswire(self,
                               source: str = 'all',
                               section: str = 'u.s.',
                               subsection: str = '2024 Elections',
                               per_facet: list = ["Biden, Joseph R Jr", "Trump, Donald J"]):
        """
        Fetches data from the NYT Newswire API for a given source and section.

        Args:
            source (str): The source of the news (e.g., 'all', 'nyt', 'inyt').
            section (str): The news section (e.g., 'science', 'sport', 'u.s.').
            subsection (str): The news subsection (e.g., 'Politics', '2024 Elections).
            per_facet (list): The list of main candidates for the 2024 us elections

        Returns:
            dict: A JSON response containing the newswire data.
        """

        params = {"api-key": self.API_KEY}

        # Construct the endpoint with the source and section
        url = f"{BASE_URL_NEWSWIRE}/{source}/{section}.json"

        # Send the HTTP GET request to the API and get the JSON response
        response = requests.get(url, params=params)
        logger.info(response)
        response_json = requests.get(url, params=params).json()
        num_results = response_json.get('num_results', 0)
        logging.info("Number of results:" + str(num_results))

        results = response_json.get('results', [])

        # If results exist, filter with subsection and person entity
        filtered_results = []
        if results:
            logging.info('api_nyt')
            logging.info(results)
            filtered_results = [doc for doc in results if doc["subsection"] == subsection
                                or (set(doc["per_facet"]).intersection(set(per_facet)))]
            logger.info("Number of filtered results:", len(filtered_results))

        return filtered_results

    def request_by_keyword(self, keyword: str, output_file: str, start_date: str = None, end_date: str = None):
        """
        Fetches NYT articles based on a keyword, with optional start and end dates.

        Args:
            keyword (str): The search keyword.
            output_file (str): The base name for the output file.
            start_date (str, optional): The start date for the search in 'yyyymmdd' format.
            end_date (str, optional): The end date for the search in 'yyyymmdd' format.

        Returns:
            list: A list of NYT articles that match the keyword search.
        """

        search_params = {
            "q": keyword,
            "api-key": self.API_KEY,
            "begin_date": start_date,
            "end_date": end_date
        }

        # Send the initial request to get the total number of hits
        r = requests.get(BASE_URL_KW, params=search_params)
        response = r.json()['response']
        hits = response['meta']['hits']
        logger.info("Number of hits:", hits)

        # Determine the number of pages (10 results per page)
        num_pages = int(math.ceil(hits / 10))
        logger.info("Number of pages:", num_pages)

        list_docs = []

        # Iterate through all pages to fetch the documents
        with open(f"{output_file}_{start_date}.json", 'w', encoding='utf-8') as f:
            for i in range(num_pages):
                logger.info(f"Fetching page {i}")
                search_params['page'] = i
                r = requests.get(BASE_URL_KW, params=search_params)
                response = r.json()['response']

                # Get docs from the current page
                docs = response.get('docs', [])
                list_docs.extend(docs)

                # According to NYT FAQ, sleep 12 seconds between requests to avoid rate limits
                time.sleep(12)
            json.dump(list_docs, f, ensure_ascii=False, indent=4)

        return list_docs

    def request_bestsellers_list(self):
        """
        Fetches the name and informations of all the NYT Best Sellers lists. 

        Returns:
            A dict containing all NYT Best Sellers lists and their informations.
        """
        params = {"api-key": self.API_KEY}
        # Build the endpoint URL for fetching book lists
        url = f"{BASE_URL_BOOKS}/lists/names.json"

        # Generate an output file name
        output_file_name = f"data_all_NYT_best_sellers_lists_.json"

        # Send the HTTP GET request and get the JSON response
        response = requests.get(url, params=params).json()

        # If response, save them to the output file
        if response:
            with open(output_file_name, 'w', encoding='utf-8') as f:
                json.dump(response, f, ensure_ascii=False, indent=4)

        return response

    def request_bestsellers(self, list_name, start_date, end_date):
        """
        This function retrieves the unique bestsellers books of the NYT of a specific list over a specified period and
        save it in a JSON file.

        Args :
            list_name : The name of the list to be fetch.
            start_date : The starting date for the retrieval of books.
            end_date : The end date for the retrieval of books.

        Retruns:
            A list of the published dates the loop when through.
            A list of NYT best sellers from the starting date until the end date.

        """
        date_format = '%Y-%m-%d'
        end_date_obj = datetime.strptime(end_date, date_format)
        next_published_date = start_date  # Inital date to start fetching the books.
        next_published_date_obj = datetime.strptime(start_date, date_format)  # Inital date to start fetching the books.

        unique_titles = []  # List of unique book titles
        published_dates = []  # List of the published date the loop went through.
        books = []  # List to store books

        while next_published_date_obj <= end_date_obj:

            # Build the endpoint URL for fetching the book list.
            url = f"{BASE_URL_BOOKS}/lists/{next_published_date}/{list_name}.json"

            counter_request = 1  # Initial number of requests.
            total_request_iteration = 1  # Initial number of requests iterations of the same list
            offset = 0  # Start reading the book list from the first book in the list

            while counter_request <= total_request_iteration:

                # Set request parameters
                params = {"api-key": self.API_KEY, "offset": str(offset)}

                # Send the HTTP GET request and get the JSON response
                response = requests.get(url, params=params).json()

                # Save the number of books of the entire liste
                num_books = response['num_results']

                # List of the 20th first NYT bestselling books of the list requested.
                books_list = response['results']['books']

                for book in books_list:

                    title = book["title"]

                    # if the title is not in the list of unique title, add the book to the books list
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

                total_request_iteration = math.ceil(num_books / 20)  # The total number of request calls needed
                counter_request += 1  # Increase the request counter
                offset += 20  # Add 20 to the offset to query the next 20 books

                # According to NYT FAQ, sleep 12 seconds between requests to avoid rate limits
                time.sleep(12)

            next_published_date = response['results']['next_published_date']  # Get the publication date of the next list
            if next_published_date:
                published_dates.append(next_published_date)

            next_published_date_obj = datetime.strptime(next_published_date, date_format)

        # If books were retrieved, save the list to the output file
        last_published_date = published_dates[-2]
        output_file_name = f"bestsellers_{list_name}_from_{start_date}_to_{last_published_date}.json"

        if books:
            with open(output_file_name, 'w', encoding='utf-8') as f:
                json.dump(books, f, ensure_ascii=False, indent=4)

        return published_dates, books
    
    def add_books_genre_and_abstract(self, books_list):
        """
        This function adds the book's abstract and the books's genre to the books list by scraping data from AppleBook.
        
        Args: 
        - books_list: a list of books. Each book must contain their AppleBook url. 
        
        Return: 
        - A list of books with their genre and abstract. 
        """
        scraper = sc.AppleBooksScraper()
        book_count = 0

        for book in books_list:
            url = book['buy_links']
            scraper.open_apple_books_link(url)
            book_name, author_name, genre_name, summary_text = scraper.extract_book_information()
            book['genre'] = genre_name
            book['abstract'] = summary_text
            book_count += 1
        
        output_file_name = f"bestsellers_with_abstract_and_genre_{book_count}"
        with open(output_file_name, 'w', encoding='utf-8') as f:
                json.dump(books_list, f, ensure_ascii=False, indent=4)

        return books_list


if __name__ == "__main__":
    nyt_c = NYTConnector()
    res = nyt_c.request_times_newswire('all', 'u.s.')
    # nyt_c.request_weelkly_nonfiction_bestsellers_books('05', '08', '2020')
    # nyt_c.request_most_popular(30)
    # nyt_c.request_by_keyword('Presidential Election of 2024', 'data_us_election', '20240508', '20240512')
    # nyt_c.request_bestsellers_list()

    # file_paths = "data/merged_nonfiction_bestsellers.json"
    # with open(file_paths, 'r') as file:
    #         data = json.load(file)
    #
    # new_list = nyt_c.add_books_genre_and_abstract(data)


