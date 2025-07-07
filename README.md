# Crypto Prediction API

API pour collecter des données de marché sur les cryptomonnaies à partir de diverses sources publiques. Le projet a été nettoyé pour ne conserver que les modules stables et fonctionnels.

## État Actuel du Projet

L'API est stable et agrège les données des sources suivantes :

-   **CoinGecko** : Fournit les métriques de base pour le Bitcoin (prix, volume, capitalisation boursière).
-   **Etherscan** : Scrape le top 25 des comptes les plus riches en Ethereum.
-   **Alternative.me (Fear & Greed Index)** : Récupère l'indice de sentiment de marché "Fear & Greed".
-   **Binance (Funding Rates)** : Récupère les taux de financement pour les paires BTC/USDT et ETH/USDT.

Les scrapers qui dépendaient de Selenium (comme Hyperdash) ou qui se sont avérés instables (comme Blockchain.com) ont été retirés.

## Installation et Lancement

### Prérequis

-   Python 3.10+
-   `pip` et `venv`

### Instructions

1.  **Clonez le projet et placez-vous dans le répertoire :**

    ```bash
    git clone <URL_DU_PROJET>
    cd Projet-Etienne
    ```

2.  **Créez un environnement virtuel et activez-le :**

    ```bash
    python -m venv venv
    # Sur Windows
    .\venv\Scripts\activate
    # Sur macOS/Linux
    source venv/bin/activate
    ```

3.  **Installez les dépendances :**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Lancez le serveur API :**
    Le serveur se lancera sur `http://localhost:8000` et se rechargera automatiquement si des modifications sont apportées au code.

    ```bash
    python -m uvicorn src.api.main:app --reload
    ```

## Utilisation de l'API

L'API expose un endpoint principal pour récupérer toutes les données agrégées.

### Endpoint `/market-data`

-   **URL** : `http://localhost:8000/market-data`
-   **Méthode** : `GET`
-   **Description** : Renvoie un objet JSON contenant l'ensemble des métriques collectées depuis toutes les sources de données actives.
-   **Exemple de commande `curl`** :

    ```bash
    curl http://localhost:8000/market-data
    ```

-   **Exemple de réponse :**

    ```json
    {
      "coingecko_btc": {
        "price_usd": 108710,
        "market_cap_usd": 2162386219204,
        "volume_24h_usd": 21008073795,
        "change_24h_percent": 0.62751,
        "circulating_supply": 19888856,
        "last_updated": "2025-07-07T11:43:59.320Z"
      },
      "top_eth_accounts": [
        {
          "rank": 1,
          "address": "0x00000000...03d7705Fa",
          "name_tag": "Beacon Deposit Contract",
          "balance_ether": "64,327,618.31065726 ETH",
          "source": "Etherscan"
        }
      ],
      "fear_and_greed_index": {
        "current_value": 73,
        "classification": "Greed",
        "timestamp": "2025-07-07T02:00:00"
      },
      "funding_rates": {
        "BTCUSDT": {
          "funding_rate": 0.00003438,
          "funding_time": "2025-07-07T10:00:00.007000",
          "mark_price": 109016.3
        },
        "ETHUSDT": {
          "funding_rate": 0.0001,
          "funding_time": "2025-07-07T10:00:00.007000",
          "mark_price": 2577.57985659
        }
      }
    }
    ```

---

## Structure du Projet

L'arborescence des fichiers a été restructurée pour suivre une logique claire et fonctionnelle.

```
/
├── 📁 admin/              # Configuration (Docker, etc.) et scripts d'administration.
├── 📁 archive/            # Données brutes et traitées issues des exécutions passées.
├── 📁 src/                # Code source principal de l'application.
│   ├── 📁 api/             # Point d'entrée de l'API FastAPI (main.py).
│   ├── 📁 core/             # Logique métier : validation, nettoyage, moteur de prédiction.
│   └── 📁 scrapers/         # Modules de scraping pour les différentes sources de données.
├── 📁 development/         # Scripts et outils utilisés pour le développement.
├── 📁 documentation/       # Documentation du projet (log de nettoyage, etc.).
├── .gitignore             # Fichiers ignorés par Git.
├── LICENSE                # Licence du projet.
├── README.md              # Ce fichier.
└── requirements.txt       # Dépendances Python du projet.
```

---

## Standards de Développement

Pour maintenir la qualité et la cohérence du projet, tout nouveau code doit respecter les standards suivants :

### 1. Documentation du Code

Toute fonction ou classe doit être documentée en utilisant le format suivant :

```python
def nom_de_la_fonction(param1: type) -> type:
    """
    OBJECTIF : Description claire et concise de ce que fait la fonction.
    
    PARAMÈTRES :
    - param1 (type) : Description du paramètre.
    
    RETOURNE :
    - type : Description de la valeur de retour.
    
    LOGIQUE :
    1. Étape 1 de la logique interne.
    2. Étape 2...
    """
    # Code ici
```

### 2. Responsabilité Unique

Chaque fonction et chaque module doit avoir une seule et unique responsabilité. Évitez les fonctions "fourre-tout".

### 3. Pas de Code Dupliqué

Centralisez la logique réutilisable dans des fonctions utilitaires (comme `src/scrapers/common/driver_setup.py`).

### 4. Tests

(Futur) Tout nouveau code devra être accompagné de tests unitaires et d'intégration.

---

## Démarrage Rapide

1.  **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```

2.  **Lancer l'API** :
    Le serveur peut être lancé via un gestionnaire comme Uvicorn.
    ```bash
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
    ```

3.  **Consulter la documentation de l'API** :
    Une fois le serveur lancé, la documentation interactive est disponible à l'adresse : `http://127.0.0.1:8000/docs`. 