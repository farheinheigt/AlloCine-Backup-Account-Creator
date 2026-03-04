# AlloCine Backup Account Creator

Sauvegarde les notes de films et de séries d'un profil AlloCiné public au format CSV.

> **Fork de [CLeBeRFR/AlloCine-Backup-Account-Creator](https://github.com/CLeBeRFR/AlloCine-Backup-Account-Creator)**
> Merci à [@CLeBeRFR](https://github.com/CLeBeRFR) pour le projet original qui a rendu tout cela possible.

## Pourquoi ce fork ?

Le projet original (dernière mise à jour en 2020) fonctionne toujours, mais présentait quelques problèmes :

- Les titres étaient préfixés par `poster de ` / `poster du ` (provenant de l'attribut `alt` des balises `<img>`)
- Le format CSV utilisait un séparateur `;` avec virgule décimale, peu pratique pour l'import dans d'autres outils
- Pas d'option pour choisir le format de sortie
- Installation automatique de paquets via `os.system("pip3 install ...")` sans demander

### Modifications apportées

- **Nettoyage des titres** : suppression automatique des préfixes `poster de/du/d'`
- **Nouveau format `--format clean`** : CSV standard avec séparateur `,`, point décimal, headers `title,rating` — compatible avec des outils comme [mesfilms](https://github.com/farheinheigt/mesfilms)
- **Options CLI** : `--films-only`, `--series-only`, `--format` via `argparse`
- **HTTPS** : utilisation de `https://` au lieu de `http://`
- **User-Agent** : ajout d'un header User-Agent pour éviter les blocages
- **Progression** : affichage de la progression pendant le scraping
- **Code modernisé** : f-strings, session requests, structure plus propre

## Prérequis

- Python 3.7+
- `beautifulsoup4` et `requests`

```bash
pip install beautifulsoup4 requests
```

## Utilisation

```bash
# Format original (Nom;Note avec virgule décimale)
python Allocine_Backup_Account_Creator.py https://www.allocine.fr/membre-XXXXX/

# Format clean (title,rating avec point décimal)
python Allocine_Backup_Account_Creator.py https://www.allocine.fr/membre-XXXXX/ --format clean

# Films uniquement
python Allocine_Backup_Account_Creator.py https://www.allocine.fr/membre-XXXXX/ --films-only

# Séries uniquement
python Allocine_Backup_Account_Creator.py https://www.allocine.fr/membre-XXXXX/ --series-only
```

### Trouver son URL de profil

1. Connectez-vous sur [allocine.fr](https://www.allocine.fr)
2. Cliquez sur votre avatar → "Mon profil"
3. L'URL ressemble à : `https://www.allocine.fr/membre-Z20100120021920830649555/`

### Fichiers générés

| Format | Films | Séries |
|--------|-------|--------|
| `standard` (défaut) | `liste_notes_films.csv` | `liste_notes_series.csv` |
| `clean` | `notes_films.csv` | `notes_series.csv` |

**Format standard :**
```csv
Nom;Note
Inception;4,5
The Matrix;4,0
```

**Format clean :**
```csv
title,rating
"Inception",4.5
"The Matrix",4.0
```

## Utilisation avec mesfilms

Le format `clean` est directement compatible avec l'option `--my-ratings` de [mesfilms](https://github.com/farheinheigt/mesfilms) :

```bash
# 1. Exporter ses notes
python Allocine_Backup_Account_Creator.py https://www.allocine.fr/membre-XXXXX/ --format clean --films-only

# 2. Utiliser dans mesfilms
mesfilms /Volumes/MonDisque/Films --my-ratings notes_films.csv
```

## Notes

- Le scraping se fait sur les **profils publics** d'AlloCiné. Assurez-vous que votre profil est visible publiquement.
- Les notes AlloCiné sont sur une échelle de **0.5 à 5.0** (par pas de 0.5).
- Le script respecte le site — pas de requêtes parallèles, une page à la fois.
- Pour les gros profils (1000+ films), le scraping peut prendre quelques minutes.

## Licence

[MIT](LICENSE) — Projet original par [@CLeBeRFR](https://github.com/CLeBeRFR)
