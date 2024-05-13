# Les bases de données

Les données récupérées des différents API sont renvoyées au format json. Les API utilisent un style d’achitecture RESTful orientée ressources.
Pour stocker les données récoltées il est nécessaire de se tourner vers des BDD NoSQL.
## Question pour Dan (13/05/2024)
* quel est l'intérêt de réaliser un UML pour des BDD NoSQL dont la particularité est qu'elles sont schemaless ?
* est-il possible de faire un lien entre deux index/collection ? cf [UML full NoSQL](#V1)
* est-ce qu'on peut traiter des données en temps réel avec des BDD SQL ? cf [UML SQL + NoSQL](#V2)
* que doit on délivrer à la fin du projet ? Une simple API ? Une application web front-end qui communique avec l'API ?
* où créer la BDD ?
    *  est-il possible de déployer la même BDD (avec le même contenu) via docker ?
    *  peut-on partir de la même base avec Docker et l'instancier puis la peupler chacune sur nos machines ?
    *  créer une VM sur Amazon Cloud ?
* ElasticSearch vs MongoDB : quelle est la plus utilisée en entreprise ?

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
### V1
![nyt_uml (1)](https://github.com/Linenlp/nyt_news/assets/40054464/c5e8b1af-86ec-47a0-930a-c331c489c47e)

### V2 
![Flux de données UML](https://github.com/Linenlp/nyt_news/assets/62116551/d07ad78e-1961-4171-ad21-1f14e6694ffb)

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
