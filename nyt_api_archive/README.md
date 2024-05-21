Structure: 
nyt_api_archive/
├── config/
│   ├── nyt_api.cfg
│   ├── election_candidates.csv
│   └── api_description.yaml
├── csv_service/
│   ├── __init__.py
│   └── csv_reader.py
├── db_service/
│   ├── __init__.py
│   └── mongodb_connector.py
├── fetcher_service/
│   ├── __init__.py
│   └── nyt_article_fetcher.py
├── main.py
├── requirements.txt
└── setup.py

Les élections américaines à travers les articles du New-York Times

Nous utilisons l'API Archive du New-York Times pour créer une base de donnée qui reprendra tous les articles sur les candidats finalistes et leurs partis de chaque élection américaine depuis 1852. 
La période considérée sera du 1er janvier de l'année électorale jusqu'au jour du scrutin (novembre).

Nous disposons d'une liste de candidats et de leurs partis respectifs pour chaque élection (election_candidates.csv).

L'API fournit tous les articles publiés sur un mois donné. Il faut donc effectuer la requête en spécifiant le mois et l'année. 

Les limites de taux sont de 500 requêtes par jour et 5 requêtes par minute. Conseil d'utiliser un timesleep de 12 secondes entre chaque requête.

Nous allons également appliquer un filtre pour extraire uniquement les articles qui mentionnent les candidats ou leurs partis dans les clés suivantes : "abstract", "lead_paragraph", "headline", "kicker".

Si l'on retrouve le nom d'un des candidats ou la mention de leur parti dans la valeur de ces clés, alors nous extrairons l'article et le stockerons dans notre base de données MongoDB.

