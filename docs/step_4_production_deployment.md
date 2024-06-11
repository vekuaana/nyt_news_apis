# Déploiement

## Objectif

Dans ce sprint il faudra réaliser une API du modèle de ML qui devra être "conteneuriser". Les attendus :

* Création d'une API du modèle de Machine Learning ( + BDD si besoin)
* Réaliser des tests unitaires de l'API
* Conteneuriser cette API et la BDD via Docker
* Mesurer la dérive des données avec DataDrift

## Questions pour Dan

### Point du 11/06/2024
* faut-il faire un conteneur par modèle ? Par exemple la liste des requirements diffère d'un système à l'autre
    * <ins>réponse</ins>: oui c'est mieux de faire un conteneur par modèle car les environnements de développement sont différents et ça permet de relancer l'entrainement que d'un modèle si besoin
* comment exporter le modèle en dehors du conteneur sans volume de façon automatique ?
    * <ins>réponse</ins>: il faut forcément utiliser un volume. La solution la plus "élégante" serait d'avoir un troisième conteneur qui serait up tout le temps et qui exposerait les modèles via une API. Les modèles seraient sotckés dans un colume partagé par les 3 conteneurs de ML
* est-ce qu'il vaut mieux dupliquer la donnée "article" pour attribuer une entité et une polarité directement dans l'attribut sans passer par des listes et faciliter les aggrégations ou conserver un seul article et stocker les informations sur les paires entité/polarité dans une liste de docs ?
    * <ins>réponse</ins>: éviter de dupliquer
