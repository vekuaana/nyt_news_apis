
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import csv
import time
import os
import pprint

class AppleBooksScraper:
    def __init__(self):
        self.soup = None

    def open_apple_books_link(self, url):
        """ 
        Opens the Apple Books link provided by the books data from the New York Times Books API.
        """
        self.url = url
        headers = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15"}
        try:
            page = requests.get(url, headers=headers)
            page.raise_for_status()  # Raise an exception for non-200 status codes
            self.soup = BeautifulSoup(page.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching URL: {e}")

    def extract_book_information(self):
        """ 
        Extracts data from the opened Apple Books page.
        """
        if self.soup:
            # Extract author's name
            author_location = self.soup.find('div', class_="book-header__author")
            author_name = author_location.find('a').text.strip() if author_location else "N/A"

            # Extract book's name
            book_location = self.soup.find('h1', class_="product-header__title book-header__title")
            book_name = book_location.text.strip() if book_location else "N/A"

            # Extract book's genre
            genre_location = self.soup.find('div', class_="book-badge__caption")
            genre_name = genre_location.text.strip() if genre_location else "N/A"

            # Extract summary
            summary_location = self.soup.find('div', class_="we-truncate--multi-line")
            summary_text = summary_location.text.strip() if summary_location else "N/A"

            return book_name, author_name, genre_name, summary_text
        return "N/A", "N/A", "N/A", "N/A"  # Return a default tuple if soup is None

if __name__ == "__main__":
    scraper = AppleBooksScraper()
    scraper.open_apple_books_link(url='https://goto.applebooks.apple/9780593237465?at=10lIEQ')
    book_name, author_name, genre_name, summary_text = scraper.extract_book_information()

    # Save as a dictionary
    data = {
        'Title': book_name,
        'Author': author_name,
        'Genre': genre_name,
        'Summary': summary_text,
        'Date': str(datetime.date.today()) 
         }
    
    pprint.pprint(data)

