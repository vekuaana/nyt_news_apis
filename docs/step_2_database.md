# Les bases de données

Les données récupérées des différents API sont renvoyées au format json. Les API utilisent un style d’achitecture RESTful orientée ressources.
Pour stocker les données récoltées, nous utiliserons des BDD NoSQL sur MongoDB.


## MongoDB : BBD NoSQL pour le stockage de gros volumes de données

Organisation
* stockage dans une collection : élément qui contient le même ensemble de documents.
* Compatible avec le format JSON et BJSON

Recherche
* les champs dans un document peuvent être indexés
* stockage et la récupération de données robustes dans divers types d'applications.

Spécificité :
* Agilité et flexibilité pour le stockage de données hétérogèness
* Système offrant une excellente scalabilité
* Facilite le déploiment ;

## UML
L'architecture est composée de 4 collections de données hébergées sur MongoDB:
* La collection Book reprenant les informations sur les bestsellers du NYT.
* La collection USA election articles reprenant les articles liés aux élections américaines. Elle est composée de données provenant des API Archive et Times wire ainsi que des données sorties du model d'analyse de sentiments (main_candidate, polarity) et du modèle de recommandation de livres (recommended_books).
* La collection Election reprenant les informations liées aux différentes élections américaines.
* La collection Polarity_dataset contient les données pour l'entrainement du modèle de ML pour l'analyse de sentiment
  
<img width="1000" alt="Screenshot 2024-05-15 at 11 55 47" src=https://github.com/Linenlp/nyt_news/assets/40054464/421ae158-4f2e-4644-b410-77d2470c5765>

## API NYT : Liste des clés à extraire
### Books API
* book_uri:	*Str*
* title:	*Str*
* author:	*Str*
* buy_links: *Document[{name, url}]*
* description:	*Str*
* genre:  *Str*
* publisher: *Str*

### Times Wire API
* uri:	*Int*
* title:	*Str*
* section: *Str*
* subsection: *Str*
* url: *Str*
* abstract:	*Str*
* per_facet:	*Str[]*
* des_facet:	*Str[]*
* org_facet:	*Str[]*
* pub_date: *Date*
* byline:	*Str*
* material_type_facet: *Str*

### Archive API
* uri:	*Int*
* abstract:	*Str*
* web_url : *Str*
* lead_paragraph : *Str*
* headline : *Str*
* pub_date: *Date
* byline:	*Str*
* section_name: *Str*
* document_type: *Str*
* keywords: *Str[]*

### Article Search API
* uri:	*Int*
* abstract:	*Str*
* web_url : *Str*
* lead_paragraph : *Str*
* headline : *Str*
* pub_date: *Date*
* byline:	*Str*
* news_desk: *Str*
* section_name: *Str*
* subsection_name: *Str*
* type_of_material: *Str*
* keywords: *Str[]*
* snippet: *Str*

## Question pour Dan
### Point du 21/05/2024
* as tu des ressources sur les bonnes pratiques en ce qui concerne l'arborescence du projet, le nom des fichiers, la composition des conteneurs Docker ?
    * <ins>réponse</ins>: pas vraiment de ressources identifiées
* sans utilisation d'un cloud provider, est-ce une bonne pratique de stoker les données de la BDD, les modèles dans les volumes des conteneurs associés ?
    * <ins>réponse</ins>: c'est possible
* un docker-compose suffit-il comme orchestrateur ou en faut-il plusieurs ?
    * <ins>réponse</ins>: oui quand on a moisn de 10 conteneurs (environ)
* peut on stocker le jeu de données d'entrainement dans la même bdd ? (mais dans une collection distincte)
    * <ins>réponse</ins>: oui c'est même une bonne pratique
  
### Point du 13/05/2024
* quel est l'intérêt de réaliser un UML pour des BDD NoSQL dont la particularité est qu'elles sont schemaless ?
    * <ins>réponse</ins> : représenter simplement les collections avec les attributs et avoir ainsi une idée de l'architecture du SGBD. Il est aussi possible de fixer un schéma sur une BDD Mongo avec *jsonSchema*
* est-il possible de faire un lien entre deux index/collection ? cf [UML full NoSQL](#V1)
    * <ins>réponse</ins>: il est possible de faire des liens en récupérant les infos dans des dataframes pandas
* est-ce qu'on peut traiter des données en temps réel avec des BDD SQL ? cf [UML SQL + NoSQL](#V2)
    * <ins>réponse</ins>: oui c'est possible même si ce n'est pas le plus optimal. En cas de surcharge de la machine, on peut passer le traitement en batch 
* que doit on délivrer à la fin du projet ? Une simple API ? Une application web front-end qui communique avec l'API ?
    * <ins>réponse</ins> :
        * documentation de l'API
        * dashboard de monitoring des algo de ML
        * bonus : front avec des tableaux etc. 
* où créer la BDD ?
    *  est-il possible de déployer la même BDD (avec le même contenu) via docker ?
    *  peut-on partir de la même base avec Docker et l'instancier puis la peupler chacune sur nos machines ?
    *  créer une VM sur Amazon Cloud ?
    *  <ins>réponse</ins> : tout est possible
* ElasticSearch vs MongoDB : quelle est la plus utilisée en entreprise ?
    * <ins>réponse</ins>: MongoDb est plus populaire en France
        * se déploie plus facilement
        * version Cloud
        * syntaxe plus simple
        * mise à jour fréquente       
