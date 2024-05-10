# Les bases de données

Les données récupérées des différents API sont renvoyées au format json. Les API utilisent un style d’achitecture RESTful orientée ressources.
Pour stocker les données récoltées il est nécessaire de se tourner vers des BDD NoSQL.

## ElasticSearch : moteur de recherche spécialisé plein texte

Organisation
* stockage dans des index
* Compatible avec le format JSON et API REST.

Recherche
* Excellente capacité et qualité d’indexation
* Excelle dans la recherche plein texte

DataViz : 
* Kibana permet de créer rapidement des dashboards
* Différentes présentations disponibles, graphiques, tableaux, textes
* Visualisation des données en temps réel

Autres :
* Adapté au traitement et à l'analyse des données en temps réel
* Adapté au texte

## MongoDB : BBD NoSQL pour le stockage de gros volumes de données

Organisation
* stockage dans une collection : élément qui contient le même ensemble de documents.
* Compatible avec le format JSON et BJSON

Recherche
* les champs dans un document peuvent être indexés
* stockage et la récupération de données robustes dans divers types d'applications.

DataViz : 
* Atlas ??

Spécificité :
* Agilité et flexibilité pour le stockage de données hétérogèness
* Système offrant une excellente scalabilité ;

## UML (draft)
![nyt_uml (1)](https://github.com/Linenlp/nyt_news/assets/40054464/c5e8b1af-86ec-47a0-930a-c331c489c47e)

## Liste des variables à garder
### Books
* book_uri:	*Str*
* title:	*Str*
* author:	*Str*
* buy_links: *Document[]*
* resume_amazon:	*Str*
* description:	*Str*

### Article
* uri:	*Int*
* title:	*Str*
* abstract:	*Str*
* lead_paragraph:	*Str*
* election_id:	*Int*
* per_facet:	*Str[]*
* pub_date: *Date*
* polarity:	*Str*
* recommended_book:	*Int[]*
* byline:	*Str*
* main_candidat:	*Str*

### Election
* date	*Date*
* candidates	*Document[]*
* winner	*Document*
