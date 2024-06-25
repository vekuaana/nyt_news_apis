# Déploiement

## Objectif

Dans ce sprint il faudra réaliser une API du modèle de ML qui devra être "conteneuriser". Les attendus :

* Création d'une API du modèle de Machine Learning :
   * conteneur polarity : entrainement du modèle
   * conteneur predict : exposition via une API (FastAPI) du modèle de polarité et d'un système de recommandation de livres
* Réaliser des tests unitaires de l'API
* Conteneuriser cette API et la BDD via Docker

## Questions pour Dan

### Point du 25/06/2024
* comment test le endpoint du consumer ?
* pourquoi les builds se refont même si aucun fichier n'a bougé dans le conteneur (ex : polarity)


### Point du 18/06/2024
* docker-compose lance un conteneur avec une commande python mais la commande ne fonctionne que manuellement dans le conteneur
    * <ins>réponse</ins>: problème résolu (ports)
* peut on lancer le producer et consumer dans le même conteneur ? (le lancement des deux commandes ne fonctionnent pas)
    * <ins>réponse</ins>: il vaut mieux séparer les deux pour pouvoir les monitorer indépendamment
* Dans le fichier gtlab-ci.yml, faut-il nécessairement séparer les étapes de build et deploy car il est possible de les rassembler avec la "commande docker compose up" ?
    * <ins>réponse</ins>: En fait on va bien dissocier ces 2 phases pour séparer et tester aux maximum ces étapes. Un fois que c'est build et fonctionnel, on teste le docker-compose up et les containers puis si c'est bon, on met ça dans le deploy. Exemple de fichier

```
stages:
  - build
  - test
  - deploy

variables:
  DOCKER_DRIVER: overlay2

services:
  - docker:19.03.12-dind

before_script:
  - docker info
  - docker-compose --version

build:
  stage: build
  script:
    - docker-compose build

test:
  stage: test
  script:
    - docker-compose up -d
    - docker-compose exec web pytest
  after_script:
    - docker-compose down

deploy:
  stage: deploy
  script:
    - docker-compose up -d
  only:
    - master
```
### Point du 11/06/2024
* faut-il faire un conteneur par modèle ? Par exemple la liste des requirements diffère d'un système à l'autre
    * <ins>réponse</ins>: oui c'est mieux de faire un conteneur par modèle car les environnements de développement sont différents et ça permet de relancer l'entrainement que d'un modèle si besoin
* comment exporter le modèle en dehors du conteneur sans volume de façon automatique ?
    * <ins>réponse</ins>: il faut forcément utiliser un volume. La solution la plus "élégante" serait d'avoir un troisième conteneur qui serait up tout le temps et qui exposerait les modèles via une API. Les modèles seraient sotckés dans un colume partagé par les 3 conteneurs de ML
* est-ce qu'il vaut mieux dupliquer la donnée "article" pour attribuer une entité et une polarité directement dans l'attribut sans passer par des listes et faciliter les aggrégations ou conserver un seul article et stocker les informations sur les paires entité/polarité dans une liste de docs ?
    * <ins>réponse</ins>: éviter de dupliquer

