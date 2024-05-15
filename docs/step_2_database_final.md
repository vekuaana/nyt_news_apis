# Les bases de données

Les données récupérées des différents API sont renvoyées au format json. Les API utilisent un style d’achitecture RESTful orientée ressources.
Pour stocker les données récoltées, nous utiliserons des BDD NoSQL.


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
