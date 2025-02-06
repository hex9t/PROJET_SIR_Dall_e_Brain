# Projet Deep Learning pour la Génération d'Images de Cerveau à partir de Prompt Text
![Image comparant les deux Atlas](data/readmeFILES/images/logo.png)

Dans ce projet, nous continuons le travail déjà effectué par [GLucas01/projet_SIR](https://github.com/GLucas01/projet_SIR) pour construire une base de données afin d'appliquer le deep learning et générer des images de cerveaux à partir de prompts textuels. 
![Image comparant les deux Atlas](images/code.png)
## Structure de la base de données (sur disque dure)
### Nouvelle Arborescence utilisée
├── SIR  
│   ├── FL  
│   │   ├── Kirby  
│   │   │   ├── brain  
│   │   │   ├── NG  
│   │   │   ├── descriptions  
│   │   │   ├── descriptions_simple  
│   │   │   ├── captions_3d_simple  
│   │   │   ├── captions_3d  
│   │   │   ├── analyse_statistics 
│   │   │   └── analyse_statistics_simplified  



- `descriptions` : contient les descriptions des images avec **ANATOMIE_IBSR.info.csv**  
- `descriptions_simple` : contient les descriptions des images avec **simplified_IBSR.info.csv**  
- `captions_3d` : contient les captions générés avec **captions_generator_advanced.py**  
- `captions_3d_simple` : contient les captions générés avec **simple_captions.py**  
- `analyse_statistics` : contient 6 fichiers JSON analytiques avec **ANATOMIE_IBSR.info.csv**
- `analyse_statistics_simplified` : contient 6 fichiers JSON analytiques avec **simplified_IBSR.info.csv**  

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

   4. **Comparaison des deux atlas**:

Cette étape est cruciale, car elle nous permet de déterminer si les deux atlas sont similaires ou non. Pour cela, un script nommé COMPARAISON.py a été créé. Son principal objectif est de comparer deux images segmentées, c'est-à-dire les deux segments d'une même image. Il applique ensuite les métriques IoU, DICE et la distance de Hausdorff sur chaque label de ces segments. Ce processus est répété pour toutes les paires, et enfin, trois graphes sont générés, présentant la moyenne des métriques sur l’ensemble des paires. Sur ces graphes, l’axe des ordonnées représente la valeur de la métrique, tandis que l’axe des abscisses représente les labels.

 **Les résultats de comparaison pour IXI:**

![DiceIXI](https://github.com/user-attachments/assets/42d65526-54a1-40ca-8723-916219843441)

![HausdorffIXI](https://github.com/user-attachments/assets/252c6a90-9895-4d1d-9a6d-ecb3decf86f0)

![IoUIXI](https://github.com/user-attachments/assets/cc7ae813-0c62-4844-94ec-065e91541787)

 **Les résultats de comparaison pour OASIS:**

![DiceOasis](https://github.com/user-attachments/assets/f1ae8424-8bac-4012-8831-7666733e2d43)

![HausdorffOasis](https://github.com/user-attachments/assets/3a07e213-1d7f-4525-99fd-73aa2b97de8c)

![IoUOasis](https://github.com/user-attachments/assets/e1bdfad1-7769-429c-9e68-a5085a810ebc)

 **Les résultats de comparaison pour Kirby:**

![DiceKirby](https://github.com/user-attachments/assets/a9bb3bbd-3ced-4814-a60b-1b07778018bc)

![HausdorffKirby](https://github.com/user-attachments/assets/fd463dab-f619-4a2f-b2d6-bc7b779c841a)

![IoUKirby](https://github.com/user-attachments/assets/baf85831-e78b-49fb-949e-66dbb3e54154)

   
# Construction de Légendes pour Volumes 3D

## Description du processus

Cette section explique comment utiliser les codes pour générer des légendes (captions) pour les volumes 3D.

### 1. Générer les Descriptions

Pour commencer, il est essentiel d’avoir des descriptions. Pour cela, utilisez le script `description_generator.py` avec la commande suivante :

```bash
python script.py "SIR/statistiques/IBSR/labels.csv" "SIR/FL/Kirby/brain" "SIR/FL/Kirby/descriptions"
```

Les résultats seront enregistrés dans le dossier `descriptions`. Ces fichiers pourront ensuite être utilisés pour générer les légendes avec le script `caption_generator_advanced.py` comme suit :

```bash
python caption_generator_advanced.py data_kirby descriptions_3D ./metafolder/ captions_test --var 5
```

**Attention** : Les résultats générés avec cette méthode ne sont pas parfaits et ne répondent pas entièrement aux exigences des légendes. Il est donc préférable d’utiliser le script `simple_captions.py` pour obtenir des résultats de meilleure qualité.

### 2. Générer des Descriptions Simples

Avant d'utiliser `simple_captions.py`, il est nécessaire de créer des descriptions simples. Utilisez le script `simple_descriptions.py` pour cela. Vous devrez seulement ajuster les chemins au début du code pour qu’ils pointent vers le dossier `descriptions`.

Une fois que les nouveaux fichiers CSV sont générés, vous pouvez ensuite exécuter le script `simple_captions.py` pour créer des légendes plus détaillées et adaptées. Voici un exemple de commande :

```bash
python simple_captions.py D:\SIR\T2\IXI\seg D:\SIR\T2\IXI\descriptions_simple .\metafolder\ D:\SIR\T2\IXI\captions_3d_simple\captions_exhaustive
```

**Important** : N’oubliez pas de **changer manuellement** la modalité des légendes à la sortie, car nous n’avons pas eu le temps de l’adapter pour chaque base de données. Cette modification se fait dans la variable `a` de la fonction `process_folder()`.

### 3. Dossier des Métadonnées

Enfin, veillez à ne pas oublier d’inclure le dossier des métadonnées dans vos répertoires de travail.

  


