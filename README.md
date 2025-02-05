# Projet Deep Learning pour la Génération d'Images de Cerveau à partir de Prompt Text
![Image comparant les deux Atlas](data/readmeFILES/images/logo.png)

Dans ce projet, nous continuons le travail déjà effectué par [GLucas01/projet_SIR](https://github.com/GLucas01/projet_SIR) pour construire une base de données afin d'appliquer le deep learning et générer des images de cerveaux à partir de prompts textuels. 
![Image comparant les deux Atlas](images/code.png)
### Tâches principales :

1. **Complétion des bases de données** :  

Notre objectif est de compléter notre base de données en ajoutant des images 3D et leurs segments. Cependant, nous commençons par les dossiers IBSR_IXI/seg, IBSR_OASIS/seg et IBSR_Kirby/seg. Pour cela, il est nécessaire de compléter leurs sous-dossiers reg et reg_brain, qui contiennent respectivement :

.Les images en niveaux de gris, sans boîte crânienne, des 18 images IBSR recalées sur les images des bases (IXI, OASIS, Kirby)
.Les fichiers .mat correspondant aux transformations appliquées
Nous avons choisi de commencer par ces dossiers, car ils sont indispensables à la création des nouveaux atlas.

Ensuite, nous complétons les bases de données de la modalité, qui ont une priorité plus élevée par rapport aux autres modalités. Pour cela, nous traitons les dossiers seg, reg et reg_brain des bases Kirby_OASIS et Kirby_IXI
2. **Création des nouveaux atlas** :  

En plus des atlas obtenus par recalage inverse sur les 18 images IBSR avec leurs segments, nous créons également des atlas selon un autre processus. Nous effectuons un recalage direct des 18 images IBSR sur les images cérébrales (sans boîte crânienne) de la base que nous souhaitons segmenter. Ensuite, en utilisant les fichiers .mat de ces recalages, nous parvenons à recaler uniquement les 18 segments IBSR afin d'obtenir la segmentation des images à traiter.


![Étape importante pour la création des nouveaux atlas](https://github.com/user-attachments/assets/f437ccf4-a82e-4026-bef2-be75f6a423ee)


Enfin, nous appliquons le script MajorityVoting.py, qui exécute le processus de majority voting sur les 18 segments d'une image, puis effectue la correction des labels. (Pour plus d’informations, veuillez consulter le README de MajorityVoting.py.)


![Segment obtenu après le processus de majority voting et la correction des labels](https://github.com/user-attachments/assets/65481181-6e0d-4a89-b2a7-fb820aec27ca)

4.**Comparaison des deux atlas**:
Cette étape est cruciale, car elle nous permet de déterminer si les deux atlas sont similaires ou non. Pour cela, un script nommé COMPARAISON.py a été créé. Son principal objectif est de comparer deux images segmentées, c'est-à-dire les deux segments d'une même image. Il applique ensuite les métriques IoU, DICE et la distance de Hausdorff sur chaque label de ces segments. Ce processus est répété pour toutes les paires, et enfin, trois graphes sont générés, présentant la moyenne des métriques sur l’ensemble des paires. Sur ces graphes, l’axe des ordonnées représente la valeur de la métrique, tandis que l’axe des abscisses représente les labels.

**IXI:**

![DiceIXI](https://github.com/user-attachments/assets/42d65526-54a1-40ca-8723-916219843441)

![HausdorffIXI](https://github.com/user-attachments/assets/252c6a90-9895-4d1d-9a6d-ecb3decf86f0)

![IoUIXI](https://github.com/user-attachments/assets/cc7ae813-0c62-4844-94ec-065e91541787)

3. **Construction de Légendes pour Volumes 3D** :  
   Nous générons des captions pour des volumes d'images 3D, une tâche essentielle pour la création de notre base de données d'entraînement. Le code utilisé pour cette tâche se trouve dans le répertoire ci-dessus.

   Exemple pour le fichier `KKI2009-1-FLAIR_brainMajorityDirect.nii` :
   - Fichier JSON associé : [lien_vers_le_fichier.json](data/readmeFILES/caption.json)

### Structure du Projet

- `scripts/` : Contient les scripts de traitement et d'analyse des données.
  


