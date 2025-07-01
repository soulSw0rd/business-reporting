# HyperDash Top-Traders Scraper

Ce projet contient une API simple conçue pour scraper les données des "Top Traders" depuis le site [hyperdash.info](https://hyperdash.info).

## Structure

-   `SRC/`: Contient le code source de l'API et du scraper.
-   `DATA/processed/`: Le dossier où les données scrapées sont sauvegardées au format JSON.
-   `requirements.txt`: La liste des dépendances Python.
-   `venv/`: L'environnement virtuel Python (doit être créé localement).

## Démarrage Rapide

Suivez ces étapes pour lancer et utiliser l'application.

### 1. Prérequis

-   Avoir [Python](https://www.python.org/downloads/) (version 3.8+ recommandée) installé.
-   Avoir [Google Chrome](https://www.google.com/chrome/) installé (le scraper en a besoin).

### 2. Installation

Clonez le projet, puis installez les dépendances dans un environnement virtuel.

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement (sur Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Installer les paquets requis
pip install -r requirements.txt
```

### 3. Lancer le serveur API

Le serveur contient la logique pour exécuter le scraper. Lancez-le avec la commande suivante. **Laissez ce terminal ouvert.**

```bash
uvicorn SRC.api.main:app --host 0.0.0.0 --port 8000
```

Le serveur est maintenant accessible à l'adresse `http://127.0.0.1:8000`.

### 4. Lancer le Scraping

Pour déclencher le processus de scraping, ouvrez un **nouveau terminal** et exécutez la commande `curl` suivante :

```bash
curl -X POST http://127.0.0.1:8000/scrape/top-traders
```

### 5. Vérifier les résultats

-   Le terminal où le serveur tourne affichera les logs du scraping en temps réel.
-   Une fois terminé, un fichier JSON contenant les données des traders sera créé dans le dossier `DATA/processed/`.
-   Le nom du fichier sera horodaté, par exemple : `top_traders_YYYYMMDD_HHMMSS.json`. 