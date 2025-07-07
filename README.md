# CryptoTrader Dashboard - Business Intelligence

Ce projet combine un scraper de données crypto (HyperDash Top-Traders) avec un dashboard Streamlit moderne pour l'analyse et la visualisation de données de trading.

## 🚀 Fonctionnalités principales

### 📊 Dashboard Streamlit
- **Vue d'ensemble** : KPI crypto, performance du marché, status des données
- **Top Traders** : Analyse des meilleurs traders avec filtres avancés
- **Analyse Crypto** : Prix, volumes, market cap, sentiment par crypto
- **Données Live** : Prix en temps réel via Yahoo Finance
- **Portfolio** : Simulateur de performance avec allocation personnalisée
- **API Status** : Monitoring de l'API et diagnostic système

### 🔌 API FastAPI
- Scraping automatisé des données HyperDash
- Endpoints RESTful pour récupérer les données
- Documentation interactive (Swagger)
- Cache et optimisation des performances

### 📈 Sources de données
- **Données scrapées** : Top traders depuis HyperDash.info
- **Données live** : Prix crypto via Yahoo Finance API
- **Données simulées** : Génération automatique pour les tests

## 🛠️ Installation et Configuration

### Prérequis
- Python 3.12+ 
- Google Chrome (pour le scraping)
- Environnement virtuel (déjà configuré dans `ds/`)

### Démarrage rapide
1. **Lancement simple** : Double-cliquez sur `start_app.bat`
2. **Choisissez le mode** :
   - Option 1 : Dashboard Streamlit seulement
   - Option 2 : API FastAPI seulement  
   - Option 3 : Les deux (recommandé)

### Installation manuelle des dépendances
```bash
# Activation de l'environnement
ds\Scripts\activate

# Installation des packages
pip install -r requirements.txt
```

### Lancement manuel
```bash
# Dashboard Streamlit
streamlit run app.py

# API FastAPI 
uvicorn SRC.api.main:app --host 0.0.0.0 --port 8000

# Les deux ensemble
start uvicorn SRC.api.main:app --host 0.0.0.0 --port 8000
streamlit run app.py
```

## 📁 Structure du projet

```
business-reporting/
├── app.py                     # Application Streamlit principale
├── config.py                  # Configuration de l'application
├── start_app.bat             # Script de lancement
├── requirements.txt          # Dépendances Python
├── .streamlit/
│   └── config.toml           # Configuration Streamlit
├── SRC/                      # Code source de l'API
│   ├── api/                  # Endpoints FastAPI
│   └── core/                 # Logique métier
├── data/
│   └── processed/            # Données scrapées (JSON)
│       ├── top_traders_data.json
│       └── market_data.json
├── ds/                       # Environnement virtuel Python
└── DOCUMENTATION/            # Documentation technique
```

## 🎯 Utilisation du Dashboard

### Navigation
Le dashboard est organisé en 6 pages principales :

1. **🏠 Vue d'ensemble**
   - Status API et données disponibles
   - Performance des principales cryptos
   - Distribution ROI des top traders
   - Accès aux données scrapées

2. **👑 Top Traders**
   - Classement des meilleurs traders
   - Filtres par ROI, nombre de trades, win rate
   - Graphiques de corrélation et performance
   - Données détaillées des traders

3. **📊 Analyse Crypto**
   - Sélection de cryptomonnaies
   - Analyse prix, volume, market cap, sentiment
   - Métriques temps réel
   - Graphiques interactifs

4. **🔥 Données Live**
   - Prix crypto en temps réel (Yahoo Finance)
   - Comparaison multi-crypto
   - Performance relative
   - Données historiques

5. **📈 Performance Portfolio**
   - Simulateur d'allocation de portfolio
   - Calcul de performance historique
   - Métriques de risque (drawdown, etc.)
   - Paramètres de rééquilibrage

6. **⚙️ API Status**
   - Status de connexion API
   - Diagnostic des dépendances
   - Test des endpoints
   - Monitoring des fichiers de données

### Fonctionnalités interactives
- **Filtres dynamiques** : Dates, cryptos, traders
- **Graphiques Plotly** : Zoom, hover, sélection
- **Métriques temps réel** : Mise à jour automatique
- **Cache intelligent** : Optimisation des performances

## 🔗 Intégration API

### Endpoints disponibles
- `GET /health` - Status de l'API
- `GET /top-traders` - Données des top traders
- `GET /market` - Données de marché
- `POST /scrape` - Déclenchement du scraping

### Utilisation des données
Le dashboard peut fonctionner en mode :
- **Hybride** : API + données locales + données live
- **Local** : Fichiers JSON uniquement  
- **Live** : Yahoo Finance pour les prix crypto

### Configuration API
Dans `config.py` :
```python
API_BASE_URL = "http://127.0.0.1:8000"
API_TIMEOUT = 10
CACHE_TTL = 300  # 5 minutes
```

## 📊 Données et formats

### Fichiers JSON (data/processed/)
- `top_traders_data.json` : Données des traders
- `market_data.json` : Vue d'ensemble du marché

### Format des données traders
```json
{
  "trader_id": "TopTrader_001",
  "rank": 1,
  "username": "CryptoKing2024", 
  "total_pnl": 145230.50,
  "win_rate": 0.847,
  "roi_percentage": 234.7,
  "trading_style": "Swing Trading",
  // ...
}
```

## 🔧 Personnalisation

### Ajout de nouvelles métriques
Modifier les fonctions dans `app.py` :
- `generate_crypto_sample_data()` pour les données crypto
- `get_scraped_data()` pour les données locales

### Nouvelles pages
1. Créer une fonction `show_nouvelle_page()`
2. Ajouter dans la selectbox de navigation
3. Ajouter la condition dans `main()`

### Styling CSS
Modifier la section CSS dans `app.py` pour personnaliser l'apparence.

## 🚨 Résolution de problèmes

### API non accessible
    ```bash
# Vérifier si l'API est démarrée
curl http://localhost:8000/health

# Redémarrer l'API
uvicorn SRC.api.main:app --host 0.0.0.0 --port 8000
```

### Données manquantes
- Vérifier le dossier `data/processed/`
- Exécuter le scraping depuis l'API
- Utiliser les données de démonstration

### Erreurs de packages
    ```bash
# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

## 📞 Support

### Logs et debugging
- Logs Streamlit : Terminal de lancement
- Logs API : `http://localhost:8000/docs`
- Diagnostic : Page "API Status" du dashboard

### URLs importantes
- **Dashboard** : http://localhost:8501
- **API** : http://localhost:8000  
- **Documentation** : http://localhost:8000/docs

## 📄 Licence
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
curl -X POST http://127.0.0.1:8000/scrape/top-traders
```

### 5. Vérifier les résultats

-   Le terminal où le serveur tourne affichera les logs du scraping en temps réel.
-   Une fois terminé, un fichier JSON contenant les données des traders sera créé dans le dossier `DATA/processed/`.
-   Le nom du fichier sera horodaté, par exemple : `top_traders_YYYYMMDD_HHMMSS.json`. 