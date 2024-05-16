# coding: utf-8

import requests
import configparser
import time
import json
import math
import datetime
import re
from pprint import pprint

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
        cfg = configparser.ConfigParser()
        cfg.read('api.cfg')
        self.API_KEY = cfg.get('KEYS', 'key_nyt_news')

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

        # Generate an output file name for saving the data
        now = datetime.datetime.now()  # Get the current time
        section_clean = CLEAN_FILE_NAME_REGEX.sub('', section)
        output_file_name = f"data_news_wire_{section_clean}_{now.strftime('%Y%m%d%H%M%S')}.json"

        # Send the HTTP GET request to the API and get the JSON response
        response = requests.get(url, params=params).json()
        num_results = response.get('num_results', 0)
        print("Number of results:", num_results)

        results = response.get('results', [])

        # If results exist, save them to the output file
        if results:
            filtered_results = [doc for doc in results if doc["subsection"] == subsection
                                or (set(doc["per_facet"]).intersection(set(per_facet)))]
            with open(output_file_name, 'w', encoding='utf-8') as f:
                json.dump(filtered_results, f, ensure_ascii=False, indent=4)

        return results

    def request_most_popular(self, period_of_time: int):
        """
        Fetches the most popular NYT articles for a given time period.

        Args:
            period_of_time (int): The number of days for which to fetch popular articles.

        Returns:
            list: A list of the most popular articles.
        """
        params = {"api-key": self.API_KEY}
        # Build the endpoint URL for fetching the most popular articles
        url = f"{BASE_URL_MOST_POPULAR}/viewed/{period_of_time}.json"

        # Get the current date and the date from "period_of_time" days ago
        now = datetime.datetime.now()
        days_before = now - datetime.timedelta(days=period_of_time)

        # Create a clean output file name based on the time period
        start_date_str = CLEAN_FILE_NAME_REGEX.sub('', str(days_before))
        end_date_str = CLEAN_FILE_NAME_REGEX.sub('', str(now))
        output_file_name = f"data_most_popular_{start_date_str}_{end_date_str}.json"

        # Send the HTTP GET request and get the JSON response
        response = requests.get(url, params=params).json()
        num_results = response.get('num_results', 0)
        print("Number of results:", num_results)

        results = response.get('results', [])

        # If results exist, save them to the output file
        if results:
            with open(output_file_name, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)

        return results

    def request_archive(self, month: int, year: int):
        """
        Fetches the archived NYT articles for a given month and year.

        Args:
            month (int): The month for which to fetch articles.
            year (int): The year for which to fetch articles.

        Returns:
            list: A list of archived NYT articles for the specified month and year.
        """
        params = {"api-key": self.API_KEY}
        # Build the endpoint URL for fetching archived articles
        url = f"{BASE_URL_ARCHIVE}/{year}/{month}.json"

        # Generate an output file name based on the month and year
        output_file_name = f"data_archive_{month}_{year}.json"

        # Send the HTTP GET request and get the JSON response
        response = requests.get(url, params=params).json()
        docs = response['response'].get('docs', [])

        # If docs, save them to the output file
        if docs:
            with open(output_file_name, 'w', encoding='utf-8') as f:
                json.dump(docs, f, ensure_ascii=False, indent=4)

        return docs

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
        print("Number of hits:", hits)

        # Determine the number of pages (10 results per page)
        num_pages = int(math.ceil(hits / 10))
        print("Number of pages:", num_pages)

        list_docs = []

        # Iterate through all pages to fetch the documents
        with open(f"{output_file}_{start_date}.json", 'w', encoding='utf-8') as f:
            for i in range(num_pages):
                print(f"Fetching page {i}")
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
    
    def request_weelkly_nonfiction_bestsellers_books(self, day: str, month: str, year: str):
        """
        Fetches a list of the NYT Best Sellers Nonfictional Books for a given week, month and year.

        Args:
            day (str): The week for which to fetch the list.
            month (str): The month for which to fetch the list.
            year (str): The year for which to fetch the list.

        Returns:
            dict: A list of all NYT Best Sellers Nonfictional List for a given week, month and year.
        """
        params = {"api-key": self.API_KEY}
        # Build the endpoint URL for fetching the book list. 
        url = f"{BASE_URL_BOOKS}/lists/{year}-{month}-{day}/combined-print-and-e-book-nonfiction.json"

        # Generate an output file name based on the week, month and year
        output_file_name = f"data_nonfiction_bestsellers_{year}-{month}-{day}.json"

        # Send the HTTP GET request and get the JSON response
        response = requests.get(url, params=params).json()

        # If response, save them to the output file
        if response:
            with open(output_file_name, 'w', encoding='utf-8') as f:
                json.dump(response, f, ensure_ascii=False, indent=4)

        return response
    
    def request_all_nonfiction_bestsellers_books(self, start_date = '2011-02-13'):
        """
        This function retrieves all the unique best sellers books from the list 'combined-print-and-e-book-nonfiction list' 
        from a strarting date and save it in a JSON file. The list of books is published each week from 2011-02-13 until today.
    
        Args : 
            next_published_date : The starting date for the retrieval of books. The default value for next_published_date is '2011-02-13' because 
                                  it is the date when the first list of 'combined-print-and-e-book-nonfiction list' was published in the NYT. 

        Retruns: 
            A list of the published dates the loop when through. 
            A list of NYT nonfictional best sellers from the starting date until today.

        """

        # Load API key from config file
        cfg = configparser.ConfigParser()
        cfg.read('api.cfg')
        API_KEY = cfg.get('KEYS', 'key_nyt_news')

        unique_titles = [] # List of unique book titles
        next_published_date = start_date # Inital date to start fetching the books.
        published_dates = [] # List of the published date the loop went through.
        books = [] # List to store books

        while next_published_date:

            # Build the endpoint URL for fetching the book list. 
            url = f"{BASE_URL_BOOKS}/lists/{next_published_date}/combined-print-and-e-book-nonfiction.json"

            counter_request = 1 # Initial number of requests.
            total_request_iteration = 1 # Initial number of requests iterations of the same list
            offset = 0 # Start reading the book list from the first book in the list

            while counter_request <= total_request_iteration:

                # Set request parameters
                params = {"api-key": API_KEY, "offset" : str(offset)}

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
                        applebooks_url = None # Handle the case when no apple links are provided
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

                total_request_iteration = math.ceil(num_books/20) # The total number of request calls needed
                counter_request += 1 # Increase the request counter
                offset += 20 # Add 20 to the offset to query the next 20 books

                # According to NYT FAQ, sleep 12 seconds between requests to avoid rate limits
                time.sleep(12)
                
            next_published_date = response['results']['next_published_date'] # Get the publication date of the next list 
            if next_published_date:
                published_dates.append(next_published_date)

        # If books were retrieved, save the list to the output file
        end_date = published_dates[-1]
        output_file_name = f"all_nonfiction_bestsellers_from_{start_date}_to_{end_date}.json"

        if books:
            with open(output_file_name, 'w', encoding='utf-8') as f:
                json.dump(books, f, ensure_ascii=False, indent=4)

        return published_dates, books

if __name__ == "__main__":
    nyt_c = NYTConnector()
    res = nyt_c.request_times_newswire('all', 'u.s.')
    # nyt_c.request_archive('9', '2000')
    # nyt_c.request_weelkly_nonfiction_bestsellers_books('05', '08', '2020')
    # nyt_c.request_most_popular(30)
    # nyt_c.request_by_keyword('Presidential Election of 2024', 'data_us_election', '20240508', '20240512')
