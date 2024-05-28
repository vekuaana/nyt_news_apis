# Consommation de la donnée
Cette étape consiste à consommer la donnée pour répondre à deux objkectifs :
- classer en polarité les articles des archives et les articles en temps réel
- recommander un livre en fonction d'une requête utilisateur

## Questions pour Dan
### Point du 28/05/2024
* Comment avoir accès à la BDD MongoDB qui est sur la VM depuis son propre poste en local ? (La BDD a été créée dans un conteneur)
* Faut il donner une explication sur le fonctionnement du modèle et justifier le choix du modèle?
* Jupyter notebook VS ficher python pour écrire du code. Comment pouvoir faire des tests directement dans son fichier py sans avoir accès à une division par cellule qui permet de faire tourner des bouts de code indépendamment?
* Comment appeler des fonctions / modules / fichiers de config qui sont dans un autre conteneur ? (ce sera géré avec l'intégration de flask ou fastapi?)
