# -*- coding: utf-8 -*-
"""
Blockchain API Client
Module pour interagir avec des API publiques de blockchain (ex: Blockchair).
"""

import requests
import json
from typing import List, Dict, Any, Optional

class BlockchainApiClient:
    """
    Client pour récupérer des données de blockchain via des API publiques.
    Remplace le scraping, qui est devenu peu fiable.
    """
    def __init__(self):
        self.base_url = "https://api.blockchair.com/bitcoin"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoPredictionApp/1.0'
        })

    def get_latest_blocks(self, limit: int = 5) -> Optional[List[Dict[str, Any]]]:
        """
        Récupère les derniers blocs depuis l'API de Blockchair.
        Documentation: https://blockchair.com/api/docs#link_001
        """
        print(f"🌍 Interrogation de l'API Blockchair pour les {limit} derniers blocs...")
        url = f"{self.base_url}/blocks"
        params = {'limit': limit}

        try:
            response = self.session.get(url, params=params, timeout=20)
            response.raise_for_status()
            
            data = response.json()
            
            # La donnée est dans la clé 'data'
            blocks = data.get('data')
            
            if not blocks:
                print("❌ Aucune donnée de bloc retournée par l'API.")
                return None

            print(f"✅ {len(blocks)} blocs récupérés avec succès.")
            return blocks

        except requests.RequestException as e:
            print(f"❌ Erreur de requête vers l'API Blockchair: {e}")
            return None
        except json.JSONDecodeError:
            print("❌ Impossible de décoder la réponse JSON de l'API.")
            return None

# --- Point d'entrée pour test ---
if __name__ == '__main__':
    client = BlockchainApiClient()
    
    print("--- Test du client API Blockchair ---")
    latest_blocks = client.get_latest_blocks(limit=3)
    
    if latest_blocks:
        # Sauvegarde des résultats pour inspection
        with open("blockchair_latest_blocks.json", "w", encoding='utf-8') as f:
            json.dump(latest_blocks, f, indent=2, ensure_ascii=False)
        
        print("\nRésultats sauvegardés dans 'blockchair_latest_blocks.json'")
        print(json.dumps(latest_blocks, indent=2, ensure_ascii=False))
    else:
        print("\nLe test a échoué. Aucune donnée n'a été récupérée.") 