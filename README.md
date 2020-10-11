# Topologie-Roman
Etude de la topologie de réseaux d'acteurs extraits à partir de romans célèbres
Ce projet permet la production de réseaux d'acteurs à partir de texte de roman ou de script.

## Architecture

### Code
Le code est situé dans le répertoir Source_code_output/src
Le programme comprends 3 types de fichier en plus du "main" central "bookAnalyser" :
* les fichiers book* sont utilisés pour l'analyse des livres.
* les fichiers mainX permettent de tester individuellement les fichiers bookX.
* les fichiers aux* contiennent également une boucle principale et exécutent des fonctions externes à l'analyse principale. 
* le fichier bookAnalyser permet de lancer l'analyse complète de romans

### Input/Output

Tout les fichiers textes correctement formatés doivent être placés dans le répertoir Source_code_output/books_raw.
Pour les scripts, des outils d'aide au formattage sont disponible dans Script_processing.
Après que le programme général aie analysé un texte, le résultat du preprocessing sera stocké dans  Source_code_output/books_objects sous forme de fichiers books.
Lors des analyses suivantes, le fichiers books du roman sera automatiquement récupéré, veillez donc à le supprimer si vous avez modifier le texte correspondant.
Tout les autres output, csv graphs et images, sont situés dans plusieurs dossiers du répertoir Source_code_output.

## Exécution

### Installation du projet

Afin de pouvoir exécuter le projet avec anaconda, les commandes suivantes doivent être exécutées sur l'anaconda prompt:
* git clone https://github.com/antheymans/Topologie-Roman.git
* cd Topologie-Roman
* conda create --name topologie-roman --file spec-file.txt 
* conda activate topologie-roman
* cd Source_code_output/src

### Exécution du code

* python bookAnalyser.py permet de démarrer la boucle principale.
Le programme demandera ensuite quel document .txt doit être lu. 
L'utilisateur peut également répondre "all" pour démarrer l'analyse de tout les romans ou l'option "some" pour l'analyse des romans dont le preprocessing n'a pas été effectué.
* python mainAux.py permet de générer la signature (c-a-d la production d'un certain nombre de métrique) de tout les réseaux produits.
* différents fichiers main permettent d'exécuter des sous parties des analyses ou des aux. 
* le fichier auxGenerateGraph.py permet de générer certains graphs relatifs à la distribution de degrés de ces réseaux.

Cette version du projet tourne sur python 3.6 et demande notamment les librairies suivantes: 
* matplotlib
* network 1.11
* dill
* scipy (uniquement pour les fichiers "aux")
* pattern

Comme le projet pattern sur python 3 n'a pas abouti, une branche permettant d'utiliser les fonctions nécessaires 
a été fournie à l'adresse:
https://github.com/antheymans/pattern


## Contact

Pour des questions ou des requêtes, je suis disponible à l'adresse heymansantoine@gmail.com

