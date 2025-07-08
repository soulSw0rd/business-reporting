# CryptoTrader Dashboard

## Description

Un dashboard web simple pour analyser les performances des traders de cryptomonnaies. L'application utilise Streamlit pour créer une interface interactive avec des graphiques et des prédictions basées sur des données de trading.


## Comment ça marche

Le dashboard affiche des informations sur :
- Les performances des traders (profits/pertes)
- Les prix des cryptomonnaies populaires
- Des prédictions générées par des modèles de machine learning
- L'analyse du sentiment du marché

Toutes les données sont stockées dans des fichiers JSON et mises à jour automatiquement.

## Lancement rapide

### Option 1: Script PowerShell
```powershell
.\start_dashboard.ps1
```

### Option 2: Script Batch
```batch
start_dashboard.bat
```

### Option 3: Commande directe
```bash
streamlit run crypto_dashboard.py --server.port 8504
```

Une fois lancé, ouvrez votre navigateur sur: http://localhost:8504

## Pages disponibles

### Vue d'ensemble
- Résumé des métriques principales
- Graphique des meilleurs traders
- Aperçu du marché crypto

### Prédictions ML
- 50 prédictions avec niveau de confiance
- Filtres pour trier les résultats
- Graphiques de distribution

### Analyse Crypto
- Prix en temps réel de 10 cryptomonnaies
- Graphiques interactifs

### Sentiment Marché
- Analyse des tendances du marché
- Évolution temporelle du sentiment

### Données & Config
- Statut des sources de données
- Configuration du système

## Structure du projet

```
Projet-Etienne/
├── crypto_dashboard.py          # Application principale
├── start_dashboard.ps1          # Script de lancement PowerShell
├── start_dashboard.bat          # Script de lancement Batch
├── requirements.txt             # Dépendances Python
├── PRODUCTION/                  # Modules de production
│   ├── core/                    # Logique métier
│   ├── dashboard/               # Composants interface
│   └── models/                  # Modèles ML
├── RESOURCES/                   # Données et configuration
│   ├── configs/                 # Fichiers de configuration
│   └── data/                    # Données JSON
└── venv/                        # Environnement virtuel Python
```

## Installation

### Prérequis
- Python 3.8 ou plus récent
- pip (gestionnaire de paquets Python)

### Installation des dépendances
```bash
pip install -r requirements.txt
```

### Dépendances principales
- streamlit - Framework web
- pandas - Manipulation de données
- plotly - Graphiques interactifs
- numpy - Calculs numériques

## Configuration

Le fichier `RESOURCES/configs/app_config.json` contient la configuration :
- Port du dashboard (8504 par défaut)
- Chemins vers les données
- Paramètres de cache

## Données utilisées

Les données sont stockées dans `RESOURCES/data/processed/` :
- `market_data.json` - Prix et informations des cryptomonnaies
- `top_traders_extended.json` - Performances des traders
- `sentiment_data.json` - Données de sentiment du marché
- `historical_data.json` - Historique des prix
- `predictions_summary.json` - Prédictions ML

## Dépannage

### Le dashboard ne se lance pas
1. Vérifiez que Python est installé : `python --version`
2. Installez les dépendances : `pip install -r requirements.txt`
3. Essayez un autre port : `streamlit run crypto_dashboard.py --server.port 8505`

### Données manquantes
1. Vérifiez que le dossier `RESOURCES/data/processed/` existe
2. Générez des données d'exemple : `python generate_sample_data.py`
3. Utilisez le bouton "Rafraîchir" dans l'interface

### Erreurs de port
Si le port 8504 est occupé, modifiez le port dans `app_config.json` ou utilisez la commande avec un autre port.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Dernières modifications

- Suppression de la page "Top Traders" 
- Correction de l'erreur sur la page "Sentiment Marché"
- Suppression de la page "Visualisations Avancées"
- Nettoyage des fichiers temporaires
- Interface simplifiée à 4 pages principales

Version: 1.0.0
Date: 2025-01-08
URL: http://localhost:8504