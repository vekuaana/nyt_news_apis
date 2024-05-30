# Consommation des données

Cette étape consiste à consommer la donnée pour répondre à deux objectifs :

* classer en polarité les articles des archives et les articles en temps réel
* recommander un livre en fonction d'une requête utilisateur

## Classification en polarité orientée entité

La problématique combine à la fois l'analyse des entités et l'analyse des sentiments. L'objectif est de déterminer pour une entité donnée le sentiment (positif, négatif ou neutre) qui lui est associé dans un contexte précis.
Pour répondre à la problématique nous nous sommes inspirés des travaux proposés lors de la (shared task RuSentNE)[https://codalab.lisn.upsaclay.fr/competitions/9538]. Voici les propositions que nous avons retenues pour créer notre propre modèle :
* l'équipe (sag_m)[https://www.dialog-21.ru/media/5916/moloshnikoviplusetal113.pdf] a proposée une solutionj basée dur de la génération de texte à texte (Text2Text Generation) à l'aide du modèle ruT5. L'étape de preprocessing consiste à proposer différentes variantes de la donnée en entrée pour mettre en valeur l'entity pour laquelle on cherche à déterminé la polarité.
* l'équipe mtsai a mis en place un seuil pour la classe neutre : lorsque la classe neutre est prédite, il faut que la probabilité associée soit supérieure à un seuil sinon la deuxième classe la plus probable est attribuée.

Nous avons donc opté pour différentes variantes du modèle (T5)[https://research.google/blog/exploring-transfer-learning-with-t5-the-text-to-text-transfer-transformer] de Google.T5 repose sur une architecture Transformer. Il traite toutes les tâches de NLP comme un problème de Text2Text (modèle Encoder-Decoder) en testant les limites du Trasnfer Learning appliqués à diverses tâches du TAL.
Notre problématique sera donc formalisée en input de l'encoder.

### Training

Deux modèles sont fine tunés :
* Text2Text Generation avec le modèle (T5 base)(https://huggingface.co/google-t5/t5-base/) : modèle de base embaruqant 220 millions de paramèteres
* Text2Text with Conditional Generation avec le modèle (Flan T5-base)[https://huggingface.co/google/flan-t5-base : Il possède le même nombre de paramètres que T5 mais il a déjà été "fine-tune" sur 1 000 tâches
```python
python conditional_generation_polarity.py args_conditional_generation.json
```
