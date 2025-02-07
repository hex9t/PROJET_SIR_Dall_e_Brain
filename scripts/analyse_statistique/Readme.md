# Boîte à Moustache - Génération de Boxplots

## Description
Ce programme Python génère des **boxplots** à partir des données contenues dans des fichiers **JSON**. Les boxplots sont ensuite sauvegardés sous forme d'images dans un dossier de sortie spécifié. Chaque boxplot représente la distribution des volumes de données, avec les valeurs minimales, les quartiles, et les éventuels points aberrants.

## Prérequis
Avant d'exécuter ce programme, vous devez avoir installé les bibliothèques suivantes :

- `json` (inclus par défaut dans Python)
- `matplotlib` (pour la création des graphiques)

Vous pouvez installer `matplotlib` via pip :

```bash
pip install matplotlib
```
# Convertisseur JSON en CSV - Analyse Statistique du Cerveau

## Description
Ce programme Python convertit les fichiers de données d'analyse statistique du cerveau au format JSON en fichiers CSV. Chaque fichier JSON contenant des informations sur les statistiques de différentes régions du cerveau est traité et converti en un fichier CSV. Ce programme est conçu pour être utilisé sur un dossier contenant plusieurs fichiers JSON.

## Prérequis
Avant d'exécuter ce programme, vous devez avoir Python installé sur votre machine. Le programme utilise les bibliothèques suivantes :

- `os` (inclus par défaut dans Python)
- `json` (inclus par défaut dans Python)
- `csv` (inclus par défaut dans Python)
- `sys` (inclus par défaut dans Python)

## Utilisation

### Exemple d'exécution
Sur un système Windows, vous pouvez exécuter le programme avec la commande suivante :

```bash
python .\statistiques_cerveux.py <input_folder>
```
# Analyse Statistique du Cerveau - Volume et Ratio par Groupe

## Description
Ce programme Python analyse les volumes des structures cérébrales et calcule diverses statistiques, telles que la moyenne, l'écart-type, les quartiles, l'intervalle interquartile (IQR), ainsi que l'identification des valeurs aberrantes pour chaque région du cerveau. Les données sont regroupées par sexe et groupe d'âge. Le programme traite des fichiers CSV contenant des informations sur les volumes des régions cérébrales, puis génère des fichiers JSON contenant les statistiques par groupe.

## Prérequis
Avant d'exécuter ce programme, assurez-vous que Python est installé sur votre machine. Le programme utilise les bibliothèques suivantes :

- `csv` (inclus par défaut dans Python)
- `os` (inclus par défaut dans Python)
- `json` (inclus par défaut dans Python)
- `sys` (inclus par défaut dans Python)
- `collections` (inclus par défaut dans Python)
- `statistics` (inclus par défaut dans Python)
- `numpy` (bibliothèque externe à installer)

## Installation de `numpy`
Si vous ne disposez pas de la bibliothèque `numpy`, installez-la avec la commande suivante :

```bash
pip install numpy
