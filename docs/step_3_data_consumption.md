# Consommation de la donnée
Cette étape consiste à consommer la donnée pour répondre à deux objectifs :
- classer en polarité les articles des archives et les articles en temps réel
- recommander un livre en fonction d'une requête utilisateur

## Questions pour Dan
### Point du 04/06/2024
* Quelles sont les bonnes pratiques pour stocker les modèles ? git-lfs? ne pas stocker le modèle dans github mais juste de quoi re-run ? (appel du script pour run dans Dockerfile ?)
    * <ins>réponse</ins>: ne pas stocker le modèle dans github, le stocker directement sur la VM. On en le stocke pas non plus sur un volume rattaché au conteneur car le conteneur n'est pas amené à rester tout le temps up.
* Est ce normal que le fichier requirements.txt généré par MLFlow ne contienne pas tous les packagers nécessaires au run du modèle ?
    * <ins>réponse</ins>: non -> (réponse complète en attente)
* Est ce qu’on peut créer notre propre dataset en utilisant l’outil Vader?(https://www.nltk.org/howto/sentiment.html)

### Point du 28/05/2024
* Comment avoir accès à la BDD MongoDB qui est sur la VM depuis son propre poste en local ? (La BDD a été créée dans un conteneur)
    * <ins>réponse</ins>: pending 
* Faut il donner une explication sur le fonctionnement du modèle et justifier le choix du modèle?
* Jupyter notebook VS ficher python pour écrire du code. Comment pouvoir faire des tests directement dans son fichier py sans avoir accès à une division par cellule qui permet de faire tourner des bouts de code indépendamment?
* Comment appeler des fonctions / modules / fichiers de config qui sont dans un autre conteneur ? (ce sera géré avec l'intégration de flask ou fastapi?):
    * <ins>réponse</ins>:
        * centraliser toutes les données dans la base MongoDB puis faire appel à la bdd dans les autres microservices
        * pour le fichier de config, il est possible de le dupliquer dans différents microservices

