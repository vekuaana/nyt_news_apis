# Consommation des données

Cette étape consiste à consommer la donnée pour répondre à deux objectifs :

* classer en polarité les articles des archives et les articles en temps réel
* recommander un livre en fonction d'une requête utilisateur

## Classification en polarité orientée entité

La problématique combine à la fois l'analyse des entités et l'analyse des sentiments. L'objectif est de déterminer pour une entité donnée le sentiment (positif, négatif ou neutre) qui lui est associé dans un contexte précis.
Pour répondre à la problématique nous nous sommes inspirés des travaux proposés lors de la [shared task RuSentNE](https://codalab.lisn.upsaclay.fr/competitions/9538). Voici les propositions que nous avons retenues pour créer notre propre modèle :
* l'équipe [sag_m](https://www.dialog-21.ru/media/5916/moloshnikoviplusetal113.pdf) a proposée une solution basée dur de la génération de texte à texte (Text2Text Generation) à l'aide du modèle ruT5. L'étape de preprocessing consiste à proposer différentes variantes de la donnée en entrée pour mettre en valeur l'entity pour laquelle on cherche à déterminé la polarité.
* l'équipe mtsai a mis en place un seuil pour la classe neutre : lorsque la classe neutre est prédite, il faut que la probabilité associée soit supérieure à un seuil sinon la deuxième classe la plus probable est attribuée.

Nous avons donc opté pour différentes variantes du modèle [T5](https://research.google/blog/exploring-transfer-learning-with-t5-the-text-to-text-transfer-transformer) de Google.T5 repose sur une architecture Transformer. Il traite toutes les tâches de NLP comme un problème de Text2Text (modèle Encoder-Decoder) en testant les limites du Trasnfer Learning appliqués à diverses tâches du TAL.
Notre problématique sera donc formalisée en input de l'encoder.

### Pré-requis

Environnement virtuel Python 3.11 (conda ou venv)

```
pip install -r requirements.txt
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
python predict.py --text "Buttigieg soars, Biden slips, Sanders still on top in newest New Hampshire poll" --year 2024 --verbose
```

Output :
```
Titre : Biden Reacts to Trump’s Guilty Verdict

Model : trainer_seq2seq
Prediction : negative
[{'entity': 'Biden', 'prediction': 'neutral'}, {'entity': 'Trump', 'prediction': 'negative'}]

Model : trainer_flan
Prediction : neutral
[{'entity': 'Biden', 'prediction': 'neutral'}, {'entity': 'Trump', 'prediction': 'negative'}]
```

Note : Les temps d'exécution sont similaires lors de l'inférence pour uen phrase en input sur cpu et gpu 
