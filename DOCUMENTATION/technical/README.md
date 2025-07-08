# 🚀 CryptoTracker - Plateforme de Suivi Crypto en Temps Réel

Une plateforme fintech complète pour le suivi des cryptomonnaies avec API REST, interface web et données temps réel.

## 📋 Table des Matières

- [🏗️ Architecture](#️-architecture)
- [🚀 Installation](#-installation)
- [💻 Utilisation](#-utilisation)
- [📁 Structure du Projet](#-structure-du-projet)
- [🔧 Configuration](#-configuration)
- [🧪 Tests](#-tests)
- [🐳 Docker](#-docker)
- [📚 Documentation](#-documentation)
- [🤝 Contribution](#-contribution)

## 🏗️ Architecture

Le projet est organisé selon une architecture modulaire moderne :

- **API REST FastAPI** : Endpoints pour données crypto et trading
- **Interface Web Flask** : Dashboard interactif avec données temps réel
- **WebSocket Blockchain.info** : Flux temps réel Bitcoin
- **API Blockchain.com Exchange** : Données de marché et trading
- **Docker Multi-Services** : Déploiement containerisé

## 🚀 Installation

### Prérequis

- Python 3.8+
- pip
- Docker (optionnel)

### Installation Locale

```bash
# Cloner le repository
git clone https://github.com/votre-username/crypto-tracker.git
cd crypto-tracker

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configuration initiale
python scripts/setup_env.py
```

### Installation Docker

```bash
# Lancer tous les services
docker-compose up -d
```

## 💻 Utilisation

### API FastAPI

```bash
# Lancer l'API
cd src/api
uvicorn main:app --reload --port 8000
```

Accès : http://localhost:8000/docs

### Interface Web Flask

```bash
# Lancer l'interface web
cd src/web
python app.py
```

Accès : http://localhost:5000

### Script de Démarrage Unifié

```bash
# Lancer tous les services
python scripts/start.py
```

## 📁 Structure du Projet

```
crypto-tracker/
├── 📁 src/                          # Code source principal
│   ├── 📁 api/                      # API FastAPI
│   │   ├── 📁 v1/                   # Endpoints API v1
│   │   ├── 📁 models/               # Modèles de données
│   │   ├── 📁 services/             # Services métier
│   │   ├── 📁 scripts/              # Scripts API
│   │   └── main.py                  # Point d'entrée FastAPI
│   ├── 📁 web/                      # Interface Flask
│   │   ├── 📁 templates/            # Templates HTML
│   │   └── app.py                   # Application Flask
│   └── 📁 shared/                   # Code partagé
│       ├── 📁 config/               # Configuration
│       └── 📁 core/                 # Utilitaires core
├── 📁 tests/                        # Tests automatisés
├── 📁 docs/                         # Documentation
├── 📁 docker/                       # Configuration Docker
├── 📁 scripts/                      # Scripts utilitaires
├── docker-compose.yml               # Orchestration Docker
├── requirements.txt                 # Dépendances Python
└── README.md                        # Ce fichier
```

## 🔧 Configuration

### Variables d'Environnement

Créer un fichier `.env` :

```bash
# API Configuration
BLOCKCHAIN_API_KEY=your_api_key_here
REDIS_URL=redis://localhost:6379
DATABASE_URL=sqlite:///crypto_tracker.db

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# WebSocket Configuration
WEBSOCKET_URL=wss://ws.blockchain.info/inv
```

### Configuration de Base

Les fichiers de configuration se trouvent dans `src/shared/config/` :

- `settings.py` : Configuration générale
- `database.py` : Configuration base de données
- `redis.py` : Configuration Redis

## 🧪 Tests

### Lancer les Tests

```bash
# Tests API Blockchain
python tests/test_blockchain_api.py

# Tests intégration Zerion (legacy)
python tests/test_zerion_integration.py

# Tests avec pytest
pytest tests/ -v
```

### Couverture de Tests

```bash
# Générer rapport de couverture
pytest --cov=src tests/
```

## 🐳 Docker

### Services Disponibles

- **api** : FastAPI (port 8000)
- **web** : Flask (port 5000)
- **streamlit** : Dashboard Streamlit (port 8501)

### Commandes Docker

```bash
# Construire les images
docker-compose build

# Lancer en mode développement
docker-compose up

# Lancer en arrière-plan
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down
```

## 📚 Documentation

La documentation complète se trouve dans le dossier `docs/` :

- **ARCHITECTURE_COMPLETE_CRYPTOTRACKER.md** : Architecture détaillée
- **INTEGRATION_WEBSOCKET_COMPLETE.md** : Guide WebSocket
- **MIGRATION_BLOCKCHAIN.md** : Migration API Blockchain
- **INTEGRATION_ZERION_GUIDE.md** : Guide Zerion (legacy)
- **REORGANISATION_COMPLETE.md** : Guide de réorganisation

## 🤝 Contribution

### Standards de Code

- **Python** : PEP 8, type hints
- **Tests** : Couverture > 80%
- **Documentation** : Docstrings pour toutes les fonctions
- **Commits** : Messages conventionnels

### Workflow de Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -m 'Ajout: nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrir une Pull Request

### Structure des Commits

```
type(scope): description

Types: feat, fix, docs, style, refactor, test, chore
Scopes: api, web, docker, tests, docs
```

## 📊 Fonctionnalités

### ✅ Implémentées

- [x] API REST FastAPI complète
- [x] Interface web Flask responsive
- [x] WebSocket temps réel Bitcoin
- [x] API Blockchain.com Exchange
- [x] Containerisation Docker
- [x] Tests automatisés
- [x] Documentation complète

### 🚧 En Développement

- [ ] Authentification utilisateur
- [ ] Base de données persistante
- [ ] Cache Redis
- [ ] Monitoring et métriques
- [ ] API rate limiting

### 💡 Roadmap

- [ ] Support multi-cryptomonnaies
- [ ] Alertes personnalisées
- [ ] Portfolio tracking
- [ ] Mobile app
- [ ] Trading automatisé

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Équipe

- **Développeur Principal** : [Votre Nom]
- **Architecture** : Structure modulaire moderne
- **Technologies** : Python, FastAPI, Flask, Docker, WebSocket

---

**⭐ N'hésitez pas à mettre une étoile si ce projet vous plaît !** 