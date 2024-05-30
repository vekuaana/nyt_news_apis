# Consommation des données

Cette étape consiste à consommer la donnée pour répondre à deux objectifs :

* classer en polarité les articles des archives et les articles en temps réel
* recommander un livre en fonction d'une requête utilisateur

## Classification en polarité orientée entité

La problématique combine à la fois l'analyse des entités et l'analyse des sentiments. L'objectif est de déterminer pour une entité donnée le sentiment (positif, négatif ou neutre) qui lui est associé dans un contexte précis.
Pour répondre à la problématique nous nous sommes inspirés des travaux proposés lors de la [shared task RuSentNE](https://codalab.lisn.upsaclay.fr/competitions/9538). Voici les propositions que nous avons retenues pour créer notre propre modèle :
* l'équipe [sag_m](https://www.dialog-21.ru/media/5916/moloshnikoviplusetal113.pdf) a proposée une solutionj basée dur de la génération de texte à texte (Text2Text Generation) à l'aide du modèle ruT5. L'étape de preprocessing consiste à proposer différentes variantes de la donnée en entrée pour mettre en valeur l'entity pour laquelle on cherche à déterminé la polarité.
* l'équipe mtsai a mis en place un seuil pour la classe neutre : lorsque la classe neutre est prédite, il faut que la probabilité associée soit supérieure à un seuil sinon la deuxième classe la plus probable est attribuée.

Nous avons donc opté pour différentes variantes du modèle [T5](https://research.google/blog/exploring-transfer-learning-with-t5-the-text-to-text-transfer-transformer) de Google.T5 repose sur une architecture Transformer. Il traite toutes les tâches de NLP comme un problème de Text2Text (modèle Encoder-Decoder) en testant les limites du Trasnfer Learning appliqués à diverses tâches du TAL.
Notre problématique sera donc formalisée en input de l'encoder.

### Pré-requis

Environnement virtuel Python 3.11 (conda ou venv)

```
pip install -r requirements.txt
```

### Les données d'entrainement

Le dataset utilisé pour le fine-tuning est le dataset [SEN : Sentiment analysis of Entities in News headlines](https://zenodo.org/records/5211931). C'est un ensemble de titres d'actualité politique qui ont été annotés par deux groupes d'annotateurs humains : un groupe de chercheurs et via l'Amazon Mechanical Turk service . Il est composé de 3819 titres d'actualité politique provenant de plusieurs grands médias en ligne en anglais et en polonais. Pour notre cas d'usage nous avons conservé uniquement les données en anglais et non abérantes ce qui réduit le dataset à 1102 entrées.  
La taille réduite du dataset a donc aussi joué sur la décision d'utiliser des modèles déjà pré-entrainés afin d'obtenir des résultats satisfaisants.

Il est constitué de 3 colonnes :
* headline : titre de l'article
* entity : entité pour laquelle on attribue une polarité
* majority_label : polarité

  
Répartition des labels dans le dataset

| Label    | Count |
| -------- | ------- |
| Negative  | 337    |
| Neutral | 588   |
| Positive  | 177 |


### Entrainement

Deux modèles sont fine tunés :
* Text2Text Generation avec le modèle [T5 base](https://huggingface.co/google-t5/t5-base/) : modèle de base embaruqant 220 millions de paramèteres
```python
python sesq2seq_ml_polarity.py args_seq2seq_ml.json
```

* Text2Text with Conditional Generation avec le modèle [Flan T5-base](https://huggingface.co/google/flan-t5-base) : Il possède le même nombre de paramètres que T5 mais il a déjà été "fine-tune" sur 1 000 tâches et plus de langues.
```python
python conditional_generation_polarity.py args_conditional_generation.json
```

### Evaluation
La métrique d'évaluation choisie est la f1. Elle est particulièrement utilisée pour les problèmes utilisant des données déséquilibrées ce qui est notre cas avec une sur représentation de la classe "Neutral". Notre problématique n'étant pas binaire (3 classes) il a fallu adapter la f1 en utilisant la variante macro (f1_macro = moyenne arithmétique des f1 de chaque classe). La  macro accorde autant d’importance à chacune des classes ce qui permet de faire face aux données déséquilibrées.

| Model    | F1 |
| -------- | ------- |
| Baseline T5Flan-base |     |
| Baseline  T5-base|     |
| T5Flan-base FINE TUNE  |     |
| T5-base FINE TUNE  |     |
### Prediction
A modifier après intégration de FastAPI
```python
python predict.py
```
Note : Les temps d'exécution sont similaires lors de l'inférence pour uen phrase en input sur cpu et gpu 
