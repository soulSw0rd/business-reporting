# 📊 CryptoTrader Dashboard - Business Intelligence

Dashboard moderne de business intelligence pour l'analyse crypto basé sur Streamlit, avec des données enrichies et des visualisations interactives.

## 🚀 Fonctionnalités principales

### 📊 Dashboard Streamlit
- **🏠 Vue d'ensemble** : KPI du marché, top traders, prix crypto
- **👑 Top Traders** : Analyse des 50 meilleurs traders avec filtres avancés
- **📊 Analyse Crypto** : Analyse détaillée par cryptomonnaie avec données historiques
- **📈 Sentiment** : Analyse de sentiment du marché avec signaux de trading
- **⚙️ Données** : Monitoring et diagnostic des fichiers de données

### 🎯 Sources de données
- **Données structurées** : 50 top traders avec métriques complètes
- **Marché crypto** : 10 cryptomonnaies avec données temps réel simulées
- **Données historiques** : 90 jours de données OHLC pour 5 cryptos
- **Sentiment** : Signaux de trading et analyse de sentiment
- **Format Excel** : Export automatique pour analyse externe

## 🛠️ Installation et Configuration

### Prérequis
- Python 3.12+ 
- Environnement virtuel (déjà configuré dans `ds/`)

### Démarrage rapide
```bash
# Activation de l'environnement
ds\Scripts\activate

# Lancement de l'application
streamlit run app_crypto_only.py
```

### URLs d'accès
- **Dashboard** : http://localhost:8501

## 📁 Structure du projet

```
business-reporting/
├── 🎯 FICHIERS PRINCIPAUX
│   ├── app_crypto_only.py            # ✅ Application Streamlit principale
│   ├── generate_sample_data.py       # ✅ Génération de données réalistes  
│   └── envsetup.py                   # ✅ Configuration environnement
│
├── 📊 DONNÉES
│   └── data/
│       └── processed/                # ✅ Données JSON structurées
│           ├── top_traders_extended.json      # 50 traders avec métriques
│           ├── market_data_extended.json      # 10 cryptos avec données détaillées
│           ├── historical_data.json           # 90 jours OHLC pour 5 cryptos
│           └── sentiment_data.json            # Signaux et sentiment marché
│
├── 📋 CONFIGURATION
│   ├── requirements.txt              # ✅ Dépendances Python optimisées
│   ├── .streamlit/
│   │   └── config.toml               # Configuration Streamlit
│   └── ds/                           # ✅ Environnement virtuel
│
├── 📚 DOCUMENTATION
│   ├── README.md                     # Guide principal
│   ├── GUIDE_DEMARRAGE.md           # Instructions utilisateur
│   ├── PROJET_COMPLETE.md           # Bilan projet
│   ├── TECHNICAL_SUMMARY.md         # Résumé technique
│   └── DOCUMENTATION/
│       ├── GRAPHIQUES_ANALYSE.md    # Guide des visualisations
│       ├── MERMAID_VISUALIZATIONS.md # Diagrammes Mermaid
│       └── DATA_PROCESSING_FLOW.md  # Flux de traitement données
│
└── 📁 old/                          # ⚠️ Anciennes versions (ne pas utiliser)
    ├── app.py                        # Version obsolète
    ├── app_new.py                    # Version obsolète  
    ├── config.py                     # Configuration obsolète
    └── test_*.py                     # Tests obsolètes
```
│       ├── top_traders_extended.json      # 50 traders avec métriques
│       ├── market_data_extended.json      # 10 cryptos avec données détaillées
│       ├── historical_data.json           # 90 jours OHLC pour 5 cryptos
│       └── sentiment_data.json            # Signaux et sentiment marché
│
├── 📋 CONFIGURATION
│   ├── requirements.txt              # ✅ Dépendances Python optimisées
│   ├── .streamlit/
│   │   └── config.toml               # Configuration Streamlit
│   └── ds/                           # ✅ Environnement virtuel
│
├── 📚 DOCUMENTATION
│   ├── README.md                     # Guide principal
│   ├── GUIDE_DEMARRAGE.md           # Instructions utilisateur
│   ├── PROJET_COMPLETE.md           # Bilan projet
│   ├── TECHNICAL_SUMMARY.md         # Résumé technique
│   └── DOCUMENTATION/
│       ├── GRAPHIQUES_ANALYSE.md    # Guide des visualisations
│       ├── MERMAID_VISUALIZATIONS.md # Diagrammes Mermaid
│       └── DATA_PROCESSING_FLOW.md  # Flux de traitement données
│
└── 📁 old/                          # ⚠️ Anciennes versions (ne pas utiliser)
    ├── app.py                        # Version obsolète
    ├── app_new.py                    # Version obsolète  
    ├── config.py                     # Configuration obsolète
    └── test_*.py                     # Tests obsolètes
```

## 🎯 Utilisation du Dashboard

### Navigation
Le dashboard est organisé en 5 pages principales :

1. **🏠 Vue d'ensemble**
   - Métriques KPI (traders, cryptos, données historiques, signaux)
   - Top 10 traders par PnL avec graphique interactif
   - Prix des cryptomonnaies avec visualisation

2. **👑 Top Traders**
   - Classement des 50 meilleurs traders
   - Filtres par ROI minimum, nombre de trades
   - Métriques de performance et distributions
   - Graphiques de corrélation et analyses

3. **📊 Analyse Crypto**
   - Sélection de cryptomonnaies individuelles
   - Métriques détaillées (prix, volume, market cap)
   - Données historiques avec graphiques OHLC
   - Comparaisons et analyses de marché

4. **📈 Sentiment**
   - Score de sentiment global du marché
   - Analyse par cryptomonnaie avec filtres interactifs
   - Signaux de trading détaillés avec âge et confiance
   - Visualisations multi-dimensionnelles (scatter, radar)
   - Statistiques des signaux bullish/bearish

5. **⚙️ Données**
   - État des fichiers de données JSON
   - Diagnostic et monitoring
   - Détails des structures de données

### Fonctionnalités interactives
- **Filtres dynamiques** : Cryptos, traders, ROI, confiance
- **Graphiques Plotly** : Zoom, hover, sélection interactive
- **Métriques temps réel** : Mise à jour avec cache intelligent
- **Tableaux configurables** : Tri, colonnes optimisées

## 📊 Données et formats

### Fichiers actifs du projet

#### 🎯 Applications principales
- **`app_crypto_only.py`** : Application Streamlit principale (seule version utilisée)
- **`generate_sample_data.py`** : Génération de données réalistes pour les 4 fichiers JSON
- **`envsetup.py`** : Configuration et setup de l'environnement

#### 📊 Données (data/processed/)
- **`top_traders_extended.json`** : 50 traders avec 20+ métriques (PnL, ROI, trades)
- **`market_data_extended.json`** : 10 cryptos avec données complètes (prix, volume, market cap)
- **`historical_data.json`** : 90 jours de données OHLC pour 5 cryptos
- **`sentiment_data.json`** : Signaux de trading et sentiment marché

#### 📋 Configuration
- **`requirements.txt`** : Dépendances Python optimisées (streamlit, plotly, pandas)
- **`.streamlit/config.toml`** : Configuration Streamlit
- **`ds/`** : Environnement virtuel Python configuré

#### 📚 Documentation
- **`README.md`** : Guide principal (ce fichier)
- **`GUIDE_DEMARRAGE.md`** : Instructions de démarrage utilisateur
- **`PROJET_COMPLETE.md`** : Bilan complet du projet
- **`TECHNICAL_SUMMARY.md`** : Résumé technique détaillé
- **`DOCUMENTATION/GRAPHIQUES_ANALYSE.md`** : Guide des visualisations
- **`DOCUMENTATION/MERMAID_VISUALIZATIONS.md`** : Diagrammes Mermaid
- **`DOCUMENTATION/DATA_PROCESSING_FLOW.md`** : Flux de traitement données

#### ⚠️ Dossier old/ (OBSOLÈTE - Ne pas utiliser)
Ce dossier contient d'anciennes versions du projet qui ne sont **plus utilisées** :
- `app.py`, `app_new.py`, `app_backup*.py` : Versions obsolètes de l'application
- `config.py` : Configuration obsolète
- `test_*.py`, `debug_*.py` : Scripts de test obsolètes
- `verify_data.py` : Script de vérification obsolète

> **Important** : Seuls les fichiers à la racine du projet sont utilisés. Le dossier `old/` est conservé uniquement à des fins d'historique.
- `historical_data.json` : 90 jours de données OHLC
- `sentiment_data.json` : Sentiment global + 8 signaux crypto

### Génération de nouvelles données
```bash
# Générer de nouvelles données d'exemple
python generate_sample_data.py

# Vérifier l'intégrité des données
python verify_data.py
```

### Format des données traders
```json
{
  "trader_id": "TopTrader_001",
  "rank": 1,
  "username": "Trader4523", 
  "total_pnl": 145230.50,
  "win_rate": 0.847,
  "roi_percentage": 234.7,
  "trading_style": "Swing Trading",
  "country": "Singapore",
  "followers": 5432,
  "risk_score": 7,
  "consistency_score": 87.3
}
```

## 🔧 Personnalisation

### Ajout de nouvelles cryptos
Modifiez la liste dans `generate_sample_data.py` :
```python
cryptos = [
    {"symbol": "NEW", "name": "New Crypto", "base_price": 1.50},
    # ... autres cryptos
]
```

### Nouvelles pages
1. Créer une fonction `show_nouvelle_page(scraped_data)` dans `app_crypto_only.py`
2. Ajouter l'option dans la selectbox de navigation
3. Ajouter la condition dans `main()`

### Styling et couleurs
Modifier les palettes de couleurs dans les graphiques Plotly pour personnaliser l'apparence.

## 🚨 Résolution de problèmes

### Données manquantes
```bash
# Regénérer les données d'exemple
python generate_sample_data.py

# Vérifier les fichiers dans data/processed/
python verify_data.py
```

### Erreurs de packages
```bash
# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

### Erreurs de sérialisation PyArrow
L'application inclut une fonction `clean_dataframe_for_display()` qui résout automatiquement les problèmes de types mixtes dans les DataFrames.

## 📊 Métriques et KPI

### Traders
- **Total PnL** : Profit/Loss total en USD
- **Win Rate** : Taux de réussite des trades (0-1)
- **ROI** : Retour sur investissement en %
- **Risk Score** : Score de risque (1-10)
- **Consistency** : Score de consistance (60-95%)

### Cryptomonnaies
- **Prix** : Prix actuel en USD
- **Change 24h/7j/30j** : Variations en %
- **Volume 24h** : Volume de trading
- **Market Cap** : Capitalisation boursière
- **ATH/ATL** : Plus haut/bas historique

### Sentiment
- **Score Global** : Score de sentiment (-1 à +1)
- **Label** : Bullish/Bearish/Neutral
- **Confiance** : Niveau de confiance (0-100%)
- **Signaux** : Par type (Technical, Fundamental, On-Chain)

## 📞 Support

### Logs et debugging
- Logs Streamlit : Visibles dans le terminal de lancement
- Page diagnostic : "⚙️ Données" dans le dashboard
- Vérification : `python verify_data.py`

### Fichiers essentiels
- Application : `app_crypto_only.py`
- Données : Dossier `data/processed/`
- Configuration : `.streamlit/config.toml`
- Dépendances : `requirements.txt`

## � Licence
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
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
