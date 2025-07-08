# 🚀 Guide de démarrage rapide - CryptoTrader Dashboard

## ✅ Dashboard prêt à l'emploi !

Votre dashboard CryptoTrader est maintenant configuré avec :
- ✅ Application Streamlit complète (`app_crypto_only.py`)
- ✅ Données d'exemple réalistes (50 traders, 10 cryptos, 90 jours d'historique)
- ✅ Fichiers JSON structurés dans `data/processed/`
- ✅ Environnement virtuel `ds/` configuré

## 🎯 Comment démarrer

### Lancement rapide
```bash
# Activer l'environnement virtuel
ds\Scripts\activate

# Lancer l'application
streamlit run app_crypto_only.py
```

### Générer de nouvelles données (optionnel)
```bash
# Créer de nouvelles données d'exemple
python generate_sample_data.py
```

> **Note** : Le script `verify_data.py` du dossier `old/` n'est plus utilisé. La validation des données est intégrée dans l'application principale.

## 🌐 Accès au dashboard

Une fois lancé, accédez au dashboard via :
- **URL** : http://localhost:8501
- **Navigation** : Sidebar avec 5 pages principales

## 📊 Données disponibles

### Fichiers JSON générés (data/processed/)
- `top_traders_extended.json` - 50 top traders avec 20+ métriques
- `market_data_extended.json` - 10 cryptomonnaies avec données complètes  
- `historical_data.json` - 90 jours de données historiques OHLC
- `sentiment_data.json` - Sentiment global + signaux de trading

> **Important** : L'export Excel automatique a été retiré pour simplifier le projet. Les données JSON contiennent toutes les informations nécessaires.

## 🔍 Pages du Dashboard

1. **🏠 Vue d'ensemble**
   - KPI généraux (traders, cryptos, points historiques, signaux)
   - Top 10 traders par PnL
   - Prix des cryptomonnaies

2. **👑 Top Traders**
   - Tableau des 50 meilleurs traders
   - Filtres par ROI minimum et nombre de trades
   - Graphiques de distribution et métriques

3. **📊 Analyse Crypto**
   - Sélection de cryptomonnaie individuelle
   - Métriques détaillées (prix, volume, market cap)
   - Données historiques avec graphiques
   - Comparaisons et visualisations

4. **📈 Sentiment**
   - Score de sentiment global du marché
   - Analyse par crypto avec filtres interactifs
   - Signaux de trading détaillés avec confiance
   - Graphiques scatter, radar et barres

5. **⚙️ Données**
   - État des fichiers JSON
   - Diagnostic et monitoring
   - Détails des structures de données

## 🎨 Fonctionnalités clés

### Interactivité avancée
- ✅ Filtres dynamiques (cryptos, traders, ROI, confiance)
- ✅ Graphiques Plotly interactifs (zoom, hover, sélection)
- ✅ Métriques temps réel avec cache optimisé (5 minutes)
- ✅ Tableaux configurables avec tri personnalisé

### Visualisations modernes
- � Graphiques en barres avec couleurs conditionnelles
- 📈 Graphiques scatter pour corrélations
- 🎯 Graphiques radar pour comparaisons multi-dimensionnelles
- 📉 Métriques avec indicateurs visuels (deltas, émojis)

### Analyse de données
- � 50 traders avec métriques complètes (PnL, ROI, Win Rate)
- 💰 10 cryptomonnaies avec données de marché
- � 90 jours de données historiques OHLC
- � Signaux de sentiment avec types et forces

## 🛠️ Personnalisation

### Ajouter de nouvelles cryptos
Modifiez `generate_sample_data.py` :
```python
cryptos = [
    {"symbol": "BTC", "name": "Bitcoin", "base_price": 45000},
    {"symbol": "NEW", "name": "New Crypto", "base_price": 1.50},
    # ... autres cryptos
]
```

### Modifier les métriques
Éditez les fonctions `show_*()` dans `app_crypto_only.py` pour ajouter vos propres calculs.

### Personnaliser l'apparence
Modifiez les couleurs et styles des graphiques Plotly dans l'application.

## 🔧 Résolution de problèmes

### L'application ne démarre pas
```bash
# Vérifier l'environnement Python
ds\Scripts\python.exe --version

# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

### Données manquantes ou corrompues
```bash
# Regénérer toutes les données
python generate_sample_data.py

# Vérifier l'intégrité
python verify_data.py
```

### Erreurs de sérialisation PyArrow
L'application inclut une fonction automatique de nettoyage des données (`clean_dataframe_for_display`) qui résout les problèmes de types mixtes.

### Port déjà utilisé
Si le port 8501 est occupé, Streamlit choisira automatiquement un autre port (8502, 8503...).

## 📞 Support et développement

### Structure du code
- **Application principale** : `app_crypto_only.py`
- **Fonctions de page** : `show_overview()`, `show_top_traders()`, etc.
- **Données** : Dossier `data/processed/`
- **Cache** : TTL de 5 minutes pour optimiser les performances

### Ajouter une nouvelle page
1. Créer une fonction `show_ma_page(scraped_data)` dans `app_crypto_only.py`
2. Ajouter l'option dans la selectbox de navigation
3. Ajouter la condition `elif page == "Ma Page":` dans `main()`

### Debugging
- **Logs Streamlit** : Visibles dans le terminal de lancement
- **Page diagnostic** : "⚙️ Données" dans le dashboard
- **Vérification** : `python verify_data.py`

## 🎉 Dashboard opérationnel !

Votre dashboard est maintenant prêt avec :
- **Interface moderne** et responsive
- **Données réalistes** pré-générées
- **5 pages d'analyse** complètes
- **Filtres et interactions** avancés
- **Visualisations** professionnelles

**Lancez `streamlit run app_crypto_only.py` et explorez vos données crypto !**

## 📈 Métriques disponibles

### Traders (50 profils)
- Total PnL, Win Rate, ROI, Risk Score
- Trading Style, Country, Followers
- Consistency Score, Monthly Return

### Cryptomonnaies (10 coins)
- Prix, Volume 24h, Market Cap
- Variations 24h/7j/30j
- ATH/ATL, Circulating Supply

### Sentiment (8 signaux)
- Score global, Confiance
- Signaux par crypto (Technical, Fundamental, On-Chain)
- Volume social, News sentiment

---
*Dashboard créé avec Streamlit et Plotly*
*Données crypto réalistes générées automatiquement*

# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

### Pas de données live
- Vérifiez votre connexion internet
- Yahoo Finance peut avoir des limites de taux

### API non accessible
- Vérifiez que le port 8000 est libre
- Consultez la page "API Status" dans le dashboard

## 📞 Support et développement

### Ajout de nouvelles pages
1. Créer une fonction `show_ma_page()` dans `app.py`
2. Ajouter l'option dans la sidebar
3. Ajouter la condition dans `main()`

### Debugging
- Logs Streamlit : visible dans le terminal
- Page diagnostic : "API Status" dans le dashboard
- Tests de connectivité : intégrés dans l'interface

## 🎉 Prêt à l'emploi !

Votre dashboard est maintenant opérationnel avec :
- **Interface moderne** et responsive
- **Données réalistes** pré-générées
- **Fonctionnalités avancées** d'analyse
- **Support multi-sources** de données

**Lancez `start_app.bat` et commencez à explorer vos données crypto !**

---
*Dashboard créé avec Streamlit, Plotly, et FastAPI*
*Données crypto via Yahoo Finance API*
