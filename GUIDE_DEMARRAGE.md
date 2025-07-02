# 🚀 Guide de démarrage rapide - CryptoTrader Dashboard

## ✅ Installation terminée avec succès !

Votre dashboard CryptoTrader est maintenant prêt à être utilisé avec :
- ✅ Application Streamlit complète
- ✅ Données d'exemple générées (50 traders, 10 cryptos, 90 jours d'historique)
- ✅ Configuration API FastAPI
- ✅ Fichiers Excel pour analyse externe

## 🎯 Comment démarrer

### Option 1 : Lancement automatique (recommandé)
1. **Double-cliquez** sur `start_app.bat`
2. **Choisissez** le mode de lancement :
   - `1` : Dashboard Streamlit seulement
   - `2` : API FastAPI seulement
   - `3` : Les deux ensemble (recommandé)

### Option 2 : Lancement manuel
```bash
# Activer l'environnement
ds\Scripts\activate

# Dashboard seul
streamlit run app.py

# Ou avec l'API
start uvicorn SRC.api.main:app --host 0.0.0.0 --port 8000
streamlit run app.py
```

## 🌐 URLs d'accès

Une fois lancé, vous pouvez accéder à :
- **Dashboard** : http://localhost:8501
- **API** : http://localhost:8000 (si activée)
- **Documentation API** : http://localhost:8000/docs

## 📊 Données disponibles

### Fichiers JSON générés :
- `top_traders_extended.json` - 50 top traders avec métriques complètes
- `market_data_extended.json` - 10 cryptomonnaies avec données de marché
- `historical_data.json` - 90 jours de données historiques
- `sentiment_data.json` - Signaux et sentiment de marché

### Fichier Excel :
- `crypto_dashboard_data.xlsx` - Toutes les données en format Excel

## 🔍 Pages du Dashboard

1. **🏠 Vue d'ensemble** - KPI et status général
2. **👑 Top Traders** - Classement et analyse des traders
3. **📊 Analyse Crypto** - Analyse détaillée par crypto
4. **🔥 Données Live** - Prix en temps réel (Yahoo Finance)
5. **📈 Performance Portfolio** - Simulateur de portfolio
6. **⚙️ API Status** - Diagnostic et monitoring

## 🎨 Fonctionnalités clés

### Interactivité
- ✅ Filtres dynamiques (dates, montants, win rates)
- ✅ Graphiques interactifs Plotly (zoom, hover, sélection)
- ✅ Métriques temps réel avec variations
- ✅ Cache intelligent pour les performances

### Visualisations
- 📈 Graphiques en chandelles pour les prix
- 🥧 Graphiques en secteurs pour les allocations
- 📊 Histogrammes pour les distributions
- 🎯 Graphiques de corrélation
- 📉 Métriques de performance avec delta

### Données
- 🔄 Mise à jour automatique via cache (5 minutes)
- 🌐 Données live via Yahoo Finance API
- 📁 Support des fichiers JSON locaux
- 🔌 Intégration API FastAPI optionnelle

## 🛠️ Personnalisation

### Ajouter de nouvelles cryptos
Modifiez la liste dans `generate_sample_data.py` et relancez :
```bash
python generate_sample_data.py
```

### Modifier l'apparence
Éditez la section CSS dans `app.py` (lignes 20-50)

### Nouvelles métriques
Ajoutez vos calculs dans les fonctions `show_*()` de `app.py`

## 🔧 Résolution de problèmes

### L'application ne démarre pas
```bash
# Vérifier l'environnement
ds\Scripts\python.exe --version

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
