# 📚 Guide Utilisateur - Crypto-Tracker

## 🎯 Vue d'ensemble

**Crypto-Tracker** est un système d'intelligence artificielle avancé pour l'analyse et la prédiction de la profitabilité des traders de cryptomonnaies. Il combine scraping de données en temps réel, machine learning et visualisations interactives pour fournir des insights précieux sur les performances des traders.

## 🚀 Démarrage Rapide

### 1. Installation

```bash
# Cloner le projet
git clone <repository-url>
cd crypto-tracker

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows:
venv\Scripts\activate.ps1
# OU
venv\Scripts\activate.bat

# Sur Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
python ADMIN/scripts/setup_environment.py
```

### 2. Lancement de l'Application

**🚀 Méthode Recommandée (Automatique)**
```bash
# Windows - Double-clic sur le fichier ou:
start_crypto_tracker.bat

# Windows PowerShell:
.\start_crypto_tracker.ps1

# Python (toutes plateformes):
python start_crypto_tracker.py
```

**⚙️ Méthode Manuelle**
```bash
# 1. Activer l'environnement virtuel
venv\Scripts\activate.ps1  # Windows
source venv/bin/activate   # Linux/Mac

# 2. Démarrer le dashboard
streamlit run PRODUCTION/dashboard/crypto_dashboard.py

# 3. Ou utiliser le script d'administration
python ADMIN/scripts/run_application.py
```

### 3. Première Utilisation

1. **Accédez au dashboard** : http://localhost:8501
2. **Explorez les données** : Naviguez vers "🏠 Vue d'ensemble"
3. **Testez les prédictions** : Allez dans "🔮 Prédictions ML"
4. **Analysez les traders** : Consultez "👑 Top Traders"

## 📋 Fonctionnalités Principales

### 🏠 Vue d'ensemble
- **Métriques système** : Nombre de traders, cryptos suivies, statut des modèles
- **Graphiques synthèse** : Performance des top traders, aperçu marché
- **Statut en temps réel** : Santé des composants, dernières mises à jour

### 👑 Top Traders
- **Classement détaillé** : Traders classés par performance
- **Métriques avancées** : PnL, win rate, exposition, ROI
- **Analyse comparative** : Comparaison multi-critères
- **Filtres personnalisés** : Tri par période, performance, risque

### 🔮 Prédictions ML

#### Mode Données Réelles
- **Sélection trader** : Choisir parmi les traders disponibles
- **Prédictions horizons** : Court terme (7j) et long terme (30j)
- **Métriques contextuelles** : Données utilisées pour la prédiction
- **Analyse comparative** : Prédictions batch sur plusieurs traders

#### Mode Démonstration
- **Paramètres trader** : PnL 7j/30j, win rate, exposition long
- **Contexte marché** : Prix BTC, Fear & Greed Index, funding rate
- **Prédictions interactives** : Test avec paramètres personnalisés

### 📊 Analyse Crypto
- **Données marché** : Prix, volumes, capitalisation
- **Métriques techniques** : Indicateurs de volatilité, tendances
- **Corrélations** : Relations entre différentes cryptomonnaies

### 📈 Sentiment Marché
- **Score global** : Sentiment général du marché
- **Analyse par crypto** : Sentiment spécifique par actif
- **Signaux trading** : Indicateurs basés sur le sentiment

### ⚙️ Données & Config
- **Statut fichiers** : Âge, taille, type des données
- **Configuration système** : Paramètres actuels
- **Actions maintenance** : Cache, réentraînement, rapports

## 🎛️ Interface Utilisateur

### Navigation
- **Sidebar** : Menu principal avec sélection de pages
- **Bouton rafraîchissement** : Mise à jour des données
- **Informations système** : Version, environnement, statut ML

### Visualisations
- **Graphiques interactifs** : Plotly pour exploration des données
- **Jauges de prédiction** : Visualisation des probabilités
- **Tableaux dynamiques** : Tri, filtrage, export des données
- **Métriques en temps réel** : Indicateurs clés avec deltas

### Styles et Thèmes
- **Design moderne** : Interface épurée et professionnelle
- **Couleurs adaptatives** : Codes couleur par niveau de confiance
- **Responsive** : Adaptation à différentes tailles d'écran

## 🔮 Système de Prédiction

### Modèle Random Forest
- **Algorithme** : Ensemble de 100 arbres de décision
- **Features** : 14 variables (trader + marché + dérivées)
- **Horizons** : 7 jours (court terme) et 30 jours (long terme)
- **Précision** : ~75% sur données de test

### Features Utilisées

#### Trader Features
- **PnL 7 jours** : Performance financière récente
- **PnL 30 jours** : Performance financière étendue
- **Win Rate** : Taux de réussite des trades (0-1)
- **Long Percentage** : Exposition en positions longues (0-100%)

#### Market Features
- **Prix Bitcoin** : Prix actuel normalisé
- **Fear & Greed Index** : Sentiment de marché (0-100)
- **Funding Rate** : Taux de financement perpétuel

#### Derived Features
- **PnL Ratio** : Rapport PnL 7j/30j
- **Risk Score** : Score de risque basé sur l'exposition
- **Trader-Market Alignment** : Alignement trader/marché
- **Market Risk Factor** : Facteur de risque marché

### Interprétation des Résultats

#### Niveaux de Confiance
- **🟢 Très forte (>80%)** : Très fortement profitable
- **🟢 Forte (70-80%)** : Fortement profitable
- **🟡 Modérée (60-70%)** : Potentiellement profitable
- **🟠 Faible (40-60%)** : Incertain
- **🔴 Très faible (<40%)** : Peu/très peu probable

#### Métriques Complémentaires
- **Probabilité** : Score de confiance du modèle (0-100%)
- **Feature Importance** : Influence relative de chaque facteur
- **Contexte** : Données utilisées pour la prédiction

## 📊 Données et Sources

### Sources de Données
- **Hyperdash** : Données des traders, performances, métriques
- **CoinGecko** : Prix des cryptomonnaies, volumes, capitalisation
- **Fear & Greed Index** : Sentiment de marché
- **Funding Rates** : Taux de financement des contrats perpétuels

### Fréquence de Mise à Jour
- **Données traders** : Quotidienne
- **Prix crypto** : Temps réel (cache 10 minutes)
- **Sentiment** : Quotidienne
- **Funding rates** : Horaire

### Stockage et Cache
- **Format** : JSON pour interopérabilité
- **Localisation** : `RESOURCES/data/processed/`
- **Cache** : 10 minutes par défaut (configurable)
- **Backup** : Sauvegarde automatique des données critiques

## ⚙️ Configuration

### Fichier Principal
**Localisation** : `RESOURCES/configs/app_config.json`

### Sections Configurables
- **Dashboard** : Port, cache, thème, limites d'affichage
- **ML** : Paramètres modèles, seuils, features
- **Scraping** : Délais, tentatives, sources
- **Logging** : Niveaux, formats, rotation

### Modification de Configuration
```python
from PRODUCTION.core.config_manager import get_config, config_manager

# Lire une configuration
cache_ttl = get_config("dashboard", "cache_ttl")

# Modifier une configuration
config_manager.update_config("dashboard", "cache_ttl", 300)
config_manager.save_config()
```

## 🔧 Maintenance

### Actions Courantes
- **Vider le cache** : Bouton dans "⚙️ Données & Config"
- **Réentraîner modèle** : Bouton dans "⚙️ Données & Config"
- **Vérifier logs** : `ADMIN/logs/crypto_tracker.log`

### Dépannage

#### Problèmes Courants
1. **Modèle non entraîné** : Cliquer sur "Réentraîner le modèle"
2. **Données manquantes** : Vérifier `RESOURCES/data/processed/`
3. **Erreurs de prédiction** : Consulter les logs
4. **Performance lente** : Vider le cache

#### Logs et Debugging
```bash
# Consulter les logs
tail -f ADMIN/logs/crypto_tracker.log

# Mode debug
# Modifier app_config.json : "debug": true
```

## 📈 Bonnes Pratiques

### Utilisation Optimale
1. **Actualiser régulièrement** : Utiliser le bouton rafraîchissement
2. **Analyser le contexte** : Vérifier les métriques contextuelles
3. **Comparer horizons** : Utiliser 7j ET 30j pour vision complète
4. **Surveiller confiance** : Privilégier prédictions haute confiance

### Interprétation des Résultats
- **Prédictions ≠ Garanties** : Utiliser comme aide à la décision
- **Contextualiser** : Prendre en compte conditions de marché
- **Diversifier** : Ne pas se baser sur un seul trader/signal
- **Historique** : Analyser la cohérence temporelle

## 🆘 Support

### Ressources
- **Documentation technique** : `DOCUMENTATION/technical/`
- **Guide installation** : `DOCUMENTATION/guides/installation_guide.md`
- **Spécifications API** : `DOCUMENTATION/api_docs/`

### Contact
- **Issues** : Créer un ticket sur le repository
- **Améliorations** : Proposer via pull request
- **Questions** : Consulter la documentation technique

---

**Version** : 1.0.0  
**Dernière mise à jour** : 2025-01-08  
**Auteur** : Crypto-Tracker Team 