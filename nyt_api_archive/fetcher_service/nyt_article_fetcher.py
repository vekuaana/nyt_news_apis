import requests
from typing import List, Dict, Any

class NYTArticleFetcher:
    """
    Cette classe gère les requêtes vers l'API Archive du NYT, le filtrage et l'extraction des champs des articles.
    """
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key

    def fetch_articles(self, year: int, month: int) -> List[Dict[str, Any]]:
        """
        Récupère les articles d'un mois spécifique d'une année déterminée à partir de l'API Archive du NYT
        """
        request_url = f"{self.api_url}/{year}/{month}.json?api-key={self.api_key}"
        print(f"Requête URL: {request_url}")
        response = requests.get(request_url)
        response.raise_for_status()
        data = response.json()
        return data.get('response', {}).get('docs', [])

    @staticmethod
    def extract_fields(article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait les clés-valeurs déterminées au préalable.
        """
        return {
            "abstract": article.get("abstract", ""),
            "headline": article.get("headline", {}).get("main", ""),
            "keywords": article.get("keywords", []),
            "pub_date": datetime.strptime(article.get("pub_date", "1970-01-01T00:00:00Z"), '%Y-%m-%dT%H:%M:%SZ'),
            "document_type": article.get("document_type", ""),
            "section_name": article.get("section_name", ""),
            "byline": article.get("byline", {}).get("person", []),
            "web_url": article.get("web_url", ""),
            "uri": article.get("uri", ""),
            "main_candidate": article.get("main_candidate", []),
            "polarity": article.get("polarity", []),
            "recommended_book": article.get("recommended_book", None),
            "election_id": article.get("election_id", None),
            "lead_paragraph": article.get("lead_paragraph", None)
        }

    @staticmethod
    def filter_articles(articles: List[Dict[str, Any]], candidates: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Filtre les articles pour ne conserver que ceux qui mentionnent des candidats ou des partis spécifiques.
        """
        filtered_articles = []
        for article in articles:
            abstract = article.get('abstract', '') or ''
            lead_paragraph = article.get('lead_paragraph', '') or ''
            headline = article.get('headline', {}).get('main', '') or ''

            for candidate in candidates:
                name = candidate['name']
                party = candidate['party']
                if (name and (name in headline or name in lead_paragraph or name in abstract)) or \
                   (party and (party in headline or party in lead_paragraph or party in abstract)):
                    filtered_articles.append(article)
                    break
        return filtered_articles
