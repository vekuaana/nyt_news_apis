from datetime import datetime
import time
import requests
import json
import re
import logging
import os

from dotenv import load_dotenv, find_dotenv

from csv_service.csv_reader import CSVReader
from db_service.mongodb_connector import MongoDBConnector
from fetcher_service.nyt_article_fetcher import NYTArticleFetcher

load_dotenv(find_dotenv())

polarity_url = "http://prediction:8005/polarity"
books_to_article_url = "http://prediction:8005/books"


def get_token():
    response = requests.post(
        url="http://prediction:8005/get_token",
        data={
            "username": os.getenv('USER1'),
            "password": os.getenv('PASSWORD1')
        }
    )
    token = response.json()['access_token']
    return token

def main():
    # Configurer la journalisation
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler("nyt_archive_fetcher.log"),
                            logging.StreamHandler()
                        ])
    logger = logging.getLogger(__name__)

    # Charger la configuration
    api_url = "https://api.nytimes.com/svc/archive/v1"
    api_key = os.getenv('NYT_API_KEY')
    username_db = os.getenv('USER1')
    password_db = os.getenv('PASSWORD1')
    authsource_db = os.getenv('MONGO_INITDB_DATABASE')

    # Configurer la connexion à MongoDB
    mongo_connector = MongoDBConnector('localhost',
                                       'nyt_news',
                                       'usa_election_articles',
                                       username_db,
                                       password_db,
                                       authsource_db)

    # Charger les données des candidats depuis le fichier CSV
    csv_reader = CSVReader('config/election_candidates.csv')
    candidates_data = csv_reader.read_candidates()

    # Initialiser le fetcher d'articles NYT
    nyt_fetcher = NYTArticleFetcher(api_url, api_key)

    query_counter = {'count': 0}

    token = get_token()

    # Traiter chaque année
    for year, info in candidates_data.items():
        candidates = info['candidates']
        start_date = datetime.strptime(f"{year}-01-01", '%Y-%m-%d')
        end_date = datetime.strptime(info['election_date'], '%Y-%m-%d')
        logger.info(f"Traitement de l'année {year} avec {len(candidates)} candidats")

        for month in range(1, 13):
            current_date = datetime(int(year), month, 1)
            if start_date <= current_date <= end_date:
                if query_counter['count'] >= 500:
                    logger.warning("Limite de requêtes API journalière atteinte.")
                    return

                try:
                    articles = nyt_fetcher.fetch_articles(int(year), month)
                    filtered_articles = NYTArticleFetcher.filter_articles(articles, candidates)
                    logger.info(f"Articles filtrés pour {year}-{month}: {len(filtered_articles)}")

                    for article in filtered_articles:
                        article_data = NYTArticleFetcher.extract_fields(article)

                        # Add election_id, main_candidate and polarity
                        if not article_data["lead_paragraph"]:
                            article_data["lead_paragraph"] = None
                        election = mongo_connector.db['election'].find_one(
                            {'election_year': datetime.fromisoformat(article_data['pub_date']).strftime("%Y")})
                        election_id = election['election_id']
                        main_candidate = []
                        for entity in [x["name"].split()[-1] for x in election['candidate']]:
                            if re.search(r'(^' + entity + r'|\s+' + entity + r'(\s|-|[’\']s)|' + entity + '$)', article_data["headline"]):
                                main_candidate.append(entity)
                        article_data['main_candidate'] = main_candidate
                        article_data['election_id'] = election_id

                        if isinstance(article_data['byline'], str):
                            article_data['byline'] = [article_data['byline']]
                        elif isinstance(article_data['byline'], list):
                            article_data['byline'] = []
                        request_body = json.dumps(article_data)
                        logger.info('request_body')
                        logger.info(request_body)

                        # get polarity
                        res_polarity = requests.post(polarity_url, data=request_body, headers={"Authorization": "Bearer " + token})
                        logger.info(res_polarity)
                        if res_polarity.status_code == 200:
                            res_polarity_json = res_polarity.json()
                            logger.info(res_polarity_json)
                            article_data['polarity'] = res_polarity_json['response']
                            logger.info(article_data)

                        # get recommended books
                        res_books = requests.post(books_to_article_url, data=request_body, headers={"Authorization": "Bearer " + token})
                        if res_books.status_code == 200:
                            res_books_json = res_books.json()
                            article_data['recommended_book'] = res_books_json['response']
                            if not article_data['abstract']:
                                article_data['recommended_book'] = []

                        logger.info('\n\n-----------------------')
                        logger.info(article_data)
                        if not mongo_connector.db['usa_election_articles'].find_one({'uri': article_data['uri']}):
                            logging.info("new article")
                            logging.info(article_data)
                            mongo_connector.insert_article(article_data)
                            logger.info(f"Article inséré pour {year}-{month}: {article_data.get('headline', 'No Headline')}")
                        else:
                            result = mongo_connector.db['usa_election_articles'].replace_one({'uri': article_data['uri']}, article_data)
                            if result.matched_count > 0:
                                logger.info(f"Document matched and replaced: {result.matched_count}")
                            elif result.upserted_id:
                                logger.info(f"Document inserted with id: {result.upserted_id}")
                            else:
                                logger.info("No document was replaced or inserted")

                    time.sleep(12)
                    query_counter['count'] += 1

                except requests.exceptions.RequestException as e:
                    logger.error(f"Erreur de requête pour {year}-{month}: {e}")
                    if e.response.status_code == 429:
                        logger.warning("Trop de requêtes. Pause de 60 secondes.")
                        time.sleep(60)
                except Exception as e:
                    logger.exception(f"Erreur inattendue pour {year}-{month}: {e}")

if __name__ == '__main__':
    main()