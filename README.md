# Projet Data Engineer - API New York Times News
## Pré-requis
Python 3.11

## Installation

Modifier les fichiers  **.env.example** et **api.cfg** avec les informations d'authentification. Renommer **.env.example** en >> **.env**
```bash
├── nyt_news
│   ├── api.cfg
├── .env.example
```
Lancer la commande suivante :
```console
docker-compose up -d
```
## Objectifs
Réalisation d'une API qui offre une perspective dynamique sur les élections américaines.
Dans un paysage politique en perpétuelle évolution, nous souhaitons mettre en évidence l'importance de rester informé et de comprendre les nuances des médias.


| Fonctionnalités | Objectif |  Input | Output | Dataset|
| :-------------- |:---------|:-------|:-------|:-------|
|Analyse de sentiment : classification en polarité | Discerner les tendances émotionnelles dʼun article via lʼanalyse de son titre. Aperçu rapide de qui attire l'attention et comment | headline - **API Times NewsWire** | Neutre - Négatif - Positif | SEN : Sentiment analysis of Entities in News headlines :https://zenodo.org/records/5211931 |
|Recommandation de livres | Analyse des préférences du lecture et recommandation dʼun best-sellers du New York Times qui correspond le mieux aux intérêts politiques de lʼutilisateur selon les articles lus. |  Article à retrouver depuis lʼ**API Search**. **Web scraping Amazon** | livre dans lʼ**API books** | pas de données de validation: aucune données article - livre n'existe et il n'y a pas la possibilité de valider le model à postériori avec l'expérience utilisateur. https://www.evidentlyai.com/ranking-metrics/evaluating-recommender-systems#:~:text=You%20can%20use%20predictive%20metrics,novelty%2C%20or%20diversity%20of%20recommendations.
| Comparaison historique | Examiner comment le climat médiatique actuel se compare à celui des trois dernières élections. Détection de la polarité dans les archives. | headline - **API Archive** | Neutre - Négatif - Positif |  SEN : Sentiment analysis of Entities in News headlines :https://zenodo.org/records/5211931 |

## Architecture (draft)
![architecture_nyt (1)](https://github.com/Linenlp/nyt_news/assets/40054464/da52c303-0766-487d-af10-9d94b81dc4fe)

## Cas d'utilisations 
<img width="1530" alt="Capture d’écran 2024-05-13 à 19 23 06" src="https://github.com/Linenlp/nyt_news/assets/168664836/875c1ff9-5b40-4fe5-ab7c-646e890b8de4">
