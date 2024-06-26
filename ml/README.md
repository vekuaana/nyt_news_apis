# Consommation des données

Cette étape consiste à consommer la donnée pour répondre à deux objectifs :

* classer en polarité les articles des archives et les articles en temps réel
* recommander un livre en fonction d'une requête utilisateur

## Classification en polarité orientée entité

La problématique combine à la fois l'analyse des entités et l'analyse des sentiments. L'objectif est de déterminer pour une entité donnée le sentiment (positif, négatif ou neutre) qui lui est associé dans un contexte précis.
Pour répondre à la problématique nous nous sommes inspirés des travaux proposés lors de la [shared task RuSentNE](https://codalab.lisn.upsaclay.fr/competitions/9538). Voici les propositions que nous avons retenues pour créer notre propre modèle :
* l'équipe [sag_m](https://www.dialog-21.ru/media/5916/moloshnikoviplusetal113.pdf) a proposée une solution basée sur de la génération de texte à texte (Text2Text Generation) à l'aide du modèle ruT5. L'étape de preprocessing consiste à proposer différentes variantes de la donnée en entrée pour mettre en valeur l'entité pour laquelle on cherche à déterminé la polarité.
* l'équipe mtsai a mis en place un seuil pour la classe neutre : lorsque la classe neutre est prédite, il faut que la probabilité associée soit supérieure à un seuil sinon la deuxième classe la plus probable est attribuée.

Nous avons donc opté pour différentes variantes du modèle [T5](https://research.google/blog/exploring-transfer-learning-with-t5-the-text-to-text-transfer-transformer) de Google.T5 repose sur une architecture Transformer. Il traite toutes les tâches de NLP comme un problème de Text2Text (modèle Encoder-Decoder) en testant les limites du Trasnfer Learning appliqués à diverses tâches du TAL.
Notre problématique sera donc formalisée en input de l'encoder.

### Pré-requis

Environnement virtuel Python 3.11 (conda ou venv)

```
pip install -r requirements.txt
```

Modifier le fichier .env.example avec les informations d'authentification. Renommer .env.example en >> .env.

```bash

├── ml
    ├── polarity
        ├── .env.example
```

### Les données d'entrainement

Le dataset utilisé pour le fine-tuning est le dataset [SEN : Sentiment analysis of Entities in News headlines](https://zenodo.org/records/5211931). C'est un ensemble de titres d'actualité politique qui ont été annotés par deux groupes d'annotateurs humains : un groupe de chercheurs et via l'Amazon Mechanical Turk service . Il est composé de 3819 titres d'actualité politique provenant de plusieurs grands médias en ligne en anglais et en polonais. Pour notre cas d'usage nous avons conservé uniquement les données en anglais et non abérantes ce qui réduit le dataset à 2464 entrées.  
La taille réduite du dataset a donc aussi joué sur la décision d'utiliser des modèles déjà pré-entrainés afin d'obtenir des résultats satisfaisants.

Il est constitué de 3 colonnes :
* headline : titre de l'article
* entity : entité pour laquelle on attribue une polarité
* majority_label : polarité

  
Répartition des labels dans le dataset

| Label    | Count |
| -------- | ------- |
| Negative  | 923    |
| Neutral | 1097   |
| Positive  | 444 |

### Preprocessing 
* data augmentation : La classe Positive est sous représentée. Nous avons ajouté une étape de data augmentation par bask translation (en-fr-en) en utilisant le  modèle Flan T5. 80 titres ont été ajoutés en rempalçant le nom des entités par des entités articielles.
* input : Les données en entrée sont contextualisées. On préfixe le texte en entrée avec la tâche, l'entité pour laquelle on cherche à détermienr la polarité du texte et les labels possibles : "Is this text about ENTITY is 'neutral', 'positive' or 'negative' ? text : TEXT"

### Entrainement

Deux modèles sont fine tunés :
* Text2Text Generation avec le modèle [T5 base](https://huggingface.co/google-t5/t5-base/) : modèle de base embaruqant 220 millions de paramèteres
```python
python sesq2seq_ml_polarity.py args_seq2seq_ml.json
```

* Text2Text with Conditional Generation avec le modèle [Flan T5-base](https://huggingface.co/google/flan-t5-base) : Il possède le même nombre de paramètres que T5 mais il a déjà été "fine-tune" sur 1 000 tâches et plus de langues. Méthode d'entrainement basée sur le prompting.
```python
python conditional_generation_polarity.py args_conditional_generation.json
```
**MLFlow**

![image](https://github.com/Linenlp/nyt_news/assets/40054464/d1ce91bf-a937-4485-83a7-ff04f4805c43)

### Evaluation
La métrique d'évaluation choisie est la f1. Elle est particulièrement utilisée pour les problèmes utilisant des données déséquilibrées ce qui est notre cas avec une sous représentation de la classe "Positive". Notre problématique n'étant pas binaire (3 classes) il a fallu adapter la f1 en utilisant la variante macro (f1_macro = moyenne arithmétique des f1 de chaque classe). La  macro accorde autant d’importance à chacune des classes ce qui permet de faire face aux données déséquilibrées.

| Model    | F1 Dev | F1 Test |
| -------- | ------- | -- |
| Baseline T5 Flan-base | 0.38 | 0.44 |
| **Best T5 Flan-base fine-tune** | **0.64**| **0.69**|
| Best T5-base fine-tune | 0.62| 0.69|

Note 1 : pas de score Baseline pour T5 car il n'a été pré-entrainé que sur les tâches de 'summarization', 'translation_en_to_de', 'translation_en_to_fr' et 'translation_en_to_ro'
Note 2 : modèle implémenté en gras dans le tableau
### Prediction
/!\  A modifier après intégration de FastAPI  

La fonction prend deux arguemnts :
* --text : titre de l'article d'actualité du NYT entre deux guillemets
* --year : année de parution de l'article au format yyyy
* --verbose (optionnel) : affiche des informations sur les opérations effectuées

Exemple :
```
python predict.py --text "Biden Goes After Trump’s Felon Status at Connecticut Fund-Raiser" --year 2024 --verbose
```

Output :
```
Titre : Biden Goes After Trump’s Felon Status at Connecticut Fund-Raiser

Model : trainer_flan
[{'entity': 'Biden', 'prediction': 'neutral'}, {'entity': 'Trump', 'prediction': 'negative'}]
```

Note : Les temps d'exécution sont similaires lors de l'inférence pour uen phrase en input sur cpu et gpu 

## Recommandation de livres en fonction d'une requête utilisateur
L'objectif est de pouvoir recommander des livres ayant été élus New York Times Bestsellers en fonction du contenu d'un article du New York Times. La recommandation de livres se basera sur la technique du TF-IDF, permettant d'évaluer l'importance d'un terme dans un document particulier, en tenant compte de la fréquence du terme dans l'ensemble des documents et sur la similarité cosinus. 

TF-IDF signifie Term Frequency-Inverse Document Frequency (Fréquence de Terme-Fréquence Inverse de Document). C'est une fonction courante utilisée dans l'analyse de texte et le traitement du langage naturel pour calculer la similarité entre les documents. Le TF-IDF fonctionne en multipliant la fréquence de terme (Term Frequency) et la fréquence inverse de document (Inverse Document Frequency). La fréquence de terme représente le nombre de fois qu'un terme apparaît dans un document, et la fréquence inverse de document représente la fréquence de ce mot dans l'ensemble des documents.

La matrice TF-IDF attribue une valeur (TF-IDF) pour chaque document et chaque mot. Le score de similarité à travers la matrice est ensuite calculé en utilisant le calcul de similarité cosinus. En résumé, deux documents auront une similarité plus élevée s'ils partagent plus de mots entre eux et moins de mots avec d'autres documents.

### Pré-requis

Environnement virtuel Python 3.11 (conda ou venv)

```
pip install -r requirements.txt
```

### Preprocessing 
Le TF-IDF nécessite les étapes de prétraitement de texte suivantes :

* Les données textuelles sont prétraitées en supprimant la ponctuation et autres caractères non alphanumériques.
* Les mots non pertinents (mots vides) sont supprimés. Ce sont des mots tellement communs qu'il est inutile de les utiliser. 
* Les mots sont tronqués pour ne garder que leur base. 
* Tokenisation : Le texte est découpé en mots individuels.

### Calcul 

La formule du TF-IDF: 

![image](https://github.com/Linenlp/nyt_news/assets/62116551/ad7ce6a7-8521-4b81-9d2a-3a72fa4c2ab7)

* Input : Une matrice dont chaque ligne représente un résumé de livre hormis la dernière ligne qui contient le résumé de l'article (après préprocessing).
* Output : Une matrice (la matrice TF-IDF) dont chaque ligne représente un article ou un livre et chaque colonne représente un mot apparu dans les résumés. La valeur d'une cellule correspond à la valeur TF-IDF de ce mot dans le document.

La formule de la similarité cosinus:

![image](https://github.com/Linenlp/nyt_news/assets/62116551/03c54b89-b975-44f4-982d-06c581ea97bf)

* Input : La matrice TF-IDF.
* Output : Un matrice donc les lignes et les colones représentent un livre ou un article. Au plus la valeur d'une cellule est grande, au plus deux documents sont similaires. La diagonale de cette matrice est remplie de 1 car le document est comparé avec lui-même.


Les 3 livres dont les résumés sont les plus proches du résumé de l'article sont sélectionés.



