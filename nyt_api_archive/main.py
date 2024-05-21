from configparser import ConfigParser
from datetime import datetime
import time
import requests
from csv_service.csv_reader import CSVReader
from db_service.mongodb_connector import MongoDBConnector
from fetcher_service.nyt_article_fetcher import NYTArticleFetcher

def main():
    # Charger la configuration
    config = ConfigParser()
    config.read('config/nyt_api.cfg')
    api_url = config['API']['api_url']
    api_key = config['API']['api_key']
    
    # Configurer la connexion à MongoDB
    mongo_connector = MongoDBConnector('mongodb://localhost:27017/', 'nytimes', 'archive_election_articles_')

    # Charger les données des candidats depuis le fichier CSV
    csv_reader = CSVReader('config/election_candidates.csv')
    candidates_data = csv_reader.read_candidates()

    # Initialiser le fetcher d'articles NYT
    nyt_fetcher = NYTArticleFetcher(api_url, api_key)

    query_counter = {'count': 0}

    # Traiter chaque année
    for year, info in candidates_data.items():
        candidates = info['candidates']
        start_date = datetime.strptime(f"{year}-01-01", '%Y-%m-%d')
        end_date = datetime.strptime(info['election_date'], '%Y-%m-%d')
        print(f"Traitement de l'année {year} avec {len(candidates)} candidats")

        for month in range(1, 13):
            current_date = datetime(int(year), month, 1)
            if start_date <= current_date <= end_date:
                if query_counter['count'] >= 500:
                    print("Limite de requêtes API journalière atteinte.")
                    return

                try:
                    articles = nyt_fetcher.fetch_articles(int(year), month)
                    filtered_articles = NYTArticleFetcher.filter_articles(articles, candidates)
                    print(f"Articles filtrés pour {year}-{month}: {len(filtered_articles)}")

                    for article in filtered_articles:
                        article_data = NYTArticleFetcher.extract_fields(article)
                        article_data['election_year'] = int(year)
                        article_data['election_date'] = end_date
                        mongo_connector.insert_article(article_data)
                        print(f"Article inséré pour {year}-{month}: {article_data.get('headline_main', 'No Headline')}")

                    time.sleep(12)
                    query_counter['count'] += 1

                except requests.exceptions.RequestException as e:
                    print(f"Erreur de requête pour {year}-{month}: {e}")
                    if e.response.status_code == 429:
                        print("Trop de requêtes. Pause de 60 secondes.")
                        time.sleep(60)
                except Exception as e:
                    print(f"Erreur inattendue pour {year}-{month}: {e}")

if __name__ == "__main__":
    main()
