- SemEval-2023 Task 3: Detecting the Category, the Framing, and the Persuasion Techniques in Online News in a Multi-lingual Setup
	* website :  https://propaganda.math.unipd.it/semeval2023task3/
	* papier : https://aclanthology.org/2023.semeval-1.317v2.pdf
	* Les tâches :
        * Tâche 1 : Définition : à partir d'un article de presse, déterminer s'il s'agit d'un parti pris, d'un article objectif ou d'un article satirique. Il s'agit d'une tâche multi-classes.
        * Tâche 2 : à partir d'un article de presse, identifier les cadres utilisés dans l'article. Il s'agit d'une tâche à étiquettes multiples au niveau de l'article. Un cadre est la perspective sous laquelle une question ou un élément d'information est présenté. 14 cadres : Économie, capacité et ressources, moralité, équité et égalité, légalité, constitutionnalité et jurisprudence, prescription et évaluation de politiques, criminalité et punition, sécurité et défense, santé et sécurité, qualité de vie, identité culturelle, opinion publique, politique, réglementation externe et réputation.
	        * https://provalisresearch.com/fr/solutions-2/applications/cadrage-mediatique/

- SemEval 2019 Task 4 : Hyperpartisan News Detection 
    * website : https://pan.webis.de/semeval19/semeval19-web/
	* papier : https://aclanthology.org/S19-2145.pdf
	* La tâche : Les informations hyperpartisanes sont des informations qui adoptent un point de vue d'extrême gauche ou d'extrême droite. Si l'on est capable de calculer de manière fiable ces méta-informations, les articles de presse peuvent être automatiquement étiquetés, ce qui permet d'encourager ou de décourager les lecteurs à les lire.

-  Consommer les données en temps réel : classification polarité ou sentiment pour voir qui est le plus populaire
    * dataset : https://huggingface.co/datasets/fhamborg/news_sentiment_newsmtsc
	* dataset : SEN - Sentiment analysis of Entities in News headlines (accès demandé)

UPDATE 01/05/2024
Trame : élections américaines de 2024

* Classification en polarité pour voir qui est le plus populaire à l’instant T
    * données à prédire : API Times Newswire  
    * dataset : SEN - Sentiment analysis of Entities in News headlines https://zenodo.org/records/5211931 (accès autorisé)
    * Note : le dataset match bien nos données : un headline, une entité (ex: Trump), une polarité
    * BONUS : détection de la polarité dans les archives
      
* /!\ pas  d'historique = semble compliqué à réaliser - Prédiction de la popularité des articles dès leur publication sur le site.
    * données à prédire : API Times Newswire
    * dataset : extraction et jointure des données de Archive API et Most Popular API

* Détection du sarcasme dans les news headlines
    * données à predire : API Times Newswire
    * dataset : https://www.kaggle.com/datasets/rmisra/news-headlines-dataset-for-sarcasm-detection
      
* BONUS : Détection des cadres dans les titres ou titre + résumé + paragraphe principal
    * données à prédire : API Times NewsWire + join API Search pour récupérer lead paragraph
    * dataset : https://github.com/zgjiangtoby/SemEval2023_QUST/tree/main/original_data_v4/data/en
    * note : voir si c'est possible car el dataset est sur les articles complets. Mais l'analyse des cadres a déjà été réalisées juste sur des entêtes  
: Detecting Frames in News Headlines and Its Application to Analyzing News Framing Trends Surrounding U.S. Gun Violence
    * BONUS : détection de la polarité dans les archives

UPDATE 02/05/2024
Trame : élections américaines de 2024

* Classification en polarité pour voir qui est le plus populaire à l’instant T
    * données à prédire : API Times Newswire + API Archive
    * dataset : SEN - Sentiment analysis of Entities in News headlines https://zenodo.org/records/5211931 (accès autorisé)
    * Note : le dataset match bien nos données : un headline, une entité (ex: Trump), une polarité
    * BONUS : détection de la polarité dans les archives

* Recommandation de livres sur les élections yyyy ?
    * données à prédire : API Books (+ webscrapping Amazon)
    * dataset : dataset de classification en catégorie (à trouver)

* Recommandation de livres en fonction d'un article lu
    * données à prédire : API Books (+ webscrapping Amazon)
    * dataset : dataset de matching de livres (à trouver)
      
