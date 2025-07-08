# -*- coding: utf-8 -*-
"""
OBJECTIF : Récupérer l'indice Fear & Greed depuis l'API d'alternative.me.
"""
import requests
from typing import Dict, Any, Optional

URL = "https://api.alternative.me/fng/?limit=1"

def scrape_fear_and_greed_index() -> Optional[Dict[str, Any]]:
    """
    OBJECTIF : Récupérer la dernière valeur de l'indice Fear & Greed.

    LOGIQUE :
    1. Fait une requête GET à l'API de alternative.me.
    2. Extrait la valeur et la classification du sentiment de la réponse.

    RETOURNE :
    - Un dictionnaire avec les données de l'indice, ou None en cas d'erreur.
    """
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "data" in data and data["data"]:
            fng_data = data["data"][0]
            metrics = {
                "value": fng_data.get("value"),
                "value_classification": fng_data.get("value_classification"),
            }
            print("✅ Indice Fear & Greed récupéré avec succès.")
            return metrics
        else:
            print("❌ Erreur Fear & Greed : Le format des données a changé ou est vide.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur Fear & Greed : Échec de la requête vers l'API : {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"❌ Erreur Fear & Greed : Structure de données inattendue : {e}")
        return None 