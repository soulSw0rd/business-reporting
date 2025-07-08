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
    1. Fait une requête GET à l'API publique de CoinGecko.
    2. Vérifie si la requête a réussi et si les données sont présentes.
    3. Extrait les données pertinentes (prix, market cap, volume) de la réponse JSON.
    
    RETOURNE :
    - Un dictionnaire contenant les métriques extraites, ou None en cas d'erreur.
    """
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
        
        data = response.json()
        
        # Vérifier si la réponse contient des données
        if not data:
            print("❌ Erreur CoinGecko : Réponse vide de l'API.")
            return None
            
        # Extraire les métriques du premier (et unique) élément
        btc_data = data[0]
        
        metrics = {
            "price": btc_data.get("current_price"),
            "market_cap": btc_data.get("market_cap"),
            "total_volume": btc_data.get("total_volume"),
            "price_change_24h": btc_data.get("price_change_percentage_24h"),
        }
        
        print("✅ Données de CoinGecko récupérées avec succès.")
        return metrics

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur CoinGecko : Échec de la requête vers l'API : {e}")
        return None
    except (IndexError, KeyError) as e:
        print(f"❌ Erreur CoinGecko : Le format des données a changé : {e}")
        return None 