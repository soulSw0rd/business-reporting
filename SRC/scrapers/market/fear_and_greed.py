# -*- coding: utf-8 -*-
"""
OBJECTIF : Scraper l'indice "Fear & Greed" depuis l'API publique d'Alternative.me.
"""

import requests
from datetime import datetime
from typing import Dict, Any, Optional
import json

FEAR_AND_GREED_API_URL = "https://api.alternative.me/fng/?limit=1"

def scrape_fear_and_greed_index() -> Optional[Dict[str, Any]]:
    """
    OBJECTIF : Récupérer la dernière valeur de l'indice Fear & Greed.
    
    RETOURNE :
    - Optional[Dict[str, Any]] : Un dictionnaire contenant la valeur et la classification
                                 de l'indice, ou None en cas d'erreur.
    
    LOGIQUE :
    1. Interroge l'API d'Alternative.me.
    2. Vérifie que la réponse est valide et contient des données.
    3. Extrait et formate les données de l'indice le plus récent.
    4. Gère les erreurs de connexion et de parsing.
    """
    print("📊 Scraping Fear & Greed Index...")
    try:
        response = requests.get(FEAR_AND_GREED_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'data' in data and len(data['data']) > 0:
            latest_data = data['data'][0]
            result = {
                "current_value": int(latest_data['value']),
                "classification": latest_data['value_classification'],
                "timestamp": datetime.fromtimestamp(int(latest_data['timestamp'])).isoformat()
            }
            print(f"✅ Fear & Greed: {result['classification']} ({result['current_value']})")
            return result
        else:
            print("❌ Fear & Greed: Pas de données trouvées dans la réponse.")
            return None
    except requests.RequestException as e:
        print(f"❌ Fear & Greed: Erreur de connexion à l'API : {e}")
        return None
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"❌ Fear & Greed: Erreur de parsing des données : {e}")
        return None 