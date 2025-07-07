# -*- coding: utf-8 -*-
"""
OBJECTIF : Scraper les métriques de marché pour le Bitcoin via l'API CoinGecko.
"""
import requests
from typing import Dict, Any, Optional

# L'ID pour le Bitcoin sur CoinGecko est 'bitcoin'
COIN_ID = "bitcoin"
# La devise de comparaison
VS_CURRENCY = "usd"

# URL de l'API CoinGecko pour les données de marché
URL = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency={VS_CURRENCY}&ids={COIN_ID}"

def scrape_coingecko_metrics() -> Optional[Dict[str, Any]]:
    """
    OBJECTIF : Récupérer les métriques de marché clés pour le Bitcoin depuis l'API CoinGecko.
    
    LOGIQUE :
    1. Interroge l'endpoint public de CoinGecko pour les données de marché du Bitcoin.
    2. L'API retourne une liste contenant un seul objet JSON avec toutes les métriques.
    3. Extrait les données pertinentes (prix, market cap, volume, etc.).
    4. Cette méthode est très fiable car elle s'appuie sur une API structurée.
    
    RETOURNE :
    - Un dictionnaire contenant les métriques de CoinGecko, ou None en cas d'erreur.
    """
    try:
        response = requests.get(URL)
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
        data = response.json()
        
        # L'API retourne une liste d'assets, nous ne prenons que le premier (et unique)
        if not data:
            print("❌ Aucune donnée retournée par l'API CoinGecko.")
            return None
        
        asset_data = data[0]
        
        metrics = {
            "price_usd": asset_data.get("current_price"),
            "market_cap_usd": asset_data.get("market_cap"),
            "volume_24h_usd": asset_data.get("total_volume"),
            "change_24h_percent": asset_data.get("price_change_percentage_24h"),
            "circulating_supply": asset_data.get("circulating_supply"),
            "last_updated": asset_data.get("last_updated"),
        }
        
        # Filtre les valeurs None au cas où l'API change
        cleaned_metrics = {k: v for k, v in metrics.items() if v is not None}
        
        return {"coingecko_btc": cleaned_metrics}

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de requête vers l'API CoinGecko: {e}")
        return None
    except (json.JSONDecodeError, IndexError) as e:
        print(f"❌ Erreur lors du traitement de la réponse de CoinGecko: {e}")
        return None 