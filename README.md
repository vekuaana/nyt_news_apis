# Projet Data Engineer - API New York Times News
## Pré-requis
Créer un compte sur [NYT Dev](https://developer.nytimes.com/get-started) pour récupérer une clé qui permettra de requêter les API du NYT. Al'étape "*Register apps*",  sélectionner les API suivantes :
* Archive API
* Books API
* Times Wire API
  
La clé devra être ajouté au fichier **api.cfg** (voir prochaine étape)

## Installation
Modifier le fichier  **.env.example** avec les informations d'authentification. Renommer **.env.example** en >> **.env**.
```bash
├── nyt_news
│   ├── .env.example

```
Lancer la commande suivante :
```console
docker-compose --profile build up -d
```

Note : s'il n'est pas nécessaire de retrain le modèle polarity, la mise à jour de l'app peut se faire avec la commande "docker-compose up -d" en ignorant le profile "build"

## Objectifs
Réalisation d'une API qui offre une perspective dynamique sur les élections américaines.
Dans un paysage politique en perpétuelle évolution, nous souhaitons mettre en évidence l'importance de rester informé et de comprendre les nuances des médias.


| Fonctionnalités | Objectif |  Input | Output | Dataset|
| :-------------- |:---------|:-------|:-------|:-------|
|Analyse de sentiment : classification en polarité | Discerner les tendances émotionnelles dʼun article via lʼanalyse de son titre. Aperçu rapide de qui attire l'attention et comment | headline - **API Times NewsWire** | Neutre - Négatif - Positif | SEN : Sentiment analysis of Entities in News headlines :https://zenodo.org/records/5211931 |
|Recommandation de livres | Analyse des préférences du lecture et recommandation dʼun best-sellers du New York Times qui correspond le mieux aux intérêts politiques de lʼutilisateur selon les articles lus. |  Article à retrouver depuis lʼ**API Search**. **Web scraping Amazon** | livre dans lʼ**API books** | pas de données de validation: aucune données article - livre n'existe et il n'y a pas la possibilité de valider le model à postériori avec l'expérience utilisateur. https://www.evidentlyai.com/ranking-metrics/evaluating-recommender-systems#:~:text=You%20can%20use%20predictive%20metrics,novelty%2C%20or%20diversity%20of%20recommendations.
| Comparaison historique | Examiner comment le climat médiatique actuel se compare à celui des trois dernières élections. Détection de la polarité dans les archives. | headline - **API Archive** | Neutre - Négatif - Positif |  SEN : Sentiment analysis of Entities in News headlines :https://zenodo.org/records/5211931 |

## Architecture (draft)
![architecture_nyt](https://github.com/Linenlp/nyt_news/assets/40054464/2c75def2-3ea3-453c-baa5-8a5ea578b510)


## Cas d'utilisations 
<img width="1530" alt="Capture d’écran 2024-05-13 à 19 23 06" src="https://github.com/Linenlp/nyt_news/assets/168664836/875c1ff9-5b40-4fe5-ab7c-646e890b8de4">
